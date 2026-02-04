"""
Chat Router - Contract-aware AI assistant
Provides negotiation advice and contract explanations
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from google import genai

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize Gemini client
API_KEY = os.environ.get("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set")

client = genai.Client(api_key=API_KEY)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    contract_data: Optional[dict] = None
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    response: str
    success: bool = True


# ============================================================================
# CHAT ENDPOINT
# ============================================================================

@router.post("/ask", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Chat endpoint that provides contract advice and explanations.
    Uses contract context if available.
    """
    try:
        # Build system prompt with contract context
        system_prompt = _build_system_prompt(request.contract_data)
        
        # Build conversation history
        messages = _build_messages(
            system_prompt, 
            request.conversation_history, 
            request.message
        )
        
        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=messages
        )
        
        return ChatResponse(
            response=response.text,
            success=True
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _build_system_prompt(contract_data: Optional[dict]) -> str:
    """Build system prompt with optional contract context."""
    
    base_prompt = """You are an expert car lease contract advisor and negotiation assistant. Your role is to:

1. **Answer Questions**: Explain lease contract terms in simple, clear language
2. **Negotiate Better Terms**: Provide specific negotiation strategies and talking points
3. **Identify Issues**: Point out potentially unfavorable terms and red flags
4. **Empower Users**: Help users make informed decisions about their car lease

**Guidelines:**
- Be friendly, supportive, and empowering
- Use simple language - avoid legal jargon when possible
- Give response in minimal, user-friendly format, avoiding unnecessary technical details
- Provide specific, actionable advice
- When negotiating, give exact phrases/questions users can ask dealers
- Always prioritize the user's best interests
-If asked to analyze or critique a contract term, reference the specific section from the user's contract
"""

    if contract_data:
        # Extract key contract details
        contract_summary = _summarize_contract(contract_data)
        
        context_prompt = f"""

**USER'S CONTRACT CONTEXT:**
{contract_summary}

When answering questions:
- Reference SPECIFIC terms from their contract
- Compare their terms to industry standards
- Highlight both good and concerning aspects
- Provide personalized negotiation advice based on THEIR contract
"""
        return base_prompt + context_prompt
    
    return base_prompt + """

**Note:** No contract has been uploaded yet. Provide general car lease advice, but encourage the user to upload their contract for personalized assistance.
"""


def _summarize_contract(contract_data: dict) -> str:
    """Extract key information from contract for context."""
    
    summary_parts = []
    
    # Vehicle Info
    vehicle_info = contract_data.get("2. Vehicle Identification & Basic Details", {})
    if vehicle_info:
        car_name = vehicle_info.get("Car Name / Model", "Unknown")
        summary_parts.append(f"Vehicle: {car_name}")
    
    # Payment Details
    payments = contract_data.get("5. Payment Details", {})
    recurring = payments.get("5.2 Recurring Payments", {})
    if recurring:
        monthly = recurring.get("Monthly Payments", "Not disclosed")
        total = recurring.get("Total of Payments", "Not disclosed")
        summary_parts.append(f"Monthly Payment: {monthly}")
        summary_parts.append(f"Total Cost: {total}")
    
    # Lease Terms
    terms = contract_data.get("4. Lease Terms / Agreement Details", {})
    if terms:
        duration = terms.get("Agreement Duration / Term Period", "Not specified")
        mileage = terms.get("Mileage Allowance", "Not specified")
        early_term = terms.get("Early Termination Fee", "Not specified")
        summary_parts.append(f"Term: {duration}")
        summary_parts.append(f"Mileage: {mileage}")
        summary_parts.append(f"Early Termination Fee: {early_term}")
    
    # Fairness Analysis
    fairness = contract_data.get("8. Fairness Analysis", {})
    if fairness:
        score = fairness.get("fairness_score", "N/A")
        category = fairness.get("category", "N/A")
        summary_parts.append(f"Fairness Score: {score}/100 ({category})")
        
        warnings = fairness.get("warnings", [])
        if warnings:
            summary_parts.append(f"Warnings: {len(warnings)} issues identified")
    
    return "\n".join(summary_parts) if summary_parts else "Contract data incomplete"


def _build_messages(system_prompt: str, history: List[ChatMessage], user_message: str) -> str:
    """Build formatted message string for Gemini API."""
    
    # Start with system prompt
    full_prompt = f"{system_prompt}\n\n---\n\n"
    
    # Add conversation history
    if history:
        full_prompt += "**Conversation History:**\n"
        for msg in history[-6:]:  # Keep last 6 messages for context
            role = "User" if msg.role == "user" else "Assistant"
            full_prompt += f"{role}: {msg.content}\n"
        full_prompt += "\n---\n\n"
    
    # Add current user message
    full_prompt += f"User: {user_message}\n\nAssistant:"
    
    return full_prompt


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    return {
        "status": "healthy",
        "service": "chat-assistant",
        "model": "gemini-flash-latest"
    }