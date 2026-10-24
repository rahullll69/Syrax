"""
Dynamic Multi-Interface Landing Page Generator.
Provides multiple distinct design architectures (Dark Cyber AI, Minimalist SaaS, Neo-Brutalism, Gradient Glass, Editorial Luxury)
so every generated website features a completely unique aesthetic, layout, and visual identity.
"""

import html as htmllib
import json
import logging
import random
import re
from typing import Any, Dict, List, Optional

import config
import llm_client

logger = logging.getLogger("launchkit.website")


def get_copy_data(name: str, topic: str, tone: str, differentiation: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """Generate or synthesize copy data tailored to the product."""
    diff_text = ""
    if differentiation:
        diff_text = "\nKey Differentiators:\n" + "\n".join([f"- {d['pillar']}: {d['action']}" for d in differentiation])

    if llm_client.is_available():
        prompt = f"""
You are a world-class landing page copywriter.
Brand: {name}
Product Description: {topic}
Tone: {tone}
{diff_text}

Generate high-converting landing page copy in valid JSON format:
{{
  "headline": "Punchy, modern headline (under 12 words)",
  "subhead": "Persuasive subhead detailing the core benefit (under 25 words)",
  "cta": "Primary CTA button text (2-4 words)",
  "benefits": [
    {{"title": "Benefit 1 Title", "desc": "Compelling explanation of how this solves a real problem."}},
    {{"title": "Benefit 2 Title", "desc": "Compelling explanation of speed, intelligence or ease."}},
    {{"title": "Benefit 3 Title", "desc": "Compelling explanation of competitive superiority."}}
  ],
  "steps": [
    {{"num": "1", "title": "Connect & Onboard", "desc": "Get setup in under 60 seconds with zero friction."}},
    {{"num": "2", "title": "Activate Intelligence", "desc": "{name} automatically configures your optimized workflow."}},
    {{"num": "3", "title": "Scale Results", "desc": "Sit back and watch high-leverage outcomes compound daily."}}
  ],
  "faqs": [
    {{"q": "How does {name} compare to legacy solutions?", "a": "{name} removes complex manual overhead and delivers instant, automated results at a fraction of the cost."}},
    {{"q": "Is there a free trial or early access?", "a": "Yes, our early access waitlist includes full access to premium capabilities with priority onboarding."}},
    {{"q": "How fast can I get started?", "a": "Under two minutes. No complex installations or custom coding required."}}
  ]
}}
Output ONLY valid JSON.
"""
        res, _ = llm_client.single_prompt("You are an elite copywriter. Output valid JSON only.", prompt, max_tokens=1000)
        if res:
            try:
                clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", res, flags=re.M).strip()
                return json.loads(clean_json)
            except Exception as e:
                logger.warning(f"Failed to parse LLM copy JSON: {e}")

    # Fallback high quality template copy
    tone_info = config.TONES.get(tone, config.TONES["bold"])
    return {
        "headline": f"{name}: The next-generation {topic} engineered to win.",
        "subhead": tone_info["subhead"],
        "cta": f"Get Early Access to {name}",
        "benefits": [
            {"title": "Instant Time-to-Value", "desc": f"Skip weeks of manual setup. {name} activates your full {topic} stack in minutes."},
            {"title": "Autonomous Execution", "desc": "Powered by modern agentic automation that handles the heavy lifting while you focus on high-leverage work."},
            {"title": "Unrivaled Competitive Edge", "desc": "Engineered with market intelligence to keep you ahead of legacy competitors."},
        ],
        "steps": [
            {"num": "1", "title": "Connect Your Workspace", "desc": "Zero complex configuration. Jump in with one click."},
            {"num": "2", "title": "Launch the Engine", "desc": f"Let {name} analyze, optimize, and execute your target workflows."},
            {"num": "3", "title": "Compound Results", "desc": "Gain real-time momentum and monitor high-converting outcomes effortlessly."},
        ],
        "faqs": [
            {"q": f"What makes {name} stand out?", "a": f"Unlike bulky legacy software, {name} is built from the ground up to be lightweight, lightning fast, and natively intelligent."},
            {"q": "Who is this designed for?", "a": "Founders, builders, and modern teams who refuse to waste hours on repetitive manual workflows."},
            {"q": "How do I claim early access?", "a": "Click the CTA button on this page to lock in your priority spot before public rollout."},
        ],
    }


# =====================================================================
# 1. ARCHETYPE: DARK CYBER AI (Futuristic Neon / OpenAI / Vercel style)
# =====================================================================
def render_dark_cyber(name: str, topic: str, copy: Dict[str, Any], logo_svg: str, palette: List[str], dest: str) -> str:
    e = htmllib.escape
    p_primary = palette[1] if len(palette) > 1 else "#06b6d4"
    p_secondary = palette[2] if len(palette) > 2 else "#8b5cf6"

    benefits_html = "\n".join([
        f"""<div class="cyber-card">
            <div class="glow-orb"></div>
            <h3>{e(b['title'])}</h3>
            <p>{e(b['desc'])}</p>
        </div>""" for b in copy.get("benefits", [])
    ])

    steps_html = "\n".join([
        f"""<div class="step-card">
            <div class="step-badge">{e(s['num'])}</div>
            <div>
                <h4>{e(s['title'])}</h4>
                <p>{e(s['desc'])}</p>
            </div>
        </div>""" for s in copy.get("steps", [])
    ])

    faq_html = "\n".join([
        f"""<details class="cyber-faq"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>"""
        for f in copy.get("faqs", [])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — Next-Gen {e(topic)}</title>
<style>
:root {{
    --bg: #07090e;
    --card-bg: rgba(15, 23, 42, 0.65);
    --border: rgba(56, 189, 248, 0.18);
    --text: #f8fafc;
    --muted: #94a3b8;
    --p1: {p_primary};
    --p2: {p_secondary};
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "JetBrains Mono", monospace;
    line-height: 1.6;
    overflow-x: hidden;
    background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.12) 0%, transparent 60%);
}}
.container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}
header.nav {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 0; border-bottom: 1px solid var(--border);
    backdrop-filter: blur(12px); position: sticky; top: 0; z-index: 50;
}}
.brand {{ display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 1.25rem; letter-spacing: -0.02em; }}
.brand svg {{ width: 36px; height: 36px; }}
.btn {{
    background: linear-gradient(135deg, var(--p1), var(--p2));
    color: #fff; padding: 12px 28px; border-radius: 8px; text-decoration: none;
    font-weight: 700; font-size: 0.95rem; border: none; cursor: pointer;
    box-shadow: 0 0 20px rgba(6, 182, 212, 0.35); transition: transform 0.2s, box-shadow 0.2s;
    display: inline-block;
}}
.btn:hover {{ transform: translateY(-2px); box-shadow: 0 0 30px rgba(139, 92, 246, 0.5); }}
.hero {{ padding: 100px 0 80px; text-align: center; }}
.badge {{
    display: inline-block; padding: 6px 16px; border-radius: 999px;
    background: rgba(6, 182, 212, 0.1); border: 1px solid var(--p1);
    color: var(--p1); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 24px;
}}
h1 {{
    font-size: clamp(2.5rem, 6vw, 4.2rem); font-weight: 900; line-height: 1.1;
    margin-bottom: 24px; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 40%, var(--p1)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}}
