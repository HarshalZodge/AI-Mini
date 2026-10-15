"""
Seed script for CivicResolve database.
Populates ~15 realistic civic complaints across Ahilyanagar neighborhoods with
authentic statuses, coordinates, timeline logs, and upvote counts.
"""

import json
from datetime import datetime, timezone, timedelta
from db import SessionLocal, Complaint, init_db
import tools

SEED_DATA = [
    {
        "tracking_id": "CR-2026-0001",
        "title": "Deep Pothole Crater near Pipeline Road Premdan Chowk Junction",
        "description": "Extensive potholes measuring over 2 feet across and 6 inches deep on the main Pipeline Road descent towards Premdan Chowk. Causing recurring vehicular damage and two-wheeler skids during rush hours.",
        "category": "Roads & Potholes",
        "sub_issue": "Potholes & Damaged Road Surface",
        "location": "Pipeline Road, Savedi, Ahilyanagar",
        "landmark": "Near Premdan Chowk Signal",
        "city": "Ahilyanagar",
        "latitude": 19.1270,
        "longitude": 74.7340,
        "priority": 5,
        "priority_reason": "Immediate life-safety hazard for two-wheelers and high-speed vehicular traffic.",
        "department": "AMC Road & Infrastructure Department",
        "authority_title": "Executive Engineer (PWD & Roads), Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 4,
        "status": "In Progress",
        "days_ago": 3,
        "upvotes": 46,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0002",
        "title": "Garbage Overflow & Illegal Dumping near Kedgaon Bypass Road",
        "description": "Substantial accumulation of plastic, domestic organic waste, and market refuse strewn over 100 meters along the service lane. Stray animal menace and unbearable stench.",
        "category": "Sanitation & Garbage",
        "sub_issue": "Unattended Garbage Dump",
        "location": "Kedgaon Bypass Road, Ahilyanagar",
        "landmark": "Opposite Kedgaon Devi Temple Phata",
        "city": "Ahilyanagar",
        "latitude": 19.0664,
        "longitude": 74.7218,
        "priority": 4,
        "priority_reason": "High public health hazard, breeding ground for mosquitoes, blocking pedestrian walkway.",
        "department": "AMC Solid Waste Management & Health Department",
        "authority_title": "Chief Health Officer & Deputy Commissioner (Sanitation), AMC",
        "expected_resolution_days": 2,
        "status": "Submitted",
        "days_ago": 4,  # Overdue! SLA is 2 days. Perfect for escalation demo!
        "upvotes": 53,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0003",
        "title": "Drinking Water Pipeline Leakage & Low Pressure in Professor Chowk",
        "description": "Municipal distribution pipeline cracked underground near Professor Chowk. Clean drinking water gushing onto the road since 3 days while household taps run dry.",
        "category": "Water Supply",
        "sub_issue": "Pipeline Burst / Contaminated Water",
        "location": "Professor Chowk, Savedi, Ahilyanagar",
        "landmark": "Near Savedi Water Filtration Tank Road",
        "city": "Ahilyanagar",
        "latitude": 19.1180,
        "longitude": 74.7360,
        "priority": 4,
        "priority_reason": "Severe drinking water loss and severe shortage impacting 350+ households in Savedi.",
        "department": "AMC Water Supply & Filtration Department",
        "authority_title": "Superintending Engineer (Water Supply & Mula Dam Distribution), AMC",
        "expected_resolution_days": 3,
        "status": "Assigned",
        "days_ago": 1,
        "upvotes": 28,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0004",
        "title": "Broken Streetlight String on Tarakpur Bus Stand Approach Road",
        "description": "Complete blackout on the 400-meter stretch leading from Tarakpur Bus Stand towards Delhi Gate. 7 consecutive sodium streetlights non-functional.",
        "category": "Electricity & Streetlights",
        "sub_issue": "Streetlight Malfunction",
        "location": "Tarakpur, Ahilyanagar",
        "landmark": "Near MSRTC Central Bus Stand Gate",
        "city": "Ahilyanagar",
        "latitude": 19.1020,
        "longitude": 74.7390,
        "priority": 4,
        "priority_reason": "High public safety concern for women commuters, bus travelers, and elderly pedestrians at night.",
        "department": "MSEDCL Ahilyanagar Circle & AMC Electrical Department",
        "authority_title": "Junior Engineer (Public Street Lighting & Power Distribution), Ahilyanagar",
        "expected_resolution_days": 2,
        "status": "Submitted",
        "days_ago": 1,
        "upvotes": 19,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0005",
        "title": "Overflowing Stormwater Drain & Sewage Backflow in Delhi Gate Bazar",
        "description": "Choked stormwater culvert causing black sewage water to flood the pedestrian walkways and market entrance near Delhi Gate. Businesses affected.",
        "category": "Drainage & Sewage",
        "sub_issue": "Sewage Overflow / Blocked Drain",
        "location": "Delhi Gate, Ahilyanagar",
        "landmark": "Near Historical Delhi Gate Entrance Arch",
        "city": "Ahilyanagar",
        "latitude": 19.0980,
        "longitude": 74.7450,
        "priority": 4,
        "priority_reason": "Contamination hazard in high-density bazaar and risk of gastrointestinal waterborne infections.",
        "department": "AMC Drainage & Underground Sewerage Department",
        "authority_title": "Executive Engineer (Drainage Maintenance), Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 3,
        "status": "In Progress",
        "days_ago": 2,
        "upvotes": 34,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0006",
        "title": "Open Deep Manhole without Cover in Maliwada Market Circle",
        "description": "Manhole lid smashed and missing near Maliwada vegetable market. Locals placed a wooden stick with plastic bag as makeshift warning. Extreme hazard.",
        "category": "Public Safety",
        "sub_issue": "Open Manhole / Unsafe Hazard",
        "location": "Maliwada, Ahilyanagar",
        "landmark": "Near Maliwada ST Stand Road",
        "city": "Ahilyanagar",
        "latitude": 19.0910,
        "longitude": 74.7420,
        "priority": 5,
        "priority_reason": "Fatal fall risk for pedestrians, school children, and two-wheelers in crowded market zone.",
        "department": "Ahilyanagar City Police & AMC Disaster Management Cell",
        "authority_title": "Assistant Commissioner of Police / City Ward Officer, Ahilyanagar",
        "expected_resolution_days": 1,
        "status": "Assigned",
        "days_ago": 1,
        "upvotes": 62,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0007",
        "title": "Uprooted Banyan Tree Branch Blocking Cantonment Road",
        "description": "Heavy rain split a massive limb of an old banyan tree near Bhingar Cantonment, obstructing half the motorable carriageway.",
        "category": "Parks & Public Spaces",
        "sub_issue": "Fallen Tree / Overgrown Branches",
        "location": "Bhingar Cantonment, Ahilyanagar",
        "landmark": "Near Sadar Bazar Military Post",
        "city": "Ahilyanagar",
        "latitude": 19.0833,
        "longitude": 74.7833,
        "priority": 3,
        "priority_reason": "Traffic obstruction and hazard to vehicles travelling towards Bhingar Camp.",
        "department": "AMC Garden & Tree Authority Department",
        "authority_title": "Superintendent of Parks & Gardens, Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 7,
        "status": "Resolved",
        "days_ago": 5,
        "upvotes": 14,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0008",
        "title": "Illegal Chemical Effluent & Toxic Smoke Burning at Nagapur MIDC",
        "description": "Late-night burning of industrial rubber scrap and chemical wash discharge into the open nullah causing acrid fumes and eye irritation among residents.",
        "category": "Noise & Pollution",
        "sub_issue": "Illegal Burning / Industrial Noise",
        "location": "Nagapur MIDC Phase 2, Ahilyanagar",
        "landmark": "Near Bolhegaon Phata Industrial Belt",
        "city": "Ahilyanagar",
        "latitude": 19.1550,
        "longitude": 74.7200,
        "priority": 4,
        "priority_reason": "Violation of air pollution standards; severe respiratory irritation for residents of adjacent colonies.",
        "department": "Maharashtra Pollution Control Board (MPCB) Sub-Regional Office, Ahilyanagar",
        "authority_title": "Regional Officer, MPCB & Environment Cell Officer, AMC",
        "expected_resolution_days": 3,
        "status": "Submitted",
        "days_ago": 2,
        "upvotes": 27,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0009",
        "title": "Broken Water Distribution Valve Flooding Kotla Colony",
        "description": "Distribution control valve malfunctioned at Kotla pump house, causing continuous water logging in Lane 3 and zero pressure in Lane 4.",
        "category": "Water Supply",
        "sub_issue": "Pipeline Burst / Contaminated Water",
        "location": "Kotla, Ahilyanagar",
        "landmark": "Behind Old Kotla Ground",
        "city": "Ahilyanagar",
        "latitude": 19.0850,
        "longitude": 74.7350,
        "priority": 3,
        "priority_reason": "Wastage of treated municipal water and localized street flooding.",
        "department": "AMC Water Supply & Filtration Department",
        "authority_title": "Superintending Engineer (Water Supply & Mula Dam Distribution), AMC",
        "expected_resolution_days": 3,
        "status": "Resolved",
        "days_ago": 4,
        "upvotes": 11,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0010",
        "title": "Neglected Children's Play Park & Damaged Swings in Bolhegaon",
        "description": "Public garden swing chains broken, rusted slide with sharp edge, overgrown weed infestation with snake sightings.",
        "category": "Parks & Public Spaces",
        "sub_issue": "Damaged Park Equipment",
        "location": "Bolhegaon, Ahilyanagar",
        "landmark": "Near Bolhegaon Railway Crossing Garden",
        "city": "Ahilyanagar",
        "latitude": 19.1410,
        "longitude": 74.7450,
        "priority": 2,
        "priority_reason": "Risk of physical injury to young children playing in public park.",
        "department": "AMC Garden & Tree Authority Department",
        "authority_title": "Superintendent of Parks & Gardens, Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 7,
        "status": "Submitted",
        "days_ago": 3,
        "upvotes": 16,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0011",
        "title": "Exposed High-Voltage Cable near DSP Chowk Court Compound",
        "description": "Live underground electrical feed wire exposed following trench excavation by telecom contractor. Rain water puddling near live wire.",
        "category": "Electricity & Streetlights",
        "sub_issue": "Exposed Wire / Power Fluctuation",
        "location": "DSP Chowk, Ahilyanagar",
        "landmark": "Near District Court Gate & Police Headquarters",
        "city": "Ahilyanagar",
        "latitude": 19.1120,
        "longitude": 74.7380,
        "priority": 5,
        "priority_reason": "Critical electrocution hazard near high footfall government administrative zone.",
        "department": "MSEDCL Ahilyanagar Circle & AMC Electrical Department",
        "authority_title": "Junior Engineer (Public Street Lighting & Power Distribution), Ahilyanagar",
        "expected_resolution_days": 2,
        "status": "In Progress",
        "days_ago": 1,
        "upvotes": 39,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0012",
        "title": "Clogged Underground Sewer Line on Burudgaon Market Yard Road",
        "description": "Sanitary sewer backup spilling out from inspection chamber across wholesale grain market entrance. Heavy vehicular movement splashing sludge.",
        "category": "Drainage & Sewage",
        "sub_issue": "Sewage Overflow / Blocked Drain",
        "location": "Burudgaon Road, Ahilyanagar",
        "landmark": "Near APMC Market Yard Main Gate",
        "city": "Ahilyanagar",
        "latitude": 19.0790,
        "longitude": 74.7550,
        "priority": 4,
        "priority_reason": "Contamination threat to food grain trade hub and severe health hazard for porters and traders.",
        "department": "AMC Drainage & Underground Sewerage Department",
        "authority_title": "Executive Engineer (Drainage Maintenance), Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 3,
        "status": "Submitted",
        "days_ago": 2,
        "upvotes": 31,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0013",
        "title": "Damaged Culvert & Sunken Bitumen on Bhingar Road",
        "description": "Heavy truck movement caused structural crack in the stone slab culvert. Left lane sunken by 10 inches, risk of road collapse.",
        "category": "Roads & Potholes",
        "sub_issue": "Potholes & Damaged Road Surface",
        "location": "Bhingar Road, Ahilyanagar",
        "landmark": "Near Bhingar Post Office",
        "city": "Ahilyanagar",
        "latitude": 19.0833,
        "longitude": 74.7833,
        "priority": 5,
        "priority_reason": "Imminent road cave-in hazard capable of causing fatal accident for heavy transport and buses.",
        "department": "AMC Road & Infrastructure Department",
        "authority_title": "Executive Engineer (PWD & Roads), Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 4,
        "status": "In Progress",
        "days_ago": 2,
        "upvotes": 48,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0014",
        "title": "Unregulated Loudspeaker Noise Past Midnight near Gulshanabad",
        "description": "Commercial wedding lawn operating high-decibel DJ systems and sound mixers until 2 AM on weekday nights exceeding legal noise limits.",
        "category": "Noise & Pollution",
        "sub_issue": "Illegal Burning / Industrial Noise",
        "location": "Gulshanabad, Ahilyanagar",
        "landmark": "Near Gulshanabad Community Hall",
        "city": "Ahilyanagar",
        "latitude": 19.0960,
        "longitude": 74.7440,
        "priority": 3,
        "priority_reason": "Severe noise pollution during night silence hours impacting board exam students and elderly patients.",
        "department": "Ahilyanagar City Police & AMC Disaster Management Cell",
        "authority_title": "Assistant Commissioner of Police / City Ward Officer, Ahilyanagar",
        "expected_resolution_days": 1,
        "status": "Resolved",
        "days_ago": 3,
        "upvotes": 18,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0015",
        "title": "Fallen Masonry and Loose Plaster near Maliwada Municipal School",
        "description": "Boundary wall stone coping fractured and hanging loose over public footpath where primary school students assemble.",
        "category": "Public Safety",
        "sub_issue": "Open Manhole / Unsafe Hazard",
        "location": "Maliwada, Ahilyanagar",
        "landmark": "Opposite AMC Primary School No. 4",
        "city": "Ahilyanagar",
        "latitude": 19.0910,
        "longitude": 74.7420,
        "priority": 4,
        "priority_reason": "Direct physical threat of falling debris onto school students and pedestrians.",
        "department": "AMC Citizen Facilitation Center (CFC)",
        "authority_title": "Ward Grievance Redressal Officer, Ahilyanagar Municipal Corporation",
        "expected_resolution_days": 5,
        "status": "Submitted",
        "days_ago": 1,
        "upvotes": 23,
        "escalated": False
    }
]


