"""중앙 스타일 상수. 모든 부품이 이 값을 공유해 일관성을 보장한다.

물리 문제 다이어그램은 "교과서 품질"이 목표이므로 선 두께/색/폰트를
한 곳에서 통제한다. 부품 함수는 절대 자체 색·두께를 하드코딩하지 않는다.
"""

# ── 색 (structure=회색, force=강조색) ──────────────────────────────
WHITE = "#ffffff"
COLOR_STRUCTURE = "#333333"   # 물체·빗면·도르래 등 구조물
COLOR_HATCH = "#888888"       # 고정면 해칭
COLOR_FORCE = "#c0392b"       # 힘 벡터 기본 강조색 (빨강)
COLOR_DIM = "#555555"         # 치수/보조선/각도 호
COLOR_TEXT = "#111111"        # 일반 라벨 텍스트

# 서로 다른 힘을 구분해야 할 때 쓰는 팔레트.
# 기본은 COLOR_FORCE 단색이지만, 컴포넌트가 힘 종류를 명확히 구분하고
# 싶을 때 아래에서 골라 vector(color=...)로 넘긴다. 모두 "강조색 계열"로
# 통일감을 유지한다.
FORCE_PALETTE = {
    "gravity":  "#c0392b",   # 중력 mg
    "normal":   "#2c7fb8",   # 수직항력 N
    "tension":  "#2e7d32",   # 장력 T
    "friction": "#8e44ad",   # 마찰력 f
    "applied":  "#e67e22",   # 외력 F
    "default":  COLOR_FORCE,
}

# ── 선 두께 ────────────────────────────────────────────────────────
STROKE_STRUCTURE = 2.0
STROKE_FORCE = 2.4
STROKE_THIN = 1.1            # 해칭·보조선·각도 호

# ── 화살촉 (벡터 머리) ─────────────────────────────────────────────
ARROW_LEN = 12.0            # 화살촉 길이 (px)
ARROW_HALF_W = 5.0          # 화살촉 밑변 절반 폭 (px)

# ── 폰트 ───────────────────────────────────────────────────────────
FONT_FAMILY = "NanumGothic"
FONT_SIZE = 17.0
FONT_SIZE_SUB = 11.0        # 아래/위 첨자 크기
LABEL_OFFSET = 12.0         # 벡터 라벨을 화살촉에서 밀어내는 기본 거리

# 그리스 문자 이름 → 유니코드. 라벨에 "\theta" 처럼 쓰면 치환된다.
GREEK = {
    r"\theta": "θ", r"\mu": "μ", r"\alpha": "α", r"\beta": "β",
    r"\gamma": "γ", r"\phi": "φ", r"\omega": "ω", r"\pi": "π",
    r"\lambda": "λ", r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ",
    r"\delta": "δ", r"\Delta": "Δ", r"\Sigma": "Σ", r"\Omega": "Ω",
}