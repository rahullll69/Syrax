"""
Intelligent Intent Parser and Entity Extractor.
Classifies user requests into modular actions (chat, logo, website, research, seo, reddit, workflow, full kit, revise).
"""

import re
from typing import Any, Dict, Optional

import config

# Intent Constants
INTENT_CHAT = "chat"
INTENT_LOGO = "generate_logo"
INTENT_WEBSITE = "generate_website"
INTENT_RESEARCH = "research"
INTENT_SEO = "seo_marketing"
INTENT_REDDIT = "reddit_bot"
INTENT_WORKFLOW = "workflow"
INTENT_FULL_KIT = "full_kit"
INTENT_REVISE = "revise"
INTENT_DIAG = "diag"

# Regex Patterns for Intents
PATTERNS = {
    INTENT_DIAG: re.compile(r"^\s*/?(diag|diagnostics|status|health)\b", re.I),
    INTENT_LOGO: re.compile(
        r"\b(only\s+(?:the\s+)?logo|just\s+(?:the\s+)?logo|create\s+(?:a\s+|the\s+)?logo|generate\s+(?:a\s+|the\s+)?logo|make\s+(?:a\s+|the\s+)?logo|design\s+(?:a\s+|the\s+)?logo|new\s+logo|svg\s+logo|another\s+logo)\b",
        re.I,
    ),
    INTENT_WEBSITE: re.compile(
        r"\b(only\s+(?:the\s+)?(?:website|landing\s*page|web\s*page|site)|just\s+(?:the\s+)?(?:website|landing\s*page|web\s*page|site)|"
        r"(?:create|generate|make|build|design|code)\s+(?:a\s+|the\s+)?(?:website|landing\s*page|web\s*page|html|site)|"
        r"new\s+(?:website|landing\s*page))\b",
        re.I,
    ),
    INTENT_RESEARCH: re.compile(
        r"\b(competitors?|competitor\s+(?:research|analysis)|market\s+research|who\s+are\s+my\s+competitors|research\s+(?:the\s+)?(?:market|product|space)|stand\s+out|differentiat\w+)\b",
        re.I,
    ),
    INTENT_SEO: re.compile(
        r"\b(seo|meta\s+tags|keywords|schema(?:\.org)?|search\s+engine\s+optimiz\w+)\b",
        re.I,
    ),
    INTENT_REDDIT: re.compile(
        r"\b(reddit\s+bots?|reddit\s+promo(?:tion)?|promote\s+on\s+reddit|reddit\s+marketing|social\s+bots?)\b",
        re.I,
    ),
    INTENT_WORKFLOW: re.compile(
        r"\b(workflow(?:\.md)?|roadmap|continuation|product\s+plan|future\s+steps|how\s+the\s+product\s+can\s+be\s+continued)\b",
        re.I,
    ),
    INTENT_FULL_KIT: re.compile(
        r"\b(launch\s+(?:my|our|a|the)?|build\s+(?:a\s+|the\s+)?(?:full\s+)?launch\s*kit|create\s+(?:a\s+|the\s+)?(?:full\s+)?launch\s*kit|launch\s+kit|everything)\b",
        re.I,
    ),
    INTENT_REVISE: re.compile(
        r"\b(didn'?t\s+like|don'?t\s+like|hate|change|restyle|redo|re-?generate|switch|another\s+one|different\s+one|"
        r"make\s+(?:it|the\s+website|the\s+site|the\s+logo|the\s+page)?\s*(?:bold|playful|professional|friendly|futuristic|dark|minimal|cyber|neobrutal|clean|editorial|luxury|glass)|"
        r"rename\s+(?:it\s+)?to)\b",
        re.I,
    ),
}

# Conversational Greetings & Casual Prompts
GREETINGS = re.compile(r"^\s*(hi+|hello+|hey+|yo|hola|greetings|sup|good\s+(morning|afternoon|evening))\b", re.I)
CASUAL_QUESTIONS = re.compile(
    r"\b(who\s+are\s+you|what\s+can\s+you\s+do|how\s+do\s+you\s+work|help\s+me|tell\s+me\s+about\s+yourself|what\s+is\s+this)\b|^\s*help\s*[?!.]*\s*$",
    re.I,
)


