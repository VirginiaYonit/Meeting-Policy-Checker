import gradio as gr
import json
from meeting_policy_checker.schema import InputPayload, MeetingType, OrgContext
from meeting_policy_checker.agent import check_meeting
import os

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def predict(
    policy_text,
    meeting_text,
    meeting_type,
    checks_csv,
    strictness,
    max_suggestions,
    return_format,
    department,
    locale,
    timezone,
    confidentiality_level,
    auto_rewrite,
):
    checks = [c.strip() for c in (checks_csv or "").split(",") if c.strip()]
    org_ctx = OrgContext(
        department=department or None,
        locale=locale or None,
        timezone=timezone or None,
        confidentiality_level=(confidentiality_level or None),
    )

    payload = InputPayload(
        policy_text=policy_text,
        meeting_text=meeting_text,
        meeting_type=MeetingType(meeting_type),
        checks=checks or None,
        strictness=strictness,
        org_context=org_ctx,
        max_suggestions=max_suggestions,
        return_format=return_format,
    )

    out = check_meeting(payload, model_name=MODEL_NAME, rewrite=bool(auto_rewrite))
    out_json = out.model_dump()

    md_lines = [
        f"### Overall: **{out_json['summary']['overall']}** (score: {out_json['summary']['score']})",
        f"High-risk flags: {', '.join(out_json['summary'].get('high_risk_flags', [])) or '—'}",
        "",
        "#### Findings",
    ]
    for f in out_json.get("findings", []):
        md_lines += [
            f"- **{f['rule_id']}** → *{f['status']}*, risk: {f['risk']}",
            f"  - Evidence: {f.get('evidence') or '—'}",
            f"  - Why: {f['explanation']}",
            f"  - Fix: {f.get('proposed_fix') or '—'}",
        ]
    if out_json.get("auto_rewrite", {}).get("enabled"):
        md_lines += [
            "",
            "#### Auto-rewrite (proposed)",
            out_json["auto_rewrite"].get("revised_agenda_or_note") or "—",
        ]
    md = "\n".join(md_lines)
    return md, out_json


with gr.Blocks(title="Meeting Policy Checker") as demo:
    gr.Markdown(
        "# 🧭 Meeting Policy Checker\nValidate agendas/transcripts against your policy, with guardrails."
    )
    with gr.Row():
        policy_text = gr.Textbox(lines=10, label="Policy (markdown)")
        meeting_text = gr.Textbox(lines=10, label="Meeting text (agenda or transcript)")
    with gr.Row():
        meeting_type = gr.Radio(
            choices=["agenda", "transcript"], value="agenda", label="Meeting type"
        )
        strictness = gr.Radio(
            choices=["strict", "advisory"], value="advisory", label="Strictness"
        )
        auto_rewrite = gr.Checkbox(value=True, label="Enable auto-rewrite")
    checks_csv = gr.Textbox(
        label="Checks (comma-separated, optional)",
        placeholder="timeboxing, roles, objective, ...",
    )
    with gr.Accordion("Org context (optional)", open=False):
        with gr.Row():
            department = gr.Textbox(label="Department")
            locale = gr.Textbox(label="Locale (e.g., it-IT)")
            timezone = gr.Textbox(label="Timezone (e.g., Europe/Rome)")
            confidentiality_level = gr.Dropdown(
                ["public", "internal", "confidential", "restricted"],
                label="Confidentiality",
            )
    with gr.Row():
        max_suggestions = gr.Slider(1, 10, value=5, step=1, label="Max suggestions")
        return_format = gr.Dropdown(
            ["json", "markdown", "both"], value="json", label="Return format (internal)"
        )
    btn = gr.Button("Check")
    md_out = gr.Markdown(label="Report")
    json_out = gr.JSON(label="Raw JSON")

    examples = [
        [
            "# MEETING_POLICIES v1\n- Timeboxing required\n- Roles required\n- Objective must be explicit\n- Recording must be disclosed",
            "Weekly Ops Sync\nObjective: Align on blockers\n1) Incidents (10m) – Owner: Luca\n2) Deploy (15m) – Owner: Sara\nNote-taker: Giulia; Timekeeper: Marco",
            "agenda",
            "timeboxing,roles,objective",
            "advisory",
            5,
            "json",
            "Ops",
            "it-IT",
            "Europe/Rome",
            "internal",
            True,
        ]
    ]
    gr.Examples(
        examples=examples,
        inputs=[
            policy_text,
            meeting_text,
            meeting_type,
            checks_csv,
            strictness,
            max_suggestions,
            return_format,
            department,
            locale,
            timezone,
            confidentiality_level,
            auto_rewrite,
        ],
        outputs=[md_out, json_out],
        cache_examples=False,
    )

    btn.click(
        predict,
        inputs=[
            policy_text,
            meeting_text,
            meeting_type,
            checks_csv,
            strictness,
            max_suggestions,
            return_format,
            department,
            locale,
            timezone,
            confidentiality_level,
            auto_rewrite,
        ],
        outputs=[md_out, json_out],
    )

if __name__ == "__main__":
    demo.launch()
