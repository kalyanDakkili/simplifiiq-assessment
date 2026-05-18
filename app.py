"""
SimplifiIQ Lead Automation System
Author: Kalyan Dakkili
Description: End-to-end lead intake automation — form capture → web enrichment → PDF report → email delivery
"""

import os
import json
import smtplib
import threading
import logging
import base64
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify, render_template, redirect, url_for

from enrichment import enrich_company
from report_generator import generate_pdf_report

# ── Config ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Email config — set via environment variables for security
SMTP_USER     = os.getenv("SMTP_USER", "your_email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_brevo_api_key")
FROM_NAME     = os.getenv("FROM_NAME", "SimplifiIQ Team")

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)
LEADS_FILE  = os.path.join(os.path.dirname(__file__), "leads.json")

# ── Helpers ──────────────────────────────────────────────────────────────────

def load_leads():
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE) as f:
            return json.load(f)
    return []

def save_lead(lead: dict):
    leads = load_leads()
    leads.append(lead)
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)

def send_report_email(to_email: str, to_name: str, company: str, pdf_path: str):
    """Send report via Brevo HTTP API using only stdlib — works on all hosting platforms."""
    try:
        import json as _json
        import urllib.request as _urllib

        # Read and encode PDF
        with open(pdf_path, "rb") as f:
            pdf_b64 = base64.b64encode(f.read()).decode()

        # Build payload
        payload = _json.dumps({
            "sender": {"name": FROM_NAME, "email": SMTP_USER},
            "to": [{"email": to_email, "name": to_name}],
            "subject": f"Your Personalised Business Audit — {company}",
            "textContent": f"""Dear {to_name},

Thank you for your interest in SimplifiIQ.

We've prepared a personalised business audit report for {company} based on publicly available information. This report highlights key insights, potential inefficiencies, and areas where AI-driven automation could create measurable value for your organisation.

Please find your tailored report attached.

We'd love to connect and walk you through our findings. Feel free to reply to this email or book a quick call at your convenience.

Warm regards,
SimplifiIQ Recruitment / Outreach Team
career@simplifiiq.com | simplifiiq.com

---
This report was automatically generated as part of our lead onboarding process.""",
            "attachment": [{
                "content": pdf_b64,
                "name": f"{company}_Audit_Report.pdf"
            }]
        }).encode("utf-8")

        # Use stdlib urllib — no naming conflict with Flask's request
        req = _urllib.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=payload,
            headers={
                "api-key": SMTP_PASSWORD,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST"
        )

        with _urllib.urlopen(req, timeout=30) as resp:
            status = resp.status
            if status == 201:
                logger.info(f"✅ Email sent to {to_email}")
                return True
            else:
                body = resp.read().decode()
                logger.error(f"❌ Email send failed: {status} {body}")
                return False

    except Exception as e:
        logger.error(f"❌ Email send failed: {e}")
        return False

def process_lead(lead: dict):
    """Background task: enrich → report → email."""
    name    = lead["name"]
    email   = lead["email"]
    company = lead["company"]

    logger.info(f"🚀 Processing lead: {name} | {company}")

    # 1. Enrich
    enriched = enrich_company(company, lead.get("website", ""), lead.get("industry", ""))
    lead["enriched"]  = enriched
    lead["status"]    = "enriched"

    # 2. Generate PDF
    pdf_path = os.path.join(REPORTS_DIR, f"{company.replace(' ', '_')}_Report.pdf")
    generate_pdf_report(lead, enriched, pdf_path)
    lead["report_path"] = pdf_path
    lead["status"]      = "report_generated"
    logger.info(f"📄 PDF generated: {pdf_path}")

    # 3. Send email
    email_ok = send_report_email(email, name, company, pdf_path)
    lead["status"]       = "email_sent" if email_ok else "email_failed"
    lead["processed_at"] = datetime.utcnow().isoformat()

    # 4. Persist
    save_lead(lead)
    logger.info(f"✅ Lead processing complete for {company}")

# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit_lead():
    data = request.form if request.content_type.startswith("application/x-www-form-urlencoded") \
           else request.get_json(silent=True) or {}

    # Validate required fields
    required = ["name", "email", "company"]
    missing  = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"success": False, "error": f"Missing fields: {', '.join(missing)}"}), 400

    lead = {
        "name":        data["name"].strip(),
        "email":       data["email"].strip(),
        "company":     data["company"].strip(),
        "website":     data.get("website", "").strip(),
        "industry":    data.get("industry", "").strip(),
        "pain_points": data.get("pain_points", "").strip(),
        "team_size":   data.get("team_size", "").strip(),
        "submitted_at": datetime.utcnow().isoformat(),
        "status":      "received",
    }

    # Fire and forget in background thread
    t = threading.Thread(target=process_lead, args=(lead,), daemon=True)
    t.start()

    return jsonify({"success": True, "message": "Thank you! Your personalised report is on its way."})

@app.route("/leads")
def leads_dashboard():
    leads = load_leads()
    return render_template("dashboard.html", leads=leads)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
