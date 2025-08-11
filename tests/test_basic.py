import types
from meeting_policy_checker.agent import check_meeting
from meeting_policy_checker.schema import InputPayload

class DummyPayload(InputPayload):
    policy_text: str = "Sample policy text"
    meeting_text: str = "Sample meeting text"
    meeting_type: str = "agenda"
    strictness: str = "normal"
    checks: list = []
    max_suggestions: int = 0
    return_format: str = "json"
    org_context: dict = None

def test_check_meeting_function_exists():
    assert isinstance(check_meeting, types.FunctionType), "check_meeting should be a function"

def test_check_meeting_runs_without_api(monkeypatch):
    """Test that check_meeting returns an OutputPayload-like object without calling API."""

    # Monkeypatch OpenAI client to avoid real API call
    class DummyClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    class DummyChoice:
                        message = type("msg", (), {"content": '{"summary":{"overall":"needs_review","score":0,"high_risk_flags":[]},"findings":[],"auto_rewrite":{"enabled":false,"revised_agenda_or_note":null},"trace":{"model":"gpt-4.1-mini","guardrails":{"input_validated":true,"output_schema_validated":true,"truncation_notice":null,"refusal_reason":"Dummy"}}}'})
                    return type("resp", (), {"choices": [DummyChoice()]})

    monkeypatch.setattr("meeting_policy_checker.agent.OpenAI", lambda **kwargs: DummyClient())

    payload = DummyPayload()
    result = check_meeting(payload, model_name="gpt-4.1-mini", rewrite=False)

    assert hasattr(result, "summary"), "Result should have a 'summary' attribute"
    assert result.summary["overall"] in {"needs_review", "compliant", "non_compliant"}
