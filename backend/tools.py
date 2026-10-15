import json
import random
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from db import Complaint

CATEGORIES = [
    "Roads & Potholes",
    "Water Supply",
    "Sanitation & Garbage",
    "Electricity & Streetlights",
    "Drainage & Sewage",
    "Public Safety",
    "Parks & Public Spaces",
    "Noise & Pollution",
    "Other",
]

# Local lookup table for Pune civic authorities
DEPARTMENT_LOOKUP = {
    "Roads & Potholes": {
        "department_name": "PMC Road & Infrastructure Department",
        "authority_title": "Executive Engineer (Road Infrastructure), Pune Municipal Corporation",
        "expected_resolution_days": 4,
        "escalation_authority": "Chief Engineer (Projects & Infrastructure), PMC"
    },
    "Water Supply": {
        "department_name": "PMC Water Supply & Pumping Department",
        "authority_title": "Superintending Engineer (Water Works), Pune Municipal Corporation",
        "expected_resolution_days": 3,
        "escalation_authority": "Additional Municipal Commissioner (City Water Wing), PMC"
    },
    "Sanitation & Garbage": {
        "department_name": "PMC Solid Waste Management Department",
        "authority_title": "Deputy Municipal Commissioner (Solid Waste Management), Pune Municipal Corporation",
        "expected_resolution_days": 2,
        "escalation_authority": "Additional Municipal Commissioner (General Administration), PMC"
    },
    "Electricity & Streetlights": {
        "department_name": "MSEDCL & PMC Electrical Department",
        "authority_title": "Junior Engineer (Public Street Lighting & Power Distribution), Pune",
        "expected_resolution_days": 2,
        "escalation_authority": "Superintending Engineer, Maharashtra State Electricity Distribution Co. Ltd. (MSEDCL)"
    },
    "Drainage & Sewage": {
        "department_name": "PMC Drainage & Sewerage Department",
        "authority_title": "Executive Engineer (Drainage Maintenance), Pune Municipal Corporation",
        "expected_resolution_days": 3,
        "escalation_authority": "Chief Engineer (Sewerage & Environmental Sanitation), PMC"
    },
    "Public Safety": {
        "department_name": "Pune City Police & PMC Disaster Management Cell",
        "authority_title": "Assistant Commissioner of Police / Ward Disaster Officer, Pune",
        "expected_resolution_days": 1,
        "escalation_authority": "Deputy Commissioner of Police (Traffic & Safety) / Municipal Commissioner"
    },
    "Parks & Public Spaces": {
        "department_name": "PMC Garden & Tree Authority Department",
        "authority_title": "Superintendent of Parks & Gardens, Pune Municipal Corporation",
        "expected_resolution_days": 7,
        "escalation_authority": "Deputy Municipal Commissioner (Environment & Gardens), PMC"
    },
    "Noise & Pollution": {
        "department_name": "Maharashtra Pollution Control Board (MPCB) & PMC Environment Cell",
        "authority_title": "Regional Officer, MPCB & Environment Officer, PMC",
        "expected_resolution_days": 3,
        "escalation_authority": "Member Secretary, Maharashtra Pollution Control Board, Mumbai/Pune"
    },
    "Other": {
        "department_name": "PMC Citizen Facilitation Center (CFC)",
        "authority_title": "Ward Grievance Redressal Officer, Pune Municipal Corporation",
        "expected_resolution_days": 5,
        "escalation_authority": "Municipal Commissioner, Pune Municipal Corporation"
    }
}

