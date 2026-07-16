import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from physlib.solid import render_solid
from physlib.render import save

# 비전 추출 결과(원기둥 4번 문제) — API가 뱉을 형식 그대로
extracted = {
    "type": "cylinder",
    "points": [
        {"name": "A", "ring": "bottom", "t": 152},
        {"name": "B", "ring": "bottom", "t": 44},
        {"name": "C", "ring": "top", "t": 22},
        {"name": "D", "ring": "top", "t": 250},
        {"name": "H", "ring": "bottom", "t": 250},
    ],
    "edges": [
        {"a": "A", "b": "B"}, {"a": "B", "b": "C"}, {"a": "C", "b": "D"},
        {"a": "D", "b": "A"}, {"a": "A", "b": "H"}, {"a": "B", "b": "H"},
        {"a": "D", "b": "H", "dashed": True},
    ],
    "ring_labels": [
        {"text": "C_2", "ring": "top", "t": 200, "dx": -22, "dy": -8},
        {"text": "C_1", "ring": "bottom", "t": 205, "dx": -30, "dy": 20},
    ],
}

svg = render_solid(extracted)
_, png = save(svg, "outputs/_solid/cylinder_extracted")
print("saved:", png)