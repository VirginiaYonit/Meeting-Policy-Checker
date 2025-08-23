from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator


class MeetingType(str, Enum):
    agenda = "agenda"
    transcript = "transcript"


class Strictness(str, Enum):
    strict = "strict"
    advisory = "advisory"


class FindingStatus(str, Enum):
    pass_ = "pass"
    fail = "fail"
    warn = "warn"
    not_applicable = "not_applicable"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class OrgContext(BaseModel):
    department: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    confidentiality_level: Optional[Literal["public","internal","confidential","restricted"]] = None


class InputPayload(BaseModel):
    policy_text: str = Field(..., min_length=10, description="Org meeting policy in markdown/text")
    meeting_text: str = Field(..., min_length=10, description="Agenda or transcript")
    meeting_type: MeetingType
    checks: Optional[List[str]] = None
    strictness: Strictness = Strictness.advisory
    org_context: Optional[OrgContext] = None
    max_suggestions: int = 5
    return_format: Literal["json","markdown","both"] = "json"

    @validator("max_suggestions")
    def _cap_suggestions(cls, v):
        return max(1, min(v, 10))


class Finding(BaseModel):
    rule_id: str
    status: FindingStatus
    evidence: Optional[str] = None
    explanation: str
    risk: RiskLevel = RiskLevel.low
    proposed_fix: Optional[str] = None


class Summary(BaseModel):
    overall: Literal["compliant","non_compliant","needs_review"]
    score: int = Field(ge=0, le=100)
    high_risk_flags: List[str] = []


class AutoRewrite(BaseModel):
    enabled: bool = False
    revised_agenda_or_note: Optional[str] = None


class GuardrailTrace(BaseModel):
    input_validated: bool
    output_schema_validated: bool
    truncation_notice: Optional[str] = None
    refusal_reason: Optional[str] = None


class Trace(BaseModel):
    model: str
    guardrails: GuardrailTrace


class OutputPayload(BaseModel):
    summary: Summary
    findings: List[Finding]
    auto_rewrite: AutoRewrite = AutoRewrite()
    trace: Trace
