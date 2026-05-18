"""
enrichment.py — Company data enrichment via free web scraping
No paid APIs required. Uses requests + BeautifulSoup + DuckDuckGo HTML search.
"""

import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TIMEOUT = 10


# ── Utilities ─────────────────────────────────────────────────────────────────

def safe_get(url: str, params=None) -> requests.Response | None:
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r
    except Exception as e:
        logger.warning(f"GET failed for {url}: {e}")
        return None


def extract_text(soup, selector: str, default="") -> str:
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else default


def duckduckgo_search(query: str, max_results=5) -> list[dict]:
    """Scrape DuckDuckGo HTML results (no API key needed)."""
    url  = "https://html.duckduckgo.com/html/"
    resp = safe_get(url, params={"q": query})
    if not resp:
        return []

    soup    = BeautifulSoup(resp.text, "html.parser")
    results = []
    for a in soup.select("a.result__a")[:max_results]:
        href = a.get("href", "")
        results.append({"title": a.get_text(strip=True), "url": href})
    return results


# ── Scraper helpers ───────────────────────────────────────────────────────────

def scrape_website(url: str) -> dict:
    """Scrape a company's own website for description, tagline, services."""
    if not url:
        return {}
    if not url.startswith("http"):
        url = "https://" + url

    resp = safe_get(url)
    if not resp:
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    # Meta description
    meta_desc = ""
    meta = soup.find("meta", attrs={"name": re.compile("description", re.I)})
    if meta:
        meta_desc = meta.get("content", "")

    # OG description fallback
    if not meta_desc:
        og = soup.find("meta", property="og:description")
        if og:
            meta_desc = og.get("content", "")

    # Title
    title = soup.title.string.strip() if soup.title else ""

    # H1 tagline
    h1 = soup.find("h1")
    tagline = h1.get_text(strip=True) if h1 else ""

    # Key paragraphs (first 3 non-trivial)
    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) > 60:
            paragraphs.append(text)
        if len(paragraphs) >= 3:
            break

    return {
        "site_title":   title,
        "tagline":      tagline,
        "meta_desc":    meta_desc,
        "paragraphs":   paragraphs,
    }


def search_linkedin_info(company: str) -> dict:
    """Try to extract basic LinkedIn company info from public search snippet."""
    results = duckduckgo_search(f"site:linkedin.com/company {company}")
    for r in results:
        if "linkedin.com/company" in r.get("url", ""):
            return {"linkedin_url": r["url"], "linkedin_snippet": r["title"]}
    return {}


def search_news(company: str) -> list[str]:
    """Get recent news headlines about the company."""
    results = duckduckgo_search(f"{company} news 2024 2025", max_results=5)
    headlines = []
    for r in results:
        title = r.get("title", "")
        if company.lower().split()[0] in title.lower():
            headlines.append(title)
    return headlines[:3]


def guess_industry_insights(industry: str) -> dict:
    """Return curated static insights per industry (no API needed)."""
    INSIGHTS = {
        "finance": {
            "trend": "AI-driven risk analysis and automated compliance are reshaping the sector.",
            "pain":  "Manual reconciliation and regulatory reporting consume ~30% of staff time.",
            "opp":   "Workflow automation can cut operational costs by up to 40%.",
        },
        "consulting": {
            "trend": "Data-backed consulting and AI-augmented research are differentiating top firms.",
            "pain":  "Proposal generation and client reporting are highly manual and time-consuming.",
            "opp":   "Automating report generation can free consultants for high-value advisory work.",
        },
        "saas": {
            "trend": "AI copilots embedded in SaaS products are becoming table stakes by 2025.",
            "pain":  "Customer onboarding and support ticket triage are scaling bottlenecks.",
            "opp":   "AI-powered onboarding flows can increase activation rates by 25–35%.",
        },
        "ecommerce": {
            "trend": "Hyper-personalisation and AI-driven inventory management are market leaders.",
            "pain":  "Cart abandonment and poor product discovery cost significant revenue.",
            "opp":   "Personalised recommendation engines increase AOV by up to 20%.",
        },
        "healthcare": {
            "trend": "Predictive diagnostics and patient workflow automation are high priority.",
            "pain":  "Administrative burden accounts for nearly 34% of healthcare costs.",
            "opp":   "AI-driven scheduling and documentation can reclaim thousands of staff hours.",
        },
        "education": {
            "trend": "Adaptive learning platforms and AI tutors are disrupting traditional e-learning.",
            "pain":  "Content personalisation and learner engagement remain major challenges.",
            "opp":   "Automated progress tracking and nudge systems improve completion rates by 40%.",
        },
        "logistics": {
            "trend": "Route optimisation and predictive maintenance are critical differentiators.",
            "pain":  "Manual dispatch and last-mile coordination drive up costs.",
            "opp":   "AI-optimised routing reduces fuel and time costs by up to 15%.",
        },
    }
    key = industry.lower().split()[0] if industry else ""
    for k, v in INSIGHTS.items():
        if k in key or key in k:
            return v
    return {
        "trend": "Digital transformation and process automation are universal priorities.",
        "pain":  "Repetitive manual workflows are limiting team productivity and scalability.",
        "opp":   "AI-assisted automation can unlock significant time savings across operations.",
    }


def extract_social_links(website: str) -> dict:
    """Scrape social links from website footer."""
    if not website:
        return {}
    if not website.startswith("http"):
        website = "https://" + website

    resp = safe_get(website)
    if not resp:
        return {}

    soup   = BeautifulSoup(resp.text, "html.parser")
    social = {}
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "linkedin.com" in href:
            social["linkedin"] = href
        elif "twitter.com" in href or "x.com" in href:
            social["twitter"] = href
        elif "facebook.com" in href:
            social["facebook"] = href
    return social


# ── Main enrichment entry ────────────────────────────────────────────────────

def enrich_company(company: str, website: str = "", industry: str = "") -> dict:
    """
    Orchestrates all enrichment steps.
    Returns a structured dict with everything the PDF report needs.
    """
    logger.info(f"🔍 Enriching: {company}")
    enriched = {
        "company":   company,
        "website":   website,
        "industry":  industry,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M UTC"),
    }

    # 1. Scrape own website
    site_data = {}
    if website:
        logger.info(f"  → Scraping website: {website}")
        site_data = scrape_website(website)
        time.sleep(1)
    else:
        # Try to find website via search
        results = duckduckgo_search(f"{company} official website")
        for r in results:
            url = r.get("url", "")
            parsed = urlparse(url)
            # skip aggregators
            if parsed.netloc and "duckduckgo" not in parsed.netloc and "wikipedia" not in parsed.netloc:
                site_data = scrape_website(url)
                enriched["website"] = url
                break
        time.sleep(1)

    enriched["site_data"] = site_data

    # 2. LinkedIn snippet
    logger.info(f"  → Searching LinkedIn presence")
    enriched["linkedin"] = search_linkedin_info(company)
    time.sleep(1)

    # 3. Recent news
    logger.info(f"  → Fetching news headlines")
    enriched["news_headlines"] = search_news(company)
    time.sleep(1)

    # 4. Social links
    if website:
        enriched["social_links"] = extract_social_links(website)

    # 5. Industry insights
    enriched["industry_insights"] = guess_industry_insights(industry)

    # 6. Derive description
    description = (
        site_data.get("meta_desc")
        or (site_data.get("paragraphs", [""])[0] if site_data.get("paragraphs") else "")
        or f"{company} is a business operating in the {industry or 'technology'} sector."
    )
    enriched["description"] = description[:500]

    logger.info(f"✅ Enrichment complete for {company}")
    return enriched
