import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
import re
import hashlib

from apify import Actor

# ============================================================
# ENTERPRISE CONFIG
# ============================================================

BLOCKED_PATH_KEYWORDS = [
    "/login", "/admin", "/account", "/checkout",
    "/cart", "/auth", "/register"
]

QUESTION_SELECTORS = "h2, h3, dt"
ANSWER_STOP_TAGS = ["h2", "h3", "dt"]

ENTERPRISE_CONTRACT = {
    "product": "CONVEXO",
    "tier": "Enterprise-Graded",
    "deterministic": True,
    "noisePolicy": "strict",
}

DEFAULT_UI = {
    "presentation": "card",
    "priority": "medium"
}


# ============================================================
# UTILITIES
# ============================================================

def clean(text: str) -> str:
    return " ".join(text.split()).strip().rstrip(".")


def looks_like_question(text: str) -> bool:
    return text.endswith("?") and len(text) >= 8


def is_blocked_url(path: str) -> bool:
    return any(p in path for p in BLOCKED_PATH_KEYWORDS)


def matches_category(text: str, keywords):
    if not keywords:
        return True
    text = text.lower()
    return any(k.lower() in text for k in keywords)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def stable_id(question: str, answer: str) -> str:
    raw = f"{question.lower()}::{answer.lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def infer_locale(path: str) -> str:
    mapping = {
        "fr": "fr-FR",
        "de": "de-DE",
        "de-de": "de-DE",
        "au": "en-AU",
        "in": "en-IN",
        "in-hi": "hi-IN"
    }
    key = path.strip("/").split("/")[0].lower()
    return mapping.get(key, "en-US")


# ============================================================
# FAQ EXTRACTION
# ============================================================

def extract_faqs(html: str, url: str, categories):
    soup = BeautifulSoup(html, "lxml")
    faqs = {}

    for q in soup.select(QUESTION_SELECTORS):
        question = clean(q.get_text())
        if not looks_like_question(question):
            continue

        answer_parts = []
        node = q.find_next_sibling()

        while node and node.name not in ANSWER_STOP_TAGS:
            text = clean(node.get_text())
            if text:
                answer_parts.append(text)
            node = node.find_next_sibling()

        answer = " ".join(answer_parts)
        if not answer or not matches_category(question, categories):
            continue

        intent = slugify(question)
        checked_at = datetime.utcnow().isoformat() + "Z"

        uid = stable_id(question, answer)
        faqs[intent] = {
            "id": uid,
            "type": "faq",
            "question": question,
            "answer": answer + ".",
            "intent": intent,
            "confidence": {
                "score": 0.900,
                "derivedFrom": "faq-structure"
            },
            "source": {
                "url": url,
                "checkedAt": checked_at
            },
            "lastUpdated": checked_at,
            "version": "1.0",
            "ui": DEFAULT_UI
        }

    return faqs


# ============================================================
# NAVIGATION INTENTS
# ============================================================

def extract_navigation_intents(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    base = urlparse(base_url)
    intents = {}

    for a in soup.select("a[href]"):
        href = a["href"]
        full = urljoin(base_url, href)
        parsed = urlparse(full)

        if not parsed.netloc.endswith(base.netloc):
            continue
        if is_blocked_url(parsed.path):
            continue

        top = parsed.path.strip("/").split("/")[0]
        if not top:
            continue

        locale = infer_locale(parsed.path)
        nav_id = f"nav_{top}"

        intents[nav_id] = {
            "id": nav_id,
            "type": "navigation",
            "intent": f"visit_{top}",
            "keywords": [
                top,
                f"{top} page",
                f"open {top}",
                f"go to {top}"
            ],
            "label": top.replace("-", " ").title(),
            "url": f"{parsed.scheme}://{parsed.netloc}/{top}",
            "locale": locale,
            "confidence": {
                "score": 0.800,
                "derivedFrom": "site-structure"
            }
        }

    return intents


# ============================================================
# MAIN ACTOR
# ============================================================

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}

        start_url = input_data["startUrl"]
        max_depth = input_data.get("maxDepth", 1)
        categories = input_data.get("categoriesToInclude", [])

        visited = set()
        queue = [(start_url, 0)]

        faq_by_intent = {}
        nav_items = {}

        async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                headers={"User-Agent": "CONVEXO/Enterprise"}
        ) as client:

            while queue:
                url, depth = queue.pop(0)
                if url in visited or depth > max_depth:
                    continue

                visited.add(url)

                try:
                    r = await client.get(url)
                    r.raise_for_status()
                except Exception:
                    continue

                html = r.text

                faq_by_intent.update(extract_faqs(html, url, categories))
                nav_items.update(extract_navigation_intents(html, url))

        nodes = {
            "start": {
                "type": "system",
                "message": "How can I help you today?",
                "options": [],
                "ui": DEFAULT_UI
            }
        }

        for faq in faq_by_intent.values():
            nodes["start"]["options"].append({
                "text": faq["question"],
                "next": faq["id"]
            })
            nodes[faq["id"]] = faq | {
                "options": [{"text": "Back", "next": "start"}]
            }

        output = {
            "contract": ENTERPRISE_CONTRACT,
            "version": "0.0",
            "type": "tree",
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "totalNodes": len(nodes),
                "faqNodes": len(faq_by_intent),
                "navItems": len(nav_items),
                "uniqueIntents": len(set(faq_by_intent.keys())),
                "lastValidated": datetime.utcnow().isoformat() + "Z"
            },
            "conversation": {
                "entryMessage": "How can I help you today?",
                "fallback": {
                    "message": "I couldn’t find an exact answer, but these might help.",
                    "strategy": "intent-based",
                    "fallbackConfidence": 0.600,
                    "navigation": list(nav_items.values())
                }
            },
            "nodes": nodes
        }

        await Actor.set_value("OUTPUT", output)
        await Actor.push_data(output)


if __name__ == "__main__":
    asyncio.run(main())
