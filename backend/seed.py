"""
Seed script for CivicResolve database.
Populates ~15 realistic civic complaints across Pune neighborhoods with
authentic statuses, coordinates, timeline logs, and upvote counts.
"""

import json
from datetime import datetime, timezone, timedelta
from db import SessionLocal, Complaint, init_db
import tools

SEED_DATA = [
    {
        "tracking_id": "CR-2026-0001",
        "title": "Severe Pothole Cluster near Paud Phata Flyover",
        "description": "Dangerous pothole cluster measuring nearly 2 feet wide on the Paud Road descent. Multiple two-wheelers skidding during evening peak hours.",
        "category": "Roads & Potholes",
        "sub_issue": "Potholes & Damaged Road Surface",
        "location": "Paud Road, Kothrud, Pune",
        "landmark": "Near Paud Phata Flyover Pillar 14",
        "city": "Pune",
        "latitude": 18.5074,
        "longitude": 73.8077,
        "priority": 5,
        "priority_reason": "Immediate life-safety hazard for two-wheelers and high-speed vehicular traffic.",
        "department": "PMC Road & Infrastructure Department",
        "authority_title": "Executive Engineer (Road Infrastructure), Pune Municipal Corporation",
        "expected_resolution_days": 4,
        "status": "In Progress",
        "days_ago": 3,
        "upvotes": 38,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0002",
        "title": "Unattended Garbage Dump opposite IT Park Phase 1",
        "description": "Massive overflow of municipal waste and construction debris dumped by commercial vehicles. Severe stench spreading into nearby residential societies.",
        "category": "Sanitation & Garbage",
        "sub_issue": "Unattended Garbage Dump",
        "location": "Hinjawadi Phase 1, Pune",
        "landmark": "Opposite Tech Mahindra Gate 2",
        "city": "Pune",
        "latitude": 18.5913,
        "longitude": 73.7389,
        "priority": 4,
        "priority_reason": "High public health hazard, breeding ground for mosquitoes, blocking pedestrian walkway.",
        "department": "PMC Solid Waste Management Department",
        "authority_title": "Deputy Municipal Commissioner (Solid Waste Management), Pune Municipal Corporation",
        "expected_resolution_days": 2,
        "status": "Submitted",
        "days_ago": 4,  # Overdue! SLA is 2 days. Perfect for escalation demo!
        "upvotes": 42,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0003",
        "title": "Drinking Water Contamination & Zero Pressure in Lane 7",
        "description": "Turbid, brownish drinking water supplied for past 3 mornings. Foul smell indicating cross-contamination with old sewage line.",
        "category": "Water Supply",
        "sub_issue": "Pipeline Burst / Contaminated Water",
        "location": "Baner Main Road, Pune",
        "landmark": "Lane 7, Near Orchid School",
        "city": "Pune",
        "latitude": 18.5590,
        "longitude": 73.7868,
        "priority": 5,
        "priority_reason": "Severe public health hazard threatening waterborne epidemic near a school zone.",
        "department": "PMC Water Supply & Pumping Department",
        "authority_title": "Superintending Engineer (Water Works), Pune Municipal Corporation",
        "expected_resolution_days": 3,
        "status": "Assigned",
        "days_ago": 1,
        "upvotes": 29,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0004",
        "title": "Entire Stretch of 10 Streetlights Dark on JM Road",
        "description": "All LED streetlights between Balgandharva Chowk and Deccan Gymkhana have been dark for 4 consecutive nights. Vulnerable for late commuters.",
        "category": "Electricity & Streetlights",
        "sub_issue": "Non-functional Streetlights",
        "location": "JM Road, Shivajinagar, Pune",
        "landmark": "Between Balgandharva Rangmandir and Deccan Bus Stop",
        "city": "Pune",
        "latitude": 18.5280,
        "longitude": 73.8480,
        "priority": 4,
        "priority_reason": "Compromised women safety and traffic collision risk on high-density arterial road.",
        "department": "MSEDCL & PMC Electrical Department",
        "authority_title": "Junior Engineer (Public Street Lighting & Power Distribution), Pune",
        "expected_resolution_days": 2,
        "status": "Resolved",
        "days_ago": 5,
        "upvotes": 17,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0005",
        "title": "Open Uncovered Stormwater Drain Near Datta Mandir",
        "description": "Heavy concrete cover broken 2 weeks ago and left open without barricading or warning signs. Deep 6-foot pit.",
        "category": "Drainage & Sewage",
        "sub_issue": "Open / Hazardous Manhole",
        "location": "Viman Nagar, Pune",
        "landmark": "Near Datta Mandir, Dutta Mandir Chowk",
        "city": "Pune",
        "latitude": 18.5679,
        "longitude": 73.9143,
        "priority": 5,
        "priority_reason": "Fatal falling hazard for pedestrians, especially children returning from nearby coaching centers.",
        "department": "PMC Drainage & Sewerage Department",
        "authority_title": "Executive Engineer (Drainage Maintenance), Pune Municipal Corporation",
        "expected_resolution_days": 3,
        "status": "In Progress",
        "days_ago": 2,
        "upvotes": 53,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0006",
        "title": "Aggressive Stray Dog Pack Harassing Cyclists",
        "description": "Pack of 8-10 stray dogs barking and lunging at morning cyclists and elderly walkers near the central garden perimeter.",
        "category": "Public Safety",
        "sub_issue": "Public Safety & Animal Menace",
        "location": "Magarpatta City, Hadapsar, Pune",
        "landmark": "Near Aditi Garden Gate 3",
        "city": "Pune",
        "latitude": 18.5158,
        "longitude": 73.9272,
        "priority": 3,
        "priority_reason": "Public distress and risk of dog bite incidents requiring animal birth control intervention.",
        "department": "Pune City Police & PMC Disaster Management Cell",
        "authority_title": "Assistant Commissioner of Police / Ward Disaster Officer, Pune",
        "expected_resolution_days": 1,
        "status": "Resolved",
        "days_ago": 6,
        "upvotes": 19,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0007",
        "title": "Broken Children's Swing & Hazardous Rusty Nails in Ward Garden",
        "description": "Children playground swing chains snapped and exposed sharp rusted metal corners on slide.",
        "category": "Parks & Public Spaces",
        "sub_issue": "Poor Park Maintenance",
        "location": "Aundh, Pune",
        "landmark": "Near Medipoint Hospital, DP Road",
        "city": "Pune",
        "latitude": 18.5580,
        "longitude": 73.8073,
        "priority": 3,
        "priority_reason": "Tetanus and injury risk for playing toddlers.",
        "department": "PMC Garden & Tree Authority Department",
        "authority_title": "Superintendent of Parks & Gardens, Pune Municipal Corporation",
        "expected_resolution_days": 7,
        "status": "Assigned",
        "days_ago": 2,
        "upvotes": 11,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0008",
        "title": "Commercial Generator Running 24/7 Exceeding Decibel Limits",
        "description": "Heavy industrial diesel generator operating continuously behind hotel, exceeding 85dB through the night.",
        "category": "Noise & Pollution",
        "sub_issue": "Loudspeaker & Noise Violation",
        "location": "Kalyani Nagar, Pune",
        "landmark": "Behind Jogger's Park Lane",
        "city": "Pune",
        "latitude": 18.5484,
        "longitude": 73.9030,
        "priority": 3,
        "priority_reason": "Chronic sleep deprivation and violation of residential zone noise regulations.",
        "department": "Maharashtra Pollution Control Board (MPCB) & PMC Environment Cell",
        "authority_title": "Regional Officer, MPCB & Environment Officer, PMC",
        "expected_resolution_days": 3,
        "status": "Submitted",
        "days_ago": 5,  # Overdue! SLA is 3 days.
        "upvotes": 24,
        "escalated": True
    },
    {
        "tracking_id": "CR-2026-0009",
        "title": "Water Pipeline Burst Causing Flooding on Bus Bay",
        "description": "4-inch municipal main line fractured; thousands of liters of clean water gushing onto the road causing major bottleneck.",
        "category": "Water Supply",
        "sub_issue": "Pipeline Burst / Contaminated Water",
        "location": "Swargate, Pune",
        "landmark": "PMPML Bus Station Entry Gate",
        "city": "Pune",
        "latitude": 18.5018,
        "longitude": 73.8636,
        "priority": 4,
        "priority_reason": "Wastage of precious treated municipal water and commuter congestion.",
        "department": "PMC Water Supply & Pumping Department",
        "authority_title": "Superintending Engineer (Water Works), Pune Municipal Corporation",
        "expected_resolution_days": 3,
        "status": "Resolved",
        "days_ago": 7,
        "upvotes": 61,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0010",
        "title": "Fallen Gulmohar Tree Blocking 2 Lanes on Karve Road",
        "description": "Large tree trunk collapsed after afternoon wind, blocking traffic heading towards Deccan.",
        "category": "Parks & Public Spaces",
        "sub_issue": "Fallen Tree / Dangerous Branch",
        "location": "Karve Nagar, Pune",
        "landmark": "Near Pratibha Garden Chowk",
        "city": "Pune",
        "latitude": 18.4912,
        "longitude": 73.8188,
        "priority": 5,
        "priority_reason": "Total traffic obstruction on major transit road and risk to electric wires.",
        "department": "PMC Garden & Tree Authority Department",
        "authority_title": "Superintendent of Parks & Gardens, Pune Municipal Corporation",
        "expected_resolution_days": 7,
        "status": "Resolved",
        "days_ago": 8,
        "upvotes": 35,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0011",
        "title": "Exposed High-Voltage Wire from Broken Junction Box",
        "description": "Streetlight feeder pillar damaged by vehicle impact; bare live copper cables hanging at knee height.",
        "category": "Electricity & Streetlights",
        "sub_issue": "Exposed Electrical Wire / Pole Damage",
        "location": "Wakad, Pune",
        "landmark": "Near Bhumkar Chowk Underpass",
        "city": "Pune",
        "latitude": 18.5987,
        "longitude": 73.7667,
        "priority": 5,
        "priority_reason": "Immediate risk of electrocution to pedestrians during damp weather.",
        "department": "MSEDCL & PMC Electrical Department",
        "authority_title": "Junior Engineer (Public Street Lighting & Power Distribution), Pune",
        "expected_resolution_days": 2,
        "status": "In Progress",
        "days_ago": 1,
        "upvotes": 48,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0012",
        "title": "Sewage Backflow into Ground Floor Housing Units",
        "description": "Underground sewer line choked with plastic and silt; filthy backflow into society compound.",
        "category": "Drainage & Sewage",
        "sub_issue": "Overflowing Drainage & Gutter",
        "location": "Katraj, Pune",
        "landmark": "Near Katraj Dairy, Pune-Satara Road",
        "city": "Pune",
        "latitude": 18.4575,
        "longitude": 73.8677,
        "priority": 4,
        "priority_reason": "Severe hygiene hazard and building foundation compromise.",
        "department": "PMC Drainage & Sewerage Department",
        "authority_title": "Executive Engineer (Drainage Maintenance), Pune Municipal Corporation",
        "expected_resolution_days": 3,
        "status": "Assigned",
        "days_ago": 2,
        "upvotes": 22,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0013",
        "title": "Illegal Encroachment and Hawking Blocking Footpath",
        "description": "Permanent wooden stalls erected across the entire pedestrian walkway forcing elderly citizens onto vehicular carriageway.",
        "category": "Public Safety",
        "sub_issue": "Immediate Public Hazard",
        "location": "Camp, Pune",
        "landmark": "MG Road, near Aurora Towers",
        "city": "Pune",
        "latitude": 18.5165,
        "longitude": 73.8780,
        "priority": 3,
        "priority_reason": "Pedestrian safety hazard and violation of right of way.",
        "department": "Pune City Police & PMC Disaster Management Cell",
        "authority_title": "Assistant Commissioner of Police / Ward Disaster Officer, Pune",
        "expected_resolution_days": 1,
        "status": "Submitted",
        "days_ago": 1,
        "upvotes": 15,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0014",
        "title": "Damaged Footpath Paver Blocks Causing Tripping",
        "description": "Loose, lifted concrete paving stones over 100 meters stretch. Two senior citizens reported sprained ankles this week.",
        "category": "Roads & Potholes",
        "sub_issue": "Damaged Footpath / Road Infra",
        "location": "FC Road, Deccan, Pune",
        "landmark": "Opposite Fergusson College Main Gate",
        "city": "Pune",
        "latitude": 18.5262,
        "longitude": 73.8427,
        "priority": 3,
        "priority_reason": "Pedestrian trip hazard along highest footfall student commercial corridor.",
        "department": "PMC Road & Infrastructure Department",
        "authority_title": "Executive Engineer (Road Infrastructure), Pune Municipal Corporation",
        "expected_resolution_days": 4,
        "status": "In Progress",
        "days_ago": 3,
        "upvotes": 31,
        "escalated": False
    },
    {
        "tracking_id": "CR-2026-0015",
        "title": "Open Waste Burning Generating Toxic Fumes",
        "description": "Dry leaves and plastic waste burned nightly in vacant municipal plot adjacent to residential tower.",
        "category": "Noise & Pollution",
        "sub_issue": "Air & Dust Pollution",
        "location": "Pashan, Pune",
        "landmark": "Near Pashan Lake Circle",
        "city": "Pune",
        "latitude": 18.5414,
        "longitude": 73.7925,
        "priority": 4,
        "priority_reason": "Hazardous particulate pollution affecting asthmatic residents and violation of NGT guidelines.",
        "department": "Maharashtra Pollution Control Board (MPCB) & PMC Environment Cell",
        "authority_title": "Regional Officer, MPCB & Environment Officer, PMC",
        "expected_resolution_days": 3,
        "status": "Resolved",
        "days_ago": 9,
        "upvotes": 27,
        "escalated": False
    }
]


def seed_database():
    """Populates database with realistic complaints and timeline logs."""
    init_db()
    db = SessionLocal()
    try:
        # Check existing count
        existing = db.query(Complaint).count()
        if existing >= 15:
            print(f"Database already populated with {existing} complaints.")
            return

        print("Seeding database with realistic Pune civic complaints...")
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
    seed_database()
