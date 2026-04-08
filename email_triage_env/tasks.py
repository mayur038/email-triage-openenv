from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailTask:
    task_id: str
    difficulty: str
    customer_name: str
    sender: str
    subject: str
    body: str
    expected_category: str
    expected_priority: str
    expected_team: str
    required_reply_keywords: tuple[str, ...]
    guidance: str
    business_impact: str
    success_criteria: str


TASKS: dict[str, EmailTask] = {
    "password_reset_easy": EmailTask(
        task_id="password_reset_easy",
        difficulty="easy",
        customer_name="Maya Patel",
        sender="maya.patel@northstar-health.org",
        subject="Locked out after phone reset",
        body=(
            "Hi support, I reset my work phone this morning and now I cannot get into "
            "the Northstar patient portal. I need access before my 3 PM clinic shift. "
            "Please help me regain access as soon as possible."
        ),
        expected_category="account_access",
        expected_priority="high",
        expected_team="it_support",
        required_reply_keywords=("reset", "verify", "access"),
        guidance="Restore account access quickly while asking the user to verify identity.",
        business_impact="A clinician cannot access a patient portal before a time-sensitive shift.",
        success_criteria="Route to IT, mark as high priority, and explain identity verification plus access restoration.",
    ),
    "billing_refund_medium": EmailTask(
        task_id="billing_refund_medium",
        difficulty="medium",
        customer_name="Jordan Lee",
        sender="jordan.lee@solstice-retail.com",
        subject="Charged twice for March subscription",
        body=(
            "Hello team, our company card was billed twice for the March analytics "
            "subscription. I only expected one charge. Can someone confirm the duplicate "
            "and tell me when the refund will be processed?"
        ),
        expected_category="billing",
        expected_priority="medium",
        expected_team="billing_ops",
        required_reply_keywords=("duplicate", "refund", "timeline"),
        guidance="Acknowledge the duplicate charge and route to billing with a refund timeline.",
        business_impact="A paying customer has been charged twice and expects a refund process update.",
        success_criteria="Route to billing, confirm the duplicate charge issue, and give a refund follow-up timeline.",
    ),
    "invoice_fraud_hard": EmailTask(
        task_id="invoice_fraud_hard",
        difficulty="hard",
        customer_name="Elena Gomez",
        sender="elena.gomez@alder-logistics.com",
        subject="Urgent: suspicious invoice requesting vendor bank change",
        body=(
            "I received an invoice that looks like it came from one of our regular freight "
            "vendors, but it asks us to change bank details immediately and pay today. "
            "The wording feels off and the sender domain is slightly different from prior "
            "emails. We have not paid it yet. What should we do next?"
        ),
        expected_category="security_incident",
        expected_priority="urgent",
        expected_team="security_ops",
        required_reply_keywords=("do not pay", "verify", "security"),
        guidance="Treat this as potential invoice fraud and escalate immediately.",
        business_impact="A company may send money to a fraudulent bank account if the case is mishandled.",
        success_criteria="Escalate to security, mark urgent, and clearly instruct the customer not to pay before verification.",
    ),
}

DEFAULT_TASK_ORDER = [
    "password_reset_easy",
    "billing_refund_medium",
    "invoice_fraud_hard",
]
