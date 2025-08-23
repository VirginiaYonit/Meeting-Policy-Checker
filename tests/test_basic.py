def test_imports_and_call():
    import os
    os.environ["CI_FAKE_MODEL"] = "1"

    from meeting_policy_checker.agent import check_meeting
    from meeting_policy_checker.schema import InputPayload, MeetingType, Strictness

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



