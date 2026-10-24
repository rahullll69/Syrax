"""
SEO Package and Reddit Marketing / Bot Generator.
Generates comprehensive on-page SEO metadata, JSON-LD Schema.org markup,
high-converting Reddit launch campaign posts, and an automated Python Reddit listening & promotion bot.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

import config
import llm_client

logger = logging.getLogger("launchkit.seo_reddit")


def generate_seo_package(name: str, topic: str, url: str = "") -> Dict[str, Any]:
    """Generate on-page SEO tags, target keywords, OpenGraph tags, and JSON-LD schema markup."""
    base_url = url or f"https://{name.lower().replace(' ', '')}.com"
    clean_topic = topic.replace('"', "'")

    if llm_client.is_available():
        prompt = f"""
You are a senior technical SEO director.
Product Name: {name}
Product Topic: {topic}
Website URL: {base_url}

Generate an enterprise SEO metadata package in valid JSON:
{{
  "meta_title": "Optimized title under 60 chars with primary keyword and brand",
  "meta_description": "Compelling meta description under 155 chars with call to action",
  "primary_keyword": "Main search keyword",
  "secondary_keywords": ["keyword 1", "keyword 2", "keyword 3", "keyword 4", "keyword 5"],
  "canonical_url": "{base_url}",
  "og_title": "Social OpenGraph title",
  "og_description": "Social OpenGraph description"
}}
Output ONLY valid JSON.
"""
        res, _ = llm_client.single_prompt("You are an elite SEO specialist. Output valid JSON only.", prompt, max_tokens=600)
        if res:
            try:
                clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", res, flags=re.M).strip()
                data = json.loads(clean_json)
                data["json_ld"] = _build_json_ld(name, clean_topic, base_url, data.get("meta_description", ""))
                return data
            except Exception as e:
                logger.warning(f"Failed to parse SEO JSON: {e}")

    # Fallback algorithmic SEO package
    meta_title = f"{name} — Next-Gen {topic.title()}"[:60]
    meta_desc = f"Discover {name}, the modern platform built for {topic}. Unlock automated execution and streamlined results today."[:155]
    secondary = [
        f"best {topic} tool",
        f"{name} alternative",
        f"modern {topic} software",
        f"automated {topic}",
        f"{topic} for teams",
    ]
    return {
        "meta_title": meta_title,
        "meta_description": meta_desc,
        "primary_keyword": f"{topic} software",
        "secondary_keywords": secondary,
        "canonical_url": base_url,
        "og_title": meta_title,
        "og_description": meta_desc,
        "json_ld": _build_json_ld(name, clean_topic, base_url, meta_desc),
    }


def _build_json_ld(name: str, topic: str, url: str, description: str) -> str:
    """Generate standard Schema.org SoftwareApplication JSON-LD."""
    schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "operatingSystem": "All",
        "applicationCategory": "BusinessApplication",
        "description": description or f"Modern intelligent platform for {topic}.",
        "url": url,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
            "availability": "https://schema.org/OnlineOnly",
        },
    }
    return json.dumps(schema, indent=2)


def generate_reddit_campaign(name: str, topic: str, url: str = "") -> Dict[str, Any]:
    """
    Generate target subreddits, launch post copy, comment templates,
    and a standalone executable Python Reddit Bot script.
    """
    base_url = url or f"https://{name.lower().replace(' ', '')}.com"

    subreddits = [
        {"name": "r/SideProject", "angle": "Show & tell launch; emphasize how and why you built it solo/indie."},
        {"name": "r/SaaS", "angle": "Business focus; discuss market validation, competitive friction, and technical stack."},
        {"name": "r/Entrepreneur", "angle": "Founder journey; problem discovery, user interviews, and product-market fit."},
        {"name": "r/webdev", "angle": "Engineering deep-dive; performance, modern UI stack, and API architecture."},
    ]

    launch_post_title = f"I was tired of clunky legacy tools, so I built {name} (a modern {topic}) — would love your honest brutal feedback!"
    launch_post_body = f"""Hey Reddit! 👋

Like many of you, I spent months frustrated by existing options in the {topic} space. Everything felt bloated, expensive, and required hours of tedious manual setup.

So I decided to build **{name}**.

### What it does differently:
1. **Instant Momentum:** Zero complex onboarding. You get tangible results in under 60 seconds.
2. **Autonomous Execution:** Designed from the ground up with native intelligence that automates 80% of repetitive steps.
3. **Transparent & Clean:** No surprise paywalls or predatory lock-ins.

