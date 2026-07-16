# physlib — 물리 문제 다이어그램 생성 라이브러리

손그림을 파싱해 복원하는 대신, **검증된 부품 라이브러리 + 파라미터**로
교과서 품질의 역학 다이어그램(자유물체도·도르래·빗면·용수철)을 재생성한다.
선이 삐뚤거나 벡터가 어긋날 일이 없다 — 모든 좌표는 삼각함수로 계산된다.

HWP 문제 DB에 삽입할 SVG/PNG를 만들고, 파라미터만 바꿔 변형 문제를
대량 생성하는 것이 목적이다.

## 결과 미리보기

`gallery.html`을 브라우저로 열면 모든 부품·컴포넌트·변형 예제를 격자로 볼 수 있다.

| 컴포넌트 | 설명 |
|---|---|
| `free_body_diagram` | 자유물체도 — 힘 목록을 받아 중심 물체 둘레에 자동 배치 |
| `pulley_simple` | 천장 고정 도르래 양쪽에 두 물체 |
| `incline_pulley` | 빗면 + 도르래 (빗면 아타우드). 마찰·성분분해 옵션 |
| `spring_mass` | 용수철-질량계 (수평/수직) |

## 설치

```bash
python -m pip install -r requirements.txt
```

### 한글 폰트 (NanumGothic)

라벨은 NanumGothic으로 렌더한다. 시스템에 설치돼 있어야 한다.

- **Windows**: 대부분 기본 포함(`C:\Windows\Fonts\NanumGothic.ttf`).
  없으면 [나눔글꼴](https://hangeul.naver.com/font)에서 설치.
- **macOS**: `brew install --cask font-nanum-gothic`
- **Ubuntu/Debian**: `sudo apt install fonts-nanum`

폰트가 없으면 그리스 문자·한글이 네모(□)로 나온다.

### PNG 백엔드

기본 백엔드는 **resvg-py**(순수 파이썬 휠, 시스템 의존성 없음)다.
`cairosvg`가 설치돼 있으면 그것도 자동 인식한다. 단, Windows에서
cairosvg는 별도의 `libcairo-2.dll`이 필요하므로 resvg-py를 권장한다.
둘 다 없으면 SVG만 저장된다.

## 실행

### 전체 예제 + 갤러리 생성

```bash
python examples/render_gallery.py     # outputs/gallery/*.png 와 gallery.html
```

### 브라우저 생성기 (파이썬 불필요)

`web/generator.html`을 브라우저로 열면 파라미터를 조절하며 4종 다이어그램을
실시간 미리보고 **SVG/PNG 다운로드·SVG 복사**를 할 수 있다. 파이썬 라이브러리의
기하 로직을 그대로 JS로 포팅한 자립형 단일 파일이라 인터넷·설치가 필요 없다.
(PNG는 브라우저에 설치된 NanumGothic으로 렌더된다.)

### 변형 문제 5종 생성

```bash
python examples/variants.py           # outputs/variants/PHY-MEC-01xx.{svg,png}
```

### CLI로 단일 컴포넌트 렌더

파라미터를 JSON 파일로 넘기는 방식을 권장한다(셸 따옴표 이스케이프 회피,
특히 Windows PowerShell).

```bash
# examples/params_sample.json 예시를 참고
python -m physlib.render incline_pulley \
    --params-file examples/params_sample.json \
    --id PHY-MEC-0042

# 결과: outputs/PHY-MEC-0042.svg, outputs/PHY-MEC-0042.png
```

인라인 JSON도 가능하다(bash 기준):

```bash
python -m physlib.render incline_pulley \
    --params '{"angle": 37, "friction": true, "show_decomp": true}' \
    --id PHY-MEC-0042
```

주요 옵션: `--id`(파일명=문제ID), `--params`/`--params-file`(JSON),
`--out-dir`, `--zoom`(PNG 배율).

### 파이썬에서 직접

```python
from physlib import components as C
from physlib.render import save

svg = C.incline_pulley(angle=30, friction=True, show_decomp=True,
                       tension_labels=("T_1", "T_2"))
save(svg, "outputs/PHY-MEC-0042")     # .svg + .png 동시 저장
```

## 아키텍처 (3계층)

```
physlib/
  constants.py    # 색·선두께·폰트·화살촉 크기 등 스타일 상수 (중앙화)
  primitives.py   # 원자 부품: vector, block, incline, angle_arc,
                  #            pulley, rope, spring, oriented_block,
                  #            fixed_boundary, text/dim_label
  components.py   # 완성 다이어그램 4종 (물리적 의미가 여기 인코딩됨)
  render.py       # SVG→파일/PNG 변환 + CLI
```

- **primitives**는 좌표/스타일만 받아 SVG 조각(str)을 반환한다.
- **components**는 primitives를 조합하고, 벡터 방향·성분분해를
  삼각함수로 계산한다. 빗면 위 장력은 빗면과 정확히 평행,
  mg 분해 성분은 정확히 수직/평행이다.
- 모든 부품은 `constants.py`의 같은 선두께·폰트·색 규칙을 공유한다.

### 라벨 마크업

`text()`/`dim_label()` 및 모든 라벨은 다음을 지원한다.

- 아래첨자: `m_1`, `T_{12}`
- 위첨자: `x^2`, `v^{2}`
- 그리스 문자: `\theta \mu \alpha \phi ...` (또는 유니코드 직접 입력)

예) `"m_1 g sin\theta"` → m₁ g sinθ

## 좌표계 규약

- SVG 화면 좌표(y 아래로 증가)를 그대로 쓴다.
- 각도(`angle_arc`, `free_body_diagram`)는 **수학 표준**(0°=오른쪽,
  90°=위, 반시계). 화면 변환 시 y부호를 뒤집어 계산한다.

## 새 부품 추가하는 법

1. **primitives에 원자 함수 추가** — 좌표/스타일만 받고 SVG 조각(str)
   반환. 색·선두께는 반드시 `constants.py` 상수를 쓴다(하드코딩 금지).
   ```python
   def wedge(cx, cy, w, h, color=COLOR_STRUCTURE):
       ...
       return f'<polygon .../>'
   ```

2. **components에 완성 함수 추가** — primitives를 조합. 벡터 방향은
   `math.cos/sin`으로 계산하고 눈대중 좌표를 쓰지 않는다. 완전한 SVG
   문서는 `P.svg_document(w, h, body, defs=...)`로 감싼다.
   ```python
   def my_scene(angle=30, label="m"):
       defs, floor = P.fixed_boundary(...)
       body = floor + P.vector(...) + P.block(...)
       return P.svg_document(400, 300, body, defs=defs)
   ```

3. **예제 등록** — `examples/render_gallery.py`의 `render_all()`에
   `emit("comp_my_scene", C.my_scene(), "my_scene")` 한 줄 추가하면
   갤러리에 자동 포함된다. 변형은 `examples/variants.py` 패턴을 따른다.

4. **테스트 추가** — `tests/test_geometry.py`에 기하 불변식(방향 평행성,
   좌표 일치 등)을 파싱해 검증하는 테스트를 넣는다.

## 테스트

```bash
python -m pytest -q
```

기하 정확성(벡터 방향·빗면 기울기·물체 평행성)을 SVG 파싱으로 검증한다.
"""