# 장면 그래프 스키마 (Scene Graph)

사진 복원 파이프라인의 **중간 표현(IR)**. 비전 모델이 사진을 읽어 이
JSON을 채우고, `physlib.scene.render_scene()`이 이를 깨끗한 벡터(SVG)로
그린다. 4종 컴포넌트 템플릿에 묶이지 않으므로 임의 배치를 복원할 수 있다.

## 규약
- **좌표계**: 화면 좌표 — 원점 좌상단, y는 아래로 증가. 단위 px.
- **각도**: 수학 규약 — 0°=오른쪽, 90°=위, 반시계 양수.
  (`force.dir_deg`, `angle.start/end` 공통)
- **라벨 마크업**: 아래첨자 `m_1`, 위첨자 `x^2`, 그리스 `\theta \mu \alpha`.

## 최상위 구조
```json
{
  "canvas": { "width": 620, "height": 380 },
  "elements": [ /* 아래 요소들을 그리는 순서대로 */ ]
}
```
`elements`는 배열 순서대로 렌더된다(뒤 요소가 위에 겹침). 보통 경계·구조물을
먼저, 힘·라벨을 나중에.

## 요소 타입

### 구조물 / 고정면
| type | 필드 | 설명 |
|---|---|---|
| `incline` | `at:[x,y]`, `angle`, `length`, `label?` | 빗면. `at`=각 θ가 있는 왼쪽아래 꼭짓점. 내부 해칭. |
| `ground` / `floor` | `from:[x,y]`, `to:[x,y]`, `depth?` | 수평 바닥(아래쪽 해칭). |
| `ceiling` | `from`, `to` | 천장(위쪽 해칭). |
| `wall` | `from`, `to` | 수직 벽(왼쪽 해칭). `side` 로 반대편 지정 가능. |
| `pulley` | `at:[x,y]`, `r?` | 도르래. |

### 물체 / 연결
| type | 필드 | 설명 |
|---|---|---|
| `block` | `at:[x,y]`, `w?`, `h?`, `label?`, `angle?` | 물체 사각형. `angle` 주면 그 각도로 기울여 배치(빗면 위 물체). |
| `rope` | `path:[[x,y],...]`, `width?` | 줄/선(꺾은선). 도르래를 넘는 경로는 꼭짓점으로 표현. |
| `spring` | `from`, `to`, `coils?`, `label?` | 용수철. |

### 힘 / 주석
| type | 필드 | 설명 |
|---|---|---|
| `force` | `at:[x,y]`, `dir_deg`, `length?`, `label?`, `kind?`, `dash?` | 힘 화살표. `kind`∈{gravity,normal,tension,friction,applied} → 색 자동. `at`=작용점(꼬리). |
| `angle` | `at:[x,y]`, `start`, `end`, `r?`, `label?` | 각도 호. |
| `label` | `at:[x,y]`, `text`, `anchor?`, `halo?` | 자유 텍스트. |

## 비전 추출 지침 (프롬프트 설계용)
사진을 이 스키마로 옮길 때 모델에게 지시할 원칙:

1. **정밀 좌표 추적 금지, 상대 배치 파악** — 물체가 "빗면 위/바닥 위/매달림"
   중 무엇인지, 힘이 어느 물체에 어느 방향인지를 먼저 판정. 좌표는 캔버스
   비율로 대략 배치하고 정밀도는 검토 단계에서 보정.
2. **각도·질량 수치는 지문 우선** — 그림에서 각도를 재지 말고, 문제 텍스트에
   "30°", "2 kg" 가 있으면 그 값을 쓴다. 없으면 그림에서 근사.
3. **힘의 종류를 분류** — 화살표를 gravity/normal/tension/friction/applied 로
   분류해 `kind`에 넣으면 색이 자동 통일된다.
4. **모르면 비운다** — 불확실한 요소는 생략하고 플래그. 사람이 검토 UI에서
   추가하는 편이 잘못 그리는 것보다 낫다.

## 파이프라인에서의 위치
```
사진 ─▶ (Claude 비전 + tool use, 출력=이 스키마) ─▶ scene.json
     ─▶ 검토·수정 UI (generator 확장) ─▶ render_scene() ─▶ 깨끗한 SVG
```
tool use의 input_schema로 이 구조를 그대로 강제하면 형식 오류 없이
검증된 JSON만 받는다.