# Pune area approximate coordinates for realistic mapping
PUNE_NEIGHBORHOODS = {
    "kothrud": (18.5074, 73.8077),
    "hinjawadi": (18.5913, 73.7389),
    "hinjewadi": (18.5913, 73.7389),
    "baner": (18.5590, 73.7868),
    "shivajinagar": (18.5308, 73.8475),
    "viman nagar": (18.5679, 73.9143),
    "hadapsar": (18.5089, 73.9259),
    "swargate": (18.5018, 73.8636),
    "camp": (18.5158, 73.8797),
    "mg road": (18.5165, 73.8780),
    "wakad": (18.5987, 73.7667),
    "aundh": (18.5580, 73.8073),
    "kalyani nagar": (18.5484, 73.9030),
    "katraj": (18.4575, 73.8677),
    "deccan": (18.5167, 73.8417),
    "deccan gymkhana": (18.5167, 73.8417),
    "pashan": (18.5414, 73.7925),
    "bavdhan": (18.5140, 73.7709),
    "magarpatta": (18.5158, 73.9272),
    "kondhwa": (18.4739, 73.8938),
    "pimpri": (18.6279, 73.8009),
    "chinchwad": (18.6298, 73.7997),
    "karve nagar": (18.4912, 73.8188),
    "warje": (18.4831, 73.7942),
    "fc road": (18.5262, 73.8427),
    "jm road": (18.5280, 73.8480),
}


def geocode_location(location_str: str) -> tuple[float, float]:
    """Finds lat/lng coordinates for location string within Pune, with subtle jitter if multiple."""
    loc_lower = (location_str or "").lower()
    for name, coords in PUNE_NEIGHBORHOODS.items():
        if name in loc_lower:
            # Slight random offset (~50-100m) so multiple pins don't overlap completely
            jitter_lat = (random.random() - 0.5) * 0.004
            jitter_lng = (random.random() - 0.5) * 0.004
            return round(coords[0] + jitter_lat, 5), round(coords[1] + jitter_lng, 5)

    # Default to Central Pune with random offset around PMC headquarters
    base_lat, base_lng = 18.5204, 73.8567
    jitter_lat = (random.random() - 0.5) * 0.04
    jitter_lng = (random.random() - 0.5) * 0.04
    return round(base_lat + jitter_lat, 5), round(base_lng + jitter_lng, 5)


def classify_complaint(text: str) -> Dict[str, str]:
    """
    Classifies a civic grievance text into standard civic categories and sub-issues.
    
    Categories:
    - Roads & Potholes
    - Water Supply
    - Sanitation & Garbage
    - Electricity & Streetlights
    - Drainage & Sewage
    - Public Safety
    - Parks & Public Spaces
    - Noise & Pollution
    - Other
    """
    t = text.lower()

    if any(k in t for k in ["pothole", "road", "crater", "asphalt", "tar", "speed breaker", "footpath", "sidewalk", "divider"]):
        sub = "Potholes & Damaged Road Surface" if "pothole" in t or "crater" in t else "Damaged Footpath / Road Infra"
        return {"category": "Roads & Potholes", "sub_issue": sub}

    if any(k in t for k in ["water", "pipeline", "tap", "pressure", "drinking", "tanker", "contamination", "leakage", "pani", "paani"]):
        sub = "No Water Supply" if ("no water" in t or "shut" in t or "pressure" in t) else "Pipeline Burst / Contaminated Water"
        return {"category": "Water Supply", "sub_issue": sub}

    if any(k in t for k in ["garbage", "trash", "waste", "dump", "bin", "kachra", "debris", "litter", "sweeping", "cleanliness"]):
        sub = "Unattended Garbage Dump" if ("dump" in t or "pile" in t or "overflow" in t) else "Irregular Waste Collection"
        return {"category": "Sanitation & Garbage", "sub_issue": sub}

    if any(k in t for k in ["light", "streetlight", "lamp", "dark", "wire", "pole", "transformer", "electricity", "power cut", "current", "bijli"]):
        sub = "Non-functional Streetlights" if "light" in t or "dark" in t else "Exposed Electrical Wire / Pole Damage"
        return {"category": "Electricity & Streetlights", "sub_issue": sub}

    if any(k in t for k in ["drain", "drainage", "sewage", "gutter", "manhole", "overflowing", "stagnant water", "clogged"]):
        sub = "Open / Hazardous Manhole" if "manhole" in t else "Overflowing Drainage & Gutter"
        return {"category": "Drainage & Sewage", "sub_issue": sub}

    if any(k in t for k in ["danger", "accident", "safety", "illegal parking", "stray dog", "dog bite", "harassment", "blind spot", "crime", "threat"]):
        sub = "Immediate Public Hazard" if "hazard" in t or "accident" in t else "Public Safety & Animal Menace"
        return {"category": "Public Safety", "sub_issue": sub}

    if any(k in t for k in ["park", "garden", "tree", "branch", "playground", "bench", "fence", "grass"]):
        sub = "Fallen Tree / Dangerous Branch" if "tree" in t or "branch" in t else "Poor Park Maintenance"
        return {"category": "Parks & Public Spaces", "sub_issue": sub}

    if any(k in t for k in ["noise", "loudspeaker", "pollution", "smoke", "dust", "factory", "sound", "horn", "air quality"]):
        sub = "Loudspeaker & Noise Violation" if "noise" in t or "loud" in t or "sound" in t else "Air & Dust Pollution"
        return {"category": "Noise & Pollution", "sub_issue": sub}

    return {"category": "Other", "sub_issue": "General Civic Concern"}