p.sub {{ font-size: 1.25rem; color: var(--muted); max-width: 680px; margin: 0 auto 36px; }}
.cyber-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin: 60px 0; }}
.cyber-card {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
    padding: 32px; backdrop-filter: blur(10px); position: relative; overflow: hidden;
    transition: border-color 0.3s, transform 0.3s;
}}
.cyber-card:hover {{ border-color: var(--p1); transform: translateY(-4px); }}
.cyber-card h3 {{ font-size: 1.4rem; margin-bottom: 12px; color: #fff; }}
.cyber-card p {{ color: var(--muted); font-size: 0.95rem; }}
.terminal-block {{
    background: #030712; border: 1px solid var(--border); border-radius: 12px;
    padding: 24px; font-family: monospace; font-size: 0.9rem; color: #38bdf8;
    max-width: 700px; margin: 40px auto; text-align: left; box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}}
.step-grid {{ display: grid; gap: 16px; max-width: 720px; margin: 40px auto; }}
.step-card {{
    display: flex; gap: 20px; align-items: flex-start; background: var(--card-bg);
    border: 1px solid var(--border); padding: 20px; border-radius: 12px;
}}
.step-badge {{
    width: 36px; height: 36px; border-radius: 8px; background: var(--p1); color: #000;
    font-weight: 800; display: grid; place-items: center; flex-shrink: 0;
}}
.cyber-faq {{
    background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px;
    padding: 16px 20px; margin-bottom: 12px; cursor: pointer; text-align: left;
}}
.cyber-faq summary {{ font-weight: 600; font-size: 1.05rem; outline: none; }}
.cyber-faq p {{ margin-top: 10px; color: var(--muted); }}
footer {{ text-align: center; padding: 50px 0; color: var(--muted); font-size: 0.9rem; border-top: 1px solid var(--border); }}
</style>
</head>
<body>
<div class="container">
    <header class="nav">
        <div class="brand">
            {logo_svg}
            <span>{e(name)}</span>
        </div>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta', 'Get Started'))}</a>
    </header>

    <section class="hero">
        <span class="badge">Next-Generation Autonomous Tech</span>
        <h1>{e(copy.get('headline'))}</h1>
        <p class="sub">{e(copy.get('subhead'))}</p>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>

        <div class="terminal-block">
            <span style="color: #64748b">// Initialize {e(name)} Autonomous Engine</span><br>
            &gt; npx launch-{e(name.lower())} --mode=autonomous<br>
            <span style="color: #34d399">✔ Connected to live intelligence nodes</span><br>
            <span style="color: #34d399">✔ Zero latency execution pipeline primed</span>
        </div>
    </section>

    <section style="padding: 60px 0;">
        <h2 style="text-align: center; font-size: 2.2rem; margin-bottom: 16px;">Engineered to Outperform</h2>
        <div class="cyber-grid">{benefits_html}</div>
    </section>

    <section style="padding: 40px 0; text-align: center;">
        <h2 style="font-size: 2.2rem; margin-bottom: 16px;">How It Works</h2>
        <div class="step-grid">{steps_html}</div>
    </section>

    <section style="padding: 60px 0; max-width: 760px; margin: 0 auto;" id="faq">
        <h2 style="text-align: center; font-size: 2.2rem; margin-bottom: 30px;">Frequently Answered</h2>
        {faq_html}
    </section>

    <section style="padding: 80px 0; text-align: center;" id="cta">
        <div style="background: linear-gradient(180deg, rgba(15,23,42,0.8), rgba(6,182,212,0.1)); border: 1px solid var(--p1); border-radius: 24px; padding: 60px 24px;">
            <h2 style="font-size: 2.5rem; margin-bottom: 16px;">Ready to Command the Market?</h2>
            <p style="color: var(--muted); margin-bottom: 30px;">Join progressive leaders deploying {e(name)} today.</p>
            <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
        </div>
    </section>

    <footer>
        <p>© 2026 {e(name)}. All rights reserved. Powered by Autonomous Agentverse.</p>
    </footer>
</div>
</body>
</html>"""


# =====================================================================
# 2. ARCHETYPE: SAAS MINIMAL (Stripe / Linear Crisp Clean B2B style)
# =====================================================================
def render_saas_minimal(name: str, topic: str, copy: Dict[str, Any], logo_svg: str, palette: List[str], dest: str) -> str:
    e = htmllib.escape
    accent = palette[1] if len(palette) > 1 else "#4f46e5"

    benefits_html = "\n".join([
        f"""<div class="clean-box">
            <h3>{e(b['title'])}</h3>
            <p>{e(b['desc'])}</p>
        </div>""" for b in copy.get("benefits", [])
    ])

    steps_html = "\n".join([
        f"""<div class="clean-step">
            <span class="step-circle">{e(s['num'])}</span>
            <h4>{e(s['title'])}</h4>
            <p>{e(s['desc'])}</p>
        </div>""" for s in copy.get("steps", [])
    ])

    faq_html = "\n".join([
        f"""<details class="clean-faq"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>"""
        for f in copy.get("faqs", [])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — {e(topic)}</title>
<style>
:root {{
    --bg: #ffffff;
    --text: #0f172a;
    --muted: #475569;
    --line: #e2e8f0;
    --accent: {accent};
    --accent-light: #eef2ff;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
    line-height: 1.6;
}}
.wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 20px; }}
nav {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 0; border-bottom: 1px solid var(--line);
}}
.brand {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 1.2rem; }}
.brand svg {{ width: 32px; height: 32px; }}
.btn {{
    background: var(--accent); color: #fff; padding: 12px 24px;
    border-radius: 6px; font-weight: 600; text-decoration: none; display: inline-block;
    transition: background 0.2s;
}}
.btn:hover {{ opacity: 0.92; }}
.hero {{ padding: 90px 0 60px; text-align: center; }}
.pill {{
    display: inline-block; padding: 5px 14px; background: var(--accent-light);
    color: var(--accent); border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 20px;
}}
h1 {{
    font-size: clamp(2.4rem, 5vw, 3.8rem); font-weight: 800; line-height: 1.15;
    letter-spacing: -0.03em; max-width: 820px; margin: 0 auto 20px;
}}
p.lead {{ font-size: 1.2rem; color: var(--muted); max-width: 620px; margin: 0 auto 32px; }}
.grid-3 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin: 40px 0; }}
.clean-box {{
    border: 1px solid var(--line); border-radius: 8px; padding: 28px;
    background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}}
.clean-box h3 {{ font-size: 1.25rem; margin-bottom: 8px; }}
.clean-box p {{ color: var(--muted); font-size: 0.95rem; }}
.steps-wrap {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px; margin: 40px 0; }}
.clean-step {{
    border-top: 2px solid var(--accent); padding-top: 20px;
}}
.step-circle {{
    display: inline-block; width: 28px; height: 28px; border-radius: 50%;
    background: var(--accent-light); color: var(--accent); font-weight: 700;
    text-align: center; line-height: 28px; margin-bottom: 12px;
}}
.clean-faq {{
    border-bottom: 1px solid var(--line); padding: 18px 0; cursor: pointer;
}}
.clean-faq summary {{ font-weight: 600; list-style: none; display: flex; justify-content: space-between; }}
.clean-faq p {{ margin-top: 10px; color: var(--muted); }}
footer {{ border-top: 1px solid var(--line); padding: 40px 0; text-align: center; color: var(--muted); font-size: 0.9rem; margin-top: 60px; }}
</style>
</head>
<body>
<div class="wrap">
    <nav>
        <div class="brand">{logo_svg} <span>{e(name)}</span></div>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta', 'Start Free'))}</a>
    </nav>
    <section class="hero">
        <span class="pill">Intelligent Product Suite</span>
        <h1>{e(copy.get('headline'))}</h1>
        <p class="lead">{e(copy.get('subhead'))}</p>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
    </section>
    <section>
        <div class="grid-3">{benefits_html}</div>
    </section>
    <section style="padding: 40px 0;">
        <h2 style="font-size: 2rem; margin-bottom: 10px;">Three steps to full momentum</h2>
        <div class="steps-wrap">{steps_html}</div>
    </section>
    <section style="padding: 40px 0; max-width: 680px;" id="faq">
        <h2 style="font-size: 1.8rem; margin-bottom: 20px;">Frequently Asked Questions</h2>
        {faq_html}
    </section>
    <section style="text-align: center; padding: 80px 0;" id="cta">
        <h2 style="font-size: 2.2rem; margin-bottom: 16px;">Start building with {e(name)} today</h2>
        <p style="color: var(--muted); margin-bottom: 24px;">Experience the next level of performance.</p>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
    </section>
    <footer>© 2026 {e(name)}. High-Velocity Product Infrastructure.</footer>
</div>
</body>
</html>"""


# =====================================================================
# 3. ARCHETYPE: NEO-BRUTALISM (Figma / Gumroad bold borders & drop shadows)
# =====================================================================
def render_neobrutalism(name: str, topic: str, copy: Dict[str, Any], logo_svg: str, palette: List[str], dest: str) -> str:
    e = htmllib.escape
    accent_yellow = "#facc15"
    accent_pink = "#fb7185"

    benefits_html = "\n".join([
        f"""<div class="brutal-card">
            <h3>{e(b['title'])}</h3>
            <p>{e(b['desc'])}</p>
        </div>""" for b in copy.get("benefits", [])
    ])

    steps_html = "\n".join([
        f"""<div class="brutal-step">
            <span class="brutal-tag">STEP {e(s['num'])}</span>
            <h4>{e(s['title'])}</h4>
            <p>{e(s['desc'])}</p>
        </div>""" for s in copy.get("steps", [])
    ])

    faq_html = "\n".join([
        f"""<details class="brutal-faq"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>"""
        for f in copy.get("faqs", [])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} ★ {e(topic)}</title>
<style>
:root {{
    --bg: #fdfbf7;
    --ink: #111827;
    --yellow: {accent_yellow};
    --pink: {accent_pink};
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg); color: var(--ink);
    font-family: "Space Grotesk", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.5;
}}
.container {{ max-width: 1060px; margin: 0 auto; padding: 0 20px; }}
header.nav {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 24px 0; border-bottom: 3px solid var(--ink);
}}
.brand {{ display: flex; align-items: center; gap: 12px; font-weight: 900; font-size: 1.4rem; }}
.brand svg {{ width: 38px; height: 38px; }}
.btn {{
    background: var(--yellow); color: var(--ink); font-weight: 800; font-size: 1rem;
    padding: 12px 26px; border: 3px solid var(--ink); border-radius: 6px;
    box-shadow: 4px 4px 0px var(--ink); text-decoration: none; cursor: pointer;
    display: inline-block; transition: all 0.15s ease;
}}
.btn:hover {{ transform: translate(-2px, -2px); box-shadow: 6px 6px 0px var(--ink); }}
.btn:active {{ transform: translate(2px, 2px); box-shadow: 2px 2px 0px var(--ink); }}
.hero {{ padding: 80px 0 60px; text-align: center; }}
.sticker {{
    display: inline-block; background: var(--pink); color: #fff; font-weight: 900;
    padding: 6px 14px; border: 2px solid var(--ink); box-shadow: 3px 3px 0px var(--ink);
    transform: rotate(-2deg); margin-bottom: 24px; font-size: 0.9rem;
}}
h1 {{
    font-size: clamp(2.6rem, 6vw, 4.4rem); font-weight: 900; line-height: 1.05;
    letter-spacing: -0.03em; max-width: 860px; margin: 0 auto 24px;
}}
p.sub {{ font-size: 1.3rem; font-weight: 500; max-width: 660px; margin: 0 auto 36px; }}
.brutal-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin: 50px 0; }}
.brutal-card {{
    background: #fff; border: 3px solid var(--ink); border-radius: 8px; padding: 28px;
    box-shadow: 5px 5px 0px var(--ink);
}}
.brutal-card h3 {{ font-size: 1.35rem; font-weight: 800; margin-bottom: 12px; }}
.brutal-card p {{ font-size: 1rem; }}
.brutal-step {{
    background: #fff; border: 3px solid var(--ink); border-radius: 8px; padding: 24px;
    box-shadow: 5px 5px 0px var(--ink); margin-bottom: 16px;
}}
.brutal-tag {{
    display: inline-block; background: var(--yellow); font-weight: 900; font-size: 0.8rem;
    padding: 4px 8px; border: 2px solid var(--ink); margin-bottom: 8px;
}}
.brutal-faq {{
    background: #fff; border: 3px solid var(--ink); border-radius: 6px;
    padding: 18px 20px; margin-bottom: 14px; box-shadow: 4px 4px 0px var(--ink);
    cursor: pointer;
}}
.brutal-faq summary {{ font-weight: 800; font-size: 1.1rem; list-style: none; }}
.brutal-faq p {{ margin-top: 10px; font-size: 0.95rem; }}
footer {{ border-top: 3px solid var(--ink); padding: 40px 0; text-align: center; font-weight: 700; margin-top: 60px; }}
</style>
</head>
<body>
<div class="container">
    <header class="nav">
        <div class="brand">{logo_svg} <span>{e(name)}</span></div>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta', 'Claim Now'))}</a>
    </header>

    <section class="hero">
        <div class="sticker">★ NO BORING SOFTWARE ★</div>
        <h1>{e(copy.get('headline'))}</h1>
        <p class="sub">{e(copy.get('subhead'))}</p>
        <a class="btn" href="{e(dest or '#cta')}" style="font-size: 1.15rem; padding: 16px 36px;">{e(copy.get('cta'))}</a>
    </section>

    <section>
        <h2 style="font-size: 2.2rem; font-weight: 900; margin-bottom: 20px;">Why people ditch the alternatives</h2>
        <div class="brutal-grid">{benefits_html}</div>
    </section>

    <section style="padding: 40px 0;">
        <h2 style="font-size: 2.2rem; font-weight: 900; margin-bottom: 20px;">Zero Fluff. Here's How:</h2>
        <div>{steps_html}</div>
    </section>

    <section style="padding: 40px 0;" id="faq">
        <h2 style="font-size: 2.2rem; font-weight: 900; margin-bottom: 20px;">Real Talk FAQ</h2>
        {faq_html}
    </section>

    <section style="text-align: center; padding: 80px 0;" id="cta">
        <div style="background: var(--yellow); border: 4px solid var(--ink); border-radius: 12px; padding: 60px 20px; box-shadow: 8px 8px 0px var(--ink);">
            <h2 style="font-size: 2.6rem; font-weight: 900; margin-bottom: 16px;">Stop Waiting. Start Dominating.</h2>
            <p style="font-size: 1.2rem; font-weight: 600; margin-bottom: 28px;">Lock in your spot before doors close.</p>
            <a class="btn" href="{e(dest or '#cta')}" style="background: var(--pink); color: #fff; font-size: 1.2rem; padding: 16px 36px;">{e(copy.get('cta'))}</a>
        </div>
    </section>

    <footer>© 2026 {e(name)}. Loud. Bold. Unapologetically Fast.</footer>
