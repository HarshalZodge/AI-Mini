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

# Local lookup table for Ahilyanagar civic authorities
DEPARTMENT_LOOKUP = {
    "Roads & Potholes": {
        "department_name": "AMC Road & Infrastructure Department",
        "authority_title": "Executive Engineer (PWD & Roads), Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 4,
        "escalation_authority": "Chief Engineer (Infrastructure), Ahilyanagar Municipal Corporation"
    },
    "Water Supply": {
        "department_name": "AMC Water Supply & Filtration Department",
        "authority_title": "Superintending Engineer (Water Supply & Mula Dam Distribution), AMC",
        "expected_resolution_days": 3,
        "escalation_authority": "Additional Municipal Commissioner (Water Works), Ahilyanagar"
    },
    "Sanitation & Garbage": {
        "department_name": "AMC Solid Waste Management & Health Department",
        "authority_title": "Chief Health Officer & Deputy Commissioner (Sanitation), AMC",
        "expected_resolution_days": 2,
        "escalation_authority": "Deputy Municipal Commissioner (General Administration), AMC"
    },
    "Electricity & Streetlights": {
        "department_name": "MSEDCL Ahilyanagar Circle & AMC Electrical Department",
        "authority_title": "Junior Engineer (Public Street Lighting & Power Distribution), Ahilyanagar",
        "expected_resolution_days": 2,
        "escalation_authority": "Superintending Engineer, MSEDCL Ahilyanagar Circle"
    },
    "Drainage & Sewage": {
        "department_name": "AMC Drainage & Underground Sewerage Department",
        "authority_title": "Executive Engineer (Drainage Maintenance), Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 3,
        "escalation_authority": "Chief Engineer (Environmental Sanitation), AMC"
    },
    "Public Safety": {
        "department_name": "Ahilyanagar City Police & AMC Disaster Management Cell",
        "authority_title": "Assistant Commissioner of Police / City Ward Officer, Ahilyanagar",
        "expected_resolution_days": 1,
        "escalation_authority": "Deputy Commissioner of Police / Municipal Commissioner, AMC"
    },
    "Parks & Public Spaces": {
        "department_name": "AMC Garden & Tree Authority Department",
        "authority_title": "Superintendent of Parks & Gardens, Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 7,
        "escalation_authority": "Deputy Municipal Commissioner (Environment), AMC"
    },
    "Noise & Pollution": {
        "department_name": "Maharashtra Pollution Control Board (MPCB) Sub-Regional Office, Ahilyanagar",
        "authority_title": "Regional Officer, MPCB & Environment Cell Officer, AMC",
        "expected_resolution_days": 3,
        "escalation_authority": "Regional Officer, MPCB Nashik/Ahilyanagar Division"
    },
    "Other": {
        "department_name": "AMC Citizen Facilitation Center (CFC)",
        "authority_title": "Ward Grievance Redressal Officer, Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 5,
        "escalation_authority": "Municipal Commissioner, Ahilyanagar Municipal Corporation"
    }
}

# Ahilyanagar, Maharashtra area approximate coordinates for mapping
AHILYANAGAR_NEIGHBORHOODS = {
    "savedi": (19.1235, 74.7381),
    "kedgaon": (19.0664, 74.7218),
    "bhingar": (19.0833, 74.7833),
    "pipeline road": (19.1350, 74.7320),
    "tarakpur": (19.1020, 74.7390),
    "delhi gate": (19.0980, 74.7450),
    "maliwada": (19.0910, 74.7420),
    "nagapur": (19.1550, 74.7200),
    "nagapur midc": (19.1550, 74.7200),
    "kotla": (19.0850, 74.7350),
    "burudgaon": (19.0790, 74.7550),
    "burudgaon road": (19.0790, 74.7550),
    "bolhegaon": (19.1410, 74.7450),
    "market yard": (19.0930, 74.7520),
    "professor chowk": (19.1180, 74.7360),
    "premdan chowk": (19.1270, 74.7340),
    "camp": (19.0880, 74.7700),
    "cantonment": (19.0880, 74.7700),
    "station road": (19.0890, 74.7310),
    "dsp chowk": (19.1120, 74.7380),
    "gulshanabad": (19.0960, 74.7440),
    # Marathi Devanagari spellings for local civic inquiries
    "सावेडी": (19.1235, 74.7381),
    "केडगाव": (19.0664, 74.7218),
    "भिंगार": (19.0833, 74.7833),
    "पाईपलाईन रोड": (19.1350, 74.7320),
    "पाईपलाईन": (19.1350, 74.7320),
    "तारकपूर": (19.1020, 74.7390),
    "दिल्ली गेट": (19.0980, 74.7450),
    "माळीवाडा": (19.0910, 74.7420),
    "नागापूर": (19.1550, 74.7200),
    "प्रेमदान चौक": (19.1270, 74.7340),
    "प्रेमदान": (19.1270, 74.7340),
    "प्रोफेसर चौक": (19.1180, 74.7360),
    "मार्केट यार्ड": (19.0930, 74.7520),
    "कोठला": (19.0850, 74.7350),
    "बुरुडगाव": (19.0790, 74.7550),
    "बोलहेगाव": (19.1410, 74.7450),
    "कँप": (19.0880, 74.7700),
    "स्टेशन रोड": (19.0890, 74.7310),
}
# Backward compatibility alias
PUNE_NEIGHBORHOODS = AHILYANAGAR_NEIGHBORHOODS


