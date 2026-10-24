"""
Launch Kit Agent v3: chat with it, or give it an idea and get a finished, audited launch kit
(single-file uAgent for Agentverse hosted agents)

AGENTVERSE README (paste into the agent profile):
  Launch Kit Agent is a friendly assistant that also does real work. Chat with it about your idea,
  or just describe a product and it delivers a complete launch kit inside the conversation: live
  market research, landing page copy, a 6-tweet launch thread, an SVG logo with palette and tagline,
  and a polished single-file landing page (navigation, hero, features, how it works, FAQ, launch
  thread, call-to-action band). It audits its own work before delivering and repairs or replaces
  anything that fails, and it can restyle the kit when you ask.
  Input:  normal chat, or an idea such as "Launch my travel planning app called Wanderly. Tone: playful."
          Optional: a product URL, an email (for the button), a tone (friendly, bold, playful, professional).
  Follow-ups: "make it bold", "rename it to Zoomly" (reuses your last idea).
  Output: labeled steps (PLAN, RESEARCH, WRITE, FIX, DESIGN, AUDIT, PUBLISH, RECEIPT), then the
          copy, thread, logo SVG and landing page HTML.
  Data:   Hacker News Algolia API, Wikipedia API, your product URL. No keys needed.
  Health: send "diag" to get a self-check (python, network, LLM key, GitHub token).

Secrets (Agentverse > agent > Secrets), all optional:
  ASI_API_KEY   enables LLM chat and LLM-written copy (otherwise friendly built-in replies and an
                audited template are used)
  ASI_MODEL     model name, default "asi1" (send "diag" to test it)
  GITHUB_TOKEN  token with the 'gist' scope, enables PUBLISH to a private Gist
"""

import asyncio
import html as htmllib
import os
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from uuid import uuid4

import requests
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

NAME = "Launch Kit Agent"
ASI_URL = "https://api.asi1.ai/v1/chat/completions"
ASI_MODEL = os.getenv("ASI_MODEL", "asi1")
UA = "LaunchKitAgent/3.0"
HDR = {"User-Agent": UA}
JOB_TIME_LIMIT_S = 45   # slow optional steps are skipped after this many seconds
HTTP_TIMEOUT = 3

agent = Agent()
chat_proto = Protocol(spec=chat_protocol_spec)

ABOUT = (
    "Hi, I'm the " + NAME + ". We can just chat, and when you're ready I can turn an idea into a "
    "finished launch kit and I check my own work.\n\n"
    "I research the space live (Hacker News, Wikipedia, your URL), write landing copy and a "
    "6-tweet thread, design an SVG logo with palette and tagline, audit everything, and build a "
    "polished single-file landing page you can open right away.\n\n"
    "Try: Launch my travel planning app called Wanderly. Tone: playful.\n"
    "Or just tell me what you're building. Then restyle it: make it bold  |  rename it to Zoomly\n"
    "Health check: send  diag"
)

CHAT_SYSTEM = (
    "You are the Launch Kit Agent, a warm, curious and concise assistant. You chat naturally about "
    "anything the user brings up, in 1 to 4 short sentences. You can also build launch kits: live "
    "research, landing page copy, a 6-tweet thread, an SVG logo with palette and tagline, and a "
    "landing page, then restyle it on request. When the user mentions a product, business or idea, "
    "gently offer to build their launch kit and tell them they can just describe it in a sentence. "
    "Never claim abilities beyond that list. Do not invent facts about the user."
)

SYSTEM_PROMPT = (
    "You are a senior launch copywriter. Output EXACTLY this format and nothing else:\n"
    "HEADLINE: <one line>\nSUBHEAD: <one line>\nBENEFITS:\n- <benefit>\n- <benefit>\n- <benefit>\n"
    "CTA: <short call to action>\n"
    "HOWITWORKS:\n1. <Short title>: <one sentence>\n2. <Short title>: <one sentence>\n3. <Short title>: <one sentence>\n"
    "FAQ:\nQ: <question>\nA: <answer>\nQ: <question>\nA: <answer>\nQ: <question>\nA: <answer>\n"
    "THREAD:\n1/ <tweet>\n2/ <tweet>\n3/ <tweet>\n4/ <tweet>\n5/ <tweet>\n6/ <tweet with a clear call to action>\n"
    "Rules: exactly 3 benefits, exactly 3 steps, exactly 3 FAQ pairs, exactly 6 tweets, every tweet under "
    "270 characters, no placeholders, no brackets, no lorem ipsum, no invented statistics, testimonials or "
    "customer claims. Use the research signals only as context. If FEEDBACK is given, fix exactly those issues."
)

PH_CI = re.compile(
    r"lorem|ipsum|placeholder text|"
    r"\[(?:insert|your|add|name|brand|company)[A-Za-z ]{0,25}\]|your (?:brand|product|name|company) here",
    re.I,
)
PH_CS = re.compile(r"\b(?:TODO|TBD)\b")  # case-sensitive so "todo app" is fine
CTA_WORDS = re.compile(r"\b(try|join|get|download|sign up|start|grab|visit|book|waitlist|link)\b", re.I)
HEX = re.compile(r"#[0-9a-fA-F]{6}")

PALETTES = [
    ["#0F4C5C", "#E36414", "#FB8B24", "#FFFFFF"],
    ["#1B263B", "#415A77", "#E0A458", "#FFFFFF"],
    ["#2D6A4F", "#95D5B2", "#F4A261", "#FFFFFF"],
    ["#3D348B", "#7678ED", "#F7B801", "#FFFFFF"],
    ["#7F1D1D", "#DC2626", "#FBBF24", "#FFFFFF"],
    ["#0B3954", "#087E8B", "#FF5A5F", "#FFFFFF"],
]
# tone -> (subhead, 6-word tagline)
TONES = {
    "bold": ("No fluff. Just results.", "Move fast, launch bold, win big"),
    "playful": ("Fun to use, hard to put down.", "Fun to use, hard to quit"),
    "professional": ("Reliable, efficient and built for real work.", "Reliable tools for serious teams today"),
    "friendly": ("Simple, welcoming and built for everyday use.", "Built to launch, made to last"),
}
CACHED = [
    ("Hacker News front page, where early-adopter launch discussion happens", "https://news.ycombinator.com/"),
    ("Wikipedia: Landing page, conventions for launch pages", "https://en.wikipedia.org/wiki/Landing_page"),
]

