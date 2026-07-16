"""TikZ 본문 → SVG. 서버에서 xelatex로 컴파일 후 SVG로 변환.

LaTeX 툴체인(xelatex + poppler의 pdftocairo)이 필요하다 → 배포는 Docker.
성공 시 SVG 문자열 반환, 실패 시 예외(로그 포함)를 던진다.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

# standalone 문서로 감싸는 프리앰블. 그림에 흔한 라이브러리를 미리 로드.
_PREAMBLE = r"""\documentclass[border=8pt]{standalone}
\usepackage{kotex}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{tikz-3dplot}
\usetikzlibrary{calc,angles,quotes,arrows.meta,patterns,decorations.pathmorphing,
  shapes.geometric,3d,positioning,intersections,through}
\begin{document}
%%BODY%%
\end{document}
"""


def render_tikz(tikz_body: str, timeout: int = 45) -> str:
    """TikZ 본문(\\begin{tikzpicture}...\\end{tikzpicture}) → SVG 문자열."""
    tmp = tempfile.mkdtemp(prefix="tikz_")
    try:
        tex = _PREAMBLE.replace("%%BODY%%", tikz_body)
        with open(os.path.join(tmp, "fig.tex"), "w", encoding="utf-8") as f:
            f.write(tex)
        proc = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "fig.tex"],
            cwd=tmp, capture_output=True, text=True, timeout=timeout,
        )
        pdf = os.path.join(tmp, "fig.pdf")
        if not os.path.exists(pdf):
            log = (proc.stdout or "")[-1600:]
            raise RuntimeError("xelatex 컴파일 실패\n" + log)
        svg = os.path.join(tmp, "fig.svg")
        subprocess.run(["pdftocairo", "-svg", pdf, svg], check=True, timeout=timeout)
        with open(svg, encoding="utf-8") as f:
            return f.read()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def available() -> bool:
    """xelatex·pdftocairo가 설치돼 있는지."""
    return bool(shutil.which("xelatex") and shutil.which("pdftocairo"))