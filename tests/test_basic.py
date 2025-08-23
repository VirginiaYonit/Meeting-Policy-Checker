from meeting_policy_checker.agent import check_meeting
from meeting_policy_checker.schema import InputPayload, MeetingType, Strictness

def test_check_meeting_runs_without_api(monkeypatch):
    class DummyClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    class DummyChoice:
                        message = type(
                            "msg",
                            (),
                            {
                                "content": (
                                    '{"summary":{"overall":"needs_review","score":0,"high_risk_flags":[]},'
                                    '"findings":[],"auto_rewrite":{"enabled":false,"revised_agenda_or_note":null},'
                                    '"trace":{"model":"gpt-4.1-mini","guardrails":{"input_validated":true,'
                                    '"output_schema_validated":true,"truncation_notice":null,"refusal_reason":"Dummy"}}}'
                                )
                            },
                        )
                    return type("resp", (), {"choices": [DummyChoice()]})

    # Monkeypatch OpenAI client to avoid real API calls
    monkeypatch.setattr("meeting_policy_checker.agent.OpenAI", lambda **_: DummyClient())

    payload = InputPayload(
        policy_text="Policy: R1 timeboxing; R2 roles; R3 objective; R4 materials; R5 confidentiality.",
        meeting_text="Agenda: Item 1 (15m). Roles: facilitator/note-taker/timekeeper. Objective stated.",
        meeting_type=MeetingType.agenda,
        strictness=Strictness.normal,
        checks=[],
        max_suggestions=0,
        return_format="json",
        org_context=None,
    )

    out = check_meeting(payload, model_name="gpt-4.1-mini", rewrite=False)
    assert out.summary.overall in {"needs_review", "compliant", "non_compliant"}