ICONS = [
    '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    '<path d="M16 11a4 4 0 1 0-8 0 4 4 0 0 0 8 0zM4 21c0-4 3.6-6 8-6s8 2 8 6"/>',
    '<path d="M21 12a9 9 0 1 1-3-6.7M21 4v5h-5"/>',
]

# conversation routing
GOAL_VERBS = re.compile(r"\b(launch|promote|market|announce|introduce|advertise|pitch)\b", re.I)
ARTIFACTS = re.compile(r"\b(landing page|launch kit|logo|tagline|tweets?|thread|web ?page|website|brand identity)\b", re.I)
FOR_MY = re.compile(r"\b(for|about)\s+(my|our|the|a|an)\b", re.I)
GREET = re.compile(r"^\s*(hi+|hello+|hey+|yo|hola|namaste|sup|good\s+(morning|afternoon|evening))\b", re.I)
HOWARE = re.compile(r"how\s*(are|r)\s*(you|u)\b|how'?s it going|what'?s up|wass?up", re.I)
THANKS = re.compile(r"\b(thanks|thank you|thx|ty|cheers)\b", re.I)
BYE = re.compile(r"\b(bye|goodbye|see you|cya|good night)\b", re.I)
WHO = re.compile(r"\b(who are you|what are you|what can you do|what do you do|capabilities|how do you work|help me understand)\b|^\s*help\s*[?!.]*\s*$", re.I)
IDEA_HINT = re.compile(
    r"\b(i have an idea|i want to (?:start|launch|build|create|make)|help me (?:launch|start|build|promote)|"
    r"i'?m (?:building|making|starting|working on)|i am (?:building|making|starting|working on))\b", re.I)
PRODUCT_HINT = re.compile(
    r"\b(app|product|startup|saas|tool|platform|shop|store|cafe|bakery|brand|business|service|course|"
    r"newsletter|podcast|game|website|extension|plugin|studio|agency)\b", re.I)
YES = re.compile(r"^\s*(y|yes|yeah|yep|yup|sure|ok|okay|go|do it|please|go ahead|let'?s go)\b", re.I)
NO = re.compile(r"^\s*(n|no|nope|nah|cancel|never ?mind|stop|not now)\b", re.I)


# ---------- infrastructure helpers ----------

def make_msg(text):
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


async def say(ctx, sender, text):
    await ctx.send(sender, make_msg(text))


def _safe(fn, args):
    try:
        return True, fn(*args)
    except Exception as e:  # noqa: BLE001
        return False, e


async def blocking(fn, *args):
    """Run a blocking call off the event loop; fall back to a direct call if threads are unavailable."""
    try:
        loop = asyncio.get_running_loop()
        ok, val = await loop.run_in_executor(None, _safe, fn, args)
    except Exception:  # noqa: BLE001
        ok, val = _safe(fn, args)
    if ok:
        return val
    raise val


def store_get(ctx, key, default=None):
    try:
        v = ctx.storage.get(key)
        return default if v is None else v
    except Exception:  # noqa: BLE001
        return default


def store_set(ctx, key, value):
    try:
        ctx.storage.set(key, value)
    except Exception as e:  # noqa: BLE001
        ctx.logger.error("storage set failed: " + type(e).__name__)


def find_placeholder(text):
    m = PH_CI.search(text) or PH_CS.search(text)
    return m.group(0) if m else ""


# ---------- parsing ----------

