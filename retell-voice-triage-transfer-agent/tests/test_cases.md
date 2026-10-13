# Test Cases and Execution Results

Executed on 2026-10-13 using Retell **Test LLM** (text chat showing tool calls), recorded in the demo video: https://www.loom.com/share/8cc9ffc52485482ea10d58c0a615fda6
Note: Retell web calls do not support call transfer, so transfers were verified through tool-call and tool-response logs.

| ID | Scenario | Input | Expected | Actual | Result | Evidence |
|---|---|---|---|---|---|---|
| TC-001 | Intent-triggered transfer + consent | "I was double charged on my card" then "Yes, please" | Explains handoff, asks consent, calls transfer_billing | Agent asked "May I transfer you now?"; after "Yes, please" called transfer_billing (tool response: transferred successfully) | PASS | docs/screenshots/01_billing_consent_transfer.png |
| TC-003 | Consent declined | "My server is down" then "No, don't transfer me." | No tool call; stays on line | Agent said "No problem. I will keep us on the line. What else can I help you with?" No tool call | PASS | docs/screenshots/02_consent_declined.png |
| TC-002 | Emergency bypass | "I need an ambulance, it's an emergency" | Disclaimer, no consent, immediate cold transfer_crisis | Disclaimer spoken, transfer_crisis called immediately with no consent question | PASS | docs/screenshots/03_crisis_override.png |
| TC-006 | FAQ never transferred | "How do I check my balance?" | Answer from prompt, no transfer | "Check it in the app under Accounts, then Balance." No tool call | PASS | docs/screenshots/04_faq_no_transfer.png |
| TC-004 | Busy line fallback | "The transfer failed, the line is busy." | Fallback line, voicemail/callback collected and confirmed | Fallback line spoken; callback details (name, phone, time, reason) collected and read back for confirmation | PASS (failure simulated by message) | docs/screenshots/05_busy_fallback_callback.png |
| TC-005 | Webhook security | POST with invalid token | HTTP 401, nothing logged | Covered by automated test | PASS | `python -m unittest tests.test_webhook` (4 tests) |
