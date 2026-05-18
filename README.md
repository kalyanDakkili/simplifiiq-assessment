# SimplifiIQ — AI Lead Automation System

> **Author:** Kalyan Dakkili  
> **Role Applied:** AI Software Developer Intern  
> **Assessment:** SimplifiIQ Technical Evaluation  
> **Live Demo:** https://simplifiiq-assessment.onrender.com

---

## 🚀 What This Does

An end-to-end automated lead intake system that:

1. **Captures** prospect information via a professional web form
2. **Enriches** company data using free web scraping (no paid APIs)
3. **Generates** a personalised PDF audit report per prospect
4. **Emails** the report automatically via Brevo API — within minutes of form submission
5. **Logs** every lead to a local JSON tracker

**Zero paid API keys required for core functionality.**

---

## 🌐 Live Demo

**Form:** https://simplifiiq-assessment.onrender.com  
**Dashboard:** https://simplifiiq-assessment.onrender.com/leads

---

## 🏗️ Architecture

```
Browser (Form)
     │  POST /submit
     ▼
Flask App (app.py)
     │
     ├─► Validation
     │
     └─► Background Thread
              │
              ▼
       enrichment.py
       ├── Scrape company website (BeautifulSoup)
       ├── DuckDuckGo HTML search (no API key)
       ├── Extract LinkedIn / social presence
       ├── Fetch recent news headlines
       └── Map industry → insights (static knowledge)
              │
              ▼
       report_generator.py
       └── ReportLab PDF: cover + 7 sections
              │
              ▼
       Brevo HTTP API → Send PDF via email
              │
              ▼
       leads.json (local lead tracker)
```

---

## 📁 Project Structure

```
simplifiiq/
├── app.py                  # Flask application + routing + email
├── enrichment.py           # Web scraping + company intelligence
├── report_generator.py     # ReportLab PDF generation
├── requirements.txt        # Python dependencies
├── reflection.txt          # Technical decisions & trade-offs
├── leads.json              # Auto-created lead log
├── reports/                # Auto-created PDF output directory
└── templates/
    ├── index.html          # Lead intake form (dark UI)
    └── dashboard.html      # Leads tracker dashboard
```

---

## ⚙️ Setup & Running Locally

### 1. Clone / Download
```bash
git clone https://github.com/kalyanDakkili/simplifiiq-assessment.git
cd simplifiiq-assessment
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure email

Get a free Brevo API key at [brevo.com](https://brevo.com) → SMTP & API → API Keys

Set environment variables:
```bash
# Windows CMD
set SMTP_USER=your_email@gmail.com
set SMTP_PASSWORD=xkeysib-your-brevo-api-key
set FROM_NAME=SimplifiIQ Team

# Mac/Linux
export SMTP_USER="your_email@gmail.com"
export SMTP_PASSWORD="xkeysib-your-brevo-api-key"
export FROM_NAME="SimplifiIQ Team"
```

### 4. Run the server
```bash
python app.py
```

Visit: http://localhost:5000  
Dashboard: http://localhost:5000/leads

---

## 🧪 Testing Without Email

```python
from enrichment import enrich_company
from report_generator import generate_pdf_report
import os; os.makedirs('reports', exist_ok=True)

lead = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "company": "Acme Corp",
    "website": "https://example.com",
    "industry": "SaaS",
    "pain_points": "Manual reporting takes too long",
    "team_size": "11-50",
    "submitted_at": "2025-01-01T10:00:00",
}

enriched = enrich_company("Acme Corp", "https://example.com", "SaaS")
generate_pdf_report(lead, enriched, "reports/test_report.pdf")
print("PDF created!")
```

---

## 📄 PDF Report Sections

| # | Section | What's inside |
|---|---------|---------------|
| Cover | Visual cover page | Company name, industry, date, description |
| 01 | Company Overview | Info table, tagline, web-scraped content |
| 02 | Digital Presence | Website / LinkedIn / social score cards |
| 03 | Industry Intelligence | Trend, pain point, opportunity for sector |
| 04 | Recent News | DuckDuckGo-scraped headlines |
| 05 | AI Automation Opportunities | Prioritised table of workflow automations |
| 06 | Recommendations | Immediate → strategic action plan |
| 07 | Next Steps | CTA with contact info |

---

## 🔍 Enrichment Sources (all free, no API key)

| Source | Method | What we get |
|--------|--------|-------------|
| Company website | `requests` + `BeautifulSoup` | Meta description, tagline, paragraphs |
| DuckDuckGo HTML | `requests` (HTML endpoint) | Search results, LinkedIn URLs, news |
| Website footer | Link parsing | LinkedIn, Twitter, Facebook links |
| Industry lookup | Static knowledge base | Sector trends, pain points, opportunity |

---

## ⚡ Design Decisions & Trade-offs

| Decision | Rationale |
|----------|-----------|
| DuckDuckGo HTML scraping | Free, no API key, sufficient for enrichment |
| Background threading | Non-blocking form response; UX feels instant |
| ReportLab (not WeasyPrint) | Pure Python, no system dependencies, lighter |
| Static industry insights | Reliable fallback when scraping returns nothing |
| JSON lead log | Simple, zero-dependency storage; swap for DB or Sheets |
| Brevo HTTP API for email | Works on all hosting platforms including Render free tier |

---

## 🎁 BONUS Features

### Google Sheets Logging (architecture)
```python
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds  = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
gc     = gspread.authorize(creds)
sh     = gc.open("SimplifiIQ Leads").sheet1

def save_lead(lead):
    sh.append_row([
        lead["name"], lead["email"], lead["company"],
        lead["submitted_at"], lead["status"]
    ])
```

### Google Drive PDF Archiving (architecture)
```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def archive_to_drive(pdf_path, company):
    service = build("drive", "v3", credentials=creds)
    media   = MediaFileUpload(pdf_path, mimetype="application/pdf")
    service.files().create(
        body={"name": f"{company}_Report.pdf", "parents": [DRIVE_FOLDER_ID]},
        media_body=media
    ).execute()
```

---

## 🛡️ Error Handling

- Missing lead fields: 400 response with clear error message
- Website scrape failure: Falls back to DuckDuckGo search result
- DuckDuckGo unavailable: Industry insights and defaults used
- PDF generation failure: Logged; no crash
- Email send failure: Status saved as `email_failed`; lead still stored

---

## 📬 Contact

**Kalyan Dakkili**  
B.Tech Computer Science (2025), Bangalore  
GitHub: [kalyanDakkili](https://github.com/kalyanDakkili)  
Email: kalyandakkili77@gmail.com
