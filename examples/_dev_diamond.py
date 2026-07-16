import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physlib.plane import render_plane
from physlib.render import save

cx, cy, d = 310, 235, 120
second = (cx, cy - d)          # 2루 (위)
first = (cx + d, cy)           # 1루 (오른)
third = (cx - d, cy)           # 3루 (왼)
home = (cx, cy + d)            # 홈 (아래)
player = (first[0] + 0.32 * (second[0] - first[0]),
          first[1] + 0.32 * (second[1] - first[1]))


def base(p, s=7):              # 베이스(작은 마름모)
    x, y = p
    return {"type": "polygon", "points": [(x, y - s), (x + s, y), (x, y + s), (x - s, y)],
            "fill": "#ffffff", "stroke": "#3b3a36", "width": 1.4}


e = [
    # 흙(탄) 영역
    {"type": "polygon", "fill": "#e7dcc4", "stroke": "none",
     "points": [(cx, cy - d - 30), (cx + d + 30, cy), (cx, cy + d + 30), (cx - d - 30, cy)]},
    # 내야(그린)
    {"type": "polygon", "fill": "#d2e6d5", "stroke": "#3b3a36", "width": 2,
     "points": [second, first, home, third]},
    # 주자 시선/거리 선 (3루→주자)
    {"type": "segment", "a": third, "b": player, "color": "#2f6fb0", "width": 2},
    # 각도
    {"type": "angle", "at": third, "r": 32, "start": 11, "end": 45, "label": r"\theta_2"},
    {"type": "angle", "at": second, "r": 26, "start": 225, "end": 315, "label": r"\theta_1"},
    # 베이스
    base(second), base(first), base(third), base(home),
    # 주자
    {"type": "point", "at": player, "dot": True},
    # 라벨
    {"type": "label", "at": (cx, cy - d - 40), "text": "Second base", "size": 12},
    {"type": "label", "at": (first[0] + 16, first[1] + 4), "text": "First base", "anchor": "start", "size": 12},
    {"type": "label", "at": (third[0] - 16, third[1] + 4), "text": "Third base", "anchor": "end", "size": 12},
    {"type": "label", "at": (cx, cy + d + 44), "text": "Home", "size": 12},
    {"type": "label", "at": (player[0] + 12, player[1] - 6), "text": "Player", "anchor": "start", "size": 12},
    {"type": "label", "at": (232, 166), "text": "27 m", "size": 13},
    {"type": "label", "at": (player[0] + 20, player[1] + 24), "text": "9 m", "anchor": "start", "size": 13},
]

svg = render_plane(e, width=560, height=430)
_, png = save(svg, "outputs/_plane/diamond")
print("saved:", png)