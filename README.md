# SimplifiIQ — AI Lead Automation System

> **Author:** Kalyan Dakkili  
> **Role Applied:** AI Software Developer Intern  
> **Assessment:** SimplifiIQ Technical Evaluation

---

## 🚀 What This Does

An end-to-end automated lead intake system that:

1. **Captures** prospect information via a professional web form
2. **Enriches** company data using free web scraping (no paid APIs)
3. **Generates** a personalised PDF audit report per prospect
4. **Emails** the report automatically — all within minutes of form submission
5. **Logs** every lead to a local JSON tracker (bonus: swap for Google Sheets)

**Zero paid API keys required.**

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
     └─► Background Thread ──────────────────────────────┐
              │                                           │
              ▼                                           │
       enrichment.py                                      │
       ├── Scrape company website (BeautifulSoup)         │
       ├── DuckDuckGo HTML search (no API key)            │
       ├── Extract LinkedIn / social presence             │
       ├── Fetch recent news headlines                    │
       └── Map industry → insights (static knowledge)    │
              │                                           │
              ▼                                           │
       report_generator.py                               │
       └── ReportLab PDF: cover + 7 sections             │
              │                                           │
              ▼                                           │
       smtplib → Send PDF via email                      │
              │                                           │
              ▼                                           │
       leads.json (local lead tracker) ◄─────────────────┘
```

---

## 📁 Project Structure

```
simplifiiq/
├── app.py                  # Flask application + routing + email
├── enrichment.py           # Web scraping + company intelligence
├── report_generator.py     # ReportLab PDF generation
├── requirements.txt        # Python dependencies
├── leads.json              # Auto-created lead log
├── reports/                # Auto-created PDF output directory
└── templates/
    ├── index.html          # Lead intake form (dark UI)
    └── dashboard.html      # Leads tracker dashboard
```

---

## ⚙️ Setup & Running

### 1. Clone / Download

```bash
cd simplifiiq/
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure email (for sending reports)

Set environment variables — **never hardcode credentials**:

```bash
# Gmail recommended (use an App Password, not your main password)
export SMTP_HOST="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your_email@gmail.com"
export SMTP_PASSWORD="your_16_char_app_password"
export FROM_NAME="SimplifiIQ Team"
```

**How to get a Gmail App Password:**
1. Go to myaccount.google.com → Security → 2-Step Verification → App Passwords
2. Generate one for "Mail" → use that 16-character code as `SMTP_PASSWORD`

> Any SMTP provider works: Outlook, Yahoo, or a free tier of Mailtrap (for testing).

### 4. Run the server

```bash
python app.py
```

Visit: [http://localhost:5000](http://localhost:5000)  
Dashboard: [http://localhost:5000/leads](http://localhost:5000/leads)

---

## 🧪 Testing Without Email

If you just want to test PDF generation without sending emails, you can call the pipeline directly:

```python
from enrichment import enrich_company
from report_generator import generate_pdf_report

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
| SMTP via smtplib | Works with any email provider, no third-party SDK |

---

## 🎁 BONUS Features

### Google Sheets Logging (architecture)

To add Sheets logging, install `gspread` and replace `save_lead()` in `app.py`:

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

- **Missing lead fields:** 400 response with clear error message
- **Website scrape failure:** Falls back to DuckDuckGo search result
- **DuckDuckGo unavailable:** Industry insights and defaults used
- **PDF generation failure:** Logged; no crash
- **Email send failure:** Status saved as `email_failed`; lead still stored

---

## 📬 Contact

**Kalyan Dakkili**  
B.Tech Computer Science (2025), Bangalore  
GitHub: [github.com/kalyan-dakkili](https://github.com)  
Email: dakkili.kalyan@email.com