</div>
</body>
</html>"""


# =====================================================================
# 4. ARCHETYPE: GRADIENT GLASS (Modern Consumer / Arc / Apple style)
# =====================================================================
def render_gradient_glass(name: str, topic: str, copy: Dict[str, Any], logo_svg: str, palette: List[str], dest: str) -> str:
    e = htmllib.escape
    benefits_html = "\n".join([
        f"""<div class="glass-box">
            <h3>{e(b['title'])}</h3>
            <p>{e(b['desc'])}</p>
        </div>""" for b in copy.get("benefits", [])
    ])

    steps_html = "\n".join([
        f"""<div class="glass-box" style="display:flex; gap:16px; align-items:center;">
            <div style="font-size:1.8rem; font-weight:800; color:#ec4899;">{e(s['num'])}</div>
            <div>
                <h4>{e(s['title'])}</h4>
                <p>{e(s['desc'])}</p>
            </div>
        </div>""" for s in copy.get("steps", [])
    ])

    faq_html = "\n".join([
        f"""<details class="glass-faq"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>"""
        for f in copy.get("faqs", [])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — {e(topic)}</title>
<style>
:root {{
    --bg-grad: linear-gradient(135deg, #fbcfe8 0%, #c7d2fe 50%, #fed7aa 100%);
    --card: rgba(255, 255, 255, 0.65);
    --border: rgba(255, 255, 255, 0.85);
    --text: #1e1b4b;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg-grad); min-height: 100vh; color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Plus Jakarta Sans", sans-serif;
    line-height: 1.6;
}}
.wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 24px; }}
nav {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 20px 24px; margin-top: 16px; border-radius: 999px;
    background: var(--card); backdrop-filter: blur(20px); border: 1px solid var(--border);
}}
.brand {{ display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.25rem; }}
.brand svg {{ width: 34px; height: 34px; border-radius: 50%; }}
.btn {{
    background: #1e1b4b; color: #fff; padding: 12px 28px; border-radius: 999px;
    text-decoration: none; font-weight: 700; box-shadow: 0 10px 25px rgba(30, 27, 75, 0.2);
    display: inline-block; transition: all 0.2s;
}}
.btn:hover {{ transform: scale(1.03); }}
.hero {{ padding: 90px 0 60px; text-align: center; }}
h1 {{
    font-size: clamp(2.5rem, 5.5vw, 4.2rem); font-weight: 800; line-height: 1.12;
    letter-spacing: -0.03em; margin-bottom: 20px;
}}
p.sub {{ font-size: 1.25rem; max-width: 640px; margin: 0 auto 32px; opacity: 0.85; }}
.glass-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin: 40px 0; }}
.glass-box {{
    background: var(--card); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--border); border-radius: 20px; padding: 30px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.04);
}}
.glass-box h3 {{ font-size: 1.3rem; margin-bottom: 10px; }}
.glass-faq {{
    background: var(--card); backdrop-filter: blur(16px); border: 1px solid var(--border);
    border-radius: 16px; padding: 18px 24px; margin-bottom: 12px; cursor: pointer;
}}
.glass-faq summary {{ font-weight: 700; font-size: 1.1rem; list-style: none; }}
.glass-faq p {{ margin-top: 10px; opacity: 0.85; }}
footer {{ text-align: center; padding: 50px 0; opacity: 0.7; font-size: 0.9rem; }}
</style>
</head>
<body>
<div class="wrap">
    <nav>
        <div class="brand">{logo_svg} <span>{e(name)}</span></div>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta', 'Join'))}</a>
    </nav>
    <section class="hero">
        <h1>{e(copy.get('headline'))}</h1>
        <p class="sub">{e(copy.get('subhead'))}</p>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
    </section>
    <section>
        <div class="glass-grid">{benefits_html}</div>
    </section>
    <section style="padding: 40px 0;">
        <h2 style="text-align: center; font-size: 2.2rem; margin-bottom: 24px;">Effortless Journey</h2>
        <div style="display: grid; gap: 16px; max-width: 680px; margin: 0 auto;">{steps_html}</div>
    </section>
    <section style="padding: 40px 0; max-width: 700px; margin: 0 auto;" id="faq">
        <h2 style="text-align: center; font-size: 2.2rem; margin-bottom: 24px;">Got Questions?</h2>
        {faq_html}
    </section>
    <section style="text-align: center; padding: 70px 0;" id="cta">
        <div class="glass-box" style="padding: 60px 20px; border-radius: 30px;">
            <h2 style="font-size: 2.4rem; margin-bottom: 16px;">Step into the New Standard</h2>
            <p style="margin-bottom: 28px; opacity: 0.85;">Experience {e(name)} firsthand.</p>
            <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
        </div>
    </section>
    <footer>© 2026 {e(name)}. Designed for human delight.</footer>
</div>
</body>
</html>"""


