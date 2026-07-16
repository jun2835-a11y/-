"""원자 단위 그리기 함수 — 좌표/스타일만 받아 SVG 조각(str)을 반환한다.

좌표계 주의:
    SVG는 화면 좌표(y가 아래로 증가)를 쓴다. 물리적으로 "위"가 +y가
    되도록 하려면 컴포넌트 계층에서 방향을 뒤집어 넘긴다. 여기서는
    받은 좌표를 그대로 그린다.

각도 규약(angle_arc 등):
    수학 표준(반시계, +x축 기준). 화면 좌표로 변환할 때 y부호를 뒤집어
    (cx + r·cosθ, cy − r·sinθ) 로 계산하므로, 각이 커질수록 위로 돈다.
"""
from __future__ import annotations

import math

from .constants import (
    ARROW_HALF_W,
    ARROW_LEN,
    COLOR_DIM,
    COLOR_FORCE,
    COLOR_HATCH,
    COLOR_STRUCTURE,
    COLOR_TEXT,
    FONT_FAMILY,
    FONT_SIZE,
    GREEK,
    LABEL_OFFSET,
    STROKE_FORCE,
    STROKE_STRUCTURE,
    STROKE_THIN,
    WHITE,
)

_SUB_SCALE = 0.68   # 첨자 폰트 비율


# ── 유틸 ───────────────────────────────────────────────────────────
def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _tokenize(text: str):
    """라벨 마크업을 (내용, 종류) 세그먼트 목록으로 분해.

    지원: \\theta 등 그리스 문자, `_x`/`_{...}` 아래첨자, `^x`/`^{...}` 위첨자.
    """
    for name, ch in GREEK.items():
        text = text.replace(name, ch)
    segs = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in "_^":
            kind = "sub" if c == "_" else "sup"
            i += 1
            if i < n and text[i] == "{":
                j = text.index("}", i)
                content = text[i + 1:j]
                i = j + 1
            elif i < n:
                content = text[i]
                i += 1
            else:
                content = ""
            segs.append((content, kind))
        else:
            j = i
            while j < n and text[j] not in "_^":
                j += 1
            segs.append((text[i:j], "normal"))
            i = j
    return segs


# ── 텍스트 / 라벨 ──────────────────────────────────────────────────
def _build_tspans(s, size):
    """마크업을 tspan 문자열로. dy 누적을 막고자 목표-현재 시프트 차만 이동."""
    segs = _tokenize(s)
    cur = 0.0
    parts = []
    for content, kind in segs:
        if kind == "sub":
            target, fs = 0.30 * size, size * _SUB_SCALE
        elif kind == "sup":
            target, fs = -0.45 * size, size * _SUB_SCALE
        else:
            target, fs = 0.0, size
        dy = target - cur
        cur = target
        parts.append(
            f'<tspan dy="{dy:.2f}" font-size="{fs:.1f}">{_esc(content)}</tspan>'
        )
    return "".join(parts)


def text(x, y, s, size=FONT_SIZE, color=COLOR_TEXT, anchor="middle",
         baseline="alphabetic", weight="normal", halo=False,
         halo_width=3.6):
    """수식 라벨. 아래/위 첨자와 그리스 문자를 지원한다.

    halo=True면 선 위에 겹쳐도 읽히도록 흰색 테두리를 뒤에 깐다.
    """
    tsp = _build_tspans(s, size)
    common = (
        f'x="{x:.2f}" y="{y:.2f}" font-family="{FONT_FAMILY}" '
        f'font-size="{size:.1f}" text-anchor="{anchor}" '
        f'dominant-baseline="{baseline}" font-weight="{weight}"'
    )
    fg = f'<text {common} fill="{color}">{tsp}</text>'
    if not halo:
        return fg
    bg = (f'<text {common} fill="none" stroke="{WHITE}" '
          f'stroke-width="{halo_width}" stroke-linejoin="round">{tsp}</text>')
    return bg + fg


def dim_label(x, y, s, **kw):
    """치수/수식 라벨 (text의 별칭, 기본 색은 치수색)."""
    kw.setdefault("color", COLOR_DIM)
    return text(x, y, s, **kw)


