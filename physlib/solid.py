"""3D 입체 도형 (공간도형) 벡터 렌더러 — 1차: 원기둥 + 표시점.

접근: 3D 원기둥을 표준 사선(oblique) 투영으로 그린다. 원 밑면은 타원이 되고,
앞(near) 호는 실선·뒤(far) 호는 점선(숨은선). 원 위의 점은 각도(t)로 지정하면
타원 매개변수로 화면 좌표가 결정된다 → 눈대중 없이 수학으로 배치.

좌표계: 화면(y 아래로 증가). 타원 매개변수 t(도):
    점 = (cx + rx·cos t, cy_ring + ry·sin t)
    t=90 → 앞 중앙(관찰자에 가장 가까운 아래), t=270 → 뒤 중앙(먼 위쪽).
"""
from __future__ import annotations

import math

from . import primitives as P
from .constants import COLOR_STRUCTURE, COLOR_TEXT, STROKE_STRUCTURE, STROKE_THIN


def _pt(cx, cy_ring, rx, ry, t_deg):
    t = math.radians(t_deg)
    return (cx + rx * math.cos(t), cy_ring + ry * math.sin(t))


def _arc(cx, cy, rx, ry, t0, t1, n=64):
    pts = []
    for i in range(n + 1):
        t = math.radians(t0 + (t1 - t0) * i / n)
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return pts


def _poly(pts, dash=None, color=COLOR_STRUCTURE, width=STROKE_STRUCTURE):
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{d}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round"{da}/>')


def _line(p1, p2, dash=None, color=COLOR_STRUCTURE, width=STROKE_STRUCTURE):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{p1[0]:.2f}" y1="{p1[1]:.2f}" x2="{p2[0]:.2f}" '
            f'y2="{p2[1]:.2f}" stroke="{color}" stroke-width="{width}"{da}/>')


def _dot(p, r=3.0):
    return f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r}" fill="{COLOR_TEXT}"/>'


def cylinder_figure(points, edges, width=660, height=490,
                    r=150.0, squash=0.28, cyl_h=250.0, labels_ring=None):
    """원기둥 + 표시점 + 연결선.

    points: {name: {"ring": "top"|"bottom", "t": 각도}} — 원 위의 점.
    edges:  [(nameA, nameB, dashed_bool), ...] — 점 사이 선분.
    labels_ring: [(text, "top"|"bottom", t, dx, dy)] — C_1, C_2 등 원 라벨.
    """
    cx = width / 2
    cy_bot = height - 120.0
    cy_top = cy_bot - cyl_h
    rx, ry = r, r * squash

    body = []

    # ── 원기둥 몸체 ────────────────────────────────────────────────
    # 옆선 (좌/우 극점)
    body.append(_line((cx - rx, cy_top), (cx - rx, cy_bot)))
    body.append(_line((cx + rx, cy_top), (cx + rx, cy_bot)))
    # 윗면 타원: 앞 호(실선) + 뒤 호(실선) — 윗면은 다 보임
    body.append(_poly(_arc(cx, cy_top, rx, ry, 0, 360)))
    # 밑면 타원: 앞(아래) 호 실선, 뒤(위) 호 점선(숨은선)
    body.append(_poly(_arc(cx, cy_bot, rx, ry, 0, 180)))                 # 앞: 실선
    body.append(_poly(_arc(cx, cy_bot, rx, ry, 180, 360), dash="5,5",
                      width=STROKE_THIN))                                # 뒤: 점선

    # ── 점 좌표 계산 ───────────────────────────────────────────────
    P_ = {}
    for name, sp in points.items():
        cyr = cy_top if sp["ring"] == "top" else cy_bot
        P_[name] = _pt(cx, cyr, rx, ry, sp["t"])

    # ── 연결선 (도형) ──────────────────────────────────────────────
    for a, b, dashed in edges:
        body.append(_line(P_[a], P_[b], dash="5,5" if dashed else None,
                          width=STROKE_STRUCTURE))

    # ── 점 + 라벨 ──────────────────────────────────────────────────
    for name, p in P_.items():
        body.append(_dot(p))
        # 라벨은 원 중심축(cx)에서 바깥 + 위쪽으로 오프셋
        dx = 12 if p[0] >= cx else -12
        anchor = "start" if p[0] >= cx else "end"
        body.append(P.text(p[0] + dx, p[1] - 8, name, color=COLOR_TEXT,
                           anchor=anchor, halo=True))

    # ── 원 라벨 (C_1, C_2 등) ──────────────────────────────────────
    for text, ring, t, ddx, ddy in (labels_ring or []):
        cyr = cy_top if ring == "top" else cy_bot
        q = _pt(cx, cyr, rx, ry, t)
        body.append(P.text(q[0] + ddx, q[1] + ddy, text, color=COLOR_TEXT,
                           anchor="middle", halo=True))

    return P.svg_document(width, height, "".join(body))


def render_solid(data, **kw):
    """추출 JSON(dict) → SVG. 비전 추출 결과를 그대로 받는다.

    data = {
      "type": "cylinder",
      "points": [{"name","ring","t"}, ...],
      "edges":  [{"a","b","dashed"}, ...],
      "ring_labels": [{"text","ring","t","dx","dy"}, ...],
    }
    """
    if data.get("type") != "cylinder":
        raise ValueError(f"지원하지 않는 입체: {data.get('type')!r}")
    points = {p["name"]: {"ring": p["ring"], "t": p["t"]} for p in data["points"]}
    edges = [(e["a"], e["b"], bool(e.get("dashed"))) for e in data["edges"]]
    labels = [(l["text"], l["ring"], l["t"], l.get("dx", -18), l.get("dy", 0))
              for l in data.get("ring_labels", [])]
    return cylinder_figure(points, edges, labels_ring=labels, **kw)