"""복원 데모: 한글 텍스트 + MathJax 임베드 수식을 한 페이지 벡터로 조립."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physlib.render import rasterize

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RDIR = os.path.join(HERE, "outputs", "_restore")
M = json.load(open(os.path.join(RDIR, "manifest.json"), encoding="utf-8"))

W = 880
LM = 44
INK = "#111827"
ACCENT = "#1d4ed8"
FONT = "NanumGothic, 'Malgun Gothic', sans-serif"
FS = 18
parts = []


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tw(s, fs=FS):
    w = 0.0
    for ch in s:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3:
            w += 0.98 * fs
        elif 0x2460 <= o <= 0x2473:
            w += 1.08 * fs
        elif ch == " ":
            w += 1.0 * fs
        elif ch == " ":
            w += 0.30 * fs
        elif ch.isdigit():
            w += 0.56 * fs
        elif ch.isalpha():
            w += 0.55 * fs
        elif ch in "[](),.:?~":
            w += 0.34 * fs
        else:
            w += 0.55 * fs
    return w


def text(x, y, s, fs=FS, bold=False, color=INK, anchor="start"):
    weight = 700 if bold else 400
    parts.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{fs}" '
        f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{esc(s)}</text>'
    )
    return tw(s, fs)


def math(mid, x, baseY):
    m = M[mid]
    y = baseY - m["ascent"]
    parts.append(
        f'<svg x="{x:.1f}" y="{y:.1f}" width="{m["w"]:.1f}" height="{m["h"]:.1f}" '
        f'viewBox="{m["viewBox"]}">{m["inner"]}</svg>'
    )
    return m["w"]


# ── 발문 ───────────────────────────────────────────────────────────
y = 64
x = LM
x += text(x, y, "3.", bold=True) + 8
x += text(x, y, "수열 ")
x += math("seq", x, y) + 4
x += text(x, y, "에 대하여  ")
x += math("eq0", x, y) + 6
x += text(x, y, " 일 때,")
text(W - LM, y, "[3점]", color="#6b7280", anchor="end")

y += 46
x = LM
x += math("ans", x, y) + 4
x += text(x, y, "의 값은?")

# ── 선택지 ─────────────────────────────────────────────────────────
y += 50
text(LM, y, "① 1  ② 2  ③ 3"
            "  ④ 4  ⑤ 5")

# ── 구분선 ─────────────────────────────────────────────────────────
y += 26
parts.append(f'<line x1="{LM}" y1="{y}" x2="{W-LM}" y2="{y}" '
             f'stroke="#e5e7eb" stroke-width="1"/>')

# ── 출제의도 ───────────────────────────────────────────────────────
y += 40
text(LM, y, "출제의도", bold=True, color=ACCENT)
text(LM + tw("출제의도") + 8, y, ":  시그마의 정의와 성질을 이용하여 수열의 합을 구할 수 있는가?")

# ── 정답풀이 ───────────────────────────────────────────────────────
y += 46
text(LM, y, "정답풀이", bold=True, color=ACCENT)

x_sol = LM + 18
x_eq = x_sol + M["lhs"]["w"]           # '=' 정렬 기준 x
y += max(40, M["s1"]["h"] + 12)
math("s1", x_sol, y)
for sid in ["s2", "s3", "s4"]:
    y += max(38, M[sid]["h"] + 12)
    math(sid, x_eq, y)                 # 선행 '='를 기준선에 정렬

y += 56
x = LM
x += text(x, y, "에서  ")
math("efrom", x, y)

y += 64
x = LM
x += text(x, y, "따라서  ")
math("eans", x, y)

# ── 정답 ───────────────────────────────────────────────────────────
y += 50
ans_w = tw("정답 ⑤", 19)
cx = (W - ans_w) / 2
cx += text(cx, y, "정답 ", fs=19, bold=True)
text(cx, y, "⑤", fs=19, bold=True, color=ACCENT)

H = y + 40
doc = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H:.0f}" '
       f'viewBox="0 0 {W} {H:.0f}"><rect width="{W}" height="{H:.0f}" fill="#ffffff"/>'
       + "".join(parts) + "</svg>")

svg_path = os.path.join(RDIR, "page.svg")
open(svg_path, "w", encoding="utf-8").write(doc)
rasterize(doc, os.path.join(RDIR, "page.png"), zoom=2.0)
print("composed page.svg / page.png  (H=%.0f)" % H)