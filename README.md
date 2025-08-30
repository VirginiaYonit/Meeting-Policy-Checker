<p align="center">
  <img src="assets/logo_vla_small.jpg" alt="Meeting Policy Checker Logo" width="150"/>
</p>

<h1 align="center">Meeting Policy Checker Agent</h1>

<p align="center">
  <a href="https://github.com/VirginiaYonit/meeting-policy-checker/actions">
    <img src="https://github.com/VirginiaYonit/meeting-policy-checker/actions/workflows/tests.yml/badge.svg" alt="Build Status">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT">
  </a>
  <a href="https://huggingface.co/spaces/virginialevy/meeting-policy-checker">
    <img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Space-orange" alt="Hugging Face Space">
  </a>
  <a href="https://github.com/VirginiaYonit/meeting-policy-checker/releases">
  <img src="https://img.shields.io/github/v/release/VirginiaYonit/meeting-policy-checker" alt="GitHub release">
</a>

</p>

<p align="center">
An AI-powered compliance agent that evaluates meeting content against organizational policies, using the <b>Document-as-Implementation</b> pattern for maximum transparency and flexibility.
</p>

---

## Overview
The **Meeting Policy Checker Agent** is an AI-powered compliance tool that evaluates meeting content (agenda or transcript) against organizational policies, returning a structured JSON report.  
It implements the **Document-as-Implementation** pattern, loading human-readable policy documents at runtime and using them directly as the system’s decision logic.

## Key Features
- **Dynamic Policy Loading** – Reads the latest meeting policy from `meeting_policy_checker_logic.md`, so non-technical staff can update rules without code changes.
- **Strict Schema Validation** – Outputs are validated against a `pydantic` schema (`OutputPayload`) to guarantee consistent structure.
- **PII Detection** – Optional strict mode rejects inputs containing potential Personally Identifiable Information.
- **Scoring** – Calculates a compliance score (%) based on the ratio of passed to total policy checks.
- **Guardrail Traceability** – Every run includes metadata on input validation, schema validation, truncation notices, and refusal reasons.

## Design Principles
The agent follows the **MATE** design guidelines:
1. **Model Efficiency** – Uses `gpt-4.1-mini` by default for speed and cost control.
2. **Action Specificity** – Only one clear function: `check_meeting()`.
3. **Token Efficiency** – Truncates policy and meeting text to safe limits.
4. **Environment Safety** – Read-only evaluation, no destructive actions.

## How It Works
1. **Input Validation**
   - Ensures policy and meeting text meet minimum length.
   - Verifies `meeting_type` is `agenda` or `transcript`.
   - Optional PII detection in strict mode.
2. **Truncation**
   - Policy text ≤ 50k chars, meeting text ≤ 30k chars.
3. **Prompt Construction**
   - Loads and appends policy logic text to a system prompt.
4. **Model Call**
   - Sends structured request to OpenAI with `response_format=json_object`.
5. **Schema Validation**
   - Parses model output into `OutputPayload`.
   - Calculates compliance score.
   - Adds guardrail trace data.

## File Structure
meeting_policy_checker/
│
├── agent.py # Main agent logic
├── schema.py # Pydantic schemas for input/output
├── meeting_policy_checker_logic.md # Editable human-readable policy rules


## Example Usage
```python
from meeting_policy_checker.agent import check_meeting, InputPayload

payload = InputPayload(
    policy_text=open("policy.md").read(),
    meeting_type="agenda",
    strictness="normal",
    checks=["confidentiality", "attendance"],
    max_suggestions=3,
    return_format="json",
    org_context=None,
    meeting_text=open("agenda.txt").read()
)

result = check_meeting(payload)
print(result.model_dump_json(indent=2))
```

## Advantages of the Document-as-Implementation Approach
No developer bottlenecks – Policy owners update .md file directly.

* Immediate effect – Policy changes apply at next agent run.
* Transparency – Output includes the exact policy version applied.
* Audit-ready – Full traceability from decision to source document.

---

## Testing & CI
In local runtime and on Hugging Face Spaces, the agent calls the real OpenAI API.  
In GitHub Actions CI, we run tests with a simulated model (`CI_FAKE_MODEL=1`) to:
- avoid API costs,
- keep the pipeline fast and secure,
- still validate schema compliance and code imports.

This ensures that the build badge stays green without depending on external API calls.

---

## Deployment
1. Local Installation
bash
git clone https://github.com/your-username/meeting-policy-checker.git
cd meeting-policy-checker

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"   # Linux/macOS
setx OPENAI_API_KEY "your-api-key"     # Windows

Test run:
pytest -q

2. Docker
docker build -t meeting-policy-checker .
docker run -e OPENAI_API_KEY="your-api-key" meeting-policy-checker

3. Hugging Face Spaces
* Create a new Space with Python runtime.
* Upload all files (agent.py, schema.py, meeting_policy_checker_logic.md, etc.).
* Set OPENAI_API_KEY as a Secret in Space Settings.
* Run and interact via API or UI.