# =====================================================================
# 5. ARCHETYPE: EDITORIAL LUXURY (Notion / Substack Serif Elegance)
# =====================================================================
def render_editorial_luxury(name: str, topic: str, copy: Dict[str, Any], logo_svg: str, palette: List[str], dest: str) -> str:
    e = htmllib.escape
    benefits_html = "\n".join([
        f"""<div class="edit-card">
            <h3>{e(b['title'])}</h3>
            <p>{e(b['desc'])}</p>
        </div>""" for b in copy.get("benefits", [])
    ])

    steps_html = "\n".join([
        f"""<div style="margin-bottom: 28px;">
            <div style="font-weight: 700; color: #854d0e; letter-spacing: 0.08em; text-transform: uppercase; font-size: 0.85rem;">Phase {e(s['num'])}</div>
            <h4 style="font-size: 1.3rem; margin: 4px 0 8px; font-family: Georgia, serif;">{e(s['title'])}</h4>
            <p style="color: #4b5563;">{e(s['desc'])}</p>
        </div>""" for s in copy.get("steps", [])
    ])

    faq_html = "\n".join([
        f"""<details class="edit-faq"><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>"""
        for f in copy.get("faqs", [])
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(name)} — {e(topic)}</title>
<style>
:root {{
    --bg: #fcfbf9;
    --ink: #1c1917;
    --muted: #57534e;
    --gold: #854d0e;
    --line: #e7e5e4;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg); color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    line-height: 1.7;
}}
.container {{ max-width: 900px; margin: 0 auto; padding: 0 24px; }}
header.nav {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 30px 0; border-bottom: 1px solid var(--line);
}}
.brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; font-family: Georgia, serif; font-size: 1.35rem; }}
.brand svg {{ width: 32px; height: 32px; }}
.btn {{
    background: var(--ink); color: #fff; padding: 12px 26px; border-radius: 4px;
    font-size: 0.95rem; font-weight: 600; text-decoration: none; display: inline-block;
    transition: opacity 0.2s;
}}
.btn:hover {{ opacity: 0.88; }}
.hero {{ padding: 100px 0 70px; text-align: center; }}
h1 {{
    font-family: Georgia, "Times New Roman", serif; font-size: clamp(2.6rem, 5.5vw, 4rem);
    font-weight: 400; line-height: 1.15; margin-bottom: 24px; letter-spacing: -0.01em;
}}
p.sub {{ font-size: 1.25rem; color: var(--muted); max-width: 620px; margin: 0 auto 36px; font-style: italic; }}
.edit-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 30px; margin: 50px 0; }}
.edit-card {{ border-top: 1px solid var(--gold); padding-top: 18px; }}
.edit-card h3 {{ font-family: Georgia, serif; font-size: 1.3rem; margin-bottom: 8px; font-weight: 600; }}
.edit-card p {{ color: var(--muted); font-size: 0.95rem; }}
.edit-faq {{ border-bottom: 1px solid var(--line); padding: 18px 0; cursor: pointer; }}
.edit-faq summary {{ font-family: Georgia, serif; font-size: 1.15rem; list-style: none; }}
.edit-faq p {{ margin-top: 10px; color: var(--muted); }}
footer {{ border-top: 1px solid var(--line); padding: 50px 0; text-align: center; color: var(--muted); font-size: 0.9rem; margin-top: 70px; }}
</style>
</head>
<body>
<div class="container">
    <header class="nav">
        <div class="brand">{logo_svg} <span>{e(name)}</span></div>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta', 'Request Invitation'))}</a>
    </header>

    <section class="hero">
        <div style="color: var(--gold); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 16px;">The Modern Standard</div>
        <h1>{e(copy.get('headline'))}</h1>
        <p class="sub">{e(copy.get('subhead'))}</p>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
    </section>

    <section>
        <div class="edit-grid">{benefits_html}</div>
    </section>

    <section style="padding: 50px 0; max-width: 640px; margin: 0 auto;">
        <h2 style="font-family: Georgia, serif; font-size: 2.2rem; font-weight: 400; margin-bottom: 30px;">Methodology</h2>
        {steps_html}
    </section>

    <section style="padding: 40px 0; max-width: 640px; margin: 0 auto;" id="faq">
        <h2 style="font-family: Georgia, serif; font-size: 2rem; font-weight: 400; margin-bottom: 24px;">Inquiries</h2>
        {faq_html}
    </section>

    <section style="text-align: center; padding: 80px 0;" id="cta">
        <h2 style="font-family: Georgia, serif; font-size: 2.4rem; font-weight: 400; margin-bottom: 16px;">Elevate your workflow with {e(name)}</h2>
        <p style="color: var(--muted); margin-bottom: 28px; font-style: italic;">Reserve your priority access.</p>
        <a class="btn" href="{e(dest or '#cta')}">{e(copy.get('cta'))}</a>
    </section>

    <footer>© 2026 {e(name)}. Thoughtfully crafted.</footer>
