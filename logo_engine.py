"""
Dynamic SVG Logo, Color Palette, and Brand Identity Generator.
Supports fine-grained iterative improvisation (different styles, shapes, palettes, and typography).
"""

import html as htmllib
import random
import re
from typing import Dict, List, Optional, Tuple

import config

# Palette lists
PALETTE_KEYS = list(config.PALETTES.keys())


def generate_logo(
    name: str,
    tone: str = "bold",
    style_preference: Optional[str] = None,
    feedback: str = "",
    seed_offset: int = 0,
) -> Tuple[str, List[str], str, Dict[str, str]]:
    """
    Generate an SVG logo, 4-color palette, and tagline.
    Takes seed_offset and feedback into account so revisions always produce a fresh, improved design.
    """
    initial = (name[0].upper() if name and name[0].isalnum() else "N")
    clean_name = htmllib.escape(name)

    # 1. Choose Palette
    p_keys = PALETTE_KEYS
    # Feedback-driven palette overrides
    if "purple" in feedback.lower() or "violet" in feedback.lower():
        palette = config.PALETTES["electric_violet"]
    elif "green" in feedback.lower() or "emerald" in feedback.lower():
        palette = config.PALETTES["cyber_emerald"]
    elif "yellow" in feedback.lower() or "orange" in feedback.lower() or "neobrutal" in feedback.lower():
        palette = config.PALETTES["neobrutal_yellow"]
    elif "blue" in feedback.lower() or "cyan" in feedback.lower() or "ocean" in feedback.lower():
        palette = config.PALETTES["ocean_pulse"]
    elif "red" in feedback.lower() or "crimson" in feedback.lower() or "pink" in feedback.lower():
        palette = config.PALETTES["crimson_neo"]
    elif "minimal" in feedback.lower() or "clean" in feedback.lower() or "black" in feedback.lower():
        palette = config.PALETTES["pure_minimal"]
    else:
        # Offset seed guarantees new palette on each retry
        p_index = (sum(ord(c) for c in name) + seed_offset) % len(p_keys)
        palette = config.PALETTES[p_keys[p_index]]

    c_dark, c_primary, c_accent, c_light = palette[0], palette[1], palette[2], palette[3]

    # 2. Choose Design Style (0 to 5)
    design_idx = (sum(ord(c) for c in name) // 3 + seed_offset) % 6
    if "minimal" in feedback.lower():
        design_idx = 3  # Minimalist Monogram
    elif "cyber" in feedback.lower() or "ring" in feedback.lower() or "glow" in feedback.lower():
        design_idx = 0  # Concentric Orbit
    elif "shield" in feedback.lower() or "badge" in feedback.lower():
        design_idx = 4  # Diamond Shield
    elif "spark" in feedback.lower() or "star" in feedback.lower() or "playful" in feedback.lower():
        design_idx = 5  # Radiant Spark

    style_names = [
        "Concentric Cyber Orbit",
        "Interlocking Isometric Hex",
        "Dynamic Aerodynamic Spark",
        "Minimal Precision Monogram",
        "Apex Cybernetic Shield",
        "Radiant Star Emblem",
    ]
    chosen_style = style_names[design_idx]

    # 3. Construct SVG Elements based on design
    if design_idx == 0:
        # Concentric Cyber Orbit
        body = f"""
        <circle cx="100" cy="100" r="92" fill="{c_dark}"/>
        <circle cx="100" cy="100" r="74" fill="none" stroke="{c_primary}" stroke-width="6" stroke-dasharray="16 10"/>
        <circle cx="100" cy="100" r="50" fill="{c_accent}" opacity="0.25"/>
        <circle cx="100" cy="100" r="38" fill="{c_primary}"/>
        <text x="100" y="114" font-family="-apple-system, sans-serif" font-size="44" font-weight="900" text-anchor="middle" fill="{c_light}">{initial}</text>
        """
    elif design_idx == 1:
        # Interlocking Isometric Hex
        body = f"""
        <rect width="200" height="200" rx="36" fill="{c_dark}"/>
        <polygon points="100,26 166,64 166,136 100,174 34,136 34,64" fill="{c_primary}"/>
        <polygon points="100,48 146,74 146,126 100,152 54,126 54,74" fill="{c_accent}"/>
        <polygon points="100,68 126,84 126,116 100,132 74,116 74,84" fill="{c_dark}"/>
        <text x="100" y="112" font-family="-apple-system, sans-serif" font-size="34" font-weight="800" text-anchor="middle" fill="{c_light}">{initial}</text>
        """
    elif design_idx == 2:
        # Dynamic Aerodynamic Spark
        body = f"""
        <rect width="200" height="200" rx="44" fill="{c_dark}"/>
        <path d="M40 140 Q100 40 160 140 Q100 80 40 140 Z" fill="{c_accent}"/>
        <path d="M50 155 Q100 70 150 155 Q100 110 50 155 Z" fill="{c_primary}"/>
        <circle cx="100" cy="80" r="18" fill="{c_light}"/>
        <text x="100" y="87" font-family="-apple-system, sans-serif" font-size="20" font-weight="900" text-anchor="middle" fill="{c_dark}">{initial}</text>
        """
    elif design_idx == 3:
        # Minimal Precision Monogram
        body = f"""
        <rect width="200" height="200" rx="28" fill="{c_dark}"/>
        <circle cx="100" cy="100" r="68" fill="none" stroke="{c_primary}" stroke-width="4"/>
        <line x1="100" y1="20" x2="100" y2="180" stroke="{c_accent}" stroke-width="2" opacity="0.4"/>
        <line x1="20" y1="100" x2="180" y2="100" stroke="{c_accent}" stroke-width="2" opacity="0.4"/>
        <rect x="55" y="55" width="90" height="90" rx="14" fill="{c_primary}"/>
        <text x="100" y="118" font-family="Helvetica, Arial, sans-serif" font-size="62" font-weight="800" text-anchor="middle" fill="{c_light}">{initial}</text>
        """
    elif design_idx == 4:
        # Apex Cybernetic Shield
        body = f"""
        <rect width="200" height="200" rx="36" fill="{c_dark}"/>
        <path d="M100 24 L170 56 L170 116 Q170 168 100 184 Q30 168 30 116 L30 56 Z" fill="{c_primary}"/>
        <path d="M100 44 L152 70 L152 116 Q152 152 100 166 Q48 152 48 116 L48 70 Z" fill="{c_accent}"/>
        <text x="100" y="122" font-family="Arial, sans-serif" font-size="52" font-weight="900" text-anchor="middle" fill="{c_light}">{initial}</text>
        """
    else:
        # Radiant Star Emblem
        body = f"""
        <circle cx="100" cy="100" r="95" fill="{c_dark}"/>
        <path d="M100 25 L122 78 L175 100 L122 122 L100 175 L78 122 L25 100 L78 78 Z" fill="{c_primary}"/>
        <circle cx="100" cy="100" r="32" fill="{c_accent}"/>
        <text x="100" y="112" font-family="-apple-system, sans-serif" font-size="36" font-weight="900" text-anchor="middle" fill="{c_light}">{initial}</text>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200" role="img" aria-label="{clean_name} Logo">
    {body}
</svg>"""

    # 4. Generate Tone-Aligned 6-Word Tagline
    tone_dict = config.TONES.get(tone, config.TONES["bold"])
    tagline = tone_dict["tagline"]

    metadata = {
        "style": chosen_style,
        "primary_color": c_primary,
        "accent_color": c_accent,
        "dark_bg": c_dark,
        "tagline": tagline,
    }

    return svg, palette, tagline, metadata


def format_logo_delivery(name: str, svg: str, palette: List[str], tagline: str, meta: Dict[str, str]) -> str:
    """Format logo delivery as a concise, beautiful chat output."""
    palette_str = " | ".join(palette)
    return f"""🎨 **BRAND LOGO & IDENTITY: {name.upper()}**
• **Style Concept:** {meta.get('style', 'Custom Geometric Emblem')}
• **Palette:** `{palette_str}` (Base, Primary, Accent, Contrast)
• **Official Tagline:** *"{tagline}"*

```xml
{svg}
```
*(Tip: Save the code above as `logo.svg` to use directly in web & apps. Say "create another logo" or "make it purple and minimal" to improvise anytime!)*"""