## Configuration
| Parameter          | Description                           | Default        |
|--------------------|---------------------------------------|----------------|
| OPENAI_API_KEY     | API key for OpenAI                   | required       |
| MAX_POLICY_CHARS   | Max characters for policy text        | 50000          |
| MAX_MEETING_CHARS  | Max characters for meeting text       | 30000          |
| model_name         | OpenAI model to use                  | gpt-4.1-mini   |
| rewrite            | Enable auto-rewrite suggestions      | True           |
| meeting_type       | Type of meeting text (agenda/transcript) | –           |
| strictness         | PII mode (normal or strict)          | –              |


## API Integration Example
python
from fastapi import FastAPI
from meeting_policy_checker.agent import check_meeting, InputPayload

app = FastAPI()

@app.post("/check-meeting")
def api_check_meeting(payload: InputPayload):
    return check_meeting(payload).model_dump()


## Development Notes
Internal Structure

meeting_policy_checker/
│
├── agent.py
├── schema.py
├── meeting_policy_checker_logic.md

Execution Flow:

1. Input validation
2. Truncation
3. Logic loading
4. Prompt construction
5. Model call
6. Schema validation
7. Trace enrichment

## Customizing Logic Without Code Changes

- Edit meeting_policy_checker_logic.md to change rules.
- Save the file; next run uses the updated logic.
- No rebuild or code modification required.

## Possible Extensions

- Multi-document policy support
- Version tagging for audit
- Multi-agent delegation via call_agent

## Methodology – How Meeting Policy Checker Was Built

Meeting Policy Checker was created through a design-driven AI process focused on transparency, modularity, and usability.
Rather than a “developer-only” pipeline, the project grew iteratively by combining:

- 🧩 Modular architecture – clear separation between logic file, schemas, and agent core

- 🗣️ Prompt engineering & pattern testing – ensuring structured, auditable outputs

- 📄 Document-as-Implementation – meeting rules defined directly in Markdown, editable by anyone

- 🔁 Feedback loop – refined through real tests, CI integration, and deployment constraints

**This reflects principles of responsible AI: intelligibility, flexibility, and human-in-the-loop control.**


## 🤖 Built with ChatGPT – My Invisible Partner

This agent was developed in close collaboration with ChatGPT, which acted as:

- A coding assistant, translating compliance logic into working Python tools

- A co-designer, helping shape architecture and workflow choices

- A testing partner, suggesting CI strategies to validate schema and guardrails

- A documentation sparring partner, supporting the writing of clear, transparent technical notes

This README — like the code and design decisions — is the product of human–AI collaboration, grounded in reflection and iteration

## AI Responsible Use Policy

**System: Meeting Policy Checker
Version: 1.0
Date: August 30, 2025
Next review: August 2026
AI System Owner: Virginia Levy Abulafia**

**🎯 Purpose**
The Meeting Policy Checker is a micro–AI agent designed to support the verification of meeting agendas and transcripts against predefined organizational policies.
The system produces structured reports (JSON/Markdown) with compliance scores, findings, and proposed fixes. It does not take autonomous decisions: it requires textual input and assumes human supervision for interpretation and use of the results.

**🌱 Guiding Principles**

- Transparency
The agent is designed to be understandable: compliance logic is defined in editable Markdown documents and outputs follow a strict, verifiable JSON schema. Users are clearly informed about what the system does and its limitations.

- Mandatory Human Oversight
The system does not replace compliance officers or meeting managers.
Reports must be interpreted and validated by authorized staff. No organizational decision is applied automatically.

- Data Minimization
The agent only processes policy and meeting texts provided by the user. It does not retain or log personal data beyond execution. In CI/CD test mode, no external model calls are performed.

- Content Neutrality
Outputs are limited to technical and organizational compliance criteria, and never generate discriminatory or sensitive content. The system is not suitable for processing medical, legal, or other critical data.

- Proportionate Responsibility
The organization guarantees technical functioning within declared limits. It is not responsible for misinterpretations or improper use of the reports by users.

- Continuous Improvement
The system is subject to periodic review. Every update to policy logic or features will be documented transparently.

**📌 Organizational Commitments**
The organization commits to:

- Operate in line with ISO/IEC 42001:2023, the EU AI Act, and GDPR where applicable;

- Document risk and impact assessments;

- Release only tested and traceable versions;

- Provide users with complete information on system limits and intended uses;

- Integrate user feedback into continuous improvement.

**✍️ Approval**

This policy was approved on 30/08/2025 and will be reviewed within 12 months.
AI System Owner: Virginia Levy Abulafia
Digital or equivalent signature: Virginia Levy Abulafia


**Curious how micro-AI agents could support your business?**

[Contact me](https://www.linkedin.com/in/virginia-levy-abulafia/)
 | [Try the Demo](https://huggingface.co/spaces/virginialevy/meeting-policy-checker)
