#!/usr/bin/env python3
"""
Generate an ADTC-compliant A0 portrait research poster.

Output:
- output/poster/adtc_poster_a0.pdf
- output/poster/adtc_poster_a0_preview.png
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A0
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "output" / "poster"
PDF_PATH = OUT_DIR / "adtc_poster_a0.pdf"
PREVIEW_PATH = OUT_DIR / "adtc_poster_a0_preview.png"


# Colors chosen for high-contrast readability on print and screen.
BG = colors.HexColor("#EEF3FA")
HEADER_BG = colors.HexColor("#0B3A66")
SECTION_BG = colors.HexColor("#FFFFFF")
SECTION_TITLE_BG = colors.HexColor("#0F4C81")
TEXT_PRIMARY = colors.HexColor("#102235")
TEXT_MUTED = colors.HexColor("#355070")
ACCENT_POSITIVE = colors.HexColor("#0B7A56")
ACCENT_NEGATIVE = colors.HexColor("#B03A2E")
ACCENT_NEUTRAL = colors.HexColor("#DDE7F2")


TITLE = "Evaluative Benchmarking of Code Mode vs Standard MCP in Agentic Workflows"
AUTHORS = "Oselumese Agbonrofo, Abasiono Mbat, Abaniwonnda Oladimeji"
AFFILIATION = "Pan-Atlantic University, Lagos, Nigeria"
SUBHEAD = "African Deep Tech Conference 2026"

# Increased typography scale to better utilize A0 page space.
SECTION_TITLE_SIZE = 46
BODY_SIZE = 28
BODY_LEADING = 36
BODY_GAP = 12
BODY_PAD = 26


def _make_wrap_safe(text: str) -> str:
    """Insert soft break opportunities into long URL-like tokens."""
    tokens: list[str] = []
    for token in text.split(" "):
        if token.startswith("http://") or token.startswith("https://"):
            token = token.replace("://", ":// ").replace("/", "/ ").replace("-", "- ").replace("_", "_ ").replace(".", ". ")
        elif len(token) > 28 and ("/" in token or "_" in token or "-" in token):
            token = token.replace("/", "/ ").replace("-", "- ").replace("_", "_ ")
        tokens.append(token)
    return " ".join(tokens)


def wrap_bullet_lines(items: list[str], width: float, font: str, size: int) -> list[list[str]]:
    wrapped: list[list[str]] = []
    for item in items:
        wrapped.append(simpleSplit(f"- {_make_wrap_safe(item)}", font, size, width))
    return wrapped


def estimate_bullets_height(
    items: list[str],
    width: float,
    body_font: str = "Helvetica",
    body_size: int = BODY_SIZE,
    leading: int = BODY_LEADING,
    item_gap: int = BODY_GAP,
) -> float:
    groups = wrap_bullet_lines(items, width, body_font, body_size)
    return sum((len(lines) * leading) + item_gap for lines in groups)


def draw_card(
    c: canvas.Canvas,
    title: str,
    x: float,
    y_top: float,
    width: float,
    body_height: float,
    title_size: int = SECTION_TITLE_SIZE,
    pad: int = BODY_PAD,
) -> dict[str, float]:
    title_lines = simpleSplit(title, "Helvetica-Bold", title_size, width - (2 * pad))
    title_height = max(68, len(title_lines) * (title_size + 4) + 18)
    total_height = title_height + body_height
    y_bottom = y_top - total_height

    c.setFillColor(SECTION_BG)
    c.roundRect(x, y_bottom, width, total_height, 14, fill=1, stroke=0)

    c.setFillColor(SECTION_TITLE_BG)
    c.roundRect(x, y_top - title_height, width, title_height, 14, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", title_size)
    ty = y_top - title_size - 8
    for line in title_lines:
        c.drawString(x + pad, ty, line)
        ty -= title_size + 4

    return {
        "content_x": x + pad,
        "content_y_top": y_top - title_height - pad,
        "content_w": width - (2 * pad),
        "content_h": body_height - (2 * pad),
        "y_bottom": y_bottom,
        "next_y": y_bottom - 28,
    }


def draw_text_fit_in_cell(
    c: canvas.Canvas,
    text: str,
    x: float,
    y_bottom: float,
    w: float,
    h: float,
    *,
    bold: bool = False,
    max_size: int = 24,
    min_size: int = 14,
    pad: int = 8,
) -> None:
    font_name = "Helvetica-Bold" if bold else "Helvetica"
    size = max_size
    while size > min_size and c.stringWidth(text, font_name, size) > (w - (2 * pad)):
        size -= 1

    c.setFont(font_name, size)
    c.setFillColor(TEXT_PRIMARY)
    text_x = x + (w / 2.0)
    text_y = y_bottom + ((h - size) / 2.0) + 2
    c.drawCentredString(text_x, text_y, text)


def draw_bullet_section(
    c: canvas.Canvas,
    title: str,
    items: list[str],
    x: float,
    y_top: float,
    width: float,
) -> float:
    body_size = BODY_SIZE
    leading = BODY_LEADING
    item_gap = BODY_GAP
    pad = BODY_PAD

    content_width = width - (2 * pad)
    text_height = estimate_bullets_height(
        items,
        content_width,
        body_font="Helvetica",
        body_size=body_size,
        leading=leading,
        item_gap=item_gap,
    )
    body_height = text_height + (2 * pad) + 8

    card = draw_card(c, title, x, y_top, width, body_height)
    y = card["content_y_top"] - 2
    c.setFillColor(TEXT_PRIMARY)
    c.setFont("Helvetica", body_size)

    wrapped_groups = wrap_bullet_lines(items, card["content_w"], "Helvetica", body_size)
    for lines in wrapped_groups:
        for line in lines:
            c.drawString(card["content_x"], y, line)
            y -= leading
        y -= item_gap

    return card["next_y"]


def draw_architecture_section(c: canvas.Canvas, x: float, y_top: float, width: float) -> float:
    body_height = 1040
    card = draw_card(c, "Architecture Comparison", x, y_top, width, body_height)
    cx = card["content_x"]
    cy_top = card["content_y_top"]
    cw = card["content_w"]
    ch = card["content_h"]

    lane_gap = 24
    lane_w = (cw - lane_gap) / 2.0
    left_x = cx
    right_x = cx + lane_w + lane_gap

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(TEXT_MUTED)
    c.drawString(left_x, cy_top, "Regular MCP Path")
    c.drawString(right_x, cy_top, "Code Mode Path")

    regular = ["User task", "LLM call", "Tool call", "LLM call", "Tool call", "Repeat loop", "Final response"]
    codemode = ["User task", "LLM generates code", "Sandbox execution", "Batched tool ops", "Final response"]

    node_h = 60
    node_gap = 13
    start_y = cy_top - 60

    def draw_flow(nodes: list[str], lane_x: float, fill_color: colors.Color) -> None:
        y = start_y
        c.setFont("Helvetica", 25)
        for idx, node in enumerate(nodes):
            c.setFillColor(fill_color)
            c.roundRect(lane_x, y - node_h, lane_w, node_h, 8, fill=1, stroke=0)
            c.setFillColor(TEXT_PRIMARY)
            c.drawString(lane_x + 14, y - 39, node)
            if idx < len(nodes) - 1:
                mid_x = lane_x + (lane_w / 2.0)
                c.setStrokeColor(TEXT_MUTED)
                c.setLineWidth(2.2)
                c.line(mid_x, y - node_h - 2, mid_x, y - node_h - node_gap + 2)
                c.line(mid_x, y - node_h - node_gap + 2, mid_x - 7, y - node_h - node_gap + 10)
                c.line(mid_x, y - node_h - node_gap + 2, mid_x + 7, y - node_h - node_gap + 10)
            y -= node_h + node_gap

    draw_flow(regular, left_x, colors.HexColor("#E8EEF7"))
    draw_flow(codemode, right_x, colors.HexColor("#E4F2EC"))

    caption = (
        "Code Mode compresses repeated tool turns into one generated program. "
        "This reduces round trips on models that benefit from batching."
    )
    c.setFont("Helvetica", 26)
    c.setFillColor(TEXT_PRIMARY)
    y = card["y_bottom"] + 88
    for line in simpleSplit(caption, "Helvetica", 26, cw):
        c.drawString(cx, y, line)
        y -= 32

    return card["next_y"]


def draw_results_section(c: canvas.Canvas, x: float, y_top: float, width: float) -> float:
    body_height = 860
    card = draw_card(c, "Results", x, y_top, width, body_height)
    cx = card["content_x"]
    cy = card["content_y_top"]
    cw = card["content_w"]

    table_top = cy
    row_h = 66
    rows = [
        ["Model", "Time Change", "Iteration Change", "Token Change"],
        ["Opus 4.6", "-58.2%", "-68.6%", "-75.5%"],
        ["GPT-5.2", "+251.4%", "0.0%", "+84.3%"],
    ]
    col_w = [cw * 0.28, cw * 0.24, cw * 0.24, cw * 0.24]

    y = table_top
    for r, row in enumerate(rows):
        row_top = y
        row_bottom = row_top - row_h
        x_cursor = cx
        for i, value in enumerate(row):
            w = col_w[i]
            c.setFillColor(colors.HexColor("#D9E6F5") if r == 0 else colors.white)
            c.rect(x_cursor, row_bottom, w, row_h, fill=1, stroke=1)
            draw_text_fit_in_cell(
                c,
                value,
                x_cursor,
                row_bottom,
                w,
                row_h,
                bold=(r == 0),
                max_size=24 if r == 0 else 26,
                min_size=14,
                pad=8,
            )
            x_cursor += w
        y -= row_h

    chart_top = y - 24
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(TEXT_PRIMARY)
    c.drawString(cx, chart_top, "Average Latency (seconds)")

    bars = [
        ("Opus 4.6 Regular", 43.26, colors.HexColor("#4A6FA5")),
        ("Opus 4.6 Code Mode", 18.10, colors.HexColor("#0B7A56")),
        ("GPT-5.2 Regular", 11.17, colors.HexColor("#4A6FA5")),
        ("GPT-5.2 Code Mode", 39.24, colors.HexColor("#B03A2E")),
    ]
    max_value = 45.0
    label_w = 290
    bar_w = cw - label_w - 100
    bar_h = 40
    bar_gap = 30

    y = chart_top - 40
    c.setFont("Helvetica", 27)
    for label, value, color in bars:
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(cx, y - 4, label)
        c.setFillColor(ACCENT_NEUTRAL)
        c.rect(cx + label_w, y - 18, bar_w, bar_h, fill=1, stroke=0)
        c.setFillColor(color)
        c.rect(cx + label_w, y - 18, bar_w * (value / max_value), bar_h, fill=1, stroke=0)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(cx + label_w + bar_w + 12, y - 4, f"{value:.2f}s")
        y -= (bar_h + bar_gap)

    c.setFont("Helvetica", 27)
    c.setFillColor(TEXT_PRIMARY)
    validation_text = "Validation parity: 8/8 scenarios passed for both agents on both models."
    vy = card["y_bottom"] + 78
    for line in simpleSplit(validation_text, "Helvetica", 27, cw):
        c.drawString(cx, vy, line)
        vy -= 32

    return card["next_y"]


def build_poster(pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(pdf_path), pagesize=A0)
    w, h = A0

    # Background
    c.setFillColor(BG)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Header
    header_h = 340
    c.setFillColor(HEADER_BG)
    c.rect(0, h - header_h, w, header_h, fill=1, stroke=0)

    c.setFillColor(colors.white)
    title_font = 66
    title_lines = simpleSplit(TITLE, "Helvetica-Bold", title_font, w - 180)
    ty = h - 90
    c.setFont("Helvetica-Bold", title_font)
    for line in title_lines:
        c.drawCentredString(w / 2.0, ty, line)
        ty -= 70

    c.setFont("Helvetica", 34)
    c.drawCentredString(w / 2.0, ty - 8, AUTHORS)
    c.drawCentredString(w / 2.0, ty - 50, AFFILIATION)
    c.setFont("Helvetica", 28)
    c.drawCentredString(w / 2.0, ty - 80, SUBHEAD)

    # Column layout
    margin = 58
    gap = 30
    col_w = (w - (2 * margin) - (2 * gap)) / 3.0
    top_y = h - header_h - 100

    x1 = margin
    x2 = margin + col_w + gap
    x3 = margin + (2 * (col_w + gap))

    # Column 1
    y1 = top_y
    y1 = draw_bullet_section(
        c,
        "Abstract",
        [
            "Benchmark compares Code Mode vs standard MCP tool calling in 8 validated accounting workflows.",
            "Models tested: Opus 4.6 and GPT-5.2.",
            "Both agent paths used identical tools, shared state, and the same validators.",
            "Measured metrics: latency, iterations, total tokens, success, and validation rate.",
        ],
        x1,
        y1,
        col_w,
    )
    y1 = draw_bullet_section(
        c,
        "Introduction and Background",
        [
            "Multi-turn MCP loops can grow context and increase model round trips.",
            "Code Mode generates Python once and executes in a restricted sandbox.",
            "This design enables batching with loops, variables, and control flow.",
        ],
        x1,
        y1,
        col_w,
    )
    y1 = draw_bullet_section(
        c,
        "Objectives and Questions",
        [
            "Quantify time, iteration, and token differences between both agent modes.",
            "Check reliability with strict end-state validators across all scenarios.",
            "Evaluate safety controls for generated code execution.",
            "Assess deployment relevance in resource-constrained African contexts.",
        ],
        x1,
        y1,
        col_w,
    )
    y1 = draw_bullet_section(
        c,
        "Methodology",
        [
            "Regular agent: native MCP function calls with iterative model turns.",
            "Code Mode agent: Python generation and RestrictedPython execution.",
            "Shared setup: 11 accounting tools, common mutable state, 8 scenarios.",
            "Sandbox controls: import allowlist, timeout, memory cap, tool-call audit logs.",
        ],
        x1,
        y1,
        col_w,
    )
    # Column 2
    y2 = top_y
    y2 = draw_architecture_section(c, x2, y2, col_w)
    y2 = draw_results_section(c, x2, y2, col_w)
    _ = draw_bullet_section(
        c,
        "Findings",
        [
            "Opus 4.6: Code Mode was faster in 7 of 8 scenarios.",
            "GPT-5.2: regular MCP calling was faster in all 8 scenarios.",
            "Sandbox overhead remained low (about 7-10 ms average).",
            "Accuracy was unchanged: 8/8 validation for both approaches.",
        ],
        x2,
        y2,
        col_w,
    )

    # Column 3
    y3 = top_y
    y3 = draw_bullet_section(
        c,
        "Discussion and Implications",
        [
            "Code Mode is not universally better; behavior depends on model characteristics.",
            "Routing strategy should be model-specific and benchmark-driven.",
            "For some models, fewer round trips improve responsiveness and cost.",
            "For others, code-generation overhead can outweigh batching gains.",
        ],
        x3,
        y3,
        col_w,
    )
    y3 = draw_bullet_section(
        c,
        "Technical Emphasis",
        [
            "Targets deep-tech constraints: bandwidth instability, compute limits, and cost pressure.",
            "Supports practical African workflows: bookkeeping, invoicing, reconciliation.",
            "Restricted execution improves safety when running generated code.",
        ],
        x3,
        y3,
        col_w,
    )
    y3 = draw_bullet_section(
        c,
        "Conclusion and Future Work",
        [
            "The benchmark provides a reproducible basis for model-level routing decisions.",
            "Code Mode is high leverage for Opus 4.6, but not yet for GPT-5.2.",
            "Next steps: tune prompts and adapters, then rerun to confirm stable policy.",
        ],
        x3,
        y3,
        col_w,
    )
    y3 = draw_bullet_section(
        c,
        "References",
        [
            "Anthropic Engineering, Code execution with MCP (anthropic.com).",
            "Cloudflare, Code Mode (blog.cloudflare.com).",
            "RestrictedPython documentation (restrictedpython.readthedocs.io).",
        ],
        x3,
        y3,
        col_w,
    )
    _ = draw_bullet_section(
        c,
        "Acknowledgements",
        [
            "Pan-Atlantic University, African Deep Tech Conference organizers, and project contributors.",
        ],
        x3,
        y3,
        col_w,
    )

    c.showPage()
    c.save()


def render_preview(pdf_path: Path, png_path: Path, dpi: int = 120) -> None:
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(pdf_path))
    page = doc[0]
    scale = dpi / 72.0
    bitmap = page.render(scale=scale)
    pil_image = bitmap.to_pil()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    pil_image.save(png_path)
    page.close()
    doc.close()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_poster(PDF_PATH)
    render_preview(PDF_PATH, PREVIEW_PATH, dpi=120)
    print(f"Wrote {PDF_PATH}")
    print(f"Wrote {PREVIEW_PATH}")


if __name__ == "__main__":
    main()