def parse_goal(text):
    url_m = re.search(r"https?://[^\s<>\"']+", text)
    url = url_m.group(0).rstrip(".,)") if url_m else ""
    email_m = re.search(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+", text)
    email = email_m.group(0).rstrip(".,") if email_m else ""
    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+", "", clean)
    clean = re.sub(r"\bemail\s*[:=]?", "", clean, flags=re.I)

    name_m = re.search(r"(?:called|named|name\s*[:=])\s*[\"']?([A-Za-z][\w\-]{1,24})", clean, re.I)
    name = name_m.group(1) if name_m else ""

    tone_m = re.search(r"tone\s*[:=]\s*([A-Za-z][A-Za-z ,\-]{2,30}?)(?:[.\n;]|$)", clean, re.I)
    tone_raw = tone_m.group(1).strip().lower() if tone_m else ""
    if not tone_raw:
        for k in TONES:
            if re.search(r"\b" + k + r"\b", clean, re.I):
                tone_raw = k
                break
    tone = "friendly"
    for k in TONES:
        if k in tone_raw:
            tone = k
            break

    topic_m = (
        re.search(r"(?:launch|promote|market|announce|introduce)\s+(?:my|our|the|a|an)?\s*([^.,:;\n]{3,60})", clean, re.I)
        or re.search(r"(?:building|making|starting|creating|developing|working on)\s+(?:my|our|the|a|an)?\s*([^.,:;\n]{3,60})", clean, re.I)
        or re.search(r"(?:for|about)\s+(?:my|our|the|a|an)\s+([^.,:;\n]{3,60})", clean, re.I)
    )
    topic = topic_m.group(1) if topic_m else clean.strip()[:60]
    topic = re.sub(r"\s+(?:called|named)\s+.*$", "", topic, flags=re.I)
    topic = re.sub(r"\s*\btone\s*([:=].*)?$", "", topic, flags=re.I)
    topic = re.sub(r"\s+", " ", topic).strip(" ,.;")
    topic = re.sub(r"^(?:a|an|my|our|the)\s+", "", topic, flags=re.I) or "product"
    if not name:
        base = re.split(r"\s+(?:for|in|to|that|which)\s+", topic)[0] or topic
        name = base.title()[:24]
    return {"url": url, "email": email, "name": name, "tone": tone, "topic": topic}


def is_goal(text):
    words = len(text.split())
    if words >= 4 and GOAL_VERBS.search(text):
        return True
    if words >= 5 and ARTIFACTS.search(text) and FOR_MY.search(text):
        return True
    return False


def parse_followup(text, last):
    """'make it bold' / 'rename it to Zoomly' on top of the last job. Returns new job dict or None."""
    if not last or FOR_MY.search(text) or GOAL_VERBS.search(text):
        return None
    imperative = re.match(r"\s*(?:please\s+)?(make|change|switch|restyle|redo|rewrite|try|use|go|rename|call|name)\b", text, re.I)
    if not (imperative or re.search(r"\btone\b", text, re.I)):
        return None
    new = dict(last)
    changed = False
    low = text.lower()
    for k in TONES:
        if re.search(r"\b" + k + r"\b", low):
            new["tone"] = k
            changed = True
            break
    m = re.search(r"(?:rename(?: it)?(?: to)?|call it|name it)\s+[\"']?([A-Za-z][\w\-]{1,24})", text, re.I)
    if m:
        new["name"] = m.group(1)
        changed = True
    return new if changed else None


def get_tweets(text):
    m = re.search(r"THREAD:\s*(.*)", text, re.S | re.I)
    block = m.group(1) if m else ""
    return [t.strip() for t in re.findall(r"^\s*\d+\s*[/.)]\s*(.+)$", block, re.M)]


def get_benefits(text):
    m = re.search(r"BENEFITS:\s*(.*?)\n\s*CTA:", text, re.S | re.I)
    block = m.group(1) if m else ""
    return [b.strip() for b in re.findall(r"^\s*[-•*]\s*(.+)$", block, re.M)]


def get_steps(text):
    m = re.search(r"HOWITWORKS:\s*(.*?)\n\s*FAQ:", text, re.S | re.I)
    block = m.group(1) if m else ""
    out = []
    for line in re.findall(r"^\s*\d+\s*[.)]\s*(.+)$", block, re.M):
        title, _, body = line.partition(":")
        out.append((title.strip(), body.strip()) if body.strip() else (title.strip(), ""))
    return out


def get_faq(text):
    m = re.search(r"FAQ:\s*(.*?)\n\s*THREAD:", text, re.S | re.I)
    block = m.group(1) if m else ""
    return [(q.strip(), a.strip()) for q, a in re.findall(r"^\s*Q:\s*(.+)\n\s*A:\s*(.+)$", block, re.M)]


def field(text, name):
    m = re.search(r"^" + name + r":\s*(.+)$", text, re.M | re.I)
    return m.group(1).strip() if m else ""


# ---------- RESEARCH (live data) ----------

def hn_search(query):
    r = requests.get(
        "https://hn.algolia.com/api/v1/search",
        params={"query": query, "tags": "story", "hitsPerPage": 5},
        timeout=HTTP_TIMEOUT, headers=HDR,
    )
    r.raise_for_status()
    out = []
    for h in r.json().get("hits", []):
        if h.get("title"):
            url = h.get("url") or "https://news.ycombinator.com/item?id=" + str(h.get("objectID"))
            out.append(("Hacker News: " + h["title"] + " (" + str(h.get("points") or 0) + " points)", url))
    return out[:4]


def wiki_search(query):
    r = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={"action": "query", "list": "search", "srsearch": query, "format": "json", "srlimit": 3},
        timeout=HTTP_TIMEOUT, headers=HDR,
    )
    r.raise_for_status()
    out = []
    for i in r.json().get("query", {}).get("search", []):
        snippet = re.sub(r"<[^>]+>", "", i.get("snippet", "")).strip()
        out.append(("Wikipedia: " + i["title"] + ": " + snippet,
                    "https://en.wikipedia.org/wiki/" + i["title"].replace(" ", "_")))
    return out


def page_summary(url):
    r = requests.get(url, timeout=HTTP_TIMEOUT, headers=HDR)
    r.raise_for_status()
    body = r.text[:200000]
    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    desc = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', body, re.S | re.I)
    parts = [re.sub(r"\s+", " ", x.group(1)).strip() for x in (title, desc) if x]
    return [("Your product page: " + " | ".join(parts), url)] if parts else []


async def research(topic, url, deadline):
    items, live, errors = [], False, []
    steps = []
    if url:
        steps.append(("product page", page_summary, url))
    steps.append(("Hacker News", hn_search, topic))
    steps.append(("Wikipedia", wiki_search, topic))
    for label, fn, arg in steps:
        if time.time() > deadline:
            errors.append(label + " (skipped, time limit)")
            continue
        try:
            found = await blocking(fn, arg)
            if found:
                items.extend(found)
                live = True
        except Exception as e:  # noqa: BLE001
            errors.append(label + " (" + type(e).__name__ + ")")
    short = " ".join(topic.split()[-2:])
    if short != topic and not any(t.startswith("Hacker News") for t, _ in items) and time.time() < deadline:
        try:
            found = await blocking(hn_search, short)
            items.extend(found)
            live = live or bool(found)
        except Exception:  # noqa: BLE001
            pass
    seen, unique = set(), []
    for t, u in items:
        if u not in seen:
            seen.add(u)
            unique.append((t, u))
    if not unique:
        return CACHED, False, errors
    return unique[:7], live, errors


# ---------- LLM ----------

def llm_messages(messages, max_tokens=900, temperature=0.7, timeout=12):
    key = os.getenv("ASI_API_KEY")
    if not key:
        return None, "no ASI_API_KEY secret set"
    try:
        r = requests.post(
            ASI_URL,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"model": ASI_MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
            timeout=timeout,
        )
        if r.status_code >= 400:
            return None, "HTTP " + str(r.status_code) + ": " + r.text[:120].replace("\n", " ")
        out = r.json()["choices"][0]["message"]["content"].strip()
        return re.sub(r"^```(?:\w+)?|```$", "", out, flags=re.M).strip(), ""
    except Exception as e:  # noqa: BLE001
        return None, type(e).__name__


def llm_chat(system, user, max_tokens=900, temperature=0.7, timeout=12):
    return llm_messages([{"role": "system", "content": system}, {"role": "user", "content": user}],
                        max_tokens, temperature, timeout)


def llm_copy(name, topic, tone, signals, feedback=""):
    user = ("Product: " + topic + "\nBrand name: " + name + "\nTone: " + tone
            + "\nResearch signals (context only):\n" + "\n".join("- " + t for t, _ in signals[:5]))
    if feedback:
        user += "\nFEEDBACK: " + feedback
    return llm_chat(SYSTEM_PROMPT, user, 1300)


# ---------- WRITE (template) ----------

