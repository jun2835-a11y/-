"""기하 정확성 테스트.

렌더된 SVG 문자열을 파싱해, 벡터/빗면/물체의 방향이 삼각함수로
계산한 값과 정확히 일치하는지 검증한다. (눈대중 좌표 금지 원칙 확인)
"""
import math
import re

import pytest

from physlib import components as C
from physlib import primitives as P


# ── 헬퍼: SVG 파싱 ─────────────────────────────────────────────────
def _lines(svg):
    return [tuple(map(float, m)) for m in re.findall(
        r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"',
        svg)]


def _polygons(svg):
    out = []
    for pts in re.findall(r'<polygon points="([^"]+)"', svg):
        coords = [tuple(map(float, p.split(","))) for p in pts.split()]
        out.append(coords)
    return out


def _cross(ax, ay, bx, by):
    return ax * by - ay * bx


def _parallel_err(ax, ay, bx, by):
    """두 벡터를 단위화한 뒤 외적 크기. 0에 가까울수록 평행.

    SVG 좌표는 소수 2자리로 반올림되므로, 길이에 비례하는 반올림 오차를
    없애기 위해 단위벡터로 정규화한 뒤 비교한다.
    """
    la = math.hypot(ax, ay)
    lb = math.hypot(bx, by)
    return abs(_cross(ax / la, ay / la, bx / lb, by / lb))


# ── 텍스트 마크업 ──────────────────────────────────────────────────
def test_tokenize_subscript():
    assert P._tokenize("m_1") == [("m", "normal"), ("1", "sub")]


def test_tokenize_group_and_super():
    assert P._tokenize("x^{2}") == [("x", "normal"), ("2", "sup")]


def test_greek_substitution():
    svg = P.text(0, 0, r"\theta")
    assert "θ" in svg and "\\theta" not in svg


# ── 벡터 방향 정확성 ───────────────────────────────────────────────
def test_vector_tip_is_exact():
    svg = P.vector(100, 100, 40, 0, "T")
    tip = _polygons(svg)[0][0]        # 첫 점이 화살촉 끝
    assert tip == pytest.approx((140, 100), abs=0.01)


@pytest.mark.parametrize("deg", [0, 20, 30, 37, 45, 53, 90, 135])
def test_vector_is_parallel_to_requested_direction(deg):
    th = math.radians(deg)
    ux, uy = math.cos(th), -math.sin(th)     # 화면 좌표(수학 각, y 반전)
    svg = P.vector(50, 50, ux * 70, uy * 70)
    x1, y1, x2, y2 = _lines(svg)[0]
    assert _parallel_err(x2 - x1, y2 - y1, ux, uy) < 1e-3


# ── 빗면 기하 ──────────────────────────────────────────────────────
@pytest.mark.parametrize("deg", [15, 30, 37, 45, 60])
def test_incline_apex_trig(deg):
    (ax, ay), (bx, by) = P.incline_apex(70, 300, deg, 200)
    th = math.radians(deg)
    assert (bx, by) == pytest.approx((70 + 200 * math.cos(th),
                                      300 - 200 * math.sin(th)), abs=1e-6)


@pytest.mark.parametrize("deg", [20, 30, 45])
def test_incline_surface_slope(deg):
    defs, body = P.incline(70, 300, deg, 200)
    tri = _polygons(body)[0]
    (ax, ay), (cx, cy), (bx, by) = tri     # A(아래좌), C(아래우 직각), B(위)
    th = math.radians(deg)
    # 빗변 A→B 방향은 (cosθ, -sinθ)에 정확히 평행
    assert _parallel_err(bx - ax, by - ay,
                         math.cos(th), -math.sin(th)) < 1e-3
    # 밑변 A→C는 수평
    assert (cy - ay) == pytest.approx(0, abs=0.01)


# ── 빗면 위 물체가 면과 평행 ───────────────────────────────────────
def test_oriented_block_edge_parallel():
    th = math.radians(30)
    u = (math.cos(th), -math.sin(th))
    svg = P.oriented_block(200, 200, u[0], u[1], 30, 20)
    c0, c1, c2, c3 = _polygons(svg)[0]
    edge = (c1[0] - c0[0], c1[1] - c0[1])
    assert _parallel_err(edge[0], edge[1], u[0], u[1]) < 1e-3


# ── 컴포넌트 스모크 & 불변식 ───────────────────────────────────────
def test_fbd_has_one_arrowhead_per_force():
    forces = [{"label": "N", "angle": 90}, {"label": "mg", "angle": 270},
              {"label": "F", "angle": 30}]
    svg = C.free_body_diagram(forces, "m")
    assert len(_polygons(svg)) == len(forces)   # 화살촉 = 힘 개수


@pytest.mark.parametrize("kw", [
    dict(angle=30),
    dict(angle=45, friction=True, show_decomp=True),
    dict(angle=20, tension_labels=("T_1", "T_2")),
])
def test_incline_pulley_renders(kw):
    svg = C.incline_pulley(**kw)
    assert svg.startswith("<svg") and svg.rstrip().endswith("</svg>")
    assert len(_polygons(svg)) >= 2             # 최소한 빗면 + 화살촉들


def test_spring_mass_orientations():
    for o in ("horizontal", "vertical"):
        svg = C.spring_mass(o)
        assert "<svg" in svg and "polyline" in svg   # 용수철 polyline 존재