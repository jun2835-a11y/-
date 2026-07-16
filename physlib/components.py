"""완성 다이어그램 — primitives를 조합하고 물리적 의미를 인코딩한다.

각 함수는 파라미터를 받아 완전한 SVG 문서(str)를 반환한다.
(Phase 2에서 incline_pulley부터 채운다.)
"""
from __future__ import annotations

import math

from . import primitives as P
from .constants import FORCE_PALETTE


def incline_pulley(angle=30, m1_label="m_1", m2_label="m_2", friction=False,
                   show_decomp=False, tension_labels=("T", "T"),
                   width=560, height=430):
    """빗면 꼭대기 도르래를 통해 매달린 두 물체 (빗면 아타우드).

    빗면 위 물체 m1은 줄로 도르래를 넘어 수직으로 매달린 m2와 연결.
    - 장력 벡터는 빗면과 정확히 평행.
    - show_decomp: 중력 mg를 sinθ(빗면 방향)·cosθ(수직 방향) 성분으로 분해.
    - friction: 빗면 방향 마찰력 벡터 표시(방향은 예시).
    - tension_labels: (빗면쪽 장력, 매달린쪽 장력) 라벨.
    """
    th = math.radians(angle)
    c, s = math.cos(th), math.sin(th)

    # 빗면 기하 -------------------------------------------------------
    ax, ay = 96.0, height - 90.0            # 왼쪽아래 꼭짓점(각 θ)
    length = 300.0
    (Ax, Ay), (Bx, By) = P.incline_apex(ax, ay, angle, length)
    u = (c, -s)                             # 빗면 위쪽(A→B) 단위벡터
    n = (-s, -c)                            # 빗면 바깥 법선(면에서 나오는 쪽)

    defs, incline_body = P.incline(ax, ay, angle, length)

    # 도르래 --------------------------------------------------------
    r = 16.0
    Px, Py = Bx + 20.0, By - 18.0
    T1 = (Px + r * n[0], Py + r * n[1])     # 빗면쪽 줄이 닿는 접점
    T2 = (Px + r, Py)                        # 수직 줄이 닿는 접점(오른쪽)
    post = P.rope([(Bx, By), (Px, Py)], width=P.STROKE_STRUCTURE)
    pulley = P.pulley(Px, Py, r)

    # 빗면 위 물체 m1 ------------------------------------------------
    hl, hh = 34.0, 22.0
    t1 = 0.42
    spx, spy = Ax + t1 * (Bx - Ax), Ay + t1 * (By - Ay)   # 면 위 접점
    c1 = (spx + n[0] * hh, spy + n[1] * hh)               # 물체 중심
    m1 = P.oriented_block(c1[0], c1[1], u[0], u[1], hl, hh, label=m1_label)
    attach1 = (c1[0] + hl * u[0], c1[1] + hl * u[1])       # 줄 부착점(위쪽 면)
    rope_incline = P.rope([attach1, T1])

    # 매달린 물체 m2 -------------------------------------------------
    drop = 96.0
    m2w, m2h = 56.0, 48.0
    c2 = (T2[0], T2[1] + drop)
    m2 = P.block(c2[0], c2[1], m2w, m2h, label=m2_label)
    rope_hang = P.rope([T2, (c2[0], c2[1] - m2h / 2)])

    # 각도 호 --------------------------------------------------------
    arc = P.angle_arc(Ax, Ay, 46, 0, angle, label=r"\theta")

    # 힘 벡터 --------------------------------------------------------
    Lg = 70.0                                # 중력 기준 길이
    Lt = 66.0
    forces = []

    # m1: 장력(빗면 평행, 위쪽)
    forces.append(P.vector(c1[0], c1[1], u[0] * Lt, u[1] * Lt,
                           tension_labels[0], color=FORCE_PALETTE["tension"]))
    # m1: 수직항력 N (바깥 법선)
    Ln = Lg * c
    forces.append(P.vector(c1[0], c1[1], n[0] * Ln, n[1] * Ln, "N",
                           color=FORCE_PALETTE["normal"]))
    # m1: 중력
    g_label = m1_label + " g"
    if show_decomp:
        # 성분 분해: 빗면방향(아래) = mg sinθ, 수직방향(면속) = mg cosθ
        along = (-u[0] * Lg * s, -u[1] * Lg * s)     # 빗면 아래 방향
        perp = (-n[0] * Lg * c, -n[1] * Lg * c)      # 면 속으로
        forces.append(P.vector(c1[0], c1[1], along[0], along[1],
                               m1_label + r" g sin\theta",
                               color=FORCE_PALETTE["gravity"]))
        forces.append(P.vector(c1[0], c1[1], perp[0], perp[1],
                               m1_label + r" g cos\theta",
                               color=FORCE_PALETTE["gravity"]))
        # 원래 mg는 점선 대각 안내선으로
        forces.append(P.vector(c1[0], c1[1], 0, Lg, g_label,
                               color=FORCE_PALETTE["gravity"], dash="5,4"))
        # 성분 사각형(점선 보조선)
        gx, gy = c1[0], c1[1] + Lg
        forces.append(P.rope([(c1[0] + along[0], c1[1] + along[1]),
                              (gx, gy),
                              (c1[0] + perp[0], c1[1] + perp[1])],
                             color="#bbbbbb", width=1.0))
    else:
        forces.append(P.vector(c1[0], c1[1], 0, Lg, g_label,
                               color=FORCE_PALETTE["gravity"]))

    # m1: 마찰력 (빗면 방향, 예시로 아래쪽)
    if friction:
        Lf = 50.0
        forces.append(P.vector(spx, spy, -u[0] * Lf, -u[1] * Lf, "f",
                               color=FORCE_PALETTE["friction"]))

    # m2: 장력(위) / 중력(아래)
    forces.append(P.vector(c2[0], c2[1], 0, -Lt, tension_labels[1],
                           color=FORCE_PALETTE["tension"]))
    forces.append(P.vector(c2[0], c2[1], 0, Lg, m2_label + " g",
                           color=FORCE_PALETTE["gravity"]))

    body = (incline_body + post + rope_incline + rope_hang + pulley
            + m1 + m2 + arc + "".join(forces))
    return P.svg_document(width, height, body, defs=defs)


