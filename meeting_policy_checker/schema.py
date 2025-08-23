from __future__ import annotations
from enum import Enum
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from typing import Optional

class MeetingType(str, Enum):
    agenda = "agenda"
    transcript = "transcript"

class Strictness(str, Enum):
    normal = "normal"
    strict = "strict"

class OrgContext(BaseModel):
    department: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    confidentiality_level: Optional[str] = None
    
class InputPayload(BaseModel):
    policy_text: str = Field(min_length=1)
    meeting_text: str = Field(min_length=1)
    meeting_type: MeetingType
    strictness: Strictness
    checks: Optional[List[str]] = None
    max_suggestions: Optional[int] = 0
    return_format: Optional[str] = "json"
    org_context: Optional[OrgContext] = None

class GuardrailTrace(BaseModel):
    input_validated: bool = False
    output_schema_validated: bool = False
    truncation_notice: Optional[str] = None
    refusal_reason: Optional[str] = None

class Trace(BaseModel):
    model: str = ""
    guardrails: GuardrailTrace = Field(default_factory=GuardrailTrace)

class Finding(BaseModel):
    rule_id: str
    status: Literal["pass", "fail"]
    evidence: str
    explanation: str
    risk: Literal["low", "medium", "high"]
    proposed_fix: Optional[str] = None

class OutputSummary(BaseModel):
    overall: Literal["compliant", "non_compliant", "needs_review"]
    score: int
    high_risk_flags: List[str]

class AutoRewrite(BaseModel):
    enabled: bool
    revised_agenda_or_note: Optional[str] = None

class OutputPayload(BaseModel):
    summary: OutputSummary
    findings: List[Finding]
    auto_rewrite: AutoRewrite
    trace: Trace