def find_department(category: str, city: str = "Pune") -> Dict[str, Any]:
    """
    Finds the designated municipal department, executive authority title,
    and official citizen-charter SLA resolution days based on the category.
    """
    dept_info = DEPARTMENT_LOOKUP.get(category, DEPARTMENT_LOOKUP["Other"])
    return {
        "department_name": dept_info["department_name"],
        "authority_title": dept_info["authority_title"],
        "expected_resolution_days": dept_info["expected_resolution_days"],
        "city": city,
        "escalation_authority": dept_info.get("escalation_authority", "Municipal Commissioner, PMC")
    }


def score_priority(text: str, category: str) -> Dict[str, Any]:
    """
    Calculates priority score (1 to 5) and one-sentence justification.
    Considers safety hazards (open manholes, live wires, near schools/hospitals),
    health hazards, and number of citizens impacted.
    """
    t = text.lower()
    score = 3
    reasons = []

    # High severity danger triggers
    critical_triggers = [
        "open manhole", "live wire", "exposed wire", "electric shock",
        "hospital", "school", "children", "elderly", "deep crater",
        "severe accident", "flooding", "collapsed", "fire hazard"
    ]
    high_triggers = [
        "busy road", "main road", "highway", "drinking water contamination",
        "stinking", "maggots", "disease", "fever", "dengue", "overdue",
        "days", "weeks", "months", "no water for", "traffic jam"
    ]

    is_critical = any(trig in t for trig in critical_triggers)
    is_high = any(trig in t for trig in high_triggers)

    if is_critical or ("open" in t and "manhole" in t) or ("live" in t and "wire" in t):
        score = 5
        reasons.append("Presents immediate life-safety risk or hazard near vulnerable populations")
    elif is_high or category in ["Public Safety", "Drainage & Sewage"]:
        score = 4
        reasons.append("Severe civic disruption affecting public health or major arterial movement")
    elif any(k in t for k in ["minor", "aesthetic", "small", "paint"]):
        score = 2
        reasons.append("Non-critical civic issue without immediate risk to life or health")
    else:
        score = 3
        reasons.append("Standard civic infrastructure grievance requiring prompt municipal attention")

    return {
        "score": score,
        "reason": reasons[0]
    }


def check_duplicates(location: str, category: str, db: Session) -> List[Dict[str, Any]]:
    """
    Queries SQLite database for existing active complaints in the same location and category.
    Returns list of duplicate or nearby matching complaints.
    """
    if not location or not category:
        return []

    # Extract keywords from location (e.g. "Kothrud", "Baner", "Hinjawadi", "FC Road")
    loc_words = [w.strip().lower() for w in re.split(r'[, -/]', location) if len(w.strip()) > 3]

    active_complaints = db.query(Complaint).filter(
        Complaint.category == category,
        Complaint.status.in_(["Submitted", "Assigned", "In Progress"])
    ).all()

    matches = []
    for c in active_complaints:
        c_loc_lower = (c.location or "").lower()
        # Check if any location word matches
        matched = any(w in c_loc_lower for w in loc_words)
        if matched or (location.lower() in c_loc_lower) or (c_loc_lower in location.lower()):
            matches.append({
                "id": c.id,
                "tracking_id": c.tracking_id,
                "title": c.title,
                "category": c.category,
                "location": c.location,
                "status": c.status,
                "upvotes": c.upvotes,
                "created_at": c.created_at.strftime("%d %b %Y") if c.created_at else "Recently"
            })

    return matches


