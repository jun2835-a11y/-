import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physlib.solid import cylinder_figure
from physlib.render import save

# 원기둥 문제(4번) 손 파라미터 — 그림에 대략 맞춘 각도
points = {
    "A": {"ring": "bottom", "t": 150},   # 앞-왼쪽
    "B": {"ring": "bottom", "t": 40},    # 앞-오른쪽 아래
    "C": {"ring": "top", "t": 25},       # 윗면 오른쪽
    "D": {"ring": "top", "t": 250},      # 윗면 뒤-왼쪽
    "H": {"ring": "bottom", "t": 250},   # D의 밑면 수선의 발(같은 각도)
}
edges = [
    ("A", "B", False), ("B", "C", False), ("C", "D", False), ("D", "A", False),  # 사각형 ABCD
    ("A", "H", False), ("B", "H", False),                                        # 삼각형 ABH
    ("D", "H", True),                                                            # 수선(점선)
]
labels = [
    ("C_2", "top", 200, -18, -6),
    ("C_1", "bottom", 200, -18, 14),
]
svg = cylinder_figure(points, edges, labels_ring=labels)
_, png = save(svg, "outputs/_solid/cylinder")
print("saved:", png)