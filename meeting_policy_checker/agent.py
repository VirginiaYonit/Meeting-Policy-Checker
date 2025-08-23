import os
import re
from pathlib import Path
from typing import Tuple

from pydantic import ValidationError
from .schema import InputPayload, OutputPayload, GuardrailTrace, Trace

MAX_POLICY_CHARS = 50_000
MAX_MEETING_CHARS = 30_000

LOGIC_PATH = Path(__file__).with_name("meeting_policy_checker_logic.md")

# --- Helpers ---------------------------------------------------------------


def _load_logic_text() -> str:
    if not LOGIC_PATH.exists():
        return (
            "# MEETING_POLICY_CHECKER (fallback)\n"
            "Evaluate meeting content against policy; never fabricate evidence; "
            "return JSON compliant with the provided schema."
        )
    return LOGIC_PATH.read_text(encoding="utf-8")


def _basic_pii_sniff(text: str) -> bool:
    # Very light heuristic (extensible): emails + many digits sequences (phone-like)
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        return True
    if re.search(r"\b\d{3,}[-\s]?\d{3,}[-\s]?\d{3,}\b", text):
        return True
    return False


def _truncate(text: str, limit: int) -> Tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


def _refusal_output(reason: str, model_name: str) -> OutputPayload:
    return OutputPayload(
        summary={"overall": "needs_review", "score": 0, "high_risk_flags": ["safety"]},
        findings=[],
        auto_rewrite={"enabled": False, "revised_agenda_or_note": None},
        trace=Trace(
            model=model_name,
            guardrails=GuardrailTrace(
                input_validated=True,
                output_schema_validated=True,
                truncation_notice=None,
                refusal_reason=reason,
            ),
        ),
    )


# --- Core ------------------------------------------------------------------


def check_meeting(
    payload: InputPayload, model_name: str = "gpt-4.1-mini", rewrite: bool = True
) -> OutputPayload:
    """
    Main entrypoint: validates inputs, builds prompt, calls OpenAI, validates output.
    Returns OutputPayload with guardrail trace. On failure, returns needs_review with reason.
    """
    # Input guardrails
    policy = payload.policy_text.strip()
    meeting = payload.meeting_text.strip()

    if len(policy) < 10 or len(meeting) < 10:
        return _refusal_output("Missing or trivial policy/meeting text.", model_name)

    if payload.meeting_type.value not in {"agenda", "transcript"}:
        return _refusal_output(
            "Invalid meeting_type. Must be 'agenda' or 'transcript'.", model_name
        )

    if _basic_pii_sniff(meeting) and payload.strictness.value == "strict":
        return _refusal_output(
            "Potential PII detected in meeting_text under strict mode.", model_name
        )

    policy, policy_trunc = _truncate(policy, MAX_POLICY_CHARS)
    meeting, meeting_trunc = _truncate(meeting, MAX_MEETING_CHARS)

    truncation_note = None
    if policy_trunc or meeting_trunc:
        truncation_note = "Input truncated to size limits."

    # ✅ NUOVA LOGICA: se org_context non è fornito, estrailo dal Confidentiality level del meeting
    if not payload.org_context:
        match = re.search(
            r"Confidentiality level\s*:\s*([^\n\r]+)", meeting, re.IGNORECASE
        )
        if match:
            level = match.group(1).strip()
            payload.org_context = type(
                "OrgContext",
                (),
                {"dict": lambda self: {"confidentiality_level": level}},
            )()

    logic_text = _load_logic_text()

    # Compose prompt
    system_prompt = (
        logic_text
        + """
    You are a meeting policy compliance checker.
    Your task:
    1. Read `policy_text` and `meeting_text`.
    2. Compare the meeting against the policy rules.
    3. Output **only JSON** strictly matching the following schema (no extra keys, all keys present):
    {
      "summary": {
        "overall": "compliant" | "non_compliant" | "needs_review",
        "score": integer,
        "high_risk_flags": [string]
      },
      "findings": [
        {
          "rule_id": string,
          "status": "pass" | "fail",
          "evidence": string,
          "explanation": string,
          "risk": "low" | "medium" | "high",
          "proposed_fix": string | null
        }
      ],
      "auto_rewrite": {
        "enabled": boolean,
        "revised_agenda_or_note": string | null
      },
      "trace": {
        "model": string,
        "guardrails": {
          "input_validated": boolean,
          "output_schema_validated": boolean,
          "truncation_notice": string | null,
          "refusal_reason": string | null
        }
      }
    }
    Important rules:
    - Base all findings on given `meeting_text` and `policy_text`. Never invent evidence.
    - If unsure, set summary.overall to "needs_review" with explanation.
    - Always provide `rule_id` and `explanation` for every finding.
    - All fields must be present, even if empty or null.
    - Output must be a valid JSON object. No markdown, no commentary.
    """
    )

    user_prompt = {
        "policy_text": policy,
        "meeting_type": payload.meeting_type.value,
        "strictness": payload.strictness.value,
        "checks": payload.checks or [],
        "max_suggestions": payload.max_suggestions,
        "return_format": payload.return_format,
        "org_context": payload.org_context.dict() if payload.org_context else None,
        "meeting_text": meeting,
        "rewrite": bool(rewrite),
    }

    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _call(response_format_json=True):
        return client.chat.completions.create(
            model=model_name,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"INPUT JSON:\n{user_prompt}"},
            ],
            response_format={"type": "json_object"} if response_format_json else None,
        )

    # --- First attempt ---
    completion = _call(response_format_json=True)
    content = completion.choices[0].message.content

    try:
        out = OutputPayload.model_validate_json(content)
        # Calcola punteggio percentuale
        try:
            total_rules = len(out.findings)
            passed_rules = sum(1 for f in out.findings if f.status == "pass")
            out.summary["score"] = (
                int((passed_rules / total_rules) * 100) if total_rules > 0 else 0
            )
        except Exception:
            pass
        # Enrich trace
        out.trace.guardrails.input_validated = True
        out.trace.guardrails.output_schema_validated = True
        out.trace.guardrails.truncation_notice = truncation_note
        out.trace.model = model_name
        return out
    except ValidationError:
        # --- Retry ---
        completion = _call(response_format_json=True)
        content = completion.choices[0].message.content
        try:
            out = OutputPayload.model_validate_json(content)
            try:
                total_rules = len(out.findings)
                passed_rules = sum(1 for f in out.findings if f.status == "pass")
                out.summary["score"] = (
                    int((passed_rules / total_rules) * 100) if total_rules > 0 else 0
                )
            except Exception:
                pass
            out.trace.guardrails.input_validated = True
            out.trace.guardrails.output_schema_validated = True
            out.trace.guardrails.truncation_notice = truncation_note
            out.trace.model = model_name
            return out
        except ValidationError as ve2:
            reason = f"Schema validation failed after retry: {ve2.errors()[:2]}"
            return _refusal_output(reason, model_name)