def geocode_location(location_str: str) -> tuple[float, float]:
    """Finds lat/lng coordinates for location string within Ahilyanagar, with subtle jitter if multiple."""
    loc_lower = (location_str or "").lower()
    for name, coords in AHILYANAGAR_NEIGHBORHOODS.items():
        if name in loc_lower:
            jitter_lat = (random.random() - 0.5) * 0.003
            jitter_lng = (random.random() - 0.5) * 0.003
            return round(coords[0] + jitter_lat, 5), round(coords[1] + jitter_lng, 5)

    # Default to Central Ahilyanagar around Municipal Corporation HQ
    base_lat, base_lng = 19.0952, 74.7496
    jitter_lat = (random.random() - 0.5) * 0.03
    jitter_lng = (random.random() - 0.5) * 0.03
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

    if any(k in t for k in ["pothole", "road", "crater", "asphalt", "tar", "speed breaker", "footpath", "sidewalk", "divider", "खड्डा", "खड्डे", "रस्ता", "सडक", "डामर", "गड्डा", "पूल"]):
        sub = "Potholes & Damaged Road Surface" if any(k in t for k in ["pothole", "crater", "खड्डा", "खड्डे", "गड्डा"]) else "Damaged Footpath / Road Infra"
        return {"category": "Roads & Potholes", "sub_issue": sub}

    if any(k in t for k in ["water", "pipeline", "tap", "pressure", "drinking", "tanker", "contamination", "leakage", "pani", "paani", "पाणी", "नळ", "जल", "पाईप", "टाकी"]):
        sub = "No Water Supply" if ("no water" in t or "shut" in t or "pressure" in t or "नाही" in t or "बंद" in t) else "Pipeline Burst / Contaminated Water"
        return {"category": "Water Supply", "sub_issue": sub}

    if any(k in t for k in ["garbage", "trash", "waste", "dump", "bin", "kachra", "debris", "litter", "sweeping", "cleanliness", "कचरा", "घाण", "दुर्गंधी", "सफाई"]):
        sub = "Unattended Garbage Dump" if ("dump" in t or "pile" in t or "overflow" in t or "साचला" in t) else "Irregular Waste Collection"
        return {"category": "Sanitation & Garbage", "sub_issue": sub}

    if any(k in t for k in ["light", "streetlight", "lamp", "dark", "wire", "pole", "transformer", "electricity", "power cut", "current", "bijli", "लाईट", "दिवा", "विद्युत", "तारा", "खांब", "अंधार"]):
        sub = "Non-functional Streetlights" if any(k in t for k in ["light", "dark", "दिवा", "अंधार", "बंद"]) else "Exposed Electrical Wire / Pole Damage"
        return {"category": "Electricity & Streetlights", "sub_issue": sub}

    if any(k in t for k in ["drain", "drainage", "sewage", "gutter", "manhole", "overflowing", "stagnant water", "clogged", "गटार", "नाले", "ड्रेनेज", "मॅनहोल"]):
        sub = "Open / Hazardous Manhole" if ("manhole" in t or "मॅनहोल" in t) else "Overflowing Drainage & Gutter"
        return {"category": "Drainage & Sewage", "sub_issue": sub}

    if any(k in t for k in ["danger", "accident", "safety", "illegal parking", "stray dog", "dog bite", "harassment", "blind spot", "crime", "threat", "अपघात", "धोका", "कुत्रे", "चोरी"]):
        sub = "Immediate Public Hazard" if any(k in t for k in ["hazard", "accident", "अपघात", "धोका"]) else "Public Safety & Animal Menace"
        return {"category": "Public Safety", "sub_issue": sub}

    if any(k in t for k in ["park", "garden", "tree", "branch", "playground", "bench", "fence", "grass", "झाड", "बाग", "उद्यान"]):
        sub = "Fallen Tree / Dangerous Branch" if ("tree" in t or "branch" in t or "झाड" in t) else "Poor Park Maintenance"
        return {"category": "Parks & Public Spaces", "sub_issue": sub}

    if any(k in t for k in ["noise", "loudspeaker", "pollution", "smoke", "dust", "factory", "sound", "horn", "air quality", "आवाज", "प्रदूषण", "ध्वनी"]):
        sub = "Loudspeaker & Noise Violation" if ("noise" in t or "loud" in t or "sound" in t or "आवाज" in t) else "Air & Dust Pollution"
        return {"category": "Noise & Pollution", "sub_issue": sub}

    return {"category": "Other", "sub_issue": "General Civic Concern"}