def seed_database(force_refresh: bool = True):
    """Populates database with realistic complaints and timeline logs."""
    init_db()
    db = SessionLocal()
    try:
        # Check existing count and whether old data is present
        existing_pune = db.query(Complaint).filter(Complaint.city.ilike("%Pune%")).count()
        if force_refresh or existing_pune > 0:
            print("Purging legacy complaints to refresh with Ahilyanagar dataset...")
            db.query(Complaint).delete()
            db.commit()

        existing = db.query(Complaint).count()
        if existing >= 15:
            print(f"Database already populated with {existing} complaints.")
            return

        print("Seeding database with realistic Ahilyanagar civic complaints...")
        now = datetime.now(timezone.utc)

        for item in SEED_DATA:
            # Check if tracking id already exists
            if db.query(Complaint).filter(Complaint.tracking_id == item["tracking_id"]).first():
                continue

            created_time = now - timedelta(days=item["days_ago"], hours=item.get("priority", 3) * 2)
            status = item["status"]
            sla_days = item["expected_resolution_days"]
            target_date = (created_time + timedelta(days=sla_days)).strftime("%d %b %Y")

            # Build timeline based on status
            timeline = [
                {
                    "status": "Submitted",
                    "label": "Grievance Registered",
                    "date": created_time.strftime("%d %b %Y, %I:%M %p"),
                    "description": f"Complaint officially logged with ID {item['tracking_id']}.",
                    "completed": True,
                    "current": status == "Submitted"
                },
                {
                    "status": "Assigned",
                    "label": "Assigned to Ward Department",
                    "date": (created_time + timedelta(hours=3)).strftime("%d %b %Y, %I:%M %p"),
                    "description": f"Routed to {item['department']} under {item['authority_title']}.",
                    "completed": status in ["Assigned", "In Progress", "Resolved"],
                    "current": status == "Assigned"
                },
                {
                    "status": "In Progress",
                    "label": "Field Inspection & Remediation",
                    "date": (created_time + timedelta(days=1)).strftime("%d %b %Y, %I:%M %p") if status in ["In Progress", "Resolved"] else f"Est. by {(created_time + timedelta(days=1)).strftime('%d %b %Y')}",
                    "description": f"Inspection team deployed on site. Work order assigned to zonal junior engineer.",
                    "completed": status in ["In Progress", "Resolved"],
                    "current": status == "In Progress"
                },
                {
                    "status": "Resolved",
                    "label": "Resolved & Verified",
                    "date": (created_time + timedelta(days=min(sla_days, item['days_ago']))).strftime("%d %b %Y, %I:%M %p") if status == "Resolved" else f"Target SLA: {target_date}",
                    "description": "On-site repair completed and verified by ward supervisor. Citizen closure survey dispatched." if status == "Resolved" else "Awaiting field team remediation report.",
                    "completed": status == "Resolved",
                    "current": status == "Resolved"
                }
            ]

            formal_letter = tools.generate_formal_letter({
                "category": item["category"],
                "sub_issue": item["sub_issue"],
                "location": item["location"],
                "landmark": item["landmark"],
                "department": item["department"],
                "authority_title": item["authority_title"],
                "priority": item["priority"],
                "description": item["description"]
            })

            complaint = Complaint(
                tracking_id=item["tracking_id"],
                title=item["title"],
                description=item["description"],
                category=item["category"],
                sub_issue=item["sub_issue"],
                location=item["location"],
                landmark=item["landmark"],
                city=item["city"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                priority=item["priority"],
                priority_reason=item["priority_reason"],
                department=item["department"],
                authority_title=item["authority_title"],
                expected_resolution_days=sla_days,
                formal_letter=formal_letter,
                status=status,
                timeline=json.dumps(timeline),
                upvotes=item["upvotes"],
                created_at=created_time,
                updated_at=now,
                escalated=item["escalated"]
            )
            db.add(complaint)

        db.commit()
        print(f"Successfully seeded database! Total complaints in DB: {db.query(Complaint).count()}")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database(force_refresh=True)
