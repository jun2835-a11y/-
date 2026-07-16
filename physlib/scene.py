"""장면 그래프 → 깨끗한 벡터(SVG).

사진 복원 파이프라인의 렌더 계층. 비전 모델이 사진을 읽어 채우는
"장면 그래프"(JSON/dict)를 받아, 검증된 primitives로 다시 그린다.

핵심: 장면 그래프는 4종 컴포넌트 템플릿에 묶이지 않는다. 물체·힘·경계·
라벨을 각자의 위치/각도/크기로 자유롭게 나열하므로, 사진 속 임의 배치를
그대로(단, 선은 교과서 품질로) 복원할 수 있다.

좌표계: 화면 좌표(y 아래로 증가). 각도(force.dir_deg, angle.*)는 수학
규약(0°=오른쪽, 90°=위). 스키마 상세는 docs/scene_schema.md 참고.
"""
from __future__ import annotations

import math

from . import primitives as P
from .constants import FORCE_PALETTE

# 경계(고정면) 종류별 기본 해칭 방향(side). override 가능.
_BOUNDARY_SIDE = {"ground": 1, "floor": 1, "ceiling": -1, "wall": 1}


def _force_color(el):
    return el.get("color") or FORCE_PALETTE.get(el.get("kind", "default"),
                                                FORCE_PALETTE["default"])


def render_scene(scene: dict) -> str:
    """장면 그래프 dict → 완전한 SVG 문서(str)."""
    canvas = scene.get("canvas", {})
    W = canvas.get("width", 560)
    H = canvas.get("height", 430)

    defs_parts: list[str] = []
    body_parts: list[str] = []

    for i, el in enumerate(scene.get("elements", [])):
        t = el.get("type")
        cid = f"scl{i}"                      # 요소별 유일 clip id

        if t == "incline":
            x, y = el["at"]
            d, b = P.incline(x, y, el["angle"], el["length"],
                             label=el.get("label"), clip_id=cid)
            defs_parts.append(d)
            body_parts.append(b)

        elif t in ("ground", "floor", "ceiling", "wall", "boundary"):
            p1, p2 = el["from"], el["to"]
            side = el.get("side", _BOUNDARY_SIDE.get(t, 1))
            d, b = P.fixed_boundary(tuple(p1), tuple(p2), cid,
                                    side=side, depth=el.get("depth", 13.0))
            defs_parts.append(d)
            body_parts.append(b)

        elif t == "block":
            cx, cy = el["at"]
            w = el.get("w", 64)
            h = el.get("h", 46)
            if "angle" in el:                # 빗면 위 등 기울어진 물체
                th = math.radians(el["angle"])
                body_parts.append(P.oriented_block(
                    cx, cy, math.cos(th), -math.sin(th), w / 2, h / 2,
                    label=el.get("label")))
            else:
                body_parts.append(P.block(cx, cy, w, h, label=el.get("label")))

        elif t == "pulley":
            cx, cy = el["at"]
            body_parts.append(P.pulley(cx, cy, el.get("r", 16)))

        elif t == "rope":
            pts = [tuple(p) for p in el["path"]]
            body_parts.append(P.rope(pts, width=el.get("width", 1.8)))

        elif t == "spring":
            (x1, y1), (x2, y2) = el["from"], el["to"]
            body_parts.append(P.spring(x1, y1, x2, y2,
                                       coils=el.get("coils", 7)))
            if el.get("label"):
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                body_parts.append(P.dim_label(mx, my - 16, el["label"]))

        elif t == "force":
            x, y = el["at"]
            th = math.radians(el["dir_deg"])
            L = el.get("length", 66)
            dx, dy = L * math.cos(th), -L * math.sin(th)
            body_parts.append(P.vector(
                x, y, dx, dy, el.get("label"), color=_force_color(el),
                dash=el.get("dash"),
                label_anchor=el.get("label_anchor")))

        elif t == "angle":
            cx, cy = el["at"]
            body_parts.append(P.angle_arc(
                cx, cy, el.get("r", 44), el["start"], el["end"],
                label=el.get("label")))

        elif t == "label":
            x, y = el["at"]
            body_parts.append(P.text(x, y, el["text"],
                                     anchor=el.get("anchor", "middle"),
                                     halo=el.get("halo", False)))
        else:
            raise ValueError(f"알 수 없는 장면 요소 타입: {t!r} (요소 #{i})")

    return P.svg_document(W, H, "".join(body_parts), defs="".join(defs_parts))