def find_department(category: str, city: str = "Ahilyanagar") -> Dict[str, Any]:
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
        "escalation_authority": dept_info.get("escalation_authority", "Municipal Commissioner, Ahilyanagar Municipal Corporation")
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
        "severe accident", "accident", "skid", "slipped", "injury", "fall",
        "flooding", "collapsed", "fire hazard",
        "अपघात", "दुर्घटना", "जखमी", "घसरले"
    ]
    high_triggers = [
        "busy road", "main road", "highway", "drinking water contamination",
        "stinking", "maggots", "disease", "fever", "dengue", "overdue",
        "days", "weeks", "months", "no water for", "traffic jam", "risk",
        "धोका", "दुर्गंधी", "अंधार"
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

    # Extract keywords from location (e.g. "Savedi", "Kedgaon", "Premdan Chowk", "Pipeline Road")
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
    location = details.get("location", "Ahilyanagar City")
    landmark = details.get("landmark", "")
    full_loc = f"{location} (Near: {landmark})" if landmark else location
    department = details.get("department", "Ahilyanagar Municipal Corporation")
    authority_title = details.get("authority_title", "Concerned Civic Authority")
    priority = details.get("priority", 3)
    urgency_tag = "URGENT / CRITICAL" if priority >= 4 else "REGULAR"
    description = details.get("description", "Grievance details as reported by citizen.")
    today_str = datetime.now().strftime("%B %d, %Y")

    letter = f"""To,
The {authority_title},
{department},
Ahilyanagar Municipal Corporation (AMC), Ahilyanagar, Maharashtra.

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
    higher_auth = dept_info.get("escalation_authority", "The Municipal Commissioner, Ahilyanagar Municipal Corporation")
    today_str = datetime.now().strftime("%B %d, %Y")
    days_open = 0
    if complaint.created_at:
        days_open = (datetime.now(timezone.utc) - complaint.created_at.replace(tzinfo=timezone.utc)).days

    escalation_text = f"""FORMAL NOTICE OF ESCALATION — CITIZEN GRIEVANCE OVERDUE

To,
{higher_auth},
Ahilyanagar Municipal Corporation / Government of Maharashtra.

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
    coords = geocode_location(data.get("location", "Ahilyanagar"))
    
    category = data.get("category", "Other")
    dept_info = find_department(category, data.get("city", "Ahilyanagar"))
    
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
            "location": data.get("location", "Ahilyanagar"),
            "landmark": data.get("landmark"),
            "department": dept_info["department_name"],
            "authority_title": dept_info["authority_title"],
            "priority": priority,
            "description": data.get("description", data.get("title", ""))
        })

    complaint = Complaint(
        tracking_id=tracking_id,
        title=data.get("title") or f"{category} at {data.get('location', 'Ahilyanagar')}",
        description=data.get("description") or data.get("title") or "Civic grievance filed via CivicResolve.",
        category=category,
        sub_issue=data.get("sub_issue", category),
        location=data.get("location", "Ahilyanagar"),
        landmark=data.get("landmark"),
        city=data.get("city", "Ahilyanagar"),
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
