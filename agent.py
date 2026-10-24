"""
Launch Kit AI Agent v5
Autonomous Product Launcher & Startup Co-Pilot for Agentverse (ASI-1 Chat Protocol)
"""

import asyncio
import logging
import os
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from uuid import uuid4

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

# Flat local modular imports
import config
import http_client
import intent
import llm_client
import logo_engine
import researcher
import seo_reddit_engine
import storage_state as state
import website_engine
import workflow_engine

# Logger configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("launchkit.agent")

# Initialize uAgent & Chat Protocol
agent = Agent()
chat_proto = Protocol(spec=chat_protocol_spec)

# Welcome greeting
WELCOME_MESSAGE = f"""👋 **Welcome to {config.NAME} (v{config.VERSION})!**

I am your autonomous startup co-pilot and product launcher. We can chat casually about your idea, or I can execute specific deliverables on demand:

• 🔍 **Live Competitor Research:** *"Who are my competitors for an AI email client?"*
• 🎨 **Brand Identity & Logo:** *"Generate only a logo for Nova"* (say *"improvise logo"* to refine)
• 💻 **Dynamic Landing Page:** *"Generate website for Wanderly"* (creates unique interfaces every time: Dark Cyber, SaaS Minimal, Neo-brutalist, Glass, Luxury)
• 🚀 **SEO & Reddit Promo Bot:** *"Give me SEO and a Reddit promo bot"*
• 📋 **Product Continuation Roadmap:** *"Generate WORKFLOW.md"*
• ⚡ **Full Launch Kit:** *"Launch my productivity app called FocusFlow. Tone: bold."*

What are you working on or brainstorming today?"""


def make_chat_message(text: str) -> ChatMessage:
    """Construct a protocol-compliant ChatMessage."""
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


async def send_reply(ctx: Context, sender: str, text: str) -> None:
    """Send a text response over uAgents chat protocol."""
    await ctx.send(sender, make_chat_message(text))


# =====================================================================
# ACTION HANDLERS
# =====================================================================

async def handle_casual_chat(ctx: Context, sender: str, text: str, entities: dict) -> None:
    """Handle normal, intelligent, friendly conversation without forcing templates."""
    session = state.get_session(ctx, sender)
    product = session.get("product", {})
    history = session.get("chat_history", [])

    if llm_client.is_available():
        context_prompt = config.CHAT_SYSTEM_PROMPT
        if product.get("name"):
            context_prompt += f"\nActive Product in Context: {product.get('name')} ({product.get('topic')}, tone: {product.get('tone')})."

        messages = [{"role": "system", "content": context_prompt}]
        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": text})

        reply, err = llm_client.chat(messages, max_tokens=600, temperature=0.7)
        if reply:
            state.add_chat_message(ctx, sender, "user", text)
            state.add_chat_message(ctx, sender, "assistant", reply)
            await send_reply(ctx, sender, reply)
            return

    # Fallback smart conversational replies
    if intent.GREETINGS.search(text):
        await send_reply(
            ctx,
            sender,
            f"Hey there! Great to connect with you. I'm {config.NAME}. What kind of product or idea are you exploring today?",
        )
        return

    if intent.CASUAL_QUESTIONS.search(text):
        await send_reply(ctx, sender, WELCOME_MESSAGE)
        return

    # If user mentioned a product idea in casual chat
    if entities.get("name") or entities.get("topic"):
        p_name = entities.get("name")
        p_topic = entities.get("topic")
        state.update_product(ctx, sender, entities)
        await send_reply(
            ctx,
            sender,
            f"That sounds like an exciting venture — **{p_name}** ({p_topic})! 🚀\n\n"
            f"Would you like me to:\n"
            f"1. 🔍 **Analyze competitors** and find how to stand out\n"
            f"2. 🎨 **Design a custom logo** and color palette\n"
            f"3. 💻 **Build the landing page** (we have Dark Cyber, Clean Minimal, Neo-brutalist & Glass styles)\n"
            f"4. 📢 **Create an SEO & Reddit promotion bot**\n"
            f"5. ⚡ **Generate the full launch kit** right away?\n\n"
            f"Just tell me what you'd like first, or ask me anything!",
        )
        return

    await send_reply(
        ctx,
        sender,
        "I'm here to help you brainstorm and launch. You can tell me about an idea, or ask for specific assets like 'generate only the logo', 'build landing page', 'competitor research', or 'create reddit bot'!",
    )


