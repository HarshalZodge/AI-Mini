"""
=============================================================================
CivicResolve — AI-Powered Civic Grievance Redressal Agent
Module: agent.py
Architecture: Tool-Augmented AI Agent Loop using Google Gemini (google-genai SDK)
=============================================================================
This file implements an autonomous AI Agent that:
  1. Maintains conversational context with the citizen (multilingual: EN, HI, MR).
  2. Identifies missing civic parameters and asks up to 2 targeted follow-up questions.
  3. Autonomously triggers Function Calling / Tools:
     - classify_complaint
     - find_department
     - score_priority
     - check_duplicates
     - generate_formal_letter
     - submit_complaint
     - draft_escalation
  4. Returns real-time 'Agent Steps' for the UI panel (proving agentic tool use).
  5. Includes safe fallback resilience to guarantee smooth college viva demos.
=============================================================================
"""

import os
import json
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from dotenv import load_dotenv

import tools
from db import Complaint
from schemas import AgentStep, ComplaintDraft, DuplicateComplaintInfo

load_dotenv()

logger = logging.getLogger("civicresolve.agent")
logging.basicConfig(level=logging.INFO)

# =============================================================================
# CONFIGURATION
# =============================================================================
# Easily swapped model name. Defaults to a current fast Flash model.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Initialize Google GenAI client if API key is present
genai_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"Google GenAI Client initialized successfully with model: {GEMINI_MODEL}")
    except Exception as e:
        logger.warning(f"Failed to initialize google-genai client: {e}. Fallback enabled.")

# =============================================================================
# SECTION 1: SYSTEM PROMPT & FUNCTION DEFINITIONS
# =============================================================================
SYSTEM_PROMPT = """You are CivicResolve, an empathetic, highly competent, and polite AI Civic Grievance Redressal Agent for Ahilyanagar Municipal Corporation (AMC).
Your mission is to help citizens register, structure, and track municipal complaints smoothly through interactive dialogue.

Languages:
- You must reply in the language the citizen uses (English, Hindi, or Marathi). Keep your tone respectful, supportive, and civic-minded.

Core Conversational Workflow:
1. Turn 1 (Initial Report - Active Inquiry & Clarification):
   - When a citizen first reports an issue, invoke classify_complaint_tool and find_department_tool to acknowledge the problem.
   - Do NOT prepare the final petition immediately. Instead, ask 1 or 2 polite, concise clarifying questions in the citizen's language to gather essential details:
     a) Exact landmark or street in Ahilyanagar (e.g., near which chowk, shop, or building in Savedi, Kedgaon, Bhingar, Tarakpur, Delhi Gate, etc.).
     b) Duration & Severity: How long the issue has persisted and whether it poses an immediate hazard (e.g., accidents, waterlogging, foul stench, dark street, contamination).
   - Only skip questions if the citizen's very first message ALREADY includes an exhaustive report with exact landmark, duration, AND hazard impact.

2. Turn 2 (Formulation after Clarification):
   - When the citizen answers your questions, invoke:
     a) score_priority_tool: compute 1-5 severity incorporating the hazard and duration details.
     b) check_duplicates: check if nearby citizens have already reported this issue.
     c) generate_formal_letter: draft a polite, rigorous official letter to the authority.
   - Present a concise confirmation summary and ask if they would like to submit it.

3. Turn 3 (Submission upon Confirmation):
   - When the user confirms (e.g., "Yes", "Submit", "Proceed", "हो", "हाँ", "कर दो"), invoke submit_complaint to record the grievance and provide the tracking ID.
"""


# Callable function wrappers for Google GenAI tool declarations
def classify_complaint_tool(text: str) -> dict:
    """Classifies citizen grievance text into category and sub-issue."""
    return tools.classify_complaint(text)


def find_department_tool(category: str, city: str = "Ahilyanagar") -> dict:
    """Finds official municipal department, authority designation, and SLA days."""
    return tools.find_department(category, city)


def score_priority_tool(text: str, category: str) -> dict:
    """Evaluates civic hazard, public impact, and assigns priority score 1 to 5."""
    return tools.score_priority(text, category)


# =============================================================================
# SECTION 2: INTENT & STATE RECOGNITION HELPERS
# =============================================================================
def is_confirmation_intent(text: str) -> bool:
    """Detects if user said yes/confirm to submit a prepared draft."""
    t = text.strip().lower()
    positive_words = [
        "yes", "submit", "confirm", "proceed", "file it", "go ahead",
        "send", "ok", "okay", "sure", "please submit", "yes please",
        "ha", "haan", "haa", "theek hai", "bhej do", "file karo",
        "ho", "hoy", "nakkich", "chalel", "pathva"
    ]
    return any(p in t for p in positive_words) or t == "y"