We're currently opening early access for builders and power users here: {base_url}

I'd genuinely love your most critical feedback:
- What features are missing for your daily workflow?
- How does our standing out angle resonate with you?

Drop any thoughts below, and I'll personally answer every single comment!"""

    reddit_bot_script = _generate_reddit_bot_script(name, topic, base_url)

    return {
        "subreddits": subreddits,
        "launch_post_title": launch_post_title,
        "launch_post_body": launch_post_body,
        "bot_script": reddit_bot_script,
    }


def _generate_reddit_bot_script(name: str, topic: str, url: str) -> str:
    """Generate ready-to-run Python Reddit monitoring bot script."""
    return f'''"""
Autonomous Reddit Keyword Monitoring & Promotion Bot for {name}
Scans target subreddits for user pain points and relevant discussions using Reddit's public API.
"""

import time
import requests

SUBREDDITS = ["SideProject", "SaaS", "Entrepreneur", "startups"]
KEYWORDS = ["{topic.lower()}", "recommend tool", "alternative to", "best tool for", "{name.lower()}"]
PRODUCT_NAME = "{name}"
PRODUCT_URL = "{url}"
USER_AGENT = "RedditPromoBot/1.0 (for {name}; contact@yourdomain.com)"

HEADERS = {{"User-Agent": USER_AGENT}}

def check_subreddits():
    print(f"[*] Scanning Reddit communities for '{topic}' demand signals...")
    seen_posts = set()

    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{{sub}}/new.json?limit=15"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code != 200:
                print(f"[-] HTTP {{resp.status_code}} on r/{{sub}}")
                continue

            posts = resp.json().get("data", {{}}).get("children", [])
            for p in posts:
                data = p.get("data", {{}})
                post_id = data.get("id")
                title = data.get("title", "")
                text = data.get("selftext", "")
                permalink = "https://reddit.com" + data.get("permalink", "")

                if post_id in seen_posts:
                    continue
                seen_posts.add(post_id)

                combined = (title + " " + text).lower()
                matches = [k for k in KEYWORDS if k in combined]

                if matches:
                    print(f"\\n🎯 FOUND OPPORTUNITY on r/{{sub}}!")
                    print(f"Title: {{title}}")
                    print(f"Link:  {{permalink}}")
                    print(f"Matched Keywords: {{matches}}")
                    print("Suggested Reply Draft:")
                    print(f"  > Hey! If you're exploring {topic}, check out {{PRODUCT_NAME}} ({{PRODUCT_URL}}).")
                    print(f"  > It was specifically designed to solve friction with fast onboarding and automation.")
        except Exception as e:
            print(f"[-] Error querying r/{{sub}}: {{e}}")

if __name__ == "__main__":
    print(f"=== {{PRODUCT_NAME}} Autonomous Reddit Lead Finder ===")
    check_subreddits()
'''


def format_seo_and_reddit_delivery(name: str, seo_data: Dict[str, Any], reddit_data: Dict[str, Any]) -> str:
    """Format SEO and Reddit promotion outputs into clean, actionable chat deliverables."""
    sub_lines = "\n".join([f"• **{s['name']}**: {s['angle']}" for s in reddit_data.get("subreddits", [])])
    keywords_str = ", ".join(seo_data.get("secondary_keywords", []))

    return f"""🚀 **SEO & REDDIT PROMOTION PACKAGE: {name.upper()}**

📌 **1. Search Engine Optimization (SEO) Metadata:**
• **Meta Title:** `{seo_data.get('meta_title')}`
• **Meta Description:** `{seo_data.get('meta_description')}`
• **Primary Keyword:** `{seo_data.get('primary_keyword')}`
• **Target LSI Keywords:** {keywords_str}
• **Canonical URL:** `{seo_data.get('canonical_url')}`

📄 **JSON-LD Schema.org Markup (Insert inside `<head>`):**
```html
<script type="application/ld+json">
{seo_data.get('json_ld')}
</script>
```

---

📢 **2. High-Converting Reddit Launch Post:**
**Target Subreddits:**
{sub_lines}

**Suggested Post Title:**
> {reddit_data.get('launch_post_title')}

**Post Body Copy:**
```markdown
{reddit_data.get('launch_post_body')}
```

---

🤖 **3. Autonomous Reddit Promo & Lead-Finder Bot Script:**
Save this as `reddit_promo_bot.py` and run it locally with `python3 reddit_promo_bot.py`:
```python
{reddit_data.get('bot_script')}
```"""