async def handle_logo_request(ctx: Context, sender: str, entities: dict) -> None:
    """Generate and deliver only the brand logo and palette."""
    session = state.get_session(ctx, sender)
    product = state.update_product(ctx, sender, entities)
    name = product.get("name", "NovaLaunch")
    tone = product.get("tone", "bold")
    feedback = entities.get("feedback", "")

    seed = session.get("logo_seed", 0)
    svg, palette, tagline, meta = logo_engine.generate_logo(name, tone, feedback=feedback, seed_offset=seed)
    session["logo_seed"] = seed + 1
    session["last_logo"] = {"svg": svg, "palette": palette, "tagline": tagline, "meta": meta}
    state.set_val(ctx, f"session:{sender}", session)

    delivery = logo_engine.format_logo_delivery(name, svg, palette, tagline, meta)
    await send_reply(ctx, sender, delivery)


async def handle_website_request(ctx: Context, sender: str, entities: dict) -> None:
    """Generate and deliver only the landing page with a dynamic unique interface."""
    session = state.get_session(ctx, sender)
    product = state.update_product(ctx, sender, entities)
    name = product.get("name", "NovaLaunch")
    topic = product.get("topic", "autonomous digital software")
    tone = product.get("tone", "bold")
    archetype = entities.get("archetype")
    dest = product.get("url") or (f"mailto:{product.get('email')}" if product.get("email") else "#cta")

    # Use existing logo or create one
    last_logo = session.get("last_logo")
    if last_logo:
        logo_svg = last_logo["svg"]
        palette = last_logo["palette"]
    else:
        logo_svg, palette, _, _ = logo_engine.generate_logo(name, tone)

    prev_archetype = session.get("last_website", {}).get("archetype") if session.get("last_website") else None
    research_diff = session.get("last_research", {}).get("standing_out_strategy") if session.get("last_research") else None

    html_code, chosen_archetype = website_engine.build_landing_page(
        name=name,
        topic=topic,
        tone=tone,
        archetype=archetype,
        previous_archetype=prev_archetype,
        logo_svg=logo_svg,
        palette=palette,
        dest=dest,
        differentiation=research_diff,
    )

    session["last_website"] = {"html": html_code, "archetype": chosen_archetype}
    state.set_val(ctx, f"session:{sender}", session)

    archetype_titles = {
        "dark_cyber": "Dark Cyber AI (Futuristic Neon / Vercel style)",
        "saas_minimal": "SaaS Minimal (Crisp Clean Stripe / Linear style)",
        "neobrutalism": "Neo-Brutalism (Bold High-Contrast Gumroad style)",
        "gradient_glass": "Gradient Glass (Smooth Modern Consumer style)",
        "editorial_luxury": "Editorial Luxury (Refined Notion / Substack style)",
    }
    nice_title = archetype_titles.get(chosen_archetype, chosen_archetype)

    await send_reply(
        ctx,
        sender,
        f"💻 **LANDING PAGE GENERATED: {name.upper()}**\n"
        f"• **Design Architecture:** `{nice_title}`\n"
        f"• **Destination URL/Button:** `{dest}`\n\n"
        f"```html\n{html_code}\n```\n"
        f"*(Save this code as `index.html` and open it in any browser! Say 'make it dark cyber' or 'make it neobrutalist' to switch designs instantly.)*",
    )


async def handle_research_request(ctx: Context, sender: str, entities: dict) -> None:
    """Execute deep live competitor research and differentiation strategy."""
    product = state.update_product(ctx, sender, entities)
    name = product.get("name", "NovaLaunch")
    topic = product.get("topic", "modern digital software")
    url = product.get("url", "")

    await send_reply(
        ctx,
        sender,
        f"🔍 Initiating deep live research for **{name}** ({topic}) across DuckDuckGo, Reddit, Hacker News, and Wikipedia...",
    )

    loop = asyncio.get_running_loop()
    research_data = await loop.run_in_executor(None, researcher.execute_deep_research, name, topic, url)

    session = state.get_session(ctx, sender)
    session["last_research"] = research_data
    state.set_val(ctx, f"session:{sender}", session)

    report = researcher.format_research_report(research_data, name)
    await send_reply(ctx, sender, report)