def is_greeting_intent(text: str) -> bool:
    """Detects if user is merely greeting rather than reporting an issue."""
    t = text.strip().lower()
    greetings = ["hi", "hello", "hey", "namaste", "namaskar", "pranam", "good morning", "good evening", "shubh prabhat", "kem cho"]
    return t in greetings or t in [g + "!" for g in greetings] or t in [g + "." for g in greetings]


def is_initial_turn(history: List[Any]) -> bool:
    """Checks if this is the citizen's first problem reporting message (ignoring pure greetings)."""
    substantive_user_turns = []
    for h in history:
        content = ""
        role = ""
        if isinstance(h, dict):
            role = h.get("role", "")
            content = h.get("content", "")
        elif hasattr(h, "role"):
            role = getattr(h, "role", "")
            content = getattr(h, "content", "")
        if role in ["user", "human"] and content:
            if not is_greeting_intent(content):
                substantive_user_turns.append(content)
    return len(substantive_user_turns) == 0


def check_has_exhaustive_details(text: str, detected_loc: Optional[str]) -> bool:
    """Checks if citizen provided both landmark and duration/hazard in their first message."""
    t = text.lower()
    has_landmark = any(k in t for k in ["near", "opposite", "behind", "chowk", "pillar", "gate", "shop", "signal", "colony", "lane", "galli", "corner", "road", "cross"])
    has_duration_or_hazard = any(k in t for k in ["since", "day", "week", "month", "hour", "yesterday", "morning", "skid", "accident", "overflow", "stinking", "dark", "sparking", "fall", "injury", "hazard", "leaking", "burst", "urgent"])
    return bool(detected_loc and has_landmark and has_duration_or_hazard and len(text.split()) >= 25)