# ── SVG 문서 래퍼 ──────────────────────────────────────────────────
def svg_document(width, height, body, bg=WHITE, defs=""):
    """부품 조각들을 완전한 SVG 문서로 감싼다 (흰 배경 고정)."""
    defs_block = f"<defs>{defs}</defs>" if defs else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">'
        f'{defs_block}'
        f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" fill="{bg}"/>'
        f'{body}'
        f'</svg>'
    )


# ── 벡터 (힘 화살표) ───────────────────────────────────────────────
def vector(x, y, dx, dy, label=None, color=COLOR_FORCE, width=STROKE_FORCE,
           label_offset=LABEL_OFFSET, label_pos=None, label_anchor=None,
           dash=None):
    """(x,y)에서 (dx,dy)만큼 향하는 화살표. 삼각형 머리 포함.

    label_pos를 주면 라벨 위치를 강제한다(겹침 회피용). 기본은 화살촉
    바로 너머에 방향에 맞춰 배치한다.
    """
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return ""
    ux, uy = dx / L, dy / L            # 진행 방향 단위벡터
    px, py = -uy, ux                   # 수직 단위벡터
    tipx, tipy = x + dx, y + dy
    # 화살촉 밑변 중심(샤프트는 여기까지만 그려 머리를 뚫지 않음)
    basex, basey = tipx - ux * ARROW_LEN, tipy - uy * ARROW_LEN
    b1 = (basex + px * ARROW_HALF_W, basey + py * ARROW_HALF_W)
    b2 = (basex - px * ARROW_HALF_W, basey - py * ARROW_HALF_W)

    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    shaft = (
        f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{basex:.2f}" y2="{basey:.2f}" '
        f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"'
        f'{dash_attr}/>'
    )
    head = (
        f'<polygon points="{tipx:.2f},{tipy:.2f} '
        f'{b1[0]:.2f},{b1[1]:.2f} {b2[0]:.2f},{b2[1]:.2f}" fill="{color}"/>'
    )
    out = shaft + head
    if label:
        if label_pos is not None:
            lx, ly = label_pos
        else:
            lx = tipx + ux * label_offset
            ly = tipy + uy * label_offset
        if label_anchor is not None:
            anchor = label_anchor
        else:
            anchor = "start" if ux > 0.3 else "end" if ux < -0.3 else "middle"
        out += text(lx, ly, label, color=color, anchor=anchor,
                    baseline="central", halo=True)
    return out


# ── 물체 사각형 ────────────────────────────────────────────────────
def block(cx, cy, w, h, label=None, color=COLOR_STRUCTURE,
          fill="#f2f2f2", label_color=COLOR_TEXT):
    """(cx,cy)를 중심으로 한 폭 w·높이 h 사각형."""
    x, y = cx - w / 2, cy - h / 2
    out = (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
        f'rx="2" fill="{fill}" stroke="{color}" '
        f'stroke-width="{STROKE_STRUCTURE}"/>'
    )
    if label:
        out += text(cx, cy, label, color=label_color, anchor="middle",
                    baseline="central", halo=True)
    return out


def oriented_block(cx, cy, ux, uy, hl, hh, label=None, color=COLOR_STRUCTURE,
                   fill="#f2f2f2", label_color=COLOR_TEXT):
    """축 방향 (ux,uy)로 기울어진 사각형 (빗면 위 물체용).

    hl: 축 방향 반길이, hh: 수직 방향 반높이. 네 꼭짓점을 직접 계산해
    빗면과 정확히 평행하게 놓는다.
    """
    px, py = -uy, ux
    corners = [
        (cx - hl * ux - hh * px, cy - hl * uy - hh * py),
        (cx + hl * ux - hh * px, cy + hl * uy - hh * py),
        (cx + hl * ux + hh * px, cy + hl * uy + hh * py),
        (cx - hl * ux + hh * px, cy - hl * uy + hh * py),
    ]
    poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in corners)
    out = (
        f'<polygon points="{poly}" fill="{fill}" stroke="{color}" '
        f'stroke-width="{STROKE_STRUCTURE}" stroke-linejoin="round"/>'
    )
    if label:
        out += text(cx, cy, label, color=label_color, anchor="middle",
                    baseline="central", halo=True)
    return out


