import os
from meeting_policy_checker.schema import InputPayload, MeetingType
from meeting_policy_checker.agent import check_meeting

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

sample_policy = """
# MEETING_POLICIES v1
- Timeboxing required
- Roles: facilitator, note-taker, timekeeper must be assigned
- Objective must be explicit
"""

sample_agenda = """
Weekly Ops Sync
Objective: Align on blockers and assign next steps
1) Incidents (10m) – Owner: Luca
2) Deploy plan (15m) – Owner: Sara
Note-taker: Giulia; Timekeeper: Marco
"""

payload = InputPayload(
    policy_text=sample_policy,
    meeting_text=sample_agenda,
    meeting_type=MeetingType.agenda,
    checks=["timeboxing", "roles", "objective"],
    strictness="advisory",
    max_suggestions=3,
    return_format="json",
)

out = check_meeting(payload)
print(out.model_dump_json(indent=2))