async def handle_seo_reddit_request(ctx: Context, sender: str, entities: dict) -> None:
    """Generate SEO optimization package and automated Reddit promotion bot."""
    product = state.update_product(ctx, sender, entities)
    name = product.get("name", "NovaLaunch")
    topic = product.get("topic", "modern digital software")
    url = product.get("url", "")

    loop = asyncio.get_running_loop()
    seo_data = await loop.run_in_executor(None, seo_reddit_engine.generate_seo_package, name, topic, url)
    reddit_data = await loop.run_in_executor(None, seo_reddit_engine.generate_reddit_campaign, name, topic, url)

    session = state.get_session(ctx, sender)
    session["last_seo"] = seo_data
    session["last_reddit"] = reddit_data
    state.set_val(ctx, f"session:{sender}", session)

    delivery = seo_reddit_engine.format_seo_and_reddit_delivery(name, seo_data, reddit_data)
    await send_reply(ctx, sender, delivery)


async def handle_workflow_request(ctx: Context, sender: str, entities: dict) -> None:
    """Generate comprehensive WORKFLOW.md strategic document."""
    session = state.get_session(ctx, sender)
    product = state.update_product(ctx, sender, entities)
    name = product.get("name", "NovaLaunch")
    topic = product.get("topic", "modern digital software")
    tone = product.get("tone", "bold")

    competitors = session.get("last_research", {}).get("competitors") if session.get("last_research") else None
    standing_out = session.get("last_research", {}).get("standing_out_strategy") if session.get("last_research") else None

    loop = asyncio.get_running_loop()
    workflow_md = await loop.run_in_executor(None, workflow_engine.generate_workflow_md, name, topic, tone, competitors, standing_out)

    session["last_workflow"] = workflow_md
    state.set_val(ctx, f"session:{sender}", session)

    delivery = workflow_engine.format_workflow_delivery(name, workflow_md)
    await send_reply(ctx, sender, delivery)


async def handle_revision_request(ctx: Context, sender: str, entities: dict) -> None:
    """Handle improvising or revising previously generated assets without starting from scratch."""
    session = state.get_session(ctx, sender)
    target = entities.get("target_asset", "general")
    feedback = entities.get("feedback", "")
    state.update_product(ctx, sender, entities)

    logger.info(f"Revising {target} with feedback: {feedback}")

    if target == "logo":
        await send_reply(ctx, sender, "🎨 Got it! Crafting a new improvised logo variation based on your feedback...")
        await handle_logo_request(ctx, sender, entities)
        return

    if target == "website":
        await send_reply(ctx, sender, "💻 Regenerating landing page with a fresh interface...")
        await handle_website_request(ctx, sender, entities)
        return

    if target in ("name", "tone"):
        name = entities.get("name")
        tone = entities.get("tone")
        await send_reply(
            ctx,
            sender,
            f"🔄 Updated brand settings: Name = **{name}**, Tone = **{tone}**. What asset would you like me to update first (logo, website, copy)?",
        )
        return

    await send_reply(
        ctx,
        sender,
        f"Understood: '{feedback}'. Tell me specifically what to update: the **logo**, the **website design**, the **competitor research**, or the **workflow**?",
    )


