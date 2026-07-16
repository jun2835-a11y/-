"""렌더 계층 — SVG 문자열을 파일로, 그리고 PNG로 변환한다.

PNG 변환 백엔드는 resvg(순수 파이썬 휠, 시스템 의존성 없음)를 기본으로,
설치돼 있으면 cairosvg도 지원한다. 둘 다 없으면 SVG만 저장한다.
"""
from __future__ import annotations

import argparse
import json
import os

_PNG_BACKEND = None


def _get_backend():
    global _PNG_BACKEND
    if _PNG_BACKEND is not None:
        return _PNG_BACKEND
    try:
        import resvg_py  # noqa: F401
        _PNG_BACKEND = "resvg"
    except Exception:
        try:
            import cairosvg  # noqa: F401
            _PNG_BACKEND = "cairo"
        except Exception:
            _PNG_BACKEND = "none"
    return _PNG_BACKEND


def rasterize(svg: str, png_path: str, zoom: float = 2.0) -> bool:
    """SVG 문자열을 PNG 파일로 저장. 성공하면 True."""
    backend = _get_backend()
    if backend == "resvg":
        import resvg_py
        data = resvg_py.svg_to_bytes(svg_string=svg, zoom=zoom)
        with open(png_path, "wb") as f:
            f.write(bytes(data))
        return True
    if backend == "cairo":
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=png_path,
                         scale=zoom)
        return True
    return False


def save(svg: str, base_path: str, zoom: float = 2.0):
    """base_path 기준으로 .svg 와 .png 를 함께 저장.

    base_path는 확장자 없는 경로(예: outputs/PHY-0001).
    반환: (svg_path, png_path 또는 None)
    """
    os.makedirs(os.path.dirname(os.path.abspath(base_path)), exist_ok=True)
    svg_path = base_path + ".svg"
    png_path = base_path + ".png"
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)
    ok = rasterize(svg, png_path, zoom=zoom)
    return svg_path, (png_path if ok else None)


# ── CLI ────────────────────────────────────────────────────────────
def _build_component(name: str, params: dict) -> str:
    from . import components
    fn = getattr(components, name, None)
    if fn is None or not callable(fn):
        raise SystemExit(f"알 수 없는 컴포넌트: {name}")
    return fn(**params)


def main(argv=None):
    p = argparse.ArgumentParser(
        description="물리 다이어그램 컴포넌트를 SVG/PNG로 렌더한다.")
    p.add_argument("component", help="components.py 안의 함수 이름")
    p.add_argument("--params", default="{}",
                   help="컴포넌트 인자 JSON 문자열")
    p.add_argument("--params-file", help="컴포넌트 인자 JSON 파일 경로")
    p.add_argument("--id", dest="pid",
                   help="문제 ID (파일명으로 사용, 예: PHY-MEC-0042)")
    p.add_argument("--out-dir", default="outputs")
    p.add_argument("--zoom", type=float, default=2.0)
    args = p.parse_args(argv)

    if args.params_file:
        with open(args.params_file, encoding="utf-8") as f:
            params = json.load(f)
    else:
        params = json.loads(args.params)

    svg = _build_component(args.component, params)
    name = args.pid or args.component
    base = os.path.join(args.out_dir, name)
    svg_path, png_path = save(svg, base, zoom=args.zoom)
    print(f"저장: {svg_path}")
    print(f"저장: {png_path}" if png_path
          else "PNG 백엔드 없음 — SVG만 저장 (resvg-py 또는 cairosvg 설치).")


if __name__ == "__main__":
    main()