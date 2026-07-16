"""장면 그래프 재구성 시연 — 4종 템플릿에 없는 임의 배치를 복원.

'사진에서 읽어낸 장면'을 손으로 흉내낸 dict. 비전 단계가 이 dict를
채우면 그대로 재사용된다.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physlib.scene import render_scene
from physlib.render import save

# 두 물체가 바닥 위에서 줄로 연결, 오른쪽 물체를 15° 위로 당김 —
# incline_pulley/pulley_simple/spring_mass/free_body_diagram 어디에도
# 해당하지 않는 배치.
floor_y = 300
cyA = floor_y - 27
cyB = floor_y - 27
SCENE = {
    "canvas": {"width": 620, "height": 380},
    "elements": [
        {"type": "ground", "from": [40, floor_y], "to": [590, floor_y]},

        {"type": "block", "at": [180, cyA], "w": 74, "h": 54, "label": "m_1"},
        {"type": "block", "at": [380, cyB], "w": 74, "h": 54, "label": "m_2"},

        {"type": "rope", "path": [[217, cyA], [343, cyB]]},

        # m1: 장력(오른쪽), 마찰(왼쪽, 접촉면), 중력, 수직항력
        {"type": "force", "at": [180, cyA], "dir_deg": 0, "length": 58,
         "label": "T", "kind": "tension"},
        {"type": "force", "at": [180, floor_y], "dir_deg": 180, "length": 46,
         "label": "f", "kind": "friction"},
        {"type": "force", "at": [180, cyA], "dir_deg": 270, "length": 62,
         "label": "m_1 g", "kind": "gravity"},
        {"type": "force", "at": [180, cyA], "dir_deg": 90, "length": 62,
         "label": "N_1", "kind": "normal"},

        # m2: 외력 F를 15° 위로 당김, 장력(왼쪽), 중력, 수직항력
        {"type": "force", "at": [380, cyB], "dir_deg": 15, "length": 90,
         "label": "F", "kind": "applied"},
        {"type": "force", "at": [380, cyB], "dir_deg": 180, "length": 58,
         "label": "T", "kind": "tension"},
        {"type": "force", "at": [380, cyB], "dir_deg": 270, "length": 62,
         "label": "m_2 g", "kind": "gravity"},
        {"type": "force", "at": [380, cyB], "dir_deg": 90, "length": 62,
         "label": "N_2", "kind": "normal"},

        # F의 견인각 표시
        {"type": "angle", "at": [380, cyB], "r": 40, "start": 0, "end": 15,
         "label": "\\alpha"},
    ],
}


def main():
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "outputs", "_scene", "two_block_pull")
    _, png = save(render_scene(SCENE), out)
    print("saved:", png)


if __name__ == "__main__":
    main()