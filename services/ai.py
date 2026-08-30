"""
LeaseGuard AI - AI Pipeline Service (Phase 3).
Orchestrates RocketRide Cloud pipelines with Gemini Primary and Groq Fallback LLM execution.
"""
import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from rocketride import Question, RocketRideClient

load_dotenv()
logger = logging.getLogger("leaseguard.ai")

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "lease_extraction.txt"
GEMINI_PIPE_FILE = Path(__file__).parent.parent / "pipelines" / "lease_extraction.pipe"
GROQ_PIPE_FILE = Path(__file__).parent.parent / "pipelines" / "lease_extraction_groq.pipe"


# ============================================================================
# Pydantic Structured Data Model
# ============================================================================

def _clean_number(v: Any) -> Optional[float]:
    """Helper to convert string representations like '$120,000' or '10000.00' to float."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        cleaned = re.sub(r"[^\d.]", "", v.replace(",", ""))
        if cleaned:
            try:
                return float(cleaned)
            except ValueError:
                pass
    return None


class LeaseRules(BaseModel):
    """Pydantic validation model for extracted commercial lease terms and rules."""

    base_rent: Optional[float] = Field(default=None, description="Base annual rent amount")
    base_rent_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting base rent")

    rent_frequency: Optional[str] = Field(default=None, description="Frequency of rent (annual, monthly, etc.)")
    rent_frequency_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting rent frequency")

    rent_escalation_rules: Optional[str] = Field(default=None, description="Escalation rules or formula")
    rent_escalation_evidence: Optional[str] = Field(default=None, description="Exact text quote for escalation rules")

    cam_rules: Optional[str] = Field(default=None, description="CAM rules, reconciliation terms, or obligations")
    cam_rules_evidence: Optional[str] = Field(default=None, description="Exact text quote for CAM rules")

    cam_cap: Optional[float] = Field(default=None, description="Numerical cap on CAM expenses per year/period")
    cam_cap_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting CAM cap")

    tenant_share: Optional[str] = Field(default=None, description="Tenant's pro-rata share percentage or description")
    tenant_share_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting tenant share")

    administrative_fee_rules: Optional[str] = Field(default=None, description="Administrative fee limits or rules")
    administrative_fee_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting admin fee rules")

    expense_exclusions: Optional[str] = Field(default=None, description="Explicit exclusions from CAM/operating expenses")
    expense_exclusions_evidence: Optional[str] = Field(default=None, description="Exact text quote for expense exclusions")

    tax_responsibility: Optional[str] = Field(default=None, description="Tax obligations or breakdown")
    tax_responsibility_evidence: Optional[str] = Field(default=None, description="Exact text quote for tax responsibility")

    audit_rights: Optional[str] = Field(default=None, description="Audit rights or reconciliation timeframe")
    audit_rights_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting audit rights")

    lease_start_date: Optional[str] = Field(default=None, description="Start date of lease")
    lease_start_date_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting start date")

    lease_end_date: Optional[str] = Field(default=None, description="End date of lease")
    lease_end_date_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting end date")

    renewal_terms: Optional[str] = Field(default=None, description="Renewal options or terms")
    renewal_terms_evidence: Optional[str] = Field(default=None, description="Exact text quote supporting renewal terms")

    relevant_lease_clauses: List[str] = Field(default_factory=list, description="Key verbatim clauses extracted from document")

    @field_validator("base_rent", "cam_cap", mode="before")
    @classmethod
    def validate_numeric_fields(cls, v: Any) -> Optional[float]:
        return _clean_number(v)


# ============================================================================
# Helpers & Pipeline Execution Core
# ============================================================================

def _load_prompt_template() -> str:
    """Load the lease extraction prompt template."""
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()


def _parse_and_validate_response(raw_answer: Union[str, dict]) -> LeaseRules:
    """Clean LLM output string or dict and validate against LeaseRules Pydantic schema."""
    if isinstance(raw_answer, dict):
        data_dict = raw_answer
    elif isinstance(raw_answer, str):
        clean_str = raw_answer.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[7:]
        if clean_str.startswith("```"):
            clean_str = clean_str[3:]
        if clean_str.endswith("```"):
            clean_str = clean_str[:-3]
        clean_str = clean_str.strip()
        data_dict = json.loads(clean_str)
    else:
        raise ValueError(f"Unexpected response type from pipeline: {type(raw_answer)}")

    return LeaseRules.model_validate(data_dict)


async def _run_rocketride_extraction(pipe_filepath: str, text: str, env_vars: dict) -> Union[str, dict]:
    """Connect to RocketRide Cloud, run the specified pipeline, and send text for chat Q&A."""
    async with RocketRideClient(env=env_vars) as client:
        # Start RocketRide pipeline
        result = await client.use(filepath=pipe_filepath, env=env_vars)
        token = result.get("token")
        if not token:
            raise RuntimeError(f"RocketRide server failed to return task token for {pipe_filepath}")

        # Construct Question payload
        prompt_text = _load_prompt_template()
        question = Question(expectJson=True)
        question.addQuestion(prompt_text)
        question.addContext(f"LEASE DOCUMENT TEXT:\n{text}")

        # Send request to RocketRide chat source
        response = await client.chat(token=token, question=question)
        answers = response.get("answers") or []
        if not answers:
            raise RuntimeError("RocketRide pipeline returned empty answers payload.")

        return answers[0]


def _run_async(coro):
    """Run an async coroutine synchronously, handling running loops if needed."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Handle environment with pre-existing event loop if any
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)