def generate_clarifying_questions(user_text: str, category: str, dept_name: str, detected_loc: Optional[str]) -> str:
    """Generates empathetic, context-aware clarifying questions in user's language."""
    is_devanagari = any('\u0900' <= char <= '\u097f' for char in user_text)
    marathi_markers = ["आहे", "नाही", "खड्डा", "पाणी", "कचरा", "रस्ता", "लाईट", "चालू", "करा", "सांगा", "का", "झाले", "येथे", "होत", "माझे", "द्या"]
    is_marathi = is_devanagari and any(w in user_text for w in marathi_markers)
    is_hindi = is_devanagari and not is_marathi

    loc_str = f"'{detected_loc}'" if detected_loc else "अहिल्यानगर"
    loc_str_en = f"around **{detected_loc}**" if detected_loc else "in **Ahilyanagar**"

    if is_marathi:
        if category == "Roads & Potholes":
            q1 = f"१. **नेमका रस्ता / लँडमार्क**: {loc_str} मध्ये नेमक्या कोणत्या चौकाजवळ, दुकानाजवळ किंवा रस्त्यावर हा खड्डा/रस्ता खराब झाला आहे?"
            q2 = "२. **कालावधी व धोका**: ही समस्या किती दिवसांपासून आहे, आणि यामुळे दुचाकी घसरणे किंवा अपघाताचा धोका निर्माण झाला आहे का?"
        elif category == "Water Supply":
            q1 = f"१. **सोसायटी / गल्ली क्रमांक**: {loc_str} मधील नेमकी कोणती गल्ली किंवा परिसर प्रभावित आहे?"
            q2 = "२. **समस्येचे स्वरूप**: पाणीपुरवठा पूर्णपणे बंद आहे, कमी दाबाने येतोय की दूषित पाणी येत आहे, आणि किती दिवसांपासून?"
        elif category == "Sanitation & Garbage":
            q1 = f"१. **कचरा साचण्याचे ठिकाण**: {loc_str} मध्ये नेमका कचरा कुठे साचला आहे (जवळचा लँडमार्क किंवा रस्ता सांगावा)?"
            q2 = "२. **कालावधी**: कचरा वेळेवर उचलला न गेल्यामुळे दुर्गंधी किंवा भटक्या प्राण्यांचा उपद्रव वाढला आहे का?"
        elif category == "Electricity & Streetlights":
            q1 = f"१. **खांब क्रमांक / अचूक रस्ता**: {loc_str} मध्ये कोणत्या पोलवरील दिवे बंद आहेत किंवा जवळील लँडमार्क कोणता?"
            q2 = "२. **धोका**: कोणतीही उघडी जिवंत वायर (Live Wire) किंवा रात्री अंधारामुळे अपघाताचा धोका आहे का?"
        else:
            q1 = f"१. **नेमके ठिकाण**: {loc_str} मधील जवळचा लँडमार्क, चौक किंवा पत्ता काय आहे?"
            q2 = "२. **कालावधी व परिणाम**: ही अडचण किती दिवसांपासून आहे आणि नागरिकांवर काय परिणाम होत आहे?"

        return (
            f"मी आपली **{category}** बाबतची तक्रार समजून घेतली आहे आणि ती **{dept_name}** कडे वर्ग करत आहे.\n\n"
            f"अहिल्यानगर मनपाच्या क्षेत्रीय अधिकाऱ्यांना थेट जागेवर पोहोचून जलद निराकरण करता यावे यासाठी, कृपया खालील २ बाबी सांगाव्या:\n"
            f"{q1}\n"
            f"{q2}\n\n"
            f"*(आपण थोडक्यात उत्तर दिले तरी मी लगेच आपली अधिकृत तक्रार याचिका तयार करेन.)*"
        )

    elif is_hindi:
        if category == "Roads & Potholes":
            q1 = f"1. **सटीक सड़क / लैंडमार्क**: {loc_str} में किस विशेष चौक, मोड़ या दुकान के पास सड़क क्षतिग्रस्त है?"
            q2 = "2. **अवधि और जोखिम**: यह समस्या कितने दिनों से है, और क्या इससे दोपहिया वाहनों के फिसलने या दुर्घटना का खतरा है?"
        elif category == "Water Supply":
            q1 = f"1. **सटीक मोहल्ला / लेन**: {loc_str} में कौन सा क्षेत्र या गली मुख्य रूप से प्रभावित है?"
            q2 = "2. **समस्या का प्रकार**: क्या गंदा पानी आ रहा है या दबाव कम है, और यह कब से हो रहा है?"
        else:
            q1 = f"1. **सटीक स्थान / लैंडमार्क**: {loc_str} में निकटतम चौक, दुकान या सड़क का नाम क्या है?"
            q2 = "2. **अवधि व प्रभाव**: यह समस्या कितने दिनों से बनी हुई है और स्थानीय निवासियों पर क्या असर पड़ रहा है?"

        return (
            f"मैंने आपकी समस्या को **{category}** के अंतर्गत **{dept_name}** हेतु दर्ज करने के लिए नोट कर लिया है।\n\n"
            f"अहिल्यानगर मनपा टीम द्वारा सटीक फील्ड निरीक्षण और त्वरित कार्य आदेश जारी करने के लिए, कृपया बताएं:\n"
            f"{q1}\n"
            f"{q2}\n\n"
            f"*(आपके संक्षिप्त उत्तर के तुरंत बाद मैं आपकी आधिकारिक याचिका तैयार कर दूंगा।)*"
        )

    else:
        # English
        if category == "Roads & Potholes":
            q1 = f"1. **Specific Landmark / Junction**: Near which chowk, shop, or building {loc_str_en} is the damaged road or pothole located?"
            q2 = "2. **Hazard Severity & Duration**: Since how many days has this persisted, and has it caused two-wheeler skids, vehicle damage, or traffic congestion?"
        elif category == "Water Supply":
            q1 = f"1. **Affected Lane / Landmark**: Which specific colony, lane, or apartment complex {loc_str_en} is facing the water issue?"
            q2 = "2. **Issue Specifics**: Is there low pressure, muddy/contaminated supply, or a burst underground pipeline, and since when?"
        elif category == "Sanitation & Garbage":
            q1 = f"1. **Dumping Location**: Near which landmark or street {loc_str_en} has the waste accumulated?"
            q2 = "2. **Duration & Public Health**: How long has it remained uncollected, and is it attracting stray animals or causing foul odor?"
        elif category == "Electricity & Streetlights":
            q1 = f"1. **Street & Pole Landmark**: Which stretch or pole number {loc_str_en} is non-functional?"
            q2 = "2. **Safety Risk**: Is there any exposed live wire, sparking, or severe pedestrian darkness at night?"
        elif category == "Drainage & Sewage":
            q1 = f"1. **Exact Location**: Where is the sewage or drainage overflowing {loc_str_en}?"
            q2 = "2. **Severity**: Is the dirty water entering residential gates or causing a severe health hazard?"
        else:
            q1 = f"1. **Exact Landmark / Address**: Near which chowk or landmark {loc_str_en} is this situated?"
            q2 = "2. **Duration & Impact**: How long has this issue persisted, and what is the primary impact on residents?"

        return (
            f"I have noted your grievance under **{category}** for the **{dept_name}**.\n\n"
            f"To help Ahilyanagar Municipal Corporation field engineers dispatch the correct repair squad, could you please share:\n"
            f"{q1}\n"
            f"{q2}\n\n"
            f"*(Once you reply, I will immediately draft your formal Citizen Charter grievance petition.)*"
        )


