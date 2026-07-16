"""physlib — 물리 문제 다이어그램 부품 라이브러리.

3계층: primitives(원자 그리기) → components(완성 다이어그램) → render(CLI).

사용:
    from physlib import components as C
    from physlib.render import save
    save(C.incline_pulley(angle=30), "outputs/PHY-0001")

(하위 모듈을 지연 로드해 `python -m physlib.render` 실행 시 중복 임포트
 경고가 나지 않게 한다.)
"""

__all__ = ["primitives", "components", "constants", "render"]