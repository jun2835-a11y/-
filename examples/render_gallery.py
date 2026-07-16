"""모든 예제를 렌더하고 gallery.html(격자 미리보기)을 생성한다.

실행:  python examples/render_gallery.py
결과:  outputs/gallery/*.png, gallery.html
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from physlib import components as C          # noqa: E402
from physlib import primitives as P          # noqa: E402
from physlib.render import save              # noqa: E402
from examples.variants import build as build_variants  # noqa: E402

GALLERY_DIR = os.path.join(ROOT, "outputs", "gallery")


def _fbd_demo():
    forces = [
        {"label": "N", "angle": 90, "type": "normal"},
        {"label": "mg", "angle": 270, "type": "gravity"},
        {"label": "F", "angle": 25, "mag": 1.2, "type": "applied"},
        {"label": "f", "angle": 180, "mag": 0.7, "type": "friction"},
    ]
    return C.free_body_diagram(forces, "m")


def _primitive_panels():
    """원자 부품 4종을 단독 패널로."""
    import math
    panels = {}
    # vector
    b = '<circle cx="150" cy="150" r="3" fill="#111"/>'
    b += P.vector(150, 150, 0, -90, "N", color=P.COLOR_FORCE)
    b += P.vector(150, 150, 0, 90, "mg", color="#2c7fb8")
    b += P.vector(150, 150, 100, 0, "T_1", color="#2e7d32")
    b += P.vector(150, 150, -80, -55, r"F\theta", color="#e67e22")
    panels["prim_vector"] = P.svg_document(300, 300, b)
    # block
    b = P.block(90, 80, 90, 56, "m_1")
    b += P.block(220, 90, 70, 70, "M")
    panels["prim_block"] = P.svg_document(320, 190, b)
    # incline
    defs, body = P.incline(40, 200, 30, 240, label=r"\theta")
    panels["prim_incline"] = P.svg_document(320, 250, body, defs=defs)
    # angle_arc
    cx, cy = 60, 190
    a = math.radians(35)
    b = f'<line x1="{cx}" y1="{cy}" x2="{cx+180}" y2="{cy}" stroke="#333" stroke-width="2"/>'
    b += (f'<line x1="{cx}" y1="{cy}" x2="{cx+180*math.cos(a):.1f}" '
          f'y2="{cy-180*math.sin(a):.1f}" stroke="#333" stroke-width="2"/>')
    b += P.angle_arc(cx, cy, 55, 0, 35, label=r"\theta")
    panels["prim_angle_arc"] = P.svg_document(300, 250, b)
    # spring / pulley / rope 원자 부품
    b = P.spring(30, 60, 250, 60, coils=7)
    b += P.pulley(150, 150, 26)
    b += P.rope([(30, 200), (120, 180), (210, 210)])
    panels["prim_spring_pulley_rope"] = P.svg_document(300, 250, b)
    return panels


def render_all():
    items = []  # (제목, png상대경로)

    def emit(name, svg, title):
        base = os.path.join(GALLERY_DIR, name)
        _, png = save(svg, base)
        rel = os.path.relpath(png or base + ".svg", ROOT).replace("\\", "/")
        items.append((title, rel))

    # 원자 부품
    for name, svg in _primitive_panels().items():
        emit(name, svg, name.replace("prim_", "primitive: "))

    # 4종 컴포넌트
    emit("comp_free_body_diagram", _fbd_demo(), "free_body_diagram")
    emit("comp_pulley_simple", C.pulley_simple("m_1", "m_2"),
         "pulley_simple")
    emit("comp_incline_pulley",
         C.incline_pulley(angle=35, friction=True, show_decomp=True),
         "incline_pulley (friction + decomp)")
    emit("comp_spring_mass_h", C.spring_mass("horizontal"),
         "spring_mass (horizontal)")
    emit("comp_spring_mass_v", C.spring_mass("vertical"),
         "spring_mass (vertical)")

    # 변형 5종
    for pid, svg in build_variants():
        emit(f"var_{pid}", svg, pid)

    return items


def build_html(items):
    cards = "\n".join(
        f'    <figure><img src="{rel}" alt="{title}">'
        f'<figcaption>{title}</figcaption></figure>'
        for title, rel in items
    )
    html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<title>physlib 부품 갤러리</title>
<style>
  body {{ background:#fff; color:#222; font-family:sans-serif; margin:24px; }}
  h1 {{ font-size:20px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr));
           gap:18px; }}
  figure {{ margin:0; border:1px solid #e2e2e2; border-radius:8px; padding:10px;
            background:#fff; }}
  img {{ width:100%; height:auto; display:block; }}
  figcaption {{ margin-top:8px; font-size:13px; color:#555; text-align:center; }}
</style></head>
<body>
  <h1>physlib 부품 갤러리 — {len(items)}개</h1>
  <div class="grid">
{cards}
  </div>
</body></html>
"""
    path = os.path.join(ROOT, "gallery.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def main():
    items = render_all()
    path = build_html(items)
    print(f"갤러리 생성: {path} ({len(items)}개 항목)")


if __name__ == "__main__":
    main()