def free_body_diagram(forces, mass_label="m", width=380, height=380,
                      box=True):
    """자유물체도. 힘 목록을 받아 중심 물체 둘레에 자동 배치한다.

    forces: dict 목록. 각 항목 키:
        angle : 도(°), 수학 규약(0=오른쪽, 90=위).
        label : 라벨 문자열(마크업 지원).
        mag   : 상대 크기(길이 스케일용, 생략 시 1.0).
        type  : "gravity"/"normal"/"tension"/"friction"/"applied" (색 선택).
        color : 색 직접 지정(type보다 우선).
    """
    cx, cy = width / 2, height / 2
    mags = [f.get("mag", 1.0) for f in forces] or [1.0]
    mmax = max(mags)
    base, lo = 96.0, 52.0                    # 최대/최소 화살표 길이
    body = ""
    if box:
        body += P.block(cx, cy, 66, 46, mass_label)
    else:
        body += (f'<circle cx="{cx}" cy="{cy}" r="4" fill="#111"/>'
                 + P.text(cx + 12, cy + 16, mass_label, anchor="start"))
    for f in forces:
        a = math.radians(f["angle"])
        mag = f.get("mag", 1.0)
        L = lo + (base - lo) * (mag / mmax if mmax else 1.0)
        color = f.get("color") or FORCE_PALETTE.get(f.get("type", "default"),
                                                    FORCE_PALETTE["default"])
        body += P.vector(cx, cy, L * math.cos(a), -L * math.sin(a),
                         f.get("label"), color=color)
    return P.svg_document(width, height, body)


