"""
Configuration, constants, prompts, and design tokens for Launch Kit Agent.
"""

import os

NAME = "Launch Kit AI Agent"
VERSION = "5.0.0"
UA = "LaunchKitAgent/5.0 (Autonomous Startup Co-Pilot & Launch Engine; +https://agentverse.ai)"

# LLM Configuration (ASI-1 / OpenAI compatible)
def get_asi_base_url() -> str:
    base = os.getenv("ASI1_BASE_URL", "").rstrip("/")
    if base:
        return f"{base}/chat/completions" if not base.endswith("/chat/completions") else base
    return os.getenv("ASI_URL", "https://api.asi1.ai/v1/chat/completions")

ASI_URL = get_asi_base_url()
ASI_MODEL = os.getenv("ASI_MODEL", "asi1")

# Design Archetypes for Websites
ARCHETYPES = [
    "dark_cyber",        # Glowing gradients, dark mode, terminal cards
    "saas_minimal",      # Clean Stripe/Linear aesthetic
    "neobrutalism",      # Bold black borders, hard drop shadows, playful badges
    "gradient_glass",    # Glassmorphism, smooth mesh gradients, pill elements
    "editorial_luxury",  # Warm slate, serif typography, elegant layout
]

# Free Data & Search APIs (Zero API key required)
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
DDG_INSTANT_URL = "https://api.duckduckgo.com/"
REDDIT_SEARCH_URL = "https://www.reddit.com/search.json"

# Limits & Timeouts
HTTP_TIMEOUT = 5
JOB_TIME_LIMIT_S = 60

# Curated Color Palettes (Dark, Primary, Accent, Light)
PALETTES = {
    "electric_violet": ["#0f172a", "#6366f1", "#a855f7", "#ffffff"],
    "cyber_emerald": ["#061a14", "#10b981", "#34d399", "#ffffff"],
    "solar_flare": ["#18181b", "#f97316", "#facc15", "#ffffff"],
    "ocean_pulse": ["#0c1a2e", "#0ea5e9", "#38bdf8", "#ffffff"],
    "crimson_neo": ["#1c0c11", "#e11d48", "#fb7185", "#ffffff"],
    "pure_minimal": ["#111827", "#4b5563", "#9ca3af", "#ffffff"],
    "neobrutal_yellow": ["#18181b", "#facc15", "#fb7185", "#ffffff"],
}

# Tones
TONES = {
    "bold": {
        "subhead": "No fluff. High-converting impact that commands the market.",
        "tagline": "Move fast, launch bold, dominate market",
        "vibe": "high-impact, aggressive, clear value proposition",
    },
    "playful": {
        "subhead": "Delightfully easy, addictive to use, and built to love.",
        "tagline": "Remarkably fun, refreshingly simple to use",
        "vibe": "fun, warm, engaging, conversational",
    },
    "professional": {
        "subhead": "Engineered for high performance, rock-solid stability, and mission-critical workflows.",
        "tagline": "Built for scale, engineered for reliability",
        "vibe": "authoritative, trustworthy, enterprise-grade",
    },
    "friendly": {
        "subhead": "The human-first product designed to get out of your way and make life easier.",
        "tagline": "Simple to start, effortless to master",
        "vibe": "approachable, warm, helpful, transparent",
    },
    "futuristic": {
        "subhead": "The next-generation intelligence platform redefining what's possible.",
        "tagline": "Step into the autonomous future today",
        "vibe": "bleeding-edge, AI-native, visionary, cybernetic",
    },
    "minimalist": {
        "subhead": "Zero clutter. Pure focus. Everything you need, nothing you don't.",
        "tagline": "Clarity in thought, precision in execution",
        "vibe": "clean, refined, distraction-free, elegant",
    },
}

# Conversational System Prompt
CHAT_SYSTEM_PROMPT = f"""You are {NAME}, an elite startup co-pilot and product launcher running on Agentverse and ASI-1.
You chat naturally, intelligently, and empathetically with founders and builders about their startup ideas, products, tech stacks, and growth strategies.
When they want concrete deliverables, you can build them on demand:
- Live Competitor Research & Market Differentiation
- Unique SVG Logos & Brand Palettes
- Dynamic Multi-Interface Landing Pages (Dark Cyber, SaaS Minimal, Neo-Brutalism, Gradient Glass, Editorial Luxury)
- SEO Metadata Packages & Automated Reddit Promotion Bots
- Complete WORKFLOW.md Product Continuation Roadmaps
- Full Launch Kits

Be concise, witty, actionable, and encouraging. Never output boring audit checklists or boilerplate apologies."""
