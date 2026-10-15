from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime


class AgentStep(BaseModel):
    step_name: str
    tool_name: str
    status: str = "completed"  # running, completed, skipped
    details: Dict[str, Any] = Field(default_factory=dict)
    summary: str


class ChatMessage(BaseModel):
    role: str  # "user" or "model" or "assistant"
    content: str
    image_url: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)
    image_data: Optional[str] = None  # base64 data URL
    location_hint: Optional[str] = None
    session_id: Optional[str] = None


class ComplaintDraft(BaseModel):
    title: str
    category: str
    sub_issue: Optional[str] = None
    location: str
    landmark: Optional[str] = None
    city: str = "Ahilyanagar"
    priority: int = 3
    priority_reason: str
    department: str
    authority_title: str
    expected_resolution_days: int = 3
    formal_letter: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DuplicateComplaintInfo(BaseModel):
    tracking_id: str
    title: str
    category: str
    location: str
    status: str
    upvotes: int
    created_at: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    agent_steps: List[AgentStep] = Field(default_factory=list)
    complaint_draft: Optional[ComplaintDraft] = None
    submitted_complaint: Optional[Dict[str, Any]] = None
    duplicate_found: Optional[DuplicateComplaintInfo] = None
    needs_confirmation: bool = False
    ready_for_submission: bool = False


class ComplaintOut(BaseModel):
    id: int
    tracking_id: str
    title: str
    description: str
    category: str
    sub_issue: Optional[str] = None
    location: str
    landmark: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    priority: int
    priority_reason: Optional[str] = None
    department: str
    authority_title: str
    expected_resolution_days: int
    formal_letter: Optional[str] = None
    escalation_letter: Optional[str] = None
    status: str
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    upvotes: int
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    escalated: bool


class StatusUpdateRequest(BaseModel):
    status: str  # Submitted, Assigned, In Progress, Resolved
    update_note: Optional[str] = None


class EscalateRequest(BaseModel):
    complaint_id: Optional[int] = None
    tracking_id: Optional[str] = None
    reason: Optional[str] = None


class EscalateResponse(BaseModel):
    success: bool
    tracking_id: str
    escalation_letter: str
    higher_authority: str
    message: str


class ImageAnalysisRequest(BaseModel):
    image_data: str  # base64 data url


class ImageAnalysisResponse(BaseModel):
    description: str
    suggested_category: str
    suggested_sub_issue: str
    severity_assessment: str
    priority_score: int
    visual_evidence_summary: str


class AIWeeklyInsights(BaseModel):
    summary: str
    top_categories: List[Dict[str, Any]]
    hotspot_areas: List[str]
    recommendations: List[str]
    generated_at: str


class WorkOrderRequest(BaseModel):
    assigned_officer: Optional[str] = "Er. S. Patil (Junior Engineer)"
    contractor: Optional[str] = "M/s Ahilyanagar Municipal Rapid Infra Works"
    priority_instructions: Optional[str] = "Deploy field inspection and complete barrier placement within 4 hours."
    equipment_and_materials: Optional[List[str]] = Field(default_factory=lambda: ["Cold Asphalt Mix", "Barricades", "Reflective Cones"])


class WorkOrderResponse(BaseModel):
    work_order_id: str
    tracking_id: str
    issued_date: str
    deadline_date: str
    assigned_officer: str
    contractor: str
    department: str
    location: str
    instructions: str
    materials: List[str]
    work_order_document: str