def template_copy(name, topic, tone, signals):
    punch = TONES[tone][0]
    headlines = {
        "bold": name + ": stop settling for a worse " + topic,
        "playful": "Say hello to " + name + ", the " + topic + " that is actually fun",
        "professional": name + ": a dependable " + topic + " for people who mean business",
        "friendly": "Meet " + name + ": the " + topic + " that gets out of your way",
    }
    hn = next((t for t, _ in signals if t.startswith("Hacker News:")), "")
    title = re.sub(r"\s*\(\d+ points\)$", "", hn.replace("Hacker News: ", "")).replace('"', "'")[:110]
    if title:
        second = '2/ People are already talking about this space, for example "' + title + '" on Hacker News. There is clear interest.'
    else:
        second = "2/ The problem: many " + topic + " options feel either too complicated or too limited to bother with."
    lines = [
        "HEADLINE: " + headlines[tone],
        "SUBHEAD: " + punch,
        "BENEFITS:",
        "- Designed to be simple to start, with no steep learning curve",
        "- Shaped by what people in the " + topic + " space are actually asking for",
        "- Improved in the open, with new updates shipped regularly",
        "CTA: Join the " + name + " waitlist",
        "HOWITWORKS:",
        "1. Join early: Use the button on this page to get on the list.",
        "2. Start simple: " + name + " is designed to be easy from the very first minute.",
        "3. Shape what is next: Tell us what you want and it guides the roadmap.",
        "FAQ:",
        "Q: What is " + name + "?",
        "A: " + name + " is a " + topic + " designed to be simple to start and shaped by what people in the " + topic + " space ask for.",
        "Q: Who is it for?",
        "A: Anyone who wants the result of a good " + topic + " without the overhead.",
        "Q: How do I get early access?",
        "A: Use the button at the top of this page to join the waitlist.",
        "THREAD:",
        "1/ We are launching " + name + ", a new " + topic + ". Here is why we built it and who it is for.",
        second,
        "3/ Our approach: make " + name + " clean and simple so you get from zero to done in minutes.",
        "4/ We are building in public. Tell us what you want next and it shapes the roadmap.",
        "5/ " + name + " is made for people who want the result without the overhead.",
        "6/ Ready to try " + name + "? Join the waitlist today and be first in line.",
    ]
    return "\n".join(lines) + "\n"


# ---------- DESIGN ----------

