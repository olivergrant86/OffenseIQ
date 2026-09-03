"""Renders a formation's saved points as a clean, Hudl-style diagram: a
compact white box with a horizontal line of scrimmage, tight filled dots
for the offensive line, and labeled circles for skill positions.

Kept deliberately simple (formation only, no routes yet) so Phase 2 can
layer route/blocking paths on top of the same player positions without
changing this file's data shape.
"""

FIELD_W = 300
FIELD_H = 170
LOS_Y = FIELD_H * 0.62

OL_LABELS = {"LT", "LG", "C", "RG", "RT", "T", "G"}

SKILL_COLORS = {
    "QB": "#6b7280",
}
DEFAULT_SKILL_COLOR = "#1f6feb"


def render_formation_svg(points, title="", highlight_color="#1f6feb"):
    """points: list of {"label": str, "x": 0-100, "y": 0-100}
    x = left(0) to right(100) of the field
    y = 0 (deep downfield) to 100 (deep backfield); LOS sits at ~62
    """
    svg_parts = [
        f'<svg viewBox="0 0 {FIELD_W} {FIELD_H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="background:#ffffff;border:1px solid #e2e2e2;border-radius:6px;width:100%;max-width:300px">'
    ]

    # line of scrimmage
    svg_parts.append(
        f'<line x1="6" y1="{LOS_Y}" x2="{FIELD_W-6}" y2="{LOS_Y}" stroke="#6a4fb3" stroke-width="2"/>'
    )

    for p in points or []:
        x = float(p["x"]) / 100 * FIELD_W
        y = float(p["y"]) / 100 * FIELD_H
        label = str(p.get("label", "?"))

        if label.upper() in OL_LABELS:
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="#1a1a1a"/>')
        else:
            color = SKILL_COLORS.get(label.upper(), highlight_color or DEFAULT_SKILL_COLOR)
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="9" fill="{color}" stroke="white" stroke-width="1.2"/>')
            svg_parts.append(
                f'<text x="{x}" y="{y+3.5}" font-size="8.5" font-weight="700" fill="white" '
                f'text-anchor="middle" font-family="Arial">{label}</text>'
            )

    if title:
        svg_parts.append(
            f'<text x="8" y="16" font-size="11" fill="#333" font-family="Arial" font-weight="600">{title}</text>'
        )

    svg_parts.append("</svg>")
    return "".join(svg_parts)
