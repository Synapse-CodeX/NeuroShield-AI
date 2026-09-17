"""
Website Scan Agent – Analysis Nodes
====================================
Each function is a LangGraph node that performs one aspect of the website
safety analysis.  Nodes that can run without network I/O use heuristics;
nodes that benefit from LLM reasoning use the shared ``llm`` instance.
"""

from __future__ import annotations

import re
import ssl
import socket
import json
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.shared.llm import llm
from agents.website_scan_agent.state import (
    WebsiteScanState,
    ContentQualityExtraction,
    ReputationExtraction,
)


# ═══════════════════════════════════════════════════════════════════════
# 1. URL STRUCTURE ANALYSIS  (heuristic – no network call)
# ═══════════════════════════════════════════════════════════════════════

# Common patterns seen in phishing / scam URLs
_SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".club", ".work", ".buzz", ".gq", ".ml", ".cf",
    ".tk", ".ga", ".icu", ".cam", ".rest", ".surf", ".monster",
    ".quest", ".uno", ".sbs",
}

_TRUSTED_TLDS = {
    ".com", ".org", ".net", ".edu", ".gov", ".mil", ".int",
    ".co", ".io", ".dev", ".app", ".ai",
}

_BRAND_KEYWORDS = [
    "paypal", "apple", "google", "microsoft", "amazon", "netflix",
    "facebook", "instagram", "whatsapp", "linkedin", "twitter",
    "bank", "secure", "verify", "login", "account", "update",
    "support", "service", "help",
]