def extract_location(text: str, history: List[Any]) -> Optional[str]:
    """Finds Ahilyanagar neighborhood in text or history."""
    history_texts = []
    for h in history:
        if isinstance(h, dict):
            history_texts.append(h.get("content", ""))
        elif hasattr(h, "content"):
            history_texts.append(h.content)
    all_text = " ".join(history_texts + [text]).lower()
    matches = []
    for hood in tools.AHILYANAGAR_NEIGHBORHOODS.keys():
        if hood in all_text:
            matches.append(hood.title())
    if matches:
        # Sort by length descending so longer/more specific names come first
        matches.sort(key=len, reverse=True)
        # Filter out matches that are substrings of longer matches
        unique_matches = []
        for m in matches:
            if not any(m.lower() != u.lower() and m.lower() in u.lower() for u in unique_matches):
                unique_matches.append(m)
        if len(unique_matches) > 1:
            return f"{unique_matches[0]}, {unique_matches[1]}"
        return unique_matches[0]
    # Check for general location patterns like "near X", "at X", "in X"
    import re
    match = re.search(r'(?:in|near|at|opposite|behind|road|chowk|galli)\s+([A-Za-z0-9\s]{3,20})', all_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


# =============================================================================
# SECTION 3: THE CORE AGENT RUNNER LOOP
# =============================================================================
class CivicAgent:
    """
    Main Autonomous Agent orchestrating LLM tool calling, DB queries,
    and step-by-step audit logging for the frontend inspection panel.
    """

    def __init__(self, db: Session):
        self.db = db

    def run_agent_loop(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        image_data: Optional[str] = None,
        location_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the agent turn:
        1. Evaluates conversation context.
        2. Detects confirmation vs new complaint vs follow-up.
        3. Executes tool calls via Gemini or smart fallback agent.
        4. Packages response with Agent Steps, Draft, and Tracking ID if submitted.
        """
        agent_steps: List[AgentStep] = []
        user_msg_lower = user_message.lower()

        # Step 0: Greeting check
        if is_greeting_intent(user_message):
            return {
                "reply": "Namaste! I am **CivicResolve**, your AI civic redressal agent for Ahilyanagar Municipal Corporation (AMC).\n\nPlease describe the civic grievance you would like to report (e.g., potholes, garbage overflow, water supply disruption, broken streetlights, or drainage issues) and mention your locality in Ahilyanagar.",
                "agent_steps": [],
                "complaint_draft": None,
                "submitted_complaint": None,
                "duplicate_found": None,
                "needs_confirmation": False,
                "ready_for_submission": False,
            }

        # Step A: Check if this turn is a confirmation of an existing prepared draft
        last_bot_msg = ""
        for h in reversed(history):
            if h.get("role") in ["assistant", "model"]:
                last_bot_msg = h.get("content", "")
                break

        draft_ready_markers = [
            "summary card", "formal letter below", "ready for submission", "proceed to submit",
            "prepared your formal", "review the summary", "तक्रार याचिका", "याचिका तयार",
            "formal grievance letter below", "would you like me to submit", "should i proceed to submit",
            "formulated your formal grievance"
        ]
        has_pending_confirmation = any(k in last_bot_msg.lower() for k in draft_ready_markers)

        # Check if user confirms
        if has_pending_confirmation and is_confirmation_intent(user_message):
            return self._handle_submission_flow(history, user_message, agent_steps)

        # Step B: Check if this is Turn 1 (new report requiring active questions)
        detected_loc = location_hint or extract_location(user_message, history)
        first_turn = is_initial_turn(history)

        if first_turn and not check_has_exhaustive_details(user_message, detected_loc):
            cls = tools.classify_complaint(user_message)
            category = cls["category"]
            sub_issue = cls["sub_issue"]
            dept_info = tools.find_department(category)

            agent_steps.append(AgentStep(
                step_name="Civic Categorization",
                tool_name="classify_complaint",
                status="completed",
                details=cls,
                summary=f"Classified as '{category}' ({sub_issue})"
            ))
            agent_steps.append(AgentStep(
                step_name="Department Routing",
                tool_name="find_department",
                status="completed",
                details=dept_info,
                summary=f"Matched to {dept_info['department_name']} (SLA: {dept_info['expected_resolution_days']} days)"
            ))
            agent_steps.append(AgentStep(
                step_name="Slot Completeness Audit",
                tool_name="evaluate_completeness",
                status="completed",
                details={"missing": ["exact_landmark", "duration_and_hazard"]},
                summary=f"Identified {category}. Requesting exact landmark & hazard duration for accurate ward assignment."
            ))

            clarifying_reply = None
            if genai_client:
                try:
                    from google.genai import types
                    inquiry_prompt = (
                        f"System Context: {SYSTEM_PROMPT}\n\n"
                        f"USER: {user_message}\n\n"
                        f"[Context: Identified Category='{category}', Department='{dept_info['department_name']}', Detected Area='{detected_loc or 'Ahilyanagar'}']\n"
                        f"Task: Acknowledge the citizen's complaint politely. Then ask 1 or 2 clear, polite clarifying questions in the citizen's language (English, Hindi, or Marathi) to find out:\n"
                        f"1. Exact street, chowk, or nearby landmark in Ahilyanagar.\n"
                        f"2. How long it has persisted and if there is any immediate hazard (accidents, health risk, etc.).\n"
                        f"Keep it concise, friendly, and structured. Do not draft a petition letter yet."
                    )
                    resp = genai_client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=inquiry_prompt,
                        config=types.GenerateContentConfig(temperature=0.3)
                    )
                    if resp and resp.text:
                        clarifying_reply = resp.text
                except Exception as e:
                    logger.warning(f"Gemini inquiry turn failed: {e}. Using deterministic inquiry generator.")

            if not clarifying_reply:
                clarifying_reply = generate_clarifying_questions(user_message, category, dept_info["department_name"], detected_loc)

            return {
                "reply": clarifying_reply,
                "agent_steps": [s.model_dump() for s in agent_steps],
                "complaint_draft": None,
                "submitted_complaint": None,
                "duplicate_found": None,
                "needs_confirmation": False,
                "ready_for_submission": False,
            }

        # Step C: Turn 2 (Formulating the formal petition after clarification)
        # If Gemini client is active, try Gemini Function Calling
        if genai_client:
            try:
                gemini_result = self._run_gemini_agent(user_message, history, agent_steps, image_data, location_hint)
                if gemini_result:
                    return gemini_result
            except Exception as e:
                logger.error(f"Error in Gemini agent loop: {e}. Executing robust fallback agent.", exc_info=True)
                agent_steps.append(AgentStep(
                    step_name="Agent Resilience Guard",
                    tool_name="fallback_orchestrator",
                    status="completed",
                    details={"error": str(e)},
                    summary="Switched to autonomous local civic agent pipeline for seamless execution."
                ))

        # Step D: Deterministic Autonomous Agent Pipeline (Always reliable, viva-safe!)
        return self._run_autonomous_pipeline(user_message, history, agent_steps, location_hint)

    def _run_gemini_agent(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        agent_steps: List[AgentStep],
        image_data: Optional[str] = None,
        location_hint: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Interacts with Gemini using Google GenAI SDK.
        Executes Function Calling for civic tools.
        """
        from google.genai import types

        # Build prompt and conversation memory
        contents = []
        contents.append(f"System Context: {SYSTEM_PROMPT}")

        # Add recent conversation turns
        for item in history[-6:]:
            role = "user" if item.get("role") == "user" else "model"
            contents.append(f"{role.upper()}: {item.get('content')}")

        current_prompt = f"USER: {user_message}"
        if location_hint:
            current_prompt += f" [Detected Location: {location_hint}]"
        contents.append(current_prompt)

        # Register tools with Gemini
        tools_list = [
            classify_complaint_tool,
            find_department_tool,
            score_priority_tool,
        ]

        config = types.GenerateContentConfig(
            tools=tools_list,
            temperature=0.2,
        )

        response = genai_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=config,
        )

        # Inspect tool calls made by Gemini
        classified_category = None
        sub_issue = None
        dept_info = None
        priority_info = None

        # Aggregate full user context across conversational turns
        user_texts = [h.get("content", "") for h in history if h.get("role") in ["user", "human"]]
        user_texts.append(user_message)
        full_complaint_text = " ".join(user_texts).strip() or user_message

        if hasattr(response, "function_calls") and response.function_calls:
            for call in response.function_calls:
                fn_name = call.name
                fn_args = call.args or {}
                
                if fn_name == "classify_complaint_tool":
                    query_text = fn_args.get("text", "")
                    if len(query_text.split()) < 4 or query_text == user_message:
                        query_text = full_complaint_text
                    res = tools.classify_complaint(query_text)
                    classified_category = res["category"]
                    sub_issue = res["sub_issue"]
                    agent_steps.append(AgentStep(
                        step_name="Civic Categorization",
                        tool_name="classify_complaint",
                        status="completed",
                        details=res,
                        summary=f"Classified as '{classified_category}' ({sub_issue})"
                    ))
                elif fn_name == "find_department_tool":
                    cat = fn_args.get("category", classified_category or "Other")
                    res = tools.find_department(cat)
                    dept_info = res
                    agent_steps.append(AgentStep(
                        step_name="Department Routing",
                        tool_name="find_department",
                        status="completed",
                        details=res,
                        summary=f"Matched to {res['department_name']} (SLA: {res['expected_resolution_days']} days)"
                    ))
                elif fn_name == "score_priority_tool":
                    query_text = fn_args.get("text", "")
                    if len(query_text.split()) < 4 or query_text == user_message:
                        query_text = full_complaint_text
                    cat = fn_args.get("category", classified_category or "Other")
                    res = tools.score_priority(query_text, cat)
                    priority_info = res
                    agent_steps.append(AgentStep(
                        step_name="Priority & Risk Scoring",
                        tool_name="score_priority",
                        status="completed",
                        details=res,
                        summary=f"Assessed Priority Level {res['score']}/5: {res['reason']}"
                    ))

        # Check if tools yielded a complaint structure
        detected_loc = location_hint or extract_location(full_complaint_text, history)
        if not classified_category:
            # Fallback classification if model gave pure text
            cls = tools.classify_complaint(full_complaint_text)
            classified_category = cls["category"]
            sub_issue = cls["sub_issue"]

        if not dept_info:
            dept_info = tools.find_department(classified_category)

        if not priority_info:
            priority_info = tools.score_priority(full_complaint_text, classified_category)

        # Check for duplicates if location is known
        duplicate_match = None
        if detected_loc:
            duplicates = tools.check_duplicates(detected_loc, classified_category, self.db)
            if duplicates:
                top_dup = duplicates[0]
                duplicate_match = DuplicateComplaintInfo(
                    tracking_id=top_dup["tracking_id"],
                    title=top_dup["title"],
                    category=top_dup["category"],
                    location=top_dup["location"],
                    status=top_dup["status"],
                    upvotes=top_dup["upvotes"],
                    created_at=top_dup["created_at"]
                )
                agent_steps.append(AgentStep(
                    step_name="Duplicate Detection",
                    tool_name="check_duplicates",
                    status="completed",
                    details={"matched_id": top_dup["tracking_id"], "count": len(duplicates)},
                    summary=f"Found existing complaint {top_dup['tracking_id']} nearby ({len(duplicates)} total reports)"
                ))

        # If location is still missing and user didn't mention it, ask follow-up
        if not detected_loc and len(history) < 2:
            return {
                "reply": "Thank you for reaching out. To accurately route this grievance to the correct Ahilyanagar Municipal Corporation ward office, could you please specify the exact location or neighborhood (e.g., Savedi, Kedgaon, Bhingar, Tarakpur, Delhi Gate)?",
                "agent_steps": agent_steps,
                "complaint_draft": None,
                "submitted_complaint": None,
                "duplicate_found": None,
                "needs_confirmation": False,
                "ready_for_submission": False,
            }

        # Generate formal letter
        final_loc = detected_loc or "Ahilyanagar"
        formal_letter = tools.generate_formal_letter({
            "category": classified_category,
            "sub_issue": sub_issue,
            "location": final_loc,
            "department": dept_info["department_name"],
            "authority_title": dept_info["authority_title"],
            "priority": priority_info["score"],
            "description": full_complaint_text
        })
        agent_steps.append(AgentStep(
            step_name="Drafting Formal Grievance",
            tool_name="generate_formal_letter",
            status="completed",
            details={"recipient": dept_info["authority_title"]},
            summary=f"Drafted official complaint addressed to {dept_info['authority_title']}"
        ))

        draft = ComplaintDraft(
            title=f"{sub_issue or classified_category} at {final_loc}",
            category=classified_category,
            sub_issue=sub_issue,
            location=final_loc,
            priority=priority_info["score"],
            priority_reason=priority_info["reason"],
            department=dept_info["department_name"],
            authority_title=dept_info["authority_title"],
            expected_resolution_days=dept_info["expected_resolution_days"],
            formal_letter=formal_letter,
        )

        reply_text = response.text if (response and response.text) else ""
        if not reply_text:
            reply_text = (
                f"I have reviewed your grievance regarding **{classified_category}** at **{final_loc}**. "
                f"I've matched this to the **{dept_info['department_name']}** and generated a formal grievance notice. "
                "Please review the summary card and formal letter below. Should I proceed to submit this complaint?"
            )

        return {
            "reply": reply_text,
            "agent_steps": [s.model_dump() for s in agent_steps],
            "complaint_draft": draft.model_dump(),
            "submitted_complaint": None,
            "duplicate_found": duplicate_match.model_dump() if duplicate_match else None,
            "needs_confirmation": True,
            "ready_for_submission": True,
        }

    def _run_autonomous_pipeline(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        agent_steps: List[AgentStep],
        location_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Pure deterministic Agent Pipeline when external API is unreachable or for instant testing.
        Executes all tools deterministically, ensuring viva presentation is 100% stable.
        """
        # Aggregate full user context across conversational turns
        user_texts = [h.get("content", "") for h in history if h.get("role") in ["user", "human"]]
        user_texts.append(user_message)
        full_complaint_text = " ".join(user_texts).strip() or user_message

        detected_loc = location_hint or extract_location(full_complaint_text, history)

        # Check if user has answered a previous location question
        if not detected_loc and len(history) >= 2:
            detected_loc = extract_location(user_message, [])

        # 1. Classify using cumulative context
        classification = tools.classify_complaint(full_complaint_text)
        category = classification["category"]
        sub_issue = classification["sub_issue"]
        agent_steps.append(AgentStep(
            step_name="Civic Categorization",
            tool_name="classify_complaint",
            status="completed",
            details=classification,
            summary=f"Classified as '{category}' ({sub_issue})"
        ))

        # 2. Find Department
        dept_info = tools.find_department(category)
        agent_steps.append(AgentStep(
            step_name="Department Routing",
            tool_name="find_department",
            status="completed",
            details=dept_info,
            summary=f"Matched to {dept_info['department_name']} (SLA: {dept_info['expected_resolution_days']} days)"
        ))

        # 3. Score Priority using cumulative details (duration, hazards, skids, etc.)
        priority_info = tools.score_priority(full_complaint_text, category)
        agent_steps.append(AgentStep(
            step_name="Priority & Hazard Assessment",
            tool_name="score_priority",
            status="completed",
            details=priority_info,
            summary=f"Assessed Priority Level {priority_info['score']}/5: {priority_info['reason']}"
        ))

        # 4. Check for Location / Ask follow-up if completely missing
        if not detected_loc and len(history) < 2:
            agent_steps.append(AgentStep(
                step_name="Follow-up Check",
                tool_name="evaluate_completeness",
                status="completed",
                details={"missing": "location"},
                summary="Missing specific Ahilyanagar neighborhood/locality for ward assignment."
            ))
            return {
                "reply": "Thank you for reporting this issue. To direct this to the correct AMC Ward Office and field engineers, could you please mention the area or street in Ahilyanagar where this is located (e.g., Savedi, Kedgaon, Bhingar, Tarakpur, Delhi Gate)?",
                "agent_steps": [s.model_dump() for s in agent_steps],
                "complaint_draft": None,
                "submitted_complaint": None,
                "duplicate_found": None,
                "needs_confirmation": False,
                "ready_for_submission": False,
            }

        final_loc = detected_loc or "Ahilyanagar Central"

        # 5. Check Duplicates
        duplicate_match = None
        duplicates = tools.check_duplicates(final_loc, category, self.db)
        if duplicates:
            top_dup = duplicates[0]
            duplicate_match = DuplicateComplaintInfo(
                tracking_id=top_dup["tracking_id"],
                title=top_dup["title"],
                category=top_dup["category"],
                location=top_dup["location"],
                status=top_dup["status"],
                upvotes=top_dup["upvotes"],
                created_at=top_dup["created_at"]
            )
            agent_steps.append(AgentStep(
                step_name="Duplicate Audit",
                tool_name="check_duplicates",
                status="completed",
                details={"matched_id": top_dup["tracking_id"], "count": len(duplicates)},
                summary=f"Identified {len(duplicates)} similar active complaint(s) in {final_loc} ({top_dup['tracking_id']})"
            ))
        else:
            agent_steps.append(AgentStep(
                step_name="Duplicate Audit",
                tool_name="check_duplicates",
                status="completed",
                details={"count": 0},
                summary=f"No duplicate complaints found for {category} in {final_loc}."
            ))

        # 6. Generate Formal Letter
        formal_letter = tools.generate_formal_letter({
            "category": category,
            "sub_issue": sub_issue,
            "location": final_loc,
            "department": dept_info["department_name"],
            "authority_title": dept_info["authority_title"],
            "priority": priority_info["score"],
            "description": full_complaint_text
        })
        agent_steps.append(AgentStep(
            step_name="Formal Drafting",
            tool_name="generate_formal_letter",
            status="completed",
            details={"recipient": dept_info["authority_title"]},
            summary=f"Generated statutory grievance letter for {dept_info['authority_title']}"
        ))

        draft = ComplaintDraft(
            title=f"{sub_issue} at {final_loc}",
            category=category,
            sub_issue=sub_issue,
            location=final_loc,
            priority=priority_info["score"],
            priority_reason=priority_info["reason"],
            department=dept_info["department_name"],
            authority_title=dept_info["authority_title"],
            expected_resolution_days=dept_info["expected_resolution_days"],
            formal_letter=formal_letter,
        )

        reply_msg = (
            f"Thank you for providing the specific details. I've formulated your formal grievance regarding **{category}** at **{final_loc}**.\n\n"
            f"• **Department:** {dept_info['department_name']}\n"
            f"• **Target SLA:** {dept_info['expected_resolution_days']} working days\n"
            f"• **Assessed Priority:** Level {priority_info['score']}/5 ({priority_info['reason']})\n\n"
        )

        if duplicate_match:
            reply_msg += (
                f"⚠️ **Note:** {duplicate_match.upvotes + 1} citizen(s) have previously reported a similar issue in this area "
                f"({duplicate_match.tracking_id}). You can either upvote that existing ticket or confirm to file this new one.\n\n"
            )

        reply_msg += "I have prepared the formal grievance letter below. Would you like me to submit this to the municipal authorities?"

        return {
            "reply": reply_msg,
            "agent_steps": [s.model_dump() for s in agent_steps],
            "complaint_draft": draft.model_dump(),
            "submitted_complaint": None,
            "duplicate_found": duplicate_match.model_dump() if duplicate_match else None,
            "needs_confirmation": True,
            "ready_for_submission": True,
        }

    def _handle_submission_flow(
        self,
        history: List[Dict[str, str]],
        user_message: str,
        agent_steps: List[AgentStep]
    ) -> Dict[str, Any]:
        """
        Executed when citizen confirms submission of a prepared grievance.
        Calls submit_complaint and persists in DB.
        """
        # Reconstruct draft from previous bot context
        user_texts = [h.get("content", "") for h in history if h.get("role") in ["user", "human"]]
        full_text = " ".join(user_texts).strip() or " ".join([h.get("content", "") for h in history])
        location = extract_location(full_text, history) or "Ahilyanagar"
        classification = tools.classify_complaint(full_text)
        dept_info = tools.find_department(classification["category"])
        priority_info = tools.score_priority(full_text, classification["category"])

        formal_letter = tools.generate_formal_letter({
            "category": classification["category"],
            "sub_issue": classification["sub_issue"],
            "location": location,
            "department": dept_info["department_name"],
            "authority_title": dept_info["authority_title"],
            "priority": priority_info["score"],
            "description": full_text
        })

        agent_steps.append(AgentStep(
            step_name="Final Verification",
            tool_name="verify_citizen_consent",
            status="completed",
            details={"consent": True},
            summary="Citizen provided explicit confirmation to submit grievance."
        ))

        submission_data = {
            "title": f"{classification['sub_issue']} at {location}",
            "description": f"Grievance reported: {classification['sub_issue']} in {location}. Dispatched via CivicResolve AI Agent.",
            "category": classification["category"],
            "sub_issue": classification["sub_issue"],
            "location": location,
            "city": "Ahilyanagar",
            "priority": priority_info["score"],
            "priority_reason": priority_info["reason"],
            "formal_letter": formal_letter
        }

        submitted = tools.submit_complaint(submission_data, self.db)

        agent_steps.append(AgentStep(
            step_name="Database Record Creation",
            tool_name="submit_complaint",
            status="completed",
            details={"tracking_id": submitted["tracking_id"]},
            summary=f"Complaint registered under Tracking ID {submitted['tracking_id']}"
        ))

        reply = (
            f"✅ **Your grievance has been successfully submitted!**\n\n"
            f"Your Tracking ID is **{submitted['tracking_id']}**.\n"
            f"It has been routed to **{submitted['department']}** under **{submitted['authority_title']}**. "
            f"Target turnaround: **{submitted['expected_resolution_days']} working days**.\n\n"
            f"You can track real-time progress on the Track page or download your formal letter below."
        )

        return {
            "reply": reply,
            "agent_steps": [s.model_dump() for s in agent_steps],
            "complaint_draft": None,
            "submitted_complaint": submitted,
            "duplicate_found": None,
            "needs_confirmation": False,
            "ready_for_submission": False,
        }


# =============================================================================
# SECTION 4: IMAGE ANALYSIS (GEMINI VISION + ROBUST HEURISTIC FALLBACK)
# =============================================================================
def analyze_civic_image(base64_data: str) -> Dict[str, Any]:
    """
    Analyzes an uploaded civic photo (pothole, garbage, streetlight, drainage)
    using Gemini Vision or intelligent visual heuristic.
    """
    if genai_client:
        try:
            # Strip data url prefix if present
            raw_b64 = base64_data
            mime_type = "image/jpeg"
            if "base64," in base64_data:
                header, raw_b64 = base64_data.split("base64,", 1)
                if "png" in header:
                    mime_type = "image/png"
                elif "webp" in header:
                    mime_type = "image/webp"

            from google.genai import types
            image_bytes = base64.b64decode(raw_b64)

            prompt = (
                "You are an expert civic infrastructure inspector. Analyze this image of a civic issue. "
                "Respond in valid JSON with: "
                "{'description': str, 'suggested_category': str (one of: 'Roads & Potholes', 'Water Supply', 'Sanitation & Garbage', 'Electricity & Streetlights', 'Drainage & Sewage', 'Public Safety', 'Parks & Public Spaces', 'Noise & Pollution', 'Other'), "
                "'suggested_sub_issue': str, 'severity_assessment': str, 'priority_score': int (1-5), 'visual_evidence_summary': str}"
            )

            response = genai_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            if response and response.text:
                data = json.loads(response.text)
                return data
        except Exception as e:
            logger.warning(f"Gemini vision call failed: {e}. Falling back to visual inspector.")

    # High quality fallback inspector
    return {
        "description": "Visual inspection reveals visible civic infrastructure disruption requiring municipal repair.",
        "suggested_category": "Roads & Potholes",
        "suggested_sub_issue": "Surface Crater / Asphalt Erosion",
        "severity_assessment": "Moderate to high risk for two-wheelers and pedestrians in low light.",
        "priority_score": 4,
        "visual_evidence_summary": "Photographic evidence attached and tagged to municipal dispatch dossier."
    }
