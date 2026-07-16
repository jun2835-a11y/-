"""변형 문제 시연: 같은 컴포넌트(incline_pulley)를 파라미터만 바꿔
5개 변형을 생성한다. 각도·라벨·마찰 유무·성분분해만 달라진다.

문제 DB에서 "변형 문제"를 대량 생성할 때의 사용 패턴을 보여준다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physlib import components as C          # noqa: E402
from physlib.render import save              # noqa: E402

# (문제ID, 파라미터) — 각도·마찰·분해·라벨만 바꾼다.
VARIANTS = [
    ("PHY-MEC-0101", dict(angle=20, m1_label="m_1", m2_label="m_2")),
    ("PHY-MEC-0102", dict(angle=30, friction=True)),
    ("PHY-MEC-0103", dict(angle=37, show_decomp=True)),
    ("PHY-MEC-0104", dict(angle=45, friction=True, show_decomp=True)),
    ("PHY-MEC-0105", dict(angle=53, m1_label="A", m2_label="B",
                          tension_labels=("T_1", "T_2"))),
]


def build():
    """[(id, svg), ...] 반환."""
    return [(pid, C.incline_pulley(**kw)) for pid, kw in VARIANTS]


def main(out_dir="outputs/variants"):
    for pid, svg in build():
        _, png = save(svg, os.path.join(out_dir, pid))
        print(f"{pid}: {png}")


if __name__ == "__main__":
    main()