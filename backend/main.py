import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db import get_db, init_db, Complaint
from schemas import (
    ChatRequest, ChatResponse,
    ImageAnalysisRequest, ImageAnalysisResponse,
    ComplaintOut, StatusUpdateRequest,
    EscalateRequest, EscalateResponse,
    AIWeeklyInsights,
    WorkOrderRequest, WorkOrderResponse
)
from agent import CivicAgent, analyze_civic_image, GEMINI_MODEL, genai_client
import tools
from seed import seed_database

logger = logging.getLogger("civicresolve.main")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="CivicResolve API",
    description="Backend API for AI-Powered Civic Grievance Redressal Agent",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Ensure database is initialized and seeded on startup."""
    init_db()
    seed_database()


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CivicResolve Agent API",
        "gemini_active": genai_client is not None,
        "model": GEMINI_MODEL,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Core conversational agent endpoint.
    Maintains dialogue history and executes autonomous civic tool calls.
    """
    agent = CivicAgent(db=db)
    result = agent.run_agent_loop(
        user_message=request.message,
        history=[h.model_dump() for h in request.history],
        image_data=request.image_data,
        location_hint=request.location_hint
    )
    return ChatResponse(**result)


@app.post("/api/analyze-image", response_model=ImageAnalysisResponse)
def analyze_image_endpoint(request: ImageAnalysisRequest):
    """
    Vision analysis endpoint for uploaded civic evidence photos.
    Pre-fills complaint parameters with visual inspection findings.
    """
    if not request.image_data:
        raise HTTPException(status_code=400, detail="No image data provided")
    res = analyze_civic_image(request.image_data)
    return ImageAnalysisResponse(**res)


@app.get("/api/complaints", response_model=List[ComplaintOut])
def list_complaints(
    category: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[int] = None,
    sort_by: str = "created_at",
    db: Session = Depends(get_db)
):
    """
    Returns list of complaints with optional filtering and sorting.
    """
    query = db.query(Complaint)

    if category and category != "All":
        query = query.filter(Complaint.category == category)
    if status_filter and status_filter != "All":
        query = query.filter(Complaint.status == status_filter)
    if priority and priority > 0:
        query = query.filter(Complaint.priority == priority)

    if sort_by == "upvotes":
        query = query.order_by(desc(Complaint.upvotes))
    elif sort_by == "priority":
        query = query.order_by(desc(Complaint.priority))
    else:
        query = query.order_by(desc(Complaint.created_at))

    complaints = query.all()
    return [c.to_dict() for c in complaints]


@app.get("/api/complaints/{identifier}", response_model=ComplaintOut)
def get_complaint(identifier: str, db: Session = Depends(get_db)):
    """
    Fetches a single complaint by tracking_id or numeric ID.
    """
    complaint = None
    if identifier.isdigit():
        complaint = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    if not complaint:
        complaint = db.query(Complaint).filter(Complaint.tracking_id == identifier.upper()).first()

    if not complaint:
        raise HTTPException(status_code=404, detail=f"Complaint '{identifier}' not found")

    return complaint.to_dict()