def extract_entities(text: str, previous_product: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract product metadata (name, topic, tone, url, email, archetype, feedback) from text."""
    prev = previous_product or {}

    url_m = re.search(r"https?://[^\s<>\"']+", text)
    url = url_m.group(0).rstrip(".,)") if url_m else prev.get("url", "")

    email_m = re.search(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+", text)
    email = email_m.group(0).rstrip(".,") if email_m else prev.get("email", "")

    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"[\w.+\-]+@[\w\-]+\.[\w.\-]+", "", clean)

    # Name extraction
    name_m = (
        re.search(r"(?:called|named|name\s*[:=]|brand\s*[:=]|rename(?:\s+it)?\s+to)\s*[\"']?([A-Za-z0-9\-_]{2,30})", clean, re.I)
        or re.search(r"\bfor\s+[\"']?([A-Z][A-Za-z0-9\-_]{1,25})[\"']?", clean)
    )
    name = name_m.group(1).strip() if name_m else prev.get("name", "")

    # Tone extraction
    tone = prev.get("tone", "bold")
    for t in config.TONES:
        if re.search(r"\b" + t + r"\b", clean, re.I):
            tone = t
            break

    # Design Archetype extraction
    archetype = prev.get("archetype", None)
    if re.search(r"\b(cyber|dark\s*mode|glow|futuristic|matrix|dark)\b", clean, re.I):
        archetype = "dark_cyber"
    elif re.search(r"\b(minimal|clean|stripe|linear|simple)\b", clean, re.I):
        archetype = "saas_minimal"
    elif re.search(r"\b(neobrutal|brutalism|bold\s*borders?|gumroad)\b", clean, re.I):
        archetype = "neobrutalism"
    elif re.search(r"\b(editorial|luxury|serif|notion|substack)\b", clean, re.I):
        archetype = "editorial_luxury"
    elif re.search(r"\b(glass|mesh|gradient|arc|modern\s*app)\b", clean, re.I):
        archetype = "gradient_glass"

    # Topic extraction
    topic_m = (
        re.search(r"(?:launch|building|making|creating|product\s+called|product|startup|app|tool|service)\s+(?:for|about)?\s*([^.,:;\n]{3,80})", clean, re.I)
        or re.search(r"(?:for|about)\s+([^.,:;\n]{3,80})", clean, re.I)
    )
    topic = ""
    if topic_m:
        topic = topic_m.group(1).strip()
        topic = re.sub(r"\s+(?:called|named)\s+.*$", "", topic, flags=re.I)
        topic = re.sub(r"\s*\btone\s*([:=].*)?$", "", topic, flags=re.I)
        topic = re.sub(r"^(?:a|an|my|our|the)\s+", "", topic, flags=re.I).strip()
    if not topic:
        topic = prev.get("topic", "")
    if not topic and name:
        topic = f"{name} product"

    if not name and topic:
        words = topic.split()
        if len(words) <= 3:
            name = topic.title()
        else:
            name = words[0].title()

    return {
        "name": name or "NovaLaunch",
        "topic": topic or "autonomous digital product",
        "tone": tone,
        "archetype": archetype,
        "url": url,
        "email": email,
        "feedback": text.strip(),
    }


def parse_intent(text: str, previous_product: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Parse user message into structured intent and entities."""
    text_clean = text.strip()

    # Diagnostics check
    if PATTERNS[INTENT_DIAG].search(text_clean):
        return {"intent": INTENT_DIAG, "entities": {}}

    # Revision / Improvisation check (e.g., "i didn't like the logo", "change to dark mode")
    if PATTERNS[INTENT_REVISE].search(text_clean) and previous_product:
        target = "general"
        if re.search(r"\b(logo|symbol|icon|svg|palette)\b", text_clean, re.I):
            target = "logo"
        elif re.search(r"\b(website|landing|page|interface|ui|design|dark|theme|layout)\b", text_clean, re.I):
            target = "website"
        elif re.search(r"\b(copy|headline|tagline|text|tweets?|words)\b", text_clean, re.I):
            target = "copy"
        elif re.search(r"\b(tone|vibe|feel)\b", text_clean, re.I):
            target = "tone"
        elif re.search(r"\b(rename|name|call\s+it)\b", text_clean, re.I):
            target = "name"

        entities = extract_entities(text_clean, previous_product)
        entities["target_asset"] = target
        return {"intent": INTENT_REVISE, "entities": entities}

    # Specific modular intents
    if PATTERNS[INTENT_LOGO].search(text_clean):
        return {"intent": INTENT_LOGO, "entities": extract_entities(text_clean, previous_product)}

    if PATTERNS[INTENT_WEBSITE].search(text_clean):
        return {"intent": INTENT_WEBSITE, "entities": extract_entities(text_clean, previous_product)}

    if PATTERNS[INTENT_RESEARCH].search(text_clean):
        return {"intent": INTENT_RESEARCH, "entities": extract_entities(text_clean, previous_product)}

    if PATTERNS[INTENT_REDDIT].search(text_clean):
        return {"intent": INTENT_REDDIT, "entities": extract_entities(text_clean, previous_product)}

    if PATTERNS[INTENT_SEO].search(text_clean):
        return {"intent": INTENT_SEO, "entities": extract_entities(text_clean, previous_product)}

    if PATTERNS[INTENT_WORKFLOW].search(text_clean):
        return {"intent": INTENT_WORKFLOW, "entities": extract_entities(text_clean, previous_product)}

    # Full kit explicit launch
    if PATTERNS[INTENT_FULL_KIT].search(text_clean):
        return {"intent": INTENT_FULL_KIT, "entities": extract_entities(text_clean, previous_product)}

    # Greetings / Casual Q&A
    if GREETINGS.search(text_clean) or CASUAL_QUESTIONS.search(text_clean):
        return {"intent": INTENT_CHAT, "entities": extract_entities(text_clean, previous_product)}

    # If message is short (under 4 words) and doesn't match a goal, treat as casual conversation
    if len(text_clean.split()) < 4 and not re.search(r"\b(launch|build|create|generate|make)\b", text_clean, re.I):
        return {"intent": INTENT_CHAT, "entities": extract_entities(text_clean, previous_product)}

    # If user describes a product ("I am building an AI note taker...")
    if re.search(r"\b(building|working on|making|started|created|product\s+is|idea\s+for)\b", text_clean, re.I):
        return {"intent": INTENT_CHAT, "entities": extract_entities(text_clean, previous_product), "has_product_pitch": True}

    # Default to chat
    return {"intent": INTENT_CHAT, "entities": extract_entities(text_clean, previous_product)}