def url_analysis_node(state: WebsiteScanState) -> dict[str, Any]:
    """Analyse the URL string itself for phishing / scam red-flags."""
    url = state.url.strip()
    parsed = urlparse(url if "://" in url else f"https://{url}")

    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    flags: list[str] = []
    score = 100

    # 1. IP-address instead of domain
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
        flags.append("URL uses a raw IP address instead of a domain name")
        score -= 30

    # 2. Suspicious TLD
    tld = "." + hostname.split(".")[-1] if "." in hostname else ""
    if tld in _SUSPICIOUS_TLDS:
        flags.append(f"Uses suspicious TLD '{tld}'")
        score -= 20
    elif tld not in _TRUSTED_TLDS and tld:
        flags.append(f"Uses uncommon TLD '{tld}'")
        score -= 5

    # 3. Excessive subdomains (> 3 levels)
    subdomain_count = hostname.count(".")
    if subdomain_count > 3:
        flags.append(f"Excessive subdomains ({subdomain_count} levels)")
        score -= 15

    # 4. Hyphens in domain
    domain_part = hostname.split(".")[-2] if hostname.count(".") >= 1 else hostname
    hyphen_count = domain_part.count("-")
    if hyphen_count >= 3:
        flags.append(f"Domain contains many hyphens ({hyphen_count})")
        score -= 15
    elif hyphen_count >= 1:
        flags.append(f"Domain contains hyphens ({hyphen_count})")
        score -= 5

    # 5. Long domain name (> 30 chars)
    if len(hostname) > 30:
        flags.append(f"Very long domain name ({len(hostname)} chars)")
        score -= 10

    # 6. Brand impersonation attempt
    for brand in _BRAND_KEYWORDS:
        if brand in hostname and brand != domain_part:
            flags.append(f"Possible brand impersonation ('{brand}' in subdomain)")
            score -= 20
            break

    # 7. @ symbol or encoded characters in URL
    if "@" in url:
        flags.append("URL contains '@' symbol (common phishing trick)")
        score -= 25

    if "%" in url and re.search(r"%[0-9a-fA-F]{2}", url):
        flags.append("URL contains encoded characters")
        score -= 10

    # 8. Non-HTTPS scheme
    if parsed.scheme and parsed.scheme != "https":
        flags.append(f"Uses insecure scheme '{parsed.scheme}://'")
        score -= 15

    # 9. Very long path
    if len(path) > 100:
        flags.append("Excessively long URL path")
        score -= 5

    # 10. Numbers mixed into domain (e.g. g00gle)
    if re.search(r"[a-z]+\d+[a-z]+", domain_part):
        flags.append("Domain mixes letters and numbers (leet-speak pattern)")
        score -= 15

    return {
        "url_analysis": {
            "hostname": hostname,
            "tld": tld,
            "scheme": parsed.scheme,
            "flags": flags,
            "score": max(score, 0),
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# 2. DOMAIN AGE CHECK  (WHOIS via LLM knowledge – no external API)
# ═══════════════════════════════════════════════════════════════════════

def domain_age_node(state: WebsiteScanState) -> dict[str, Any]:
    """Use LLM general knowledge to estimate domain trustworthiness."""
    hostname = state.url_analysis.get("hostname", state.url)

    prompt = f"""You are a cybersecurity domain analyst.

Analyze the domain "{hostname}" and provide your assessment as a valid JSON object.

Return ONLY a JSON object with these fields (no markdown, no explanation):
{{
    "estimated_age": "new (< 1 year) | young (1-3 years) | established (3-10 years) | old (10+ years) | unknown",
    "is_well_known": true/false,
    "domain_type": "personal | business | organization | government | suspicious | unknown",
    "flags": ["list of concerns about the domain age/registration"],
    "score": 0-100
}}

Scoring guide:
- Well-known established domains: 80-100
- Established but less known: 60-80
- Young domains: 30-60
- New/unknown domains: 10-30
- Suspicious patterns: 0-20"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        # Strip markdown code fences if present
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        data = json.loads(content)
    except Exception:
        data = {
            "estimated_age": "unknown",
            "is_well_known": False,
            "domain_type": "unknown",
            "flags": ["Could not determine domain age"],
            "score": 50,
        }

    return {"domain_age_analysis": data}


# ═══════════════════════════════════════════════════════════════════════
# 3. SCAM REPORT ANALYSIS  (LLM knowledge)
# ═══════════════════════════════════════════════════════════════════════

def scam_report_node(state: WebsiteScanState) -> dict[str, Any]:
    """Use LLM general knowledge to check for scam associations."""
    hostname = state.url_analysis.get("hostname", state.url)

    prompt = f"""You are a cybersecurity threat analyst specializing in scam/phishing detection.

Analyze the domain "{hostname}" for any known scam, phishing, or fraud associations.

Return ONLY a valid JSON object (no markdown, no explanation):
{{
    "has_scam_reports": true/false,
    "scam_type": "phishing | fraud | malware | spam | none | unknown",
    "risk_level": "low | medium | high | critical",
    "details": ["list of specific concerns or known reports"],
    "similar_to_known_scams": true/false,
    "score": 0-100
}}

Scoring guide:
- No known reports, legitimate domain: 80-100
- No reports but somewhat suspicious: 50-80
- Similar to known scam patterns: 20-50
- Known scam/phishing domain: 0-20"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        data = json.loads(content)
    except Exception:
        data = {
            "has_scam_reports": False,
            "scam_type": "unknown",
            "risk_level": "medium",
            "details": ["Could not check scam reports"],
            "similar_to_known_scams": False,
            "score": 50,
        }

    return {"scam_report_analysis": data}


# ═══════════════════════════════════════════════════════════════════════
# 4. SSL CERTIFICATE ANALYSIS  (real network check)
# ═══════════════════════════════════════════════════════════════════════

def ssl_analysis_node(state: WebsiteScanState) -> dict[str, Any]:
    """Connect to the host and inspect its TLS certificate."""
    hostname = state.url_analysis.get("hostname", state.url)
    flags: list[str] = []
    cert_info: dict[str, Any] = {}
    score = 100

    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(
            socket.socket(socket.AF_INET), server_hostname=hostname
        ) as s:
            s.settimeout(10)
            s.connect((hostname, 443))
            cert = s.getpeercert()

        if not cert:
            flags.append("No certificate returned")
            score -= 50
        else:
            # Parse expiry
            not_after = cert.get("notAfter", "")
            not_before = cert.get("notBefore", "")
            issuer_tuples = cert.get("issuer", ())
            issuer_org = ""
            for rdn in issuer_tuples:
                for attr in rdn:
                    if attr[0] == "organizationName":
                        issuer_org = attr[1]

            # Check expiry
            if not_after:
                try:
                    expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expiry - datetime.now()).days
                    cert_info["expires_in_days"] = days_left
                    if days_left < 0:
                        flags.append("SSL certificate has EXPIRED")
                        score -= 40
                    elif days_left < 30:
                        flags.append(f"SSL certificate expires soon ({days_left} days)")
                        score -= 15
                except ValueError:
                    pass

            # Check issuer
            cert_info["issuer"] = issuer_org
            known_cas = [
                "Let's Encrypt", "DigiCert", "Comodo", "Sectigo",
                "GlobalSign", "GoDaddy", "Amazon", "Google Trust Services",
                "Cloudflare", "Microsoft", "Baltimore",
            ]
            if issuer_org and not any(ca.lower() in issuer_org.lower() for ca in known_cas):
                flags.append(f"Unknown certificate authority: {issuer_org}")
                score -= 10

            # Check SAN match
            san = cert.get("subjectAltName", ())
            san_names = [entry[1] for entry in san if entry[0] == "DNS"]
            cert_info["san"] = san_names
            if san_names:
                matched = any(
                    hostname == name or
                    (name.startswith("*.") and hostname.endswith(name[1:]))
                    for name in san_names
                )
                if not matched:
                    flags.append("Certificate does not match the domain name")
                    score -= 30

            cert_info["not_before"] = not_before
            cert_info["not_after"] = not_after

    except ssl.SSLCertVerificationError as e:
        flags.append(f"SSL verification failed: {e.verify_message}")
        score -= 40
    except socket.timeout:
        flags.append("Connection timed out (host may be unreachable)")
        score -= 20
    except socket.gaierror:
        flags.append("Domain does not resolve (DNS failure)")
        score -= 50
    except Exception as e:
        flags.append(f"SSL check error: {type(e).__name__}")
        score -= 20

    return {
        "ssl_analysis": {
            "cert_info": cert_info,
            "flags": flags,
            "score": max(score, 0),
        }
    }


# ═══════════════════════════════════════════════════════════════════════
# 5. CONTENT QUALITY ANALYSIS  (LLM-based)
# ═══════════════════════════════════════════════════════════════════════

_content_llm = llm.with_structured_output(ContentQualityExtraction)


def content_analysis_node(state: WebsiteScanState) -> dict[str, Any]:
    """Fetch a snippet of the page and use LLM to evaluate content quality."""
    url = state.url if "://" in state.url else f"https://{state.url}"
    hostname = state.url_analysis.get("hostname", state.url)

    page_text = ""
    fetch_error = None

    # Attempt to fetch page content
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 NeuroShield-Scanner/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read(50_000).decode("utf-8", errors="ignore")

        # Rough HTML → text
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.S | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        page_text = text[:3000]  # Keep prompt size manageable
    except Exception as e:
        fetch_error = str(e)

    if not page_text:
        prompt = f"""You are a website safety analyst.

The website at "{hostname}" could not be fetched (error: {fetch_error or 'empty response'}).

Based on the URL alone, provide your best assessment of what kind of content this site might have.
Be conservative – if you can't determine, mark everything as unknown/false."""
    else:
        prompt = f"""You are a website safety analyst evaluating content quality.

Analyze the following page content from "{hostname}" for signs of scam, phishing, or low-quality content.

PAGE CONTENT (truncated):
{page_text}

STRICT RULES:
- Look for urgency tactics ("Act now!", "Limited time!")
- Look for fake testimonials or unrealistic promises
- Check language quality (grammar, spelling)
- Look for missing contact info, legal pages
- Identify any legitimate trust signals"""

    try:
        result: ContentQualityExtraction = _content_llm.invoke(prompt)
        data = result.model_dump()
    except Exception:
        data = {
            "has_meaningful_content": False,
            "language_quality": "unknown",
            "has_contact_info": False,
            "has_legal_pages": False,
            "red_flags": ["Content analysis failed"],
            "legitimacy_indicators": [],
        }

    # Derive score
    score = 50  # baseline
    if data.get("has_meaningful_content"):
        score += 15
    if data.get("language_quality") == "good":
        score += 15
    elif data.get("language_quality") == "poor":
        score -= 15
    elif data.get("language_quality") == "suspicious":
        score -= 25
    if data.get("has_contact_info"):
        score += 10
    if data.get("has_legal_pages"):
        score += 10
    score -= len(data.get("red_flags", [])) * 8
    score += len(data.get("legitimacy_indicators", [])) * 5

    data["score"] = max(min(score, 100), 0)
    data["fetch_error"] = fetch_error

    return {"content_analysis": data}


# ═══════════════════════════════════════════════════════════════════════
# 6. REPUTATION ANALYSIS  (LLM knowledge)
# ═══════════════════════════════════════════════════════════════════════

_reputation_llm = llm.with_structured_output(ReputationExtraction)


def reputation_node(state: WebsiteScanState) -> dict[str, Any]:
    """Use LLM knowledge to assess the domain's reputation."""
    hostname = state.url_analysis.get("hostname", state.url)

    prompt = f"""You are a cybersecurity analyst specializing in domain reputation.

Evaluate the reputation of the domain "{hostname}".

Consider:
- Is this a well-known, established brand?
- Has this domain been associated with scams, phishing, or malware?
- What category does this website fall into?
- Are there any notable concerns?

Be honest and conservative. If you don't know, say so."""

    try:
        result: ReputationExtraction = _reputation_llm.invoke(prompt)
        data = result.model_dump()
    except Exception:
        data = {
            "is_known_brand": False,
            "known_scam": False,
            "category": "unknown",
            "notes": ["Reputation check failed"],
        }

    # Derive score
    score = 50
    if data.get("is_known_brand"):
        score += 40
    if data.get("known_scam"):
        score -= 50
    if data.get("category") == "legitimate":
        score += 15
    elif data.get("category") == "suspicious":
        score -= 20
    elif data.get("category") == "malicious":
        score -= 40

    data["score"] = max(min(score, 100), 0)

    return {"reputation_analysis": data}


# ═══════════════════════════════════════════════════════════════════════
# 7. AGGREGATE SCORES
# ═══════════════════════════════════════════════════════════════════════

# Weights for final score calculation
_WEIGHTS = {
    "url_structure": 0.15,
    "domain_age": 0.15,
    "scam_reports": 0.20,
    "ssl_certificate": 0.15,
    "content_quality": 0.20,
    "reputation": 0.15,
}


def scoring_node(state: WebsiteScanState) -> dict[str, Any]:
    """Collect all individual scores and compute a weighted overall score."""
    scores = {
        "url_structure": state.url_analysis.get("score", 50),
        "domain_age": state.domain_age_analysis.get("score", 50),
        "scam_reports": state.scam_report_analysis.get("score", 50),
        "ssl_certificate": state.ssl_analysis.get("score", 50),
        "content_quality": state.content_analysis.get("score", 50),
        "reputation": state.reputation_analysis.get("score", 50),
    }

    overall = sum(scores[k] * _WEIGHTS[k] for k in scores)

    return {
        "scores": scores,
        "overall_score": round(overall),
    }


# ═══════════════════════════════════════════════════════════════════════
# 8. VERDICT + RECOMMENDATIONS  (LLM-powered summary)
# ═══════════════════════════════════════════════════════════════════════

def verdict_node(state: WebsiteScanState) -> dict[str, Any]:
    """Produce a human-readable verdict with actionable recommendations."""

    prompt = f"""You are a cybersecurity advisor generating a website safety report.

ANALYSIS DATA:
URL: {state.url}
Overall Score: {state.overall_score}/100

Individual Scores:
{json.dumps(state.scores, indent=2)}

URL Analysis Flags:
{json.dumps(state.url_analysis.get('flags', []))}

Domain Age Info:
{json.dumps(state.domain_age_analysis, indent=2)}

Scam Report Info:
{json.dumps(state.scam_report_analysis, indent=2)}

SSL Analysis Flags:
{json.dumps(state.ssl_analysis.get('flags', []))}

Content Analysis:
{json.dumps(state.content_analysis, indent=2)}

Reputation Info:
{json.dumps(state.reputation_analysis, indent=2)}

──────────────────────────────────
Return ONLY a valid JSON object (no markdown, no explanation):
{{
    "verdict": "SAFE | CAUTION | SUSPICIOUS | DANGEROUS",
    "confidence": "high | medium | low",
    "summary": "2-3 sentence executive summary for a non-technical user",
    "recommendations": [
        "actionable recommendation 1",
        "actionable recommendation 2",
        "..."
    ]
}}

VERDICT RULES:
- SAFE (score >= 75): Trusted, well-known domain with no red flags
- CAUTION (score 50-74): Some concerns but not necessarily malicious
- SUSPICIOUS (score 25-49): Multiple red flags, users should be very careful
- DANGEROUS (score < 25): Strong indicators of scam/phishing, avoid this site

Provide 3-5 specific, actionable recommendations."""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        data = json.loads(content)
    except Exception:
        # Fallback based on score
        score = state.overall_score
        if score >= 75:
            v = "SAFE"
        elif score >= 50:
            v = "CAUTION"
        elif score >= 25:
            v = "SUSPICIOUS"
        else:
            v = "DANGEROUS"

        data = {
            "verdict": v,
            "confidence": "low",
            "summary": f"The website received an overall score of {score}/100.",
            "recommendations": ["Exercise caution when visiting this website."],
        }

    return {
        "verdict": data.get("verdict", "CAUTION"),
        "recommendations": data.get("recommendations", []),
        "summary": json.dumps({
            "verdict": data.get("verdict"),
            "confidence": data.get("confidence"),
            "summary": data.get("summary"),
            "overall_score": state.overall_score,
            "scores": state.scores,
            "recommendations": data.get("recommendations"),
            "url_analysis": state.url_analysis,
            "domain_age_analysis": state.domain_age_analysis,
            "scam_report_analysis": state.scam_report_analysis,
            "ssl_analysis": state.ssl_analysis,
            "content_analysis": state.content_analysis,
            "reputation_analysis": state.reputation_analysis,
        }, indent=2),
    }
