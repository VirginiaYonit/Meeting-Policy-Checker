def test_imports_and_call(monkeypatch):
    import os
    os.environ["CI_FAKE_MODEL"] = "1"

    # Import puro
    from meeting_policy_checker.agent import check_meeting
    from meeting_policy_checker.schema import InputPayload, MeetingType, Strictness

    # Mock client (non usato se CI_FAKE_MODEL=1, ma sicuro)
    class DummyClient:
        class chat:
            class completions:
                @staticmethod
                def create(**kwargs):
                    class DummyChoice:
                        message = type(
                            "msg",
                            (),
                            {"content": '{"summary":{"overall":"needs_review","score":0,"high_risk_flags":[]},"findings":[],"auto_rewrite":{"enabled":false,"revised_agenda_or_note":null},"trace":{"model":"gpt-4.1-mini","guardrails":{"input_validated":true,"output_schema_validated":true,"truncation_notice":null,"refusal_reason":"Dummy"}}}'},
                        )
                    return type("resp", (), {"choices": [DummyChoice()]})
    monkeypatch.setattr("meeting_policy_checker.agent.OpenAI", lambda **_: DummyClient())

    payload = InputPayload(
        policy_text="Policy X",
        meeting_text="Agenda Y",
        meeting_type=MeetingType.agenda,
        strictness=Strictness.normal,
        checks=[],
        max_suggestions=0,
        return_format="json",
        org_context=None,
    )

    out = check_meeting(payload, rewrite=False)
    assert out.summary.overall in {"needs_review", "compliant", "non_compliant"}