def generate_formal_letter(details: Dict[str, Any]) -> str:
    """
    Generates a formal, professional civic grievance letter addressed to the correct municipal authority.
    """
    category = details.get("category", "Civic Grievance")
    sub_issue = details.get("sub_issue", "Civic Infrastructure Issue")
    location = details.get("location", "Pune City")
    landmark = details.get("landmark", "")
    full_loc = f"{location} (Near: {landmark})" if landmark else location
    department = details.get("department", "Pune Municipal Corporation")
    authority_title = details.get("authority_title", "Concerned Civic Authority")
    priority = details.get("priority", 3)
    urgency_tag = "URGENT / CRITICAL" if priority >= 4 else "REGULAR"
    description = details.get("description", "Grievance details as reported by citizen.")
    today_str = datetime.now().strftime("%B %d, %Y")

    letter = f"""To,
The {authority_title},
{department},
Pune Municipal Corporation (PMC), Pune, Maharashtra.

Date: {today_str}
Priority Classification: Level {priority}/5 [{urgency_tag}]
Subject: Urgent Grievance Redressal Request Regarding {category} at {full_loc}

Respected Sir/Madam,

I am writing to formally bring to your urgent attention a serious civic grievance concerning "{sub_issue}" observed at {full_loc}.

Nature & Particulars of the Grievance:
{description}

Civic & Public Impact:
This condition poses significant inconvenience and hazard to residents, commuters, and school-going children traversing this vicinity daily. Continued delay in addressing this matter will exacerbate safety hazards and civic distress.

Statutory Charter Appeal:
In accordance with the Citizen's Charter and Public Grievance Redressal guidelines of the Municipal Corporation, I request your esteemed office to:
1. Depute a field inspection officer from the {department} to inspect the site immediately.
2. Issue urgent work orders for necessary repair, remediation, or corrective action.
3. Update the civic tracking portal with the designated junior engineer's contact details and expected date of completion.

Looking forward to prompt and effective civic action.

Yours faithfully,
Concerned Citizen & Community Representative
Location: {full_loc}
Filed via CivicResolve AI Grievance Platform
"""
    return letter.strip()


def draft_escalation(complaint: Complaint, reason: Optional[str] = None) -> Dict[str, Any]:
    """
    Generates an escalation notice to a higher municipal authority for an overdue or stalled grievance.
    """
    dept_info = DEPARTMENT_LOOKUP.get(complaint.category, DEPARTMENT_LOOKUP["Other"])
    higher_auth = dept_info.get("escalation_authority", "The Municipal Commissioner, Pune Municipal Corporation")
    today_str = datetime.now().strftime("%B %d, %Y")
    days_open = 0
    if complaint.created_at:
        days_open = (datetime.now(timezone.utc) - complaint.created_at.replace(tzinfo=timezone.utc)).days

    escalation_text = f"""FORMAL NOTICE OF ESCALATION — CITIZEN GRIEVANCE OVERDUE

To,
{higher_auth},
Pune Municipal Corporation / Government of Maharashtra.

Date: {today_str}
Escalation Reference: ESC-{complaint.tracking_id}
Original Grievance Tracking ID: {complaint.tracking_id}
Category: {complaint.category} ({complaint.sub_issue or 'General'})
Location: {complaint.location}
Original Target SLA: {complaint.expected_resolution_days} working days
Current Delay Duration: {max(days_open, complaint.expected_resolution_days + 1)} days elapsed

Respected Authority,

This is a formal grievance escalation submitted under the Maharashtra Public Services Act and Civic Redressal Norms.

The grievance registered under tracking ID {complaint.tracking_id} on {complaint.location} has remained unresolved and has exceeded the stipulated Service Level Agreement (SLA) of {complaint.expected_resolution_days} days.

Original Issue Summary:
{complaint.description}

Grounds for Escalation:
{reason or 'The designated department has exceeded the mandated turnaround timeline without resolving the hazardous ground reality or providing a conclusive status report.'} Community distress has escalated with {complaint.upvotes} citizens co-signing this report.

Requested Administrative Intervention:
1. Immediate audit of the pendency of Tracking ID {complaint.tracking_id}.
2. Direction to the concerned Executive Engineer to execute emergency remediation within 48 hours.
3. Review of departmental accountability for the unaddressed SLA breach.

Respectfully submitted,
CivicResolve Community Taskforce on behalf of affected residents.
"""
    return {
        "tracking_id": complaint.tracking_id,
        "escalation_letter": escalation_text.strip(),
        "higher_authority": higher_auth,
        "message": f"Grievance successfully escalated to {higher_auth}."
    }