# ── 해칭 패턴 (고정면) ─────────────────────────────────────────────
def _hatched_polygon(points, clip_id, spacing=9.0):
    """다각형 내부를 45° 해칭으로 채운다(고정/솔리드 표시).

    points: [(x,y), ...]. clip_id는 문서 내 유일해야 한다.
    반환: (defs_str, body_str)
    """
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    poly = " ".join(f"{px:.2f},{py:.2f}" for px, py in points)
    defs = f'<clipPath id="{clip_id}"><polygon points="{poly}"/></clipPath>'
    # 45° 선: x - y = c 형태를 이동. c 범위를 넉넉히 잡아 전체를 덮는다.
    lines = []
    c = minx - maxy
    cmax = maxx - miny
    span = (maxx - minx) + (maxy - miny)
    while c <= cmax:
        # 선분: (c+miny, miny) → (c+maxy, maxy) 를 넉넉히 확장
        x1, y1 = c + miny - span, miny - span
        x2, y2 = c + maxy + span, maxy + span
        lines.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{COLOR_HATCH}" stroke-width="{STROKE_THIN}"/>'
        )
        c += spacing
    body = f'<g clip-path="url(#{clip_id})">{"".join(lines)}</g>'
    return defs, body


# ── 고정 경계 (벽/천장/바닥) ───────────────────────────────────────
def fixed_boundary(p1, p2, clip_id, depth=13.0, side=1, color=COLOR_STRUCTURE):
    """고정면: p1→p2 실선 경계 + 한쪽에 해칭 띠.

    side=+1이면 진행방향 왼쪽(법선 (-uy,ux))으로, -1이면 반대쪽으로 해칭.
    천장은 좌→우(side=-1: 위쪽), 벽은 위→아래(side=-1: 왼쪽) 식으로 쓴다.
    반환: (defs, body).
    """
    (x1, y1), (x2, y2) = p1, p2
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy * side, ux * side
    band = [(x1, y1), (x2, y2),
            (x2 + nx * depth, y2 + ny * depth),
            (x1 + nx * depth, y1 + ny * depth)]
    defs, hatch = _hatched_polygon(band, clip_id, spacing=8.0)
    line = (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{STROKE_STRUCTURE}"/>')
    return defs, hatch + line


# ── 빗면 (경사면) ──────────────────────────────────────────────────
def incline(x, y, angle, length, label=None, clip_id="incline_hatch",
            color=COLOR_STRUCTURE):
    """직각삼각형 빗면. (x,y)=왼쪽아래 꼭짓점(각 θ가 있는 곳).

    빗변(경사면)은 왼쪽아래 A → 오른쪽위 B 로 올라간다. 오른쪽아래 C에
    직각. 내부는 해칭으로 고정면임을 표시.

    반환: (defs_str, body_str) — svg_document(defs=...)에 넘길 것.
    """
    th = math.radians(angle)
    ax, ay = x, y                                   # 왼쪽아래(각 위치)
    cx, cy = x + length * math.cos(th), y           # 오른쪽아래(직각)
    bx, by = cx, y - length * math.sin(th)          # 오른쪽위(경사면 꼭대기)
    pts = [(ax, ay), (cx, cy), (bx, by)]
    defs, hatch = _hatched_polygon(pts, clip_id)
    poly = " ".join(f"{px:.2f},{py:.2f}" for px, py in pts)
    outline = (
        f'<polygon points="{poly}" fill="none" stroke="{color}" '
        f'stroke-width="{STROKE_STRUCTURE}" stroke-linejoin="round"/>'
    )
    body = hatch + outline
    if label:
        # 각도 라벨은 꼭짓점 A 안쪽에 배치
        lx = ax + 30 * math.cos(th / 2)
        ly = ay - 30 * math.sin(th / 2)
        body += text(lx, ly, label, color=COLOR_DIM, anchor="middle",
                     baseline="central")
    return defs, body


def incline_apex(x, y, angle, length):
    """빗면 경사면 위 특정 지점 좌표를 돌려주는 헬퍼.

    반환: A(하단), B(상단) 좌표. 컴포넌트가 물체·줄 배치에 사용.
    """
    th = math.radians(angle)
    a = (x, y)
    b = (x + length * math.cos(th), y - length * math.sin(th))
    return a, b


# ── 도르래 ─────────────────────────────────────────────────────────
def pulley(cx, cy, r, color=COLOR_STRUCTURE):
    """도르래: 바깥 원 + 홈(groove) + 중심 허브."""
    return (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{WHITE}" '
        f'stroke="{color}" stroke-width="{STROKE_STRUCTURE}"/>'
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r-3.5:.2f}" fill="none" '
        f'stroke="{color}" stroke-width="{STROKE_THIN}"/>'
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.4" fill="{color}"/>'
    )