def make_logo(name, tone):
    h = sum(ord(c) for c in name)
    p = PALETTES[h % len(PALETTES)]
    design = (h // len(PALETTES)) % 3
    initial = name[0].upper() if name[0].isalnum() else "L"
    letter = (
        '<text x="100" y="124" font-family="Arial, sans-serif" font-size="70" font-weight="700" '
        'text-anchor="middle" fill="{c}">' + htmllib.escape(initial) + "</text>"
    )
    if design == 0:
        body = (
            '<rect width="200" height="200" rx="44" fill="' + p[0] + '"/>'
            '<circle cx="100" cy="100" r="62" fill="' + p[1] + '"/>'
            '<path d="M40 150 Q100 60 160 150" fill="none" stroke="' + p[2] + '" stroke-width="10" stroke-linecap="round"/>'
            + letter.replace("{c}", p[3])
        )
    elif design == 1:
        body = (
            '<rect width="200" height="200" rx="44" fill="' + p[0] + '"/>'
            '<polygon points="100,28 162,64 162,136 100,172 38,136 38,64" fill="' + p[1] + '"/>'
            '<polygon points="100,52 142,76 142,124 100,148 58,124 58,76" fill="' + p[2] + '"/>'
            + letter.replace("{c}", p[0])
        )
    else:
        body = (
            '<circle cx="100" cy="100" r="100" fill="' + p[0] + '"/>'
            '<rect x="46" y="46" width="108" height="108" rx="22" transform="rotate(45 100 100)" fill="' + p[1] + '"/>'
            '<circle cx="100" cy="100" r="42" fill="' + p[2] + '"/>'
            + letter.replace("{c}", p[0])
        )
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">' + body + "</svg>"
    return svg, p, TONES[tone][1]


# ---------- BUILD ----------

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__"><meta property="og:description" content="__DESC__">
<style>
:root{--bg:#fbfbfd;--fg:#16161a;--muted:#5b5b66;--card:#fff;--line:#e6e6ee;--nav:rgba(255,255,255,.82);--ey:__P0__;--p0:__P0__;--p1:__P1__;--p2:__P2__}
@media (prefers-color-scheme: dark){:root{--bg:#0e0e11;--fg:#f2f2f5;--muted:#a3a3b0;--card:#18181d;--line:#2a2a32;--nav:rgba(14,14,17,.82);--ey:__P2__}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:var(--bg);color:var(--fg);line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:inherit}.wrap{max-width:1040px;margin:0 auto;padding:0 20px}
.lg{width:32px;height:32px;border-radius:9px;flex:none}
nav{position:sticky;top:0;z-index:10;background:var(--nav);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.nav-in{display:flex;align-items:center;justify-content:space-between;gap:16px;height:62px}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;text-decoration:none;min-width:0;white-space:nowrap}
.links{display:flex;gap:22px}.links a{text-decoration:none;color:var(--muted);font-size:14px}.links a:hover{color:var(--fg)}
.btn{display:inline-block;background:var(--p2);color:#111;font-weight:700;padding:14px 28px;border-radius:999px;text-decoration:none;box-shadow:0 8px 22px rgba(0,0,0,.18);transition:transform .2s,box-shadow .2s}
.btn:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(0,0,0,.24)}
.btn.sm{padding:8px 16px;font-size:14px;white-space:nowrap;box-shadow:none}
.btn.ghost{background:transparent;color:#fff;border:2px solid rgba(255,255,255,.55);box-shadow:none}
.hero,.band{position:relative;overflow:hidden;background:var(--p0);color:#fff;text-align:center}
.hero{padding:84px 0 96px}
.hero:before,.band:before{content:"";position:absolute;right:-120px;top:-160px;width:520px;height:520px;border-radius:50%;background:var(--p1);opacity:.35;filter:blur(40px)}
.hero:after,.band:after{content:"";position:absolute;left:-140px;bottom:-200px;width:460px;height:460px;border-radius:50%;background:var(--p2);opacity:.22;filter:blur(50px)}
.hero .wrap,.band .wrap{position:relative;z-index:1}
.logo-big svg{width:84px;height:84px;border-radius:22px;box-shadow:0 12px 32px rgba(0,0,0,.3)}
.pill{display:inline-block;margin-top:20px;padding:6px 14px;background:rgba(255,255,255,.16);border-radius:999px;font-size:13px;letter-spacing:.04em}
.hero h1{font-size:clamp(32px,6vw,58px);line-height:1.08;letter-spacing:-.02em;max-width:820px;margin:18px auto 14px}
.sub{font-size:clamp(17px,2.4vw,21px);max-width:640px;margin:0 auto 30px;opacity:.92}
.actions{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
section{padding:72px 0}
.eyebrow{color:var(--ey);font-weight:700;font-size:13px;letter-spacing:.08em;text-transform:uppercase}
h2{font-size:clamp(26px,4vw,36px);line-height:1.15;letter-spacing:-.01em;margin:6px 0 28px}
h3{margin:0 0 6px;font-size:18px}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-top:4px solid var(--p1);border-radius:18px;padding:24px;transition:transform .2s,box-shadow .2s}
.card:hover{transform:translateY(-4px);box-shadow:0 14px 34px rgba(0,0,0,.1)}
.icon{width:44px;height:44px;border-radius:12px;background:var(--p0);color:#fff;display:grid;place-items:center;margin-bottom:14px}
.icon svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.card p,.step p{margin:0;color:var(--muted)}
.step{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:24px}
.num{width:34px;height:34px;border-radius:50%;background:var(--p2);color:#111;font-weight:800;display:grid;place-items:center;margin-bottom:12px}
.src{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.src a{display:block;padding:14px 18px;border:1px solid var(--line);border-radius:14px;background:var(--card);text-decoration:none}
.src a:hover{border-color:var(--p1)}
.tw{display:grid;gap:12px;max-width:640px}
.tweet{display:flex;gap:12px;padding:16px;background:var(--card);border:1px solid var(--line);border-radius:16px}
.tweet p{margin:2px 0 0}.tweet small{color:var(--muted)}
details{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:2px 20px;margin:10px 0;max-width:760px}
summary{cursor:pointer;font-weight:600;padding:14px 0;list-style:none;display:flex;justify-content:space-between;gap:12px}
summary::-webkit-details-marker{display:none}
summary:after{content:"+";font-size:22px;line-height:1;color:var(--ey)}
details[open] summary:after{content:"\\2013"}
details p{margin:0 0 16px;color:var(--muted)}
.band{border-radius:28px;padding:56px 24px;margin:0 0 72px}
.band h2{margin:0 0 10px}.band p{margin:0 auto 24px;max-width:520px;opacity:.9}
footer{border-top:1px solid var(--line);padding:28px 0;color:var(--muted);font-size:14px;text-align:center}
a:focus-visible,summary:focus-visible{outline:3px solid var(--p2);outline-offset:3px}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.hero .wrap>*{animation:rise .7s ease both}.hero .wrap>*:nth-child(2){animation-delay:.08s}.hero .wrap>*:nth-child(3){animation-delay:.16s}.hero .wrap>*:nth-child(4){animation-delay:.24s}.hero .wrap>*:nth-child(5){animation-delay:.32s}
@media (max-width:640px){.links{display:none}.hero{padding:60px 0 70px}section{padding:52px 0}}
@media (prefers-reduced-motion: reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
</style></head><body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><symbol id="logo" viewBox="0 0 200 200">__LOGOINNER__</symbol></svg>
<nav aria-label="Main"><div class="wrap nav-in"><a class="brand" href="#top"><svg class="lg" viewBox="0 0 200 200" role="img" aria-label="__NAME__ logo"><use href="#logo"/></svg>__NAME__</a><div class="links"><a href="#features">Features</a><a href="#how">How it works</a><a href="#faq">FAQ</a></div><a class="btn sm" href="__CTAHREF__">__CTA__</a></div></nav>
<header class="hero" id="top"><div class="wrap"><div class="logo-big"><svg viewBox="0 0 200 200" role="img" aria-label="__NAME__ logo"><use href="#logo"/></svg></div><span class="pill">__TAGLINE__</span><h1>__HEADLINE__</h1><p class="sub">__SUBHEAD__</p><div class="actions"><a class="btn" href="__CTAHREF__">__CTA__</a><a class="btn ghost" href="#how">See how it works</a></div></div></header>
<main>
<section id="features"><div class="wrap"><div class="eyebrow">Why __NAME__</div><h2>What you get</h2><div class="grid3">__BENEFITS__</div></div></section>
<section id="how"><div class="wrap"><div class="eyebrow">How it works</div><h2>Three simple steps</h2><div class="grid3">__STEPS__</div></div></section>
__WHYNOW__
<section id="thread"><div class="wrap"><div class="eyebrow">Launch thread</div><h2>Follow the launch</h2><div class="tw">__THREAD__</div></div></section>
<section id="faq"><div class="wrap"><div class="eyebrow">FAQ</div><h2>Questions, answered</h2>__FAQ__</div></section>
<div class="wrap"><div class="band"><div class="wrap"><h2>Ready when you are</h2><p>__SUBHEAD__</p><a class="btn" href="__CTAHREF__">__CTA__</a></div></div></div>
</main>
<footer><div class="wrap">__NAME__ launch kit, generated and audited by Launch Kit Agent.</div></footer>
</body></html>"""


def build_page(name, topic, copy, svg, palette, tagline, signals, live, dest):
    e = htmllib.escape
    inner = re.sub(r"^<svg[^>]*>|</svg>$", "", svg)
    benefits = "".join(
        '<div class="card"><div class="icon"><svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS[i % 3]
        + "</svg></div><p>" + e(b) + "</p></div>" for i, b in enumerate(get_benefits(copy))
    )
    steps = "".join(
        '<div class="step"><div class="num">' + str(i + 1) + "</div><h3>" + e(t) + "</h3><p>" + e(b) + "</p></div>"
        for i, (t, b) in enumerate(get_steps(copy))
    )
    thread = "".join(
        '<div class="tweet"><svg class="lg" viewBox="0 0 200 200" aria-hidden="true"><use href="#logo"/></svg>'
        "<div><b>" + e(name) + "</b> <small>" + str(i + 1) + "/6</small><p>" + e(t) + "</p></div></div>"
        for i, t in enumerate(get_tweets(copy))
    )
    faq = "".join(
        "<details><summary>" + e(q) + "</summary><p>" + e(a) + "</p></details>" for q, a in get_faq(copy)
    )
    whynow = ""
    if live:
        rows = "".join('<li><a href="' + e(u, quote=True) + '">' + e(t[:140]) + "</a></li>" for t, u in signals[:4])
        whynow = ('<section id="why-now"><div class="wrap"><div class="eyebrow">Right now</div>'
                  '<h2>What people are talking about</h2><ul class="src">' + rows + "</ul></div></section>")
    subhead = field(copy, "SUBHEAD")
    values = {
        "__TITLE__": e(name + ": " + topic, quote=True), "__DESC__": e(subhead, quote=True),
        "__P0__": palette[0], "__P1__": palette[1], "__P2__": palette[2],
        "__LOGOINNER__": inner, "__NAME__": e(name), "__HEADLINE__": e(field(copy, "HEADLINE")),
        "__SUBHEAD__": e(subhead), "__CTAHREF__": e(dest or "#thread", quote=True), "__CTA__": e(field(copy, "CTA")),
        "__TAGLINE__": e(tagline), "__BENEFITS__": benefits, "__STEPS__": steps, "__WHYNOW__": whynow,
        "__THREAD__": thread, "__FAQ__": faq,
    }
    page = PAGE
    for k, v in values.items():
        page = page.replace(k, v)
    return page


# ---------- AUDIT ----------

def audit_copy(text):
    items = []
    ph = find_placeholder(text)
    items.append(("No placeholder text", not ph, "found '" + ph + "'" if ph else "none found"))
    for k in ("HEADLINE", "SUBHEAD", "CTA"):
        v = field(text, k)
        items.append((k.title() + " present", bool(v), v[:70] if v else "missing"))
    b = get_benefits(text)
    items.append(("Exactly 3 benefits", len(b) == 3, str(len(b)) + " found"))
    s = get_steps(text)
    items.append(("Exactly 3 how-it-works steps", len(s) == 3 and all(x[1] for x in s), str(len(s)) + " found"))
    f = get_faq(text)
    items.append(("Exactly 3 FAQ pairs", len(f) == 3, str(len(f)) + " found"))
    t = get_tweets(text)
    items.append(("Thread has exactly 6 tweets", len(t) == 6, str(len(t)) + " found"))
    over = [i + 1 for i, x in enumerate(t) if len(x) > 280]
    longest = max((len(x) for x in t), default=0)
    items.append(("Every tweet is 280 characters or fewer", bool(t) and not over,
                  ("over limit: " + str(over)) if over else ("longest is " + str(longest))))
    items.append(("Last tweet has a call to action", bool(t) and bool(CTA_WORDS.search(t[-1])),
                  t[-1][:70] if t else "no tweets"))
    return items


def audit_logo(svg, palette, tagline):
    items = []
    try:
        root = ET.fromstring(svg)
        items.append(("SVG parses as valid XML", True, "parsed"))
        items.append(("SVG has a viewBox", bool(root.get("viewBox")), "viewBox=" + str(root.get("viewBox"))))
    except ET.ParseError as e:
        items.append(("SVG parses as valid XML", False, str(e)[:70]))
    items.append(("SVG has no scripts or external images", not re.search(r"<script|<image|href=", svg, re.I), "checked"))
    ok = len(set(palette)) == 4 and all(HEX.fullmatch(c) for c in palette)
    items.append(("Palette has 4 hex colours", ok, str(len(set(palette))) + " found"))
    words = re.findall(r"[A-Za-z0-9'’\-]+", tagline)
    items.append(("Tagline is exactly 6 words", len(words) == 6, str(len(words)) + " words"))
    return items


class _Probe(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tags = set()

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag)


def audit_page(page, name):
    items = []
    probe = _Probe()
    try:
        probe.feed(page)
        parsed = True
    except Exception:  # noqa: BLE001
        parsed = False
    items.append(("Landing page parses as HTML", parsed, "parsed" if parsed else "parse error"))
    items.append(("Page has title, h1 and viewport", {"title", "h1", "meta"} <= probe.tags, "checked"))
    items.append(("Page has a meta description", 'name="description"' in page, "checked"))
    items.append(("Page has nav, how-it-works, FAQ and thread sections",
                  all(x in page for x in ("<nav", 'id="how"', 'id="faq"', 'id="thread"')), "checked"))
    items.append(("Page respects reduced-motion settings", "prefers-reduced-motion" in page, "checked"))
    items.append(("Page has no leftover template tokens", not re.search(r"__[A-Z0-9]+__", page), "checked"))
    items.append(("Page mentions the brand name", name.lower() in page.lower(), name))
    items.append(("Page has no scripts", "<script" not in page.lower(), "checked"))
    return items


def fmt(items):
    return "\n".join("- [" + ("PASS" if ok else "FAIL") + "] " + rule + ": " + ev for rule, ok, ev in items)


def failed(items):
    return [(r, e) for r, ok, e in items if not ok]


# ---------- PUBLISH (optional) ----------

def publish_gist(name, page, svg, thread_text):
    tok = os.getenv("GITHUB_TOKEN")
    if not tok:
        return "", "skipped (no GITHUB_TOKEN secret set)"
    try:
        r = requests.post(
            "https://api.github.com/gists",
            headers={"Authorization": "Bearer " + tok, "Accept": "application/vnd.github+json", "User-Agent": UA},
            json={"description": name + " launch kit (Launch Kit Agent)", "public": False,
                  "files": {"landing.html": {"content": page}, "logo.svg": {"content": svg},
                            "launch_thread.txt": {"content": thread_text}}},
            timeout=8,
        )
        if r.status_code >= 400:
            return "", "failed (HTTP " + str(r.status_code) + ")"
        return r.json().get("html_url", ""), "published"
    except Exception as e:  # noqa: BLE001
        return "", "failed (" + type(e).__name__ + ")"


# ---------- the job ----------

async def run_job(ctx, sender, g):
    t0 = time.time()
    deadline = t0 + JOB_TIME_LIMIT_S
    name, topic, tone, url = g["name"], g["topic"], g["tone"], g["url"]
    email = g.get("email", "")
    dest = url or (("mailto:" + email) if email else "")
    timings = {}
    ctx.logger.info("job start: " + topic + " | " + name + " | " + tone)

    await say(ctx, sender,
              "PLAN: Building a launch kit.\n- Product: " + topic + "\n- Brand name: " + name + "\n- Tone: " + tone
              + "\n- Button links to: " + (dest or "the launch thread (add a URL or email to change it)")
              + "\nPLAN: Steps: research, write, design, audit, build, publish.")

    # RESEARCH
    ts = time.time()
    signals, live, errors = await research(topic, url, t0 + 12)
    timings["research"] = round(time.time() - ts, 1)
    ctx.logger.info("step research done: live=" + str(live) + " errors=" + str(errors))
    rows = "\n".join("- " + t[:150] + "\n  " + u for t, u in signals)
    status = "live data" if live else "cached fallback (live lookups failed)"
    note = ("\nRESEARCH: some lookups failed: " + ", ".join(errors)) if errors else ""
    await say(ctx, sender, "RESEARCH: " + str(len(signals)) + " sources, " + status + ".\n" + rows + note)

    # WRITE + AUDIT + FIX
    ts = time.time()
    log, copy, source = [], None, "template"
    if os.getenv("ASI_API_KEY") and time.time() < deadline:
        raw, err = await blocking(llm_copy, name, topic, tone, signals)
        if raw is None:
            log.append("WRITE: LLM unavailable (" + err + "), using the audited template.")
        else:
            bad = failed(audit_copy(raw))
            if not bad:
                copy, source = raw, "LLM"
            else:
                log.append("AUDIT: LLM draft failed: " + "; ".join(r + " (" + e + ")" for r, e in bad))
                log.append("FIX: asking the writer to repair those issues (1 retry).")
                fb = "; ".join(r + ": " + e for r, e in bad)
                raw2, err2 = await blocking(llm_copy, name, topic, tone, signals, fb)
                if raw2 and not failed(audit_copy(raw2)):
                    copy, source = raw2, "LLM (repaired after audit)"
                    log.append("FIX: repaired draft passed the audit.")
                else:
                    log.append("FIX: retry still failed, switching to the audited template.")
    elif not os.getenv("ASI_API_KEY"):
        log.append("WRITE: no ASI_API_KEY secret set, using the audited template.")
    copy = copy or template_copy(name, topic, tone, signals)
    timings["write"] = round(time.time() - ts, 1)
    await say(ctx, sender, ("WRITE: copy ready via " + source + ".\n" + "\n".join(log)).strip())

    # DESIGN + BUILD
    svg, palette, tagline = make_logo(name, tone)
    page = build_page(name, topic, copy, svg, palette, tagline, signals, live, dest)
    await say(ctx, sender, "DESIGN: logo concept ready. Palette " + ", ".join(palette) + ". Tagline: " + tagline)

    # AUDIT everything
    results = audit_copy(copy) + audit_logo(svg, palette, tagline) + audit_page(page, name)
    bad = failed(results)
    total, passed = len(results), len(results) - len(bad)
    verdict = "PASS" if not bad else "FAIL"
    await say(ctx, sender, "AUDIT: " + verdict + " (" + str(passed) + "/" + str(total) + " checks)\n" + fmt(results))

    # PUBLISH
    thread_text = "\n".join(str(i + 1) + "/ " + t for i, t in enumerate(get_tweets(copy)))
    link, pub_status = ("", "skipped (time limit)")
    if time.time() < deadline + 10:
        link, pub_status = await blocking(publish_gist, name, page, svg, thread_text)

    # DELIVER
    benefits = "\n".join("- " + b for b in get_benefits(copy))
    await say(ctx, sender,
              "DELIVERABLE 1: Landing copy\nHEADLINE: " + field(copy, "HEADLINE") + "\nSUBHEAD: " + field(copy, "SUBHEAD")
              + "\nBENEFITS:\n" + benefits + "\nCTA: " + field(copy, "CTA")
              + "\n\nDELIVERABLE 2: Launch thread\n" + thread_text)
    await say(ctx, sender, "DELIVERABLE 3: Logo (save as logo.svg)\n```svg\n" + svg + "\n```")
    await say(ctx, sender,
              "DELIVERABLE 4: Landing page (save as index.html and open it in a browser)\n```html\n" + page + "\n```")
    elapsed = round(time.time() - t0, 1)
    tip = "" if dest else "\nTip: add a URL or 'email: you@example.com' next time so the page button goes somewhere real."
    await say(ctx, sender,
              "PUBLISH: " + pub_status + ("\nLINK: " + link if link else "") + "\n\n"
              + "RECEIPT: research " + ("live" if live else "cached") + " (" + str(timings["research"]) + "s) | copy via "
              + source + " (" + str(timings["write"]) + "s) | audit " + str(passed) + "/" + str(total) + " " + verdict
              + " | total " + str(elapsed) + "s" + tip
              + "\nWant a different feel? Say 'make it bold' or 'rename it to <name>', or tell me about another idea.")
    store_set(ctx, "last:" + sender, {"name": name, "topic": topic, "tone": tone, "url": url, "email": email})
    hist = store_get(ctx, "chat:" + sender, [])
    hist.append({"role": "assistant", "content": "I built a launch kit for " + name + " (" + topic + ", " + tone + " tone)."})
    store_set(ctx, "chat:" + sender, hist[-6:])
    ctx.logger.info("job done in " + str(elapsed) + "s verdict=" + verdict)


# ---------- chat ----------

def rule_reply(text, last):
    if WHO.search(text):
        return ABOUT
    if HOWARE.search(text):
        return ("Doing well, thanks for asking! Always happy when someone brings me a new idea. "
                "What are you working on or thinking about launching?")
    if GREET.search(text):
        return ("Hey, nice to meet you! I'm the " + NAME + ". I can chat, and I can also turn an idea into a "
                "full launch kit: research, copy, a tweet thread, a logo and a landing page. What are you building?")
    if THANKS.search(text):
        return "Anytime! " + ("Want me to restyle your kit? Try 'make it bold' or 'make it playful'." if last
                              else "If you have an idea, tell me about it and I'll build the launch kit.")
    if BYE.search(text):
        return "Take care! Come back any time you have an idea to launch."
    return ("Happy to chat. I'm especially good at launch kits, so if you tell me what you're building in a "
            "sentence, I'll research it, write the copy and thread, design a logo and build the landing page. "
            "Or ask me what I can do.")


async def chat_reply(ctx, sender, text, last):
    words = len(text.split())
    if IDEA_HINT.search(text) and not (PRODUCT_HINT.search(text) and words >= 6):
        store_set(ctx, "pending:" + sender, {"kind": "ask"})
        return ("Love that. What are you building? One sentence is enough, and you can add a name "
                "('called Zoomly'), a tone (friendly, bold, playful, professional), a URL or an email.")
    if PRODUCT_HINT.search(text) and words >= 5 and "?" not in text:
        store_set(ctx, "pending:" + sender, {"kind": "confirm", "text": text})
        return ("That sounds like something I can build a launch kit for. Want me to run with it? "
                "Reply yes to start, or tell me more (a name, a tone, a URL or an email).")
    if os.getenv("ASI_API_KEY"):
        hist = store_get(ctx, "chat:" + sender, [])
        system = CHAT_SYSTEM
        if last:
            system += (" The user's last launch kit was for " + last.get("name", "their product") + ", a "
                       + last.get("topic", "product") + ", in a " + last.get("tone", "friendly") + " tone.")
        msgs = [{"role": "system", "content": system}] + hist[-6:] + [{"role": "user", "content": text[:600]}]
        out, err = await blocking(llm_messages, msgs, 300, 0.7, 12)
        if out:
            hist = hist + [{"role": "user", "content": text[:300]}, {"role": "assistant", "content": out[:300]}]
            store_set(ctx, "chat:" + sender, hist[-6:])
            return out
        ctx.logger.error("chat LLM unavailable: " + err)
    return rule_reply(text, last)


# ---------- diagnostics ----------

async def run_diag(ctx, sender):
    lines = []
    try:
        import importlib.metadata as md
        ver = md.version("uagents")
    except Exception:  # noqa: BLE001
        ver = "unknown"
    lines.append("DIAG: python " + sys.version.split()[0] + " | uagents " + ver)
    try:
        ctx.storage.set("diag:test", "ok")
        lines.append("DIAG: storage " + ("OK" if ctx.storage.get("diag:test") == "ok" else "FAIL (read-back mismatch)"))
    except Exception as e:  # noqa: BLE001
        lines.append("DIAG: storage FAIL (" + type(e).__name__ + ")")
    for label, fn, arg in (("Hacker News API", hn_search, "todo app"), ("Wikipedia API", wiki_search, "todo app")):
        try:
            n = len(await blocking(fn, arg))
            lines.append("DIAG: " + label + " OK (" + str(n) + " results)")
        except Exception as e:  # noqa: BLE001
            lines.append("DIAG: " + label + " FAIL (" + type(e).__name__ + ")")
    if os.getenv("ASI_API_KEY"):
        out, err = await blocking(llm_chat, "Reply with the single word OK.", "ping", 5, 0, 10)
        lines.append("DIAG: LLM model '" + ASI_MODEL + "' " + ("OK" if out is not None else "FAIL (" + err + ")"))
    else:
        lines.append("DIAG: ASI_API_KEY not set (built-in chat replies and template copy will be used)")
    tok = os.getenv("GITHUB_TOKEN")
    if tok:
        try:
            r = await blocking(lambda: requests.get(
                "https://api.github.com/user",
                headers={"Authorization": "Bearer " + tok, "User-Agent": UA}, timeout=6))
            scopes = r.headers.get("X-OAuth-Scopes", "(none listed)")
            lines.append("DIAG: GitHub token " + ("valid" if r.status_code == 200 else "INVALID (HTTP " + str(r.status_code) + ")")
                         + " | scopes: " + scopes)
        except Exception as e:  # noqa: BLE001
            lines.append("DIAG: GitHub FAIL (" + type(e).__name__ + ")")
    else:
        lines.append("DIAG: GITHUB_TOKEN not set (publish step will be skipped)")
    await say(ctx, sender, "\n".join(lines))


# ---------- chat protocol ----------

@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, m: ChatMessage):
    try:
        await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=m.msg_id))
    except Exception as e:  # noqa: BLE001
        ctx.logger.error("ack failed: " + type(e).__name__)
    for item in m.content:
        if isinstance(item, StartSessionContent):
            await say(ctx, sender, ABOUT)
            continue
        if not isinstance(item, TextContent):
            continue
        text = item.text.strip()
        if not text:
            continue
        ctx.logger.info("message: " + text[:100])
        try:
            if re.fullmatch(r"/?(diag|diagnostics|status|health)", text.lower()):
                await run_diag(ctx, sender)
                continue

            last = store_get(ctx, "last:" + sender, None)
            pend = store_get(ctx, "pending:" + sender, {})
            if pend and pend.get("kind"):
                store_set(ctx, "pending:" + sender, {})
                if pend["kind"] == "ask":
                    if NO.search(text):
                        await say(ctx, sender, "No problem. Whenever you're ready, just tell me what you're building.")
                    else:
                        await run_job(ctx, sender, parse_goal(text))
                    continue
                if pend["kind"] == "confirm":
                    if YES.search(text):
                        await run_job(ctx, sender, parse_goal(pend.get("text", text)))
                        continue
                    if NO.search(text):
                        await say(ctx, sender, "No worries. Tell me more about it whenever you like, or ask me anything.")
                        continue

            follow = parse_followup(text, last)
            if follow:
                await run_job(ctx, sender, follow)
                continue
            if is_goal(text):
                await run_job(ctx, sender, parse_goal(text))
                continue
            await say(ctx, sender, await chat_reply(ctx, sender, text, last))
        except Exception as e:  # noqa: BLE001
            ctx.logger.error("job failed: " + traceback.format_exc()[-600:])
            await say(ctx, sender,
                      "ERROR: " + type(e).__name__ + ": " + str(e)[:150] + "\n"
                      "Send  diag  for a health check, or try a one-sentence idea such as: "
                      "Launch my travel planning app called Wanderly. Tone: playful.")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, m: ChatAcknowledgement):
    ctx.logger.info("ack from " + sender)


agent.include(chat_proto, publish_manifest=True)


@agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info(NAME + " v3 online. Address: " + str(ctx.agent.address))


if __name__ == "__main__":
    agent.run()