async def handle_full_kit_request(ctx: Context, sender: str, entities: dict) -> None:
    """Orchestrate the complete autonomous launch kit without audit noise."""
    t0 = time.time()
    product = state.update_product(ctx, sender, entities)
    name = product.get("name", "NovaLaunch")
    topic = product.get("topic", "modern digital software")
    tone = product.get("tone", "bold")
    dest = product.get("url") or (f"mailto:{product.get('email')}" if product.get("email") else "#cta")

    await send_reply(
        ctx,
        sender,
        f"🚀 **INITIALIZING COMPLETE LAUNCH KIT FOR {name.upper()}**\n"
        f"• Product: {topic}\n"
        f"• Tone: {tone}\n"
        f"• Pipeline: Live Research ➔ Logo & Identity ➔ Landing Page UI ➔ SEO & Reddit Bot ➔ Strategic WORKFLOW.md\n\n"
        f"Running live intelligence now...",
    )

    loop = asyncio.get_running_loop()

    # Step 1: Research
    research_data = await loop.run_in_executor(None, researcher.execute_deep_research, name, topic, product.get("url", ""))
    diff = research_data.get("standing_out_strategy", [])

    # Step 2: Logo
    session = state.get_session(ctx, sender)
    seed = session.get("logo_seed", 0)
    svg, palette, tagline, meta = logo_engine.generate_logo(name, tone, seed_offset=seed)
    session["logo_seed"] = seed + 1

    # Step 3: Dynamic Website
    html_code, chosen_archetype = website_engine.build_landing_page(
        name=name, topic=topic, tone=tone, logo_svg=svg, palette=palette, dest=dest, differentiation=diff
    )

    # Step 4: SEO & Reddit Campaign
    seo_data = await loop.run_in_executor(None, seo_reddit_engine.generate_seo_package, name, topic, product.get("url", ""))
    reddit_data = await loop.run_in_executor(None, seo_reddit_engine.generate_reddit_campaign, name, topic, product.get("url", ""))

    # Step 5: Workflow MD
    workflow_md = await loop.run_in_executor(
        None, workflow_engine.generate_workflow_md, name, topic, tone, research_data.get("competitors"), diff
    )

    # Save all to state
    session["last_research"] = research_data
    session["last_logo"] = {"svg": svg, "palette": palette, "tagline": tagline, "meta": meta}
    session["last_website"] = {"html": html_code, "archetype": chosen_archetype}
    session["last_seo"] = seo_data
    session["last_reddit"] = reddit_data
    session["last_workflow"] = workflow_md
    state.set_val(ctx, f"session:{sender}", session)

    # Deliverables (Clean & Audit-Free!)
    await send_reply(ctx, sender, researcher.format_research_report(research_data, name))
    await send_reply(ctx, sender, logo_engine.format_logo_delivery(name, svg, palette, tagline, meta))
    await send_reply(
        ctx,
        sender,
        f"💻 **DELIVERABLE: Landing Page (`index.html`)**\n"
        f"Architecture: `{chosen_archetype}` | Button: `{dest}`\n```html\n{html_code}\n```",
    )
    await send_reply(ctx, sender, seo_reddit_engine.format_seo_and_reddit_delivery(name, seo_data, reddit_data))
    await send_reply(ctx, sender, workflow_engine.format_workflow_delivery(name, workflow_md))

    elapsed = round(time.time() - t0, 1)
    await send_reply(
        ctx,
        sender,
        f"✨ **Launch Kit for {name} Completed in {elapsed}s!**\n"
        f"Everything has been generated without noisy audit logs. You can improvise any piece anytime by saying:\n"
        f"• *'I didn't like the logo, create another one'*\n"
        f"• *'Change the website style to dark cyber'*\n"
        f"• *'Rewrite the headline to be punchier'*",
    )