def generate_tracking_id(db: Session) -> str:
    """Generates unique tracking ID like CR-2026-0042."""
    year = datetime.now().year
    count = db.query(Complaint).count() + 1
    # Check for uniqueness
    while True:
        tid = f"CR-{year}-{count:04d}"
        if not db.query(Complaint).filter(Complaint.tracking_id == tid).first():
            return tid
        count += 1


def submit_complaint(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Saves a verified, structured complaint into SQLite and initializes timeline.
    """
    tracking_id = generate_tracking_id(db)
    coords = geocode_location(data.get("location", "Pune"))
    
    category = data.get("category", "Other")
    dept_info = find_department(category, data.get("city", "Pune"))
    
    priority = int(data.get("priority", 3))
    priority_reason = data.get("priority_reason") or f"Assessed at level {priority}/5 for civic safety and public convenience."

    now = datetime.now(timezone.utc)
    sla_days = dept_info["expected_resolution_days"]
    target_date = (now + timedelta(days=sla_days)).strftime("%d %b %Y")

    timeline = [
        {
            "status": "Submitted",
            "label": "Grievance Registered",
            "date": now.strftime("%d %b %Y, %I:%M %p"),
            "description": f"Complaint successfully filed and logged with ID {tracking_id}.",
            "completed": True,
            "current": False
        },
        {
            "status": "Assigned",
            "label": "Assigned to Ward Department",
            "date": (now + timedelta(hours=2)).strftime("%d %b %Y, %I:%M %p"),
            "description": f"Routed to {dept_info['department_name']} under {dept_info['authority_title']}.",
            "completed": True,
            "current": True
        },
        {
            "status": "In Progress",
            "label": "Field Inspection & Remediation",
            "date": f"Est. by {(now + timedelta(days=1)).strftime('%d %b %Y')}",
            "description": f"Field team dispatched for ground inspection and work order allocation.",
            "completed": False,
            "current": False
        },
        {
            "status": "Resolved",
            "label": "Resolved & Verified",
            "date": f"Target SLA: {target_date}",
            "description": "Remediation verified by ward supervisor and citizen closure notice issued.",
            "completed": False,
            "current": False
        }
    ]

    formal_letter = data.get("formal_letter")
    if not formal_letter:
        formal_letter = generate_formal_letter({
            "category": category,
            "sub_issue": data.get("sub_issue", category),
            "location": data.get("location", "Pune"),
            "landmark": data.get("landmark"),
            "department": dept_info["department_name"],
            "authority_title": dept_info["authority_title"],
            "priority": priority,
            "description": data.get("description", data.get("title", ""))
        })

    complaint = Complaint(
        tracking_id=tracking_id,
        title=data.get("title") or f"{category} at {data.get('location', 'Pune')}",
        description=data.get("description") or data.get("title") or "Civic grievance filed via CivicResolve.",
        category=category,
        sub_issue=data.get("sub_issue", category),
        location=data.get("location", "Pune"),
        landmark=data.get("landmark"),
        city=data.get("city", "Pune"),
        latitude=data.get("latitude") or coords[0],
        longitude=data.get("longitude") or coords[1],
        priority=priority,
        priority_reason=priority_reason,
        department=dept_info["department_name"],
        authority_title=dept_info["authority_title"],
        expected_resolution_days=sla_days,
        formal_letter=formal_letter,
        status="Assigned",
        timeline=json.dumps(timeline),
        upvotes=1,
        image_url=data.get("image_url"),
        created_at=now,
        updated_at=now,
        escalated=False
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint.to_dict()
