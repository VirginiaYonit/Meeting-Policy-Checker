# AI Responsible Use Policy – Meeting Policy Checker

**System:** Meeting Policy Checker  
**Version:** 1.0  
**Date:** September 4, 2025  
**Next review:** September 2026  
**AI System Owner:** Virginia Levy Abulafia  

---

## 🎯 Purpose
Meeting Policy Checker is a micro-agent designed to support the verification of meeting agendas and transcripts against predefined organizational policies.  
The system produces structured reports (JSON/Markdown) with compliance scores, findings, and suggested fixes.  
It does not take autonomous decisions: it requires textual input and assumes human supervision for interpretation and use of results.  

---

## 🌱 Guiding Principles

- **Transparency**  
  Compliance logic is encoded in editable Markdown files (`meeting_policy_checker_logic.md`).  
  Outputs are validated against a strict JSON schema, but no machine-readable logs are stored beyond runtime.  
  Users are clearly informed about scope and limitations.  

- **Mandatory Human Oversight**  
  Meeting Policy Checker does not replace compliance officers or meeting managers.  
  Reports must be interpreted and validated by authorized staff. No organizational decision is applied automatically.  

- **Data Minimization**  
  Meeting texts are processed transiently.  
  The system does not retain logs or personal data. In CI/CD test mode, no external model calls are performed.  

- **Content Neutrality**  
  Outputs are limited to organizational compliance.  
  The system never generates discriminatory, sensitive, or legally binding content. It is not suitable for medical, legal, or other critical domains.  

- **Proportionate Responsibility**  
  The organization guarantees technical functioning within declared limits.  
  Misuse or misinterpretation of reports falls outside its responsibility.  

- **Continuous Improvement**  
  The system is periodically reviewed. Updates to policy logic or features are documented transparently.  

---

## 📌 Organizational Commitments
The system owner commits to:  

- Operate in line with ISO/IEC 42001:2023, the EU AI Act, and GDPR where applicable.  
- Document risk and impact assessments.  
- Release only tested and traceable versions.  
- Provide users with clear information about system limits and disclaimers.  
- Integrate user feedback into continuous improvement.  

---

## ✍️ Approval
Approved on September 4, 2025. To be reviewed within 12 months.  

**AI System Owner:** Virginia Levy Abulafia  
**Signature:** Digital or equivalent approval