async def run_diagnostics(ctx: Context, sender: str) -> None:
    """Run system self-check and diagnostic report."""
    lines = [f"🩺 **{config.NAME} System Diagnostics (v{config.VERSION})**"]
    lines.append(f"• Python Runtime: `{sys.version.split()[0]}`")

    # Storage test
    try:
        state.set_val(ctx, "diag:ping", "pong")
        ok = state.get_val(ctx, "diag:ping") == "pong"
        lines.append(f"• Persistent State Storage: `{'OK' if ok else 'FAIL'}`")
    except Exception as e:
        lines.append(f"• Persistent State Storage: `FAIL ({type(e).__name__})`")

    # Intelligence providers test
    active_providers = llm_client.get_active_provider_names()
    if active_providers:
        reply, err = llm_client.single_prompt("Reply with single word OK.", "ping", max_tokens=5)
        prov_str = ", ".join(active_providers)
        lines.append(f"• Intelligence Engine: `ACTIVE ({prov_str})` [{'OK' if reply else 'FAIL (' + err + ')'}]")
    else:
        lines.append("• Intelligence Engine: `Algorithmic Mode (Set GROQ_API_KEY, GEMINI_API_KEY, or ASI1_API_KEY for live AI)`")

    # Research APIs status
    tavily_key = os.getenv("TAVILY_API_KEY", "").strip()
    serper_key = os.getenv("SERPER_API_KEY", "").strip()
    lines.append(f"• Tavily Web Research: `{'ACTIVE' if tavily_key else 'Not set (optional; set TAVILY_API_KEY in Secrets for deep AI search)'}`")
    lines.append(f"• Serper Google Search: `{'ACTIVE' if serper_key else 'Not set (optional; set SERPER_API_KEY in Secrets for Google results)'}`")

    # Free zero-key APIs status
    free_apis = [
        ("Hacker News Algolia", researcher.search_hacker_news, "ai tool"),
        ("Wikipedia REST", researcher.search_wikipedia, "software"),
        ("DuckDuckGo Instant", researcher.search_duckduckgo_instant, "python"),
    ]
    loop = asyncio.get_running_loop()
    for api_name, fn, arg in free_apis:
        try:
            res = await loop.run_in_executor(None, fn, arg)
            lines.append(f"• {api_name} API: `OK ({len(res)} results)`")
        except Exception as e:
            lines.append(f"• {api_name} API: `WARNING ({type(e).__name__})`")

    await send_reply(ctx, sender, "\n".join(lines))


# =====================================================================
# PROTOCOL EVENT HANDLERS
# =====================================================================

@chat_proto.on_message(ChatMessage)
async def handle_incoming_message(ctx: Context, sender: str, m: ChatMessage) -> None:
    """Handle incoming ASI-1 / Agentverse chat messages."""
    try:
        # Acknowledge receipt
        await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=m.msg_id))
    except Exception as e:
        logger.warning(f"Failed to send ack: {e}")

    for item in m.content:
        if isinstance(item, StartSessionContent):
            await send_reply(ctx, sender, WELCOME_MESSAGE)
            continue

        if not isinstance(item, TextContent):
            continue

        raw_text = item.text.strip()
        if not raw_text:
            continue

        logger.info(f"Incoming message from {sender}: {raw_text[:80]}")

        try:
            session = state.get_session(ctx, sender)
            prev_product = session.get("product")
            parsed = intent.parse_intent(raw_text, prev_product)
            action = parsed.get("intent")
            entities = parsed.get("entities", {})

            logger.info(f"Parsed action: {action}")

            if action == intent.INTENT_DIAG:
                await run_diagnostics(ctx, sender)
            elif action == intent.INTENT_REVISE:
                await handle_revision_request(ctx, sender, entities)
            elif action == intent.INTENT_LOGO:
                await handle_logo_request(ctx, sender, entities)
            elif action == intent.INTENT_WEBSITE:
                await handle_website_request(ctx, sender, entities)
            elif action == intent.INTENT_RESEARCH:
                await handle_research_request(ctx, sender, entities)
            elif action in (intent.INTENT_SEO, intent.INTENT_REDDIT):
                await handle_seo_reddit_request(ctx, sender, entities)
            elif action == intent.INTENT_WORKFLOW:
                await handle_workflow_request(ctx, sender, entities)
            elif action == intent.INTENT_FULL_KIT:
                await handle_full_kit_request(ctx, sender, entities)
            else:
                await handle_casual_chat(ctx, sender, raw_text, entities)

        except Exception as e:
            logger.error(f"Error processing message: {traceback.format_exc()}")
            await send_reply(
                ctx,
                sender,
                f"⚠️ Error while processing: `{type(e).__name__}: {str(e)[:120]}`.\n"
                f"Send `diag` to inspect system status, or try asking for a specific deliverable like *'generate website'* or *'competitor research'*.",
            )


@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, m: ChatAcknowledgement) -> None:
    logger.debug(f"Ack from {sender}")


agent.include(chat_proto, publish_manifest=True)