</div>
</body>
</html>"""


# =====================================================================
# MASTER DISPATCHER: Guarantees different interfaces every time
# =====================================================================
RENDERERS = {
    "dark_cyber": render_dark_cyber,
    "saas_minimal": render_saas_minimal,
    "neobrutalism": render_neobrutalism,
    "gradient_glass": render_gradient_glass,
    "editorial_luxury": render_editorial_luxury,
}


def build_landing_page(
    name: str,
    topic: str,
    tone: str = "bold",
    archetype: Optional[str] = None,
    previous_archetype: Optional[str] = None,
    logo_svg: str = "",
    palette: List[str] = None,
    dest: str = "",
    differentiation: List[Dict[str, str]] = None,
) -> Tuple[str, str]:
    """
    Generate a landing page selecting a unique design archetype every time.
    Returns (html_string, chosen_archetype_name).
    """
    if not palette:
        palette = config.PALETTES["electric_violet"]

    all_archetypes = getattr(config, "ARCHETYPES", ["dark_cyber", "saas_minimal", "neobrutalism", "gradient_glass", "editorial_luxury"])
    if archetype and archetype in RENDERERS:
        chosen_archetype = archetype
    else:
        # Pick an archetype different from the previous generation
        available = [a for a in all_archetypes if a != previous_archetype]
        if not available:
            available = all_archetypes

        # Tone hints
        if tone == "futuristic":
            chosen_archetype = "dark_cyber"
        elif tone == "playful":
            chosen_archetype = random.choice(["neobrutalism", "gradient_glass"])
        elif tone == "professional":
            chosen_archetype = random.choice(["saas_minimal", "editorial_luxury"])
        elif tone == "bold":
            chosen_archetype = random.choice(["neobrutalism", "dark_cyber"])
        else:
            chosen_archetype = random.choice(available)

    copy_data = get_copy_data(name, topic, tone, differentiation)
    renderer = RENDERERS[chosen_archetype]
    html_code = renderer(name, topic, copy_data, logo_svg, palette, dest)
    return html_code, chosen_archetype
