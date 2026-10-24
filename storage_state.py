"""
Session state and persistent memory manager for Launch Kit Agent.
Works seamlessly with uAgents ctx.storage and in-memory fallback.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("launchkit.state")

# Local in-memory cache to guarantee persistence even if storage adapter resets
_MEM_CACHE: Dict[str, Any] = {}


def get_val(ctx, key: str, default: Any = None) -> Any:
    """Retrieve a value from ctx.storage or local memory."""
    try:
        val = ctx.storage.get(key)
        if val is not None:
            return val
    except Exception as e:
        logger.debug(f"ctx.storage.get failed for {key}: {e}")
    return _MEM_CACHE.get(key, default)


def set_val(ctx, key: str, value: Any) -> None:
    """Save a value to ctx.storage and local memory."""
    _MEM_CACHE[key] = value
    try:
        ctx.storage.set(key, value)
    except Exception as e:
        logger.debug(f"ctx.storage.set failed for {key}: {e}")


def get_session(ctx, sender: str) -> Dict[str, Any]:
    """Get the full session state for a sender."""
    key = f"session:{sender}"
    return get_val(ctx, key, {
        "product": {},
        "last_logo": None,
        "last_website": None,
        "last_research": None,
        "last_seo": None,
        "last_workflow": None,
        "chat_history": [],
    })


def update_session(ctx, sender: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update fields in the sender's session."""
    session = get_session(ctx, sender)
    session.update(updates)
    set_val(ctx, f"session:{sender}", session)
    return session


def update_product(ctx, sender: str, product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update or merge active product details."""
    session = get_session(ctx, sender)
    current_product = session.get("product", {})
    current_product.update(product_data)
    session["product"] = current_product
    set_val(ctx, f"session:{sender}", session)
    return current_product


def add_chat_message(ctx, sender: str, role: str, content: str, max_history: int = 10) -> None:
    """Record a chat message in the conversation history."""
    session = get_session(ctx, sender)
    history = session.get("chat_history", [])
    history.append({"role": role, "content": content})
    session["chat_history"] = history[-max_history:]
    set_val(ctx, f"session:{sender}", session)


def clear_session(ctx, sender: str) -> None:
    """Clear the session for a sender."""
    set_val(ctx, f"session:{sender}", {
        "product": {},
        "last_logo": None,
        "last_website": None,
        "last_research": None,
        "last_seo": None,
        "last_workflow": None,
        "chat_history": [],
    })
