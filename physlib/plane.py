"""2D 평면도형 벡터 렌더러 — 다각형·원·선분·점·각도호·라벨·색칠영역.

삼각형/사각형/좌표도형/야구 다이아몬드류를 하나의 부품으로 커버한다.
좌표계: 화면(y 아래로 증가). 각도(angle)는 수학 규약(0=오른쪽, 90=위, 반시계).
요소(element) 타입:
    polygon  {points:[[x,y],..], fill?, stroke?, dashed?}
    circle   {at:[x,y], r, fill?, stroke?}
    segment  {a:[x,y], b:[x,y], dashed?, color?, width?}
    point    {at:[x,y], label?, lx?, ly?, dot?, anchor?}
    angle    {at:[x,y], start, end, r?, label?}
    label    {at:[x,y], text, anchor?, size?}
"""
from __future__ import annotations

import math

from . import primitives as P
from .constants import COLOR_STRUCTURE, COLOR_TEXT, STROKE_STRUCTURE, STROKE_THIN


def _fmt(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def render_plane(elements, width=620, height=470, bg=None):
    body = []
    for el in elements:
        t = el.get("type")

        if t == "polygon":
            fill = el.get("fill", "none")
            stroke = el.get("stroke", COLOR_STRUCTURE)
            da = ' stroke-dasharray="5,5"' if el.get("dashed") else ""
            body.append(
                f'<polygon points="{_fmt(el["points"])}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{el.get("width", STROKE_STRUCTURE)}" '
                f'stroke-linejoin="round"{da}/>')

        elif t == "circle":
            cx, cy = el["at"]
            body.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{el["r"]:.2f}" '
                f'fill="{el.get("fill", "none")}" stroke="{el.get("stroke", COLOR_STRUCTURE)}" '
                f'stroke-width="{el.get("width", STROKE_STRUCTURE)}"/>')

        elif t == "segment":
            (x1, y1), (x2, y2) = el["a"], el["b"]
            da = ' stroke-dasharray="5,5"' if el.get("dashed") else ""
            body.append(
                f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                f'stroke="{el.get("color", COLOR_STRUCTURE)}" '
                f'stroke-width="{el.get("width", STROKE_STRUCTURE)}" '
                f'stroke-linecap="round"{da}/>')

        elif t == "point":
            x, y = el["at"]
            if el.get("dot", True):
                body.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{COLOR_TEXT}"/>')
            if el.get("label"):
                body.append(P.text(x + el.get("lx", 10), y + el.get("ly", -8),
                                   el["label"], color=COLOR_TEXT,
                                   anchor=el.get("anchor", "start"), halo=True))

        elif t == "angle":
            x, y = el["at"]
            body.append(P.angle_arc(x, y, el.get("r", 26), el["start"], el["end"],
                                    label=el.get("label")))

        elif t == "label":
            x, y = el["at"]
            body.append(P.text(x, y, el["text"], color=el.get("color", COLOR_TEXT),
                               anchor=el.get("anchor", "middle"),
                               size=el.get("size", 15), halo=el.get("halo", True)))

        else:
            raise ValueError(f"알 수 없는 평면 요소: {t!r}")

    return P.svg_document(width, height, "".join(body), bg=bg or "#ffffff")