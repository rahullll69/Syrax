"""
Product Continuation and WORKFLOW.md Generator.
Produces a comprehensive strategic execution plan, technical architecture recommendations,
and autonomous agent deployment suggestions for continuing product momentum.
"""

import logging
from typing import Any, Dict, List, Optional

import llm_client

logger = logging.getLogger("launchkit.workflow")


def generate_workflow_md(
    name: str,
    topic: str,
    tone: str = "bold",
    competitors: Optional[List[Dict[str, str]]] = None,
    standing_out: Optional[List[Dict[str, str]]] = None,
) -> str:
    """Generate a full WORKFLOW.md document detailing product continuation and agent suggestions."""
    competitors_summary = ""
    if competitors:
        competitors_summary = "\n".join([f"- **{c['name']}**: Weakness: {c.get('weakness', 'N/A')}" for c in competitors[:3]])

    standing_out_summary = ""
    if standing_out:
        standing_out_summary = "\n".join([f"- **{s['pillar']}**: {s['action']}" for s in standing_out[:4]])

    if llm_client.is_available():
        prompt = f"""
You are a Principal Product Architect and Venture Studio Lead.
Product: {name}
Description: {topic}
Tone: {tone}

Competitors:
{competitors_summary}

Differentiation:
{standing_out_summary}

Create a complete, actionable, highly detailed WORKFLOW.md file that guides the user on:
1. Executive Product Vision & Core Value Proposition
2. Recommended Tech Stack & System Architecture
3. 3-Phase Execution Roadmap (Phase 1: Validation/MVP, Phase 2: Growth/Retention, Phase 3: Scaling/Monetization)
4. 4 Concrete Autonomous AI Agent Suggestions (uAgents on Agentverse) to automate ongoing operations (competitor monitoring, social listening, lead nurture, content generation)
5. Immediate Action Checklist for today.

Format the output strictly as clean, professional Markdown.
"""
        res, _ = llm_client.single_prompt(
            "You are a visionary product executive. Output comprehensive Markdown only.",
            prompt,
            max_tokens=1500,
            temperature=0.5,
        )
        if res and len(res) > 300:
            return res.strip()

    # Algorithmic comprehensive fallback WORKFLOW.md
    return f"""# 🚀 Product Continuation & Strategic Workflow: {name}

> **Document Version:** 1.0  
> **Status:** Active Execution  
> **Architecture Ecosystem:** uAgents / Agentverse / ASI-1  

---

## 1. Executive Product Vision & Positioning
**{name}** is engineered to revolutionize the **{topic}** space. Traditional market solutions suffer from excessive feature bloat, complex onboarding hurdles, and lack of autonomous native intelligence.

### Core Value Proposition
- **Frictionless Velocity:** Get users from zero to working results in under 60 seconds.
- **Autonomous Intelligence:** Replace manual repetitive tasks with proactive agentic assistance.
- **Transparent Utility:** Clear, value-aligned pricing without legacy enterprise paywalls.

---

## 2. Recommended System Architecture & Stack

| Layer | Recommended Technology | Key Advantage |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js / Tailwind CSS / Single-File HTML | Blazing fast load times, pristine SEO, and reactive UX |
| **Agentic Core** | `uagents` framework (Agentverse hosted) | Autonomous decentralized agent messaging, persistent storage, cron triggers |
| **Intelligence Engine**| ASI-1 / OpenAI API | High-reasoning chat completions, structured JSON generation, sentiment synthesis |
| **Database & Cache** | Supabase (PostgreSQL) + Upstash Redis | Real-time events, relational data integrity, and low-latency session caching |
| **Hosting & CI/CD** | Vercel / Agentverse Portal | Instant global edge deployment with zero DevOps overhead |

---

## 3. Product Execution Roadmap

```mermaid
flowchart LR
    P1["Phase 1: Launch & Validate (Weeks 1-2)"] --> P2["Phase 2: Core MVP Expansion (Weeks 3-6)"]
    P2 --> P3["Phase 3: Autonomous Scale (Weeks 7-12)"]
```

### Phase 1: Rapid Validation & Early Access (Weeks 1–2)
- [ ] Deploy landing page to custom domain with SSL.
- [ ] Connect waitlist button to email capture provider (Resend / Beehiiv / Supabase).
- [ ] Execute Reddit community launch across `r/SideProject`, `r/SaaS`, and `r/Entrepreneur`.
- [ ] Setup Google Search Console and verify `JSON-LD` Schema tags.

### Phase 2: Core Feature Expansion & Feedback Loops (Weeks 3–6)
- [ ] Roll out private alpha access to the first 50 waitlist signups.
- [ ] Implement in-app telemetry to track where users experience delight vs drop-off.
- [ ] Establish weekly build-in-public changelog on X and Reddit to foster community loyalty.
- [ ] Refine core differentiator based on initial feedback.

### Phase 3: Autonomous Scaling & Monetization (Weeks 7–12)
- [ ] Introduce usage-based self-serve tiers (Stripe integration).
- [ ] Launch autonomous lead generation and social monitoring agents.
- [ ] Establish an affiliate and ambassador program with 20% recurring reward.
- [ ] Expand API integrations and developer webhooks.

---

## 4. Autonomous Agent Suggestions (uAgents on Agentverse)
To scale {name} with minimal manual labor, deploy these specialized autonomous agents:

### 🤖 Agent A: Continuous Market & Competitor Radar
- **Function:** Runs on a scheduled cron every 12 hours. Scrapes Hacker News, Reddit, and Product Hunt for mentions of competing tools.
- **Trigger:** When users express frustration with legacy competitors, the agent flags the thread for instant outreach.

### 🤖 Agent B: Reddit & X Social Listening Bot
- **Function:** Continuously scans relevant subreddits using keyword matching for "{topic}", "looking for tool", and "alternative to".
- **Action:** Drafts authentic, value-first response templates and alerts the founder via webhook.

### 🤖 Agent C: Autonomous Onboarding & Nurture Agent
- **Function:** Detects when an early-access user hasn't completed their first project within 24 hours.
- **Action:** Sends a personalized, helpful tip email or chat prompt offering specific assistance.

### 🤖 Agent D: SEO Keyword & Content Gap Scout
- **Function:** Monitors trending search queries in the {topic} vertical and identifies high-intent long-tail keywords with low ranking difficulty.

---

## 5. Immediate Action Items (Today)
1. **Save Assets:** Copy `index.html` and `logo.svg` to your project repository.
2. **Deploy Website:** Drag and drop `index.html` to Vercel, Netlify, or GitHub Pages.
3. **Launch Reddit Post:** Post the provided launch copy on `r/SideProject` during peak weekday morning hours.
4. **Deploy Reddit Promo Bot:** Run `reddit_promo_bot.py` locally to start monitoring conversations.
"""


def format_workflow_delivery(name: str, workflow_md: str) -> str:
    """Format WORKFLOW.md deliverable for chat."""
    return f"""📋 **PRODUCT EXECUTION WORKFLOW & CONTINUATION ROADMAP: {name.upper()}**

I have engineered a complete strategic `WORKFLOW.md` document covering system architecture, a 3-phase execution roadmap, and autonomous uAgent automation concepts:

```markdown
{workflow_md}
```
*(Tip: Save this file as `WORKFLOW.md` in your repository root to guide your ongoing development and agent architecture!)*"""