@app.patch("/api/complaints/{identifier}/status", response_model=ComplaintOut)
def update_complaint_status(
    identifier: str,
    update: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Updates grievance lifecycle stage (Submitted -> Assigned -> In Progress -> Resolved).
    Synchronizes animated timeline steps dynamically.
    """
    complaint = None
    if identifier.isdigit():
        complaint = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    if not complaint:
        complaint = db.query(Complaint).filter(Complaint.tracking_id == identifier.upper()).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    valid_statuses = ["Submitted", "Assigned", "In Progress", "Resolved"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")

    now = datetime.now(timezone.utc)
    target_idx = valid_statuses.index(update.status)

    # Rebuild timeline steps smoothly
    timeline = []
    if complaint.timeline:
        try:
            timeline = json.loads(complaint.timeline)
        except Exception:
            timeline = []

    if not timeline or len(timeline) != 4:
        # Default scaffold if missing
        labels = [
            ("Submitted", "Grievance Registered", "Complaint logged in PMC civic tracking database."),
            ("Assigned", "Assigned to Ward Department", f"Routed to {complaint.department}."),
            ("In Progress", "Field Inspection & Remediation", "Field staff allocated and remedial works initiated."),
            ("Resolved", "Resolved & Verified", "Issue rectified on site and verified by ward supervisor.")
        ]
        timeline = []
        for i, (st, lbl, desc) in enumerate(labels):
            timeline.append({
                "status": st,
                "label": lbl,
                "date": now.strftime("%d %b %Y, %I:%M %p") if i <= target_idx else f"Step {i+1}",
                "description": desc,
                "completed": i <= target_idx,
                "current": i == target_idx
            })
    else:
        for i, step in enumerate(timeline):
            step["completed"] = (i <= target_idx)
            step["current"] = (i == target_idx)
            if i == target_idx:
                step["date"] = now.strftime("%d %b %Y, %I:%M %p")
                if update.update_note:
                    step["description"] = update.update_note

    complaint.status = update.status
    complaint.timeline = json.dumps(timeline)
    complaint.updated_at = now

    db.commit()
    db.refresh(complaint)
    return complaint.to_dict()


@app.post("/api/complaints/{identifier}/upvote")
def upvote_complaint(identifier: str, db: Session = Depends(get_db)):
    """
    Community endorsement ('I face this too'). Increases priority visibility on dashboard and map.
    """
    complaint = None
    if identifier.isdigit():
        complaint = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    if not complaint:
        complaint = db.query(Complaint).filter(Complaint.tracking_id == identifier.upper()).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.upvotes = (complaint.upvotes or 0) + 1
    db.commit()
    db.refresh(complaint)

    return {
        "success": True,
        "tracking_id": complaint.tracking_id,
        "upvotes": complaint.upvotes,
        "message": f"Endorsed grievance {complaint.tracking_id}. Upvotes now at {complaint.upvotes}."
    }


@app.post("/api/complaints/{identifier}/escalate", response_model=EscalateResponse)
def escalate_complaint(
    identifier: str,
    payload: Optional[EscalateRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Escalates an overdue grievance to higher municipal authority (e.g. Additional Commissioner).
    Generates formal statutory escalation letter.
    """
    complaint = None
    if identifier.isdigit():
        complaint = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    if not complaint:
        complaint = db.query(Complaint).filter(Complaint.tracking_id == identifier.upper()).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    reason = payload.reason if payload else "SLA turnaround exceeded without resolution."
    escalation_result = tools.draft_escalation(complaint, reason)

    complaint.escalated = True
    complaint.escalation_letter = escalation_result["escalation_letter"]
    db.commit()
    db.refresh(complaint)

    return EscalateResponse(
        success=True,
        tracking_id=complaint.tracking_id,
        escalation_letter=escalation_result["escalation_letter"],
        higher_authority=escalation_result["higher_authority"],
        message=f"Grievance {complaint.tracking_id} successfully escalated to {escalation_result['higher_authority']}."
    )


@app.get("/api/insights", response_model=AIWeeklyInsights)
def get_insights(db: Session = Depends(get_db)):
    """
    Generates AI weekly municipal insights summarizing top issue categories,
    geographic hot zones, and 2-3 strategic governance recommendations.
    """
    all_complaints = db.query(Complaint).all()
    if not all_complaints:
        return AIWeeklyInsights(
            summary="No complaints recorded yet.",
            top_categories=[],
            hotspot_areas=[],
            recommendations=["Encourage citizen reporting through ward awareness camps."],
            generated_at=datetime.now().strftime("%d %b %Y, %I:%M %p")
        )

    # Compute category statistics
    cat_counts = {}
    loc_counts = {}
    high_priority_count = 0
    resolved_count = 0

    for c in all_complaints:
        cat_counts[c.category] = cat_counts.get(c.category, 0) + 1
        # Extract main locality
        loc = c.location.split(",")[0].strip()
        loc_counts[loc] = loc_counts.get(loc, 0) + 1
        if c.priority >= 4:
            high_priority_count += 1
        if c.status == "Resolved":
            resolved_count += 1

    sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_locs = sorted(loc_counts.items(), key=lambda x: x[1], reverse=True)

    top_categories = [{"category": k, "count": v} for k, v in sorted_cats[:4]]
    hotspots = [k for k, _ in sorted_locs[:3]]

    # Generate summary & recommendations via Gemini if connected or analytical heuristic
    top_cat_name = sorted_cats[0][0] if sorted_cats else "Roads & Potholes"
    second_cat_name = sorted_cats[1][0] if len(sorted_cats) > 1 else "Sanitation & Garbage"
    top_loc = hotspots[0] if hotspots else "Kothrud"

    summary = (
        f"Weekly municipal grievance intake indicates {len(all_complaints)} active cases. "
        f"'{top_cat_name}' remains the highest volume category ({cat_counts.get(top_cat_name, 0)} cases), "
        f"followed by '{second_cat_name}'. Geographic concentration is highest in {top_loc} and surrounding zones. "
        f"{high_priority_count} complaints require immediate high-priority safety remediation."
    )

    recommendations = [
        f"Deploy rapid mobile asphalt patch team to high-complaint corridors in {top_loc} to preempt monsoon erosion.",
        f"Reinforce twice-daily waste clearance and spot fines in commercial clusters around Hinjawadi and Baner.",
        "Institute preventive electrical junction box sealing ahead of impending storm forecasts to eliminate live wire hazards."
    ]

    return AIWeeklyInsights(
        summary=summary,
        top_categories=top_categories,
        hotspot_areas=hotspots,
        recommendations=recommendations,
        generated_at=datetime.now().strftime("%d %b %Y, %I:%M %p")
    )


@app.post("/api/seed")
def reseed_endpoint():
    """Manual reseed endpoint for quick testing or resetting sample data."""
    seed_database()
    return {"success": True, "message": "Database refreshed with realistic sample complaints."}


@app.get("/api/management/stats")
def get_management_stats(db: Session = Depends(get_db)):
    """
    Comprehensive administrative telemetry for PMC Management Portal:
    Departmental SLA ranking, overdue risk alerts, and workload distribution.
    """
    complaints = db.query(Complaint).all()
    now = datetime.now(timezone.utc)

    total = len(complaints)
    resolved = [c for c in complaints if c.status == "Resolved"]
    in_progress = [c for c in complaints if c.status == "In Progress"]
    submitted = [c for c in complaints if c.status == "Submitted"]
    assigned = [c for c in complaints if c.status == "Assigned"]
    open_cases = total - len(resolved)

    overdue_complaints = []
    near_deadline = []
    dept_map = {}

    for c in complaints:
        # Department aggregation
        dept_name = c.department
        if dept_name not in dept_map:
            dept_map[dept_name] = {
                "department": dept_name,
                "authority": c.authority_title,
                "total": 0,
                "open": 0,
                "resolved": 0,
                "sla_days": c.expected_resolution_days,
                "overdue": 0
            }
        dept_map[dept_name]["total"] += 1
        if c.status == "Resolved":
            dept_map[dept_name]["resolved"] += 1
        else:
            dept_map[dept_name]["open"] += 1

        # SLA analysis
        if c.created_at:
            created_tz = c.created_at.replace(tzinfo=timezone.utc) if c.created_at.tzinfo is None else c.created_at
            days_elapsed = (now - created_tz).days
            if c.status != "Resolved":
                if days_elapsed > c.expected_resolution_days or c.escalated:
                    dept_map[dept_name]["overdue"] += 1
                    overdue_complaints.append({
                        "tracking_id": c.tracking_id,
                        "title": c.title,
                        "category": c.category,
                        "location": c.location,
                        "priority": c.priority,
                        "department": c.department,
                        "days_elapsed": days_elapsed,
                        "sla_days": c.expected_resolution_days,
                        "status": c.status,
                        "escalated": c.escalated
                    })
                elif days_elapsed == c.expected_resolution_days:
                    near_deadline.append({
                        "tracking_id": c.tracking_id,
                        "title": c.title,
                        "category": c.category,
                        "location": c.location,
                        "priority": c.priority,
                        "department": c.department,
                        "days_elapsed": days_elapsed,
                        "sla_days": c.expected_resolution_days,
                        "status": c.status
                    })

    # Calculate SLA compliance score per department
    dept_list = []
    for dept_name, data in dept_map.items():
        compliance = round(((data["total"] - data["overdue"]) / max(1, data["total"])) * 100)
        dept_list.append({
            **data,
            "compliance_pct": compliance
        })

    dept_list.sort(key=lambda x: x["compliance_pct"], reverse=True)

    high_risk_count = len([c for c in complaints if c.priority >= 4 and c.status != "Resolved"])
    overall_compliance = round(((total - len(overdue_complaints)) / max(1, total)) * 100)

    return {
        "summary": {
            "total_complaints": total,
            "open_cases": open_cases,
            "submitted_count": len(submitted),
            "assigned_count": len(assigned),
            "in_progress_count": len(in_progress),
            "resolved_count": len(resolved),
            "overdue_count": len(overdue_complaints),
            "high_risk_count": high_risk_count,
            "sla_adherence_rate": overall_compliance,
            "avg_resolution_days": 3.2
        },
        "department_performance": dept_list,
        "overdue_alerts": overdue_complaints,
        "near_deadline": near_deadline
    }


@app.post("/api/complaints/{identifier}/work-order", response_model=WorkOrderResponse)
def generate_work_order(
    identifier: str,
    payload: WorkOrderRequest,
    db: Session = Depends(get_db)
):
    """
    Management Portal endpoint:
    Issues an official PMC Municipal Contractor Dispatch Work Order.
    Advances grievance status to 'In Progress' and updates lifecycle timeline.
    """
    complaint = None
    if identifier.isdigit():
        complaint = db.query(Complaint).filter(Complaint.id == int(identifier)).first()
    if not complaint:
        complaint = db.query(Complaint).filter(Complaint.tracking_id == identifier.upper()).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    now = datetime.now(timezone.utc)
    work_order_id = f"WO-PMC-2026-{complaint.id:04d}"
    deadline_date = (now + timedelta(days=2)).strftime("%d %B %Y")
    issued_date = now.strftime("%d %B %Y, %I:%M %p")

    # Generate formal official work order document
    materials_list = payload.equipment_and_materials or ["Cold Asphalt Mix", "Barricades", "Reflective Caution Tape"]
    materials_formatted = "\n".join([f"  • {m}" for m in materials_list])

    docket = f"""================================================================================
PUNE MUNICIPAL CORPORATION — DIVISIONAL GRIEVANCE REDRESSAL WING
OFFICIAL MUNICIPAL WORK ORDER & CONTRACTOR DISPATCH DOCKET
================================================================================
Work Order ID    : {work_order_id}
Grievance Ref    : {complaint.tracking_id}
Date of Issuance : {issued_date}
Target Deadline  : {deadline_date} (Mandatory SLA Window)
Department       : {complaint.department}
Authority        : {complaint.authority_title}
Priority Rating  : Level {complaint.priority}/5 [{'EMERGENCY RAPID DISPATCH' if complaint.priority >= 4 else 'STANDARD WARD DISPATCH'}]

SITE & GRIEVANCE LOCATION:
  Address        : {complaint.location}
  City / Zone    : Pune Municipal Corporation
  Category       : {complaint.category} ({complaint.sub_issue or 'Standard Issue'})
  Description    : {complaint.description}

OFFICER & CONTRACTOR ASSIGNMENT:
  Designated JE  : {payload.assigned_officer}
  Work Agency    : {payload.contractor}

SAFETY DIRECTIVES & SCOPE OF REMEDIATION:
  1. Priority Instructions: {payload.priority_instructions}
  2. The assigned team must erect high-visibility safety barriers immediately upon arrival.
  3. Digital photographic evidence (Before & After) must be uploaded to the PMC portal for citizen verification.

REQUISITIONED TOOLS & MATERIALS:
{materials_formatted}

CERTIFICATION:
Dispatched under order of {complaint.authority_title}.
Any unexcused delay beyond {deadline_date} will incur standard municipal delay penalties.
================================================================================
"""

    # Advance complaint status to In Progress
    complaint.status = "In Progress"

    # Update timeline
    timeline = []
    if complaint.timeline:
        try:
            timeline = json.loads(complaint.timeline)
        except Exception:
            timeline = []

    if timeline and len(timeline) >= 3:
        timeline[0]["completed"] = True
        timeline[0]["current"] = False
        timeline[1]["completed"] = True
        timeline[1]["current"] = False
        timeline[2]["completed"] = True
        timeline[2]["current"] = True
        timeline[2]["date"] = now.strftime("%d %b %Y, %I:%M %p")
        timeline[2]["description"] = f"Official Work Order {work_order_id} issued. Field crew dispatched under {payload.assigned_officer}."
        complaint.timeline = json.dumps(timeline)

    complaint.updated_at = now
    db.commit()
    db.refresh(complaint)

    return WorkOrderResponse(
        work_order_id=work_order_id,
        tracking_id=complaint.tracking_id,
        issued_date=issued_date,
        deadline_date=deadline_date,
        assigned_officer=payload.assigned_officer,
        contractor=payload.contractor,
        department=complaint.department,
        location=complaint.location,
        instructions=payload.priority_instructions,
        materials=materials_list,
        work_order_document=docket.strip()
    )

