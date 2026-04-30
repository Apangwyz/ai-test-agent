# 文档

{
  "version": "1.0",
  "timestamp": 1777422958.262142,
  "ambiguous_points": [
    "| Section | Ambiguity | Specific Questions |",
    "|--------|-----------|---------------------|",
    "| **# 需求文档4：银行面客系统（手机银行）** | “面客系统” is a non-standard, culturally specific term (literally “facing customer”). Its scope is undefined: Does it include onboarding? KYC? biometric authentication? Wealth management? Loan applications? | • What exact customer-facing *processes* and *services* must be supported?<br>• Is this a greenfield app, or does it replace/integrate with existing mobile banking apps (e.g., legacy iOS/Android apps)?<br>• Does “面客” imply real-time human agent co-browsing or video banking? If so, what regulatory compliance (e.g., GDPR, China’s PIPL, NYDFS 500) applies? |",
    "| **Core function requirements** | Entirely blank — no functions listed. “Core” is subjective: Is fund transfer core? Investment trading? Card controls? Fraud alerts? | • Which functions are *mandatory* (MVP) vs. *phase 2*?<br>• Are there jurisdiction-specific functions required (e.g., China’s e-CNY wallet integration, EU’s PSD2/SCA support)?<br>• Must functions comply with banking standards like ISO 20022 for payments? |",
    "| **Non-functional requirements** | Blank — critical attributes (performance, security, reliability) are unspecified. | • What are acceptable response times for balance checks (<1s?) vs. fund transfers (<3s?)?<br>• What uptime SLA is required (99.9%? 99.99%)? How is downtime measured (scheduled maintenance excluded?)?<br>• What encryption standards apply (e.g., TLS 1.3+, AES-256 at rest, HSM-backed key management)? |",
    "| **Target user group** | Blank — no segmentation (e.g., retail vs. SME users, age groups, accessibility needs). | • Are users assumed to be tech-savvy? Must the app support elderly users (larger fonts, voice navigation, simplified UI)?<br>• Must it comply with WCAG 2.1 AA or China’s GB/T 37668-2019 (accessibility for older adults)?<br>• Are there unbanked/underbanked use cases (e.g., ID verification via national ID + facial recognition)? |",
    "---",
    "2. **Conduct a regulatory gap analysis** with legal/compliance teams to map every requirement to enforceable standards (CBIRC, PBOC, etc.).",
    "3. **Define traceability**: Each requirement must link to source (e.g., “CBIRC Notice [2023] No. 5, Art. 12”), test case, and design component.",
    "4. **Prioritize using MoSCoW**: Must-have (e.g., FIDO2 authentication), Should-have (e.g., investment portfolio view), Could-have (e.g., AR-based branch locator), Won’t-have (e.g., crypto wallet).",
    "Without addressing these gaps, the project faces **high risk of regulatory rejection, security breaches, cost overruns, and failure to meet business objectives"
  ],
  "conflicts": [
    "|-------------------|------------|---------------------|",
    "| **“Acceptance criteria” vs. “Core functions”** | Without defined functions, acceptance criteria cannot be testable — leading to subjective “sign-off.” | • How will “successful login” be verified? Biometric success rate ≥99.5%? Fallback to OTP within 30s? Error handling for failed liveness detection?<br>• What constitutes “successful fund transfer”? Confirmation screen + SMS + push notification + ledger update timestamp ≤2s? |",
    "---"
  ],
  "missing_information": [
    "*Critical omissions violating banking domain standards and regulatory expectations:*",
    "|----------|---------------------|---------------------|----------------------|",
    "| **Regulatory & Compliance** | Zero mention of jurisdictional regulations (e.g., China’s CBIRC guidelines, EU’s PSD2, US FFIEC CAT). | Non-compliance risks fines, operational shutdown, or reputational damage. | • Which regulatory bodies’ requirements drive design (e.g., CBIRC’s *Mobile Banking Security Guidelines*)?<br>• Must transactions >¥50,000 trigger enhanced due diligence (EDD) workflows? How is EDD initiated? |",
    "| **Security Controls** | No details on authentication (MFA types), session management, or fraud detection. | Mobile banking is a top target for malware (e.g., Cerberus, Anubis). | • Is step-up authentication required for high-risk actions (e.g., changing payee, increasing transfer limits)?<br>• How are device binding, jailbreak/root detection, and runtime application self-protection (RASP) implemented? |",
    "| **Data Management** | No data retention policies, localization rules, or PII handling. | Violates PIPL (China), GDPR (EU), or GLBA (US). | • Where is user biometric data stored (on-device only? encrypted server-side?)?<br>• Must transaction logs be retained for 5 years (CBIRC Rule 2022)? In which jurisdiction? |",
    "| **Integration Points** | No APIs, core banking systems (e.g., Temenos, Finacle), or third-party services (e.g., credit bureaus, payment gateways). | Siloed systems cause reconciliation failures and latency. | • Which core banking system(s) does this integrate with? What protocols (REST/JSON, SOAP, ISO 8583)?<br>• How are idempotency and retry logic handled for payment submissions? |",
    "---",
    "### 4. **Business Rules That Need Further Definition**",
    "*Business logic is entirely absent — yet critical for correctness, auditability, and risk control.*",
    "| Business Domain | Undefined Rule | Risk if Unspecified | Specific Questions |",
    "|----------------|----------------|------------------------|----------------------|",
    "| **Account Management** | No rules for account opening, closure, or status transitions (e.g., dormant → active). | Regulatory penalties for improper KYC/CDD; fraud exposure. | • What documents verify identity for remote onboarding (national ID + live selfie + OCR + liveness)?<br>• After how many days of inactivity is an account flagged dormant? What reactivation steps apply? |",
    "| **Transaction Limits** | No daily/monthly limits, velocity checks, or risk-based tiering. | Enables money laundering or account takeover. | • Are limits static (e.g., ¥50,000/day) or dynamic (e.g., adjusted based on behavioral biometrics and transaction history)?<br>• How are cross-channel limits enforced (mobile + web + ATM)? |",
    "| **Error Handling & Recovery** | No specification for failed transactions (e.g., network timeout during transfer). | Double-charging, inconsistent balances, customer disputes. | • If a transfer request times out, is the funds hold released immediately? How is idempotency ensured on retry?<br>• What is the SLA for dispute resolution (e.g., CBIRC requires ≤15 business days for unauthorized transactions)? |",
    "| **Notifications & Consent** | No rules for opt-in/out, channel preferences, or message templates. | Breaches privacy laws; erodes trust. | • Must push notifications for balance changes require explicit consent? Can SMS be used for OTP without consent under PIPL?<br>• Are notification templates pre-approved by compliance/legal? |",
    "---",
    "### 🔑 **Urgent Next Steps Recommended**"
  ],
  "suggestions": []
}