# ── 줄 / 선 ────────────────────────────────────────────────────────
def rope(points, color=COLOR_STRUCTURE, width=1.8):
    """꺾은선 줄. points: [(x,y), ...]."""
    if len(points) < 2:
        return ""
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return (
        f'<polyline points="{d}" fill="none" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round" '
        f'stroke-linejoin="round"/>'
    )


# ── 용수철 ─────────────────────────────────────────────────────────
def spring(x1, y1, x2, y2, coils=6, amp=9.0, color=COLOR_STRUCTURE,
           lead=0.15):
    """(x1,y1)→(x2,y2) 지그재그 용수철. 양 끝에 곧은 리드선.

    coils: 산 개수. amp: 지그재그 진폭. lead: 양끝 곧은선 비율(0~0.5).
    """
    L = math.hypot(x2 - x1, y2 - y1)
    if L < 1e-6:
        return ""
    ux, uy = (x2 - x1) / L, (y2 - y1) / L      # 축 방향
    px, py = -uy, ux                            # 진폭 방향
    lead_len = L * lead
    coil_len = L - 2 * lead_len
    pts = [(x1, y1)]
    a = (x1 + ux * lead_len, y1 + uy * lead_len)
    pts.append(a)
    n = coils * 2
    for i in range(1, n):
        t = i / n
        side = amp if i % 2 == 1 else -amp
        bx = a[0] + ux * coil_len * t + px * side
        by = a[1] + uy * coil_len * t + py * side
        pts.append((bx, by))
    b = (x1 + ux * (lead_len + coil_len), y1 + uy * (lead_len + coil_len))
    pts.append(b)
    pts.append((x2, y2))
    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    return (
        f'<polyline points="{d}" fill="none" stroke="{color}" '
        f'stroke-width="{STROKE_STRUCTURE}" stroke-linecap="round" '
        f'stroke-linejoin="round"/>'
    )


# ── 각도 호 ────────────────────────────────────────────────────────
def angle_arc(cx, cy, r, start_deg, end_deg, label=None, color=COLOR_DIM):
    """(cx,cy) 중심, 반지름 r, start_deg→end_deg (수학 규약: 반시계) 호.

    라벨은 중간각 방향 바깥에 배치.
    """
    s = math.radians(start_deg)
    e = math.radians(end_deg)
    x1, y1 = cx + r * math.cos(s), cy - r * math.sin(s)
    x2, y2 = cx + r * math.cos(e), cy - r * math.sin(e)
    sweep = end_deg - start_deg
    large = 1 if abs(sweep) > 180 else 0
    # 화면 y가 아래로 향하므로, 수학적 반시계(양의 sweep)는 SVG sweep-flag=0.
    flag = 0 if sweep > 0 else 1
    out = (
        f'<path d="M {x1:.2f} {y1:.2f} A {r:.2f} {r:.2f} 0 {large} {flag} '
        f'{x2:.2f} {y2:.2f}" fill="none" stroke="{color}" '
        f'stroke-width="{STROKE_THIN}"/>'
    )
    if label:
        mid = math.radians((start_deg + end_deg) / 2)
        lr = r + 13
        lx, ly = cx + lr * math.cos(mid), cy - lr * math.sin(mid)
        out += text(lx, ly, label, color=color, anchor="middle",
                    baseline="central")
    return out