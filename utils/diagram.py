"""Renders a formation's saved points as an SVG field diagram."""

FIELD_W = 480
FIELD_H = 300
LOS_Y = FIELD_H * 0.62  # line of scrimmage sits below center so there's room to draw routes/splits upfield


def render_formation_svg(points, title="", highlight_color="#1f6feb"):
    """points: list of {"label": str, "x": 0-100, "y": 0-100} (x=left/right, y=0 top(deep)/100 backfield)"""
    svg_parts = [
        f'<svg viewBox="0 0 {FIELD_W} {FIELD_H}" xmlns="http://www.w3.org/2000/svg" style="background:#2d5a34;border-radius:8px;width:100%;max-width:480px">'
    ]
    # yard lines
    for i in range(1, 6):
        y = FIELD_H * i / 6
        svg_parts.append(f'<line x1="0" y1="{y}" x2="{FIELD_W}" y2="{y}" stroke="#ffffff33" stroke-width="1"/>')
    # line of scrimmage
    svg_parts.append(f'<line x1="0" y1="{LOS_Y}" x2="{FIELD_W}" y2="{LOS_Y}" stroke="#ffffff" stroke-width="2"/>')

    for p in points or []:
        x = float(p["x"]) / 100 * FIELD_W
        y = float(p["y"]) / 100 * FIELD_H
        label = str(p.get("label", "?"))
        svg_parts.append(f'<circle cx="{x}" cy="{y}" r="14" fill="{highlight_color}" stroke="white" stroke-width="1.5"/>')
        svg_parts.append(
            f'<text x="{x}" y="{y+5}" font-size="13" font-weight="700" fill="white" text-anchor="middle" font-family="Arial">{label}</text>'
        )

    if title:
        svg_parts.append(
            f'<text x="10" y="20" font-size="14" fill="white" font-family="Arial" font-weight="600">{title}</text>'
        )

    svg_parts.append("</svg>")
    return "".join(svg_parts)