# ============================================================================
# Main Application AI Functions
# ============================================================================

def extract_lease_rules(
    text: str,
    gemini_key: Optional[str] = None,
    groq_key: Optional[str] = None,
    force_fallback: bool = False
) -> Dict[str, Any]:
    """
    Extract structured commercial lease rules using RocketRide Cloud pipeline.
    
    Provider Execution Strategy:
    1. Try Gemini (Primary LLM Provider)
    2. If Gemini fails due to API error/failure, Try Groq (Fallback LLM Provider)
    3. If both fail, return clear application-level error payload.

    Args:
        text (str): Raw text of the commercial lease document.
        gemini_key (str, optional): Custom Gemini API key override.
        groq_key (str, optional): Custom Groq API key override.
        force_fallback (bool, optional): Internal flag for testing Groq fallback.

    Returns:
        Dict[str, Any]: Dictionary containing status, provider, structured data, or error message.
    """
    if not text or not text.strip():
        return {
            "status": "error",
            "provider": "none",
            "message": "Lease text input is empty.",
            "data": None
        }

    # Resolve API keys from process environment or arguments
    resolved_gemini_key = gemini_key or os.getenv("GEMINI_API_KEY") or os.getenv("ROCKETRIDE_GEMINI_KEY") or ""
    resolved_groq_key = groq_key or os.getenv("GROQ_API_KEY") or os.getenv("ROCKETRIDE_GROQ_KEY") or ""

    # Shared RocketRide Cloud connection settings
    rr_uri = os.getenv("ROCKETRIDE_URI", "https://api.rocketride.ai:443")
    rr_apikey = os.getenv("ROCKETRIDE_APIKEY", "")

    # Base environment dictionary passed to RocketRideClient
    base_env = {
        "ROCKETRIDE_URI": rr_uri,
        "ROCKETRIDE_APIKEY": rr_apikey,
    }

    gemini_error: Optional[str] = None

    # ------------------------------------------------------------------------
    # STEP 1: Attempt Gemini Primary LLM Pipeline
    # ------------------------------------------------------------------------
    if not force_fallback:
        try:
            logger.info("Attempting primary LLM execution via RocketRide Gemini pipeline...")
            gemini_env = {
                **base_env,
                "ROCKETRIDE_GEMINI_KEY": resolved_gemini_key,
                "GEMINI_API_KEY": resolved_gemini_key
            }

            raw_result = _run_async(
                _run_rocketride_extraction(str(GEMINI_PIPE_FILE), text, gemini_env)
            )
            validated_rules = _parse_and_validate_response(raw_result)

            return {
                "status": "success",
                "provider": "gemini",
                "data": validated_rules.model_dump(),
                "raw_response": raw_result
            }
        except Exception as exc:
            gemini_error = str(exc)
            logger.warning("Gemini primary LLM execution failed: %s. Initiating Groq fallback...", gemini_error)
    else:
        gemini_error = "Forced fallback mode requested for testing."

    # ------------------------------------------------------------------------
    # STEP 2: Attempt Groq Fallback LLM Pipeline
    # ------------------------------------------------------------------------
    try:
        logger.info("Attempting fallback LLM execution via RocketRide Groq pipeline...")
        groq_env = {
            **base_env,
            "ROCKETRIDE_GROQ_KEY": resolved_groq_key,
            "GROQ_API_KEY": resolved_groq_key
        }

        raw_result = _run_async(
            _run_rocketride_extraction(str(GROQ_PIPE_FILE), text, groq_env)
        )
        validated_rules = _parse_and_validate_response(raw_result)

        return {
            "status": "success",
            "provider": "groq",
            "data": validated_rules.model_dump(),
            "raw_response": raw_result,
            "fallback_used": True,
            "primary_error": gemini_error
        }
    except Exception as exc:
        groq_error = str(exc)
        logger.error("Groq fallback LLM execution failed: %s", groq_error)

        return {
            "status": "error",
            "provider": "none",
            "message": f"Both Gemini and Groq AI providers failed. Gemini Error: [{gemini_error}]. Groq Error: [{groq_error}]",
            "data": None,
            "errors": {
                "gemini": gemini_error,
                "groq": groq_error
            }
        }


# ============================================================================
# AIService Class Wrapper (for backward compatibility)
# ============================================================================

class AIService:
    """Service class interface for RocketRide AI Pipelines."""

    def __init__(self):
        self.rocketride_api_key = os.getenv("ROCKETRIDE_APIKEY") or os.getenv("ROCKETRIDE_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")

    def is_configured(self) -> bool:
        """Check if RocketRide and LLM credentials are present."""
        return bool(self.rocketride_api_key and (self.gemini_api_key or self.groq_api_key))

    def extract_lease_rules(self, document_id_or_text: str, document_text: Optional[str] = None) -> Dict[str, Any]:
        """Convenience method wrapping extract_lease_rules function."""
        actual_text = document_text if document_text is not None else document_id_or_text
        return extract_lease_rules(actual_text)

    def extract_invoice_line_items(self, document_id: str, document_text: str) -> Dict[str, Any]:
        """Placeholder for Phase 4."""
        return {
            "status": "pending_implementation",
            "message": "Invoice extraction pipeline will be implemented in a future phase."
        }

    def generate_dispute_letter(self, finding_id: str, context: Dict[str, Any]) -> str:
        """Placeholder for Phase 4."""
        return "Dispute letter generation will be implemented in a future phase."