def pulley_simple(m1_label="m_1", m2_label="m_2", show_tension=True,
                  show_gravity=True, width=380, height=420):
    """천장에 매달린 단일 고정 도르래 양쪽에 두 물체."""
    cx = width / 2
    ceil_y = 46.0
    defs, ceil = P.fixed_boundary((cx - 150, ceil_y), (cx + 150, ceil_y),
                                  "ps_ceil", side=-1)
    r = 22.0
    Px, Py = cx, ceil_y + 44.0
    post = P.rope([(Px, ceil_y), (Px, Py - r)], width=P.STROKE_STRUCTURE)
    pulley = P.pulley(Px, Py, r)

    lx, rx = Px - r, Px + r                  # 줄이 도르래에 닿는 좌/우 접점
    y1, y2 = 300.0, 250.0                    # 두 물체 높이(비대칭)
    mw, mh = 54.0, 46.0
    rope_l = P.rope([(lx, Py), (lx, y1 - mh / 2)])
    rope_r = P.rope([(rx, Py), (rx, y2 - mh / 2)])
    b1 = P.block(lx, y1, mw, mh, m1_label)
    b2 = P.block(rx, y2, mw, mh, m2_label)

    forces = ""
    Lt, Lg = 58.0, 64.0
    if show_tension:
        forces += P.vector(lx, y1 - mh / 2, 0, -Lt, "T",
                           color=FORCE_PALETTE["tension"])
        forces += P.vector(rx, y2 - mh / 2, 0, -Lt, "T",
                           color=FORCE_PALETTE["tension"])
    if show_gravity:
        forces += P.vector(lx, y1 + mh / 2, 0, Lg, m1_label + " g",
                           color=FORCE_PALETTE["gravity"])
        forces += P.vector(rx, y2 + mh / 2, 0, Lg, m2_label + " g",
                           color=FORCE_PALETTE["gravity"])

    body = ceil + post + rope_l + rope_r + pulley + b1 + b2 + forces
    return P.svg_document(width, height, body, defs=defs)


def spring_mass(orientation="horizontal", k_label="k", m_label="m",
                show_forces=True, width=440, height=320):
    """용수철-질량계. orientation: "horizontal"(벽-바닥) 또는 "vertical"(천장)."""
    if orientation == "horizontal":
        floor_y = height - 80.0
        wall_x = 60.0
        mw, mh = 70.0, 60.0
        cx = 300.0
        cy = floor_y - mh / 2
        defs_w, wall = P.fixed_boundary((wall_x, floor_y - 150),
                                        (wall_x, floor_y), "sm_wall", side=1)
        defs_f, floor = P.fixed_boundary((wall_x, floor_y), (width - 30, floor_y),
                                         "sm_floor", side=1)
        blk = P.block(cx, cy, mw, mh, m_label)
        sp = P.spring(wall_x, cy, cx - mw / 2, cy, coils=7,
                      color=P.COLOR_STRUCTURE)
        klabel = P.dim_label((wall_x + cx - mw / 2) / 2, cy - 22, k_label)
        body = wall + floor + sp + blk + klabel
        if show_forces:
            Lg = 60.0
            body += P.vector(cx, cy, 66, 0, "F = -" + k_label + "x",
                             color=FORCE_PALETTE["applied"])
            body += P.vector(cx, cy + mh / 2, 0, Lg, m_label + " g",
                             color=FORCE_PALETTE["gravity"])
            body += P.vector(cx, cy - mh / 2, 0, -Lg, "N",
                             color=FORCE_PALETTE["normal"])
        return P.svg_document(width, height, body, defs=defs_w + defs_f)

    # vertical -------------------------------------------------------
    width, height = 300, 400
    cx = width / 2
    ceil_y = 46.0
    defs, ceil = P.fixed_boundary((cx - 90, ceil_y), (cx + 90, ceil_y),
                                  "sm_ceil", side=-1)
    mw, mh = 74.0, 62.0
    sp_top = ceil_y
    sp_bot = 210.0
    cy = sp_bot + mh / 2
    sp = P.spring(cx, sp_top, cx, sp_bot, coils=8, color=P.COLOR_STRUCTURE)
    blk = P.block(cx, cy, mw, mh, m_label)
    # k 라벨은 용수철 위쪽 오른편(힘 화살표와 겹치지 않게)
    klabel = P.dim_label(cx + 24, sp_top + (sp_bot - sp_top) * 0.30, k_label,
                         anchor="start")
    body = ceil + sp + blk + klabel
    if show_forces:
        Lg = 66.0
        # 중력: 물체 아래 중앙
        body += P.vector(cx, cy + mh / 2, 0, Lg, m_label + " g",
                         color=FORCE_PALETTE["gravity"])
        # 복원력: 용수철선과 겹치지 않게 중심선 왼쪽으로 오프셋
        fx = cx - 52
        body += P.vector(fx, cy - mh / 2, 0, -Lg, "F = " + k_label + "x",
                         color=FORCE_PALETTE["tension"], label_anchor="middle")
    return P.svg_document(width, height, body, defs=defs)