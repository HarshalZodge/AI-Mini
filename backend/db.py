import os
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./civic_resolve.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tracking_id = Column(String(32), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), index=True, nullable=False)
    sub_issue = Column(String(100), nullable=True)
    location = Column(String(255), nullable=False)
    landmark = Column(String(255), nullable=True)
    city = Column(String(100), default="Pune")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    priority = Column(Integer, default=3)  # 1 to 5
    priority_reason = Column(Text, nullable=True)
    department = Column(String(200), nullable=False)
    authority_title = Column(String(200), nullable=False)
    expected_resolution_days = Column(Integer, default=3)
    formal_letter = Column(Text, nullable=True)
    escalation_letter = Column(Text, nullable=True)
    status = Column(String(50), default="Submitted")  # Submitted, Assigned, In Progress, Resolved
    timeline = Column(Text, nullable=True)  # JSON list of stage objects
    upvotes = Column(Integer, default=0)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    escalated = Column(Boolean, default=False)

    def to_dict(self):
        timeline_data = []
        if self.timeline:
            try:
                timeline_data = json.loads(self.timeline)
            except Exception:
                timeline_data = []

        return {
            "id": self.id,
            "tracking_id": self.tracking_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "sub_issue": self.sub_issue,
            "location": self.location,
            "landmark": self.landmark,
            "city": self.city,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "priority": self.priority,
            "priority_reason": self.priority_reason,
            "department": self.department,
            "authority_title": self.authority_title,
            "expected_resolution_days": self.expected_resolution_days,
            "formal_letter": self.formal_letter,
            "escalation_letter": self.escalation_letter,
            "status": self.status,
            "timeline": timeline_data,
            "upvotes": self.upvotes,
            "image_url": self.image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "escalated": self.escalated,
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
