"""사진 → 구조화 JSON 추출 (Claude 비전 + 구조화 출력).

AI가 필요한 유일한 단계. 결과 JSON은 순수 로직 렌더러로 넘어간다.
ANTHROPIC_API_KEY 환경변수 필요. MODEL로 모델 교체 가능(기본 opus).
"""
from __future__ import annotations

import base64
import json
import os

MODEL = os.environ.get("MODEL", "claude-opus-4-8")

# 추출 결과 형식을 강제하는 JSON 스키마 (형식 오류 0).
# 수식은 $...$로 감싼 LaTeX, 한글은 그대로 담는다.
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "qnum":     {"type": "string", "description": "문항 번호 (예: '3')"},
        "points":   {"type": "string", "description": "배점 (예: '[3점]', 없으면 빈 문자열)"},
        "stem":     {"type": "string", "description": "발문. 한글+수식($...$)"},
        "choices":  {"type": "array", "items": {"type": "string"},
                     "description": "선택지 목록 (예: '① 1'). 없으면 빈 배열"},
        "intent":   {"type": "string", "description": "출제의도 (없으면 빈 문자열)"},
        "solution": {"type": "array", "items": {"type": "string"},
                     "description": "정답풀이 줄 목록. 각 줄 한글+수식($...$)"},
        "answer":   {"type": "string", "description": "정답 (예: '⑤', 없으면 빈 문자열)"},
        "has_figure": {"type": "boolean", "description": "그림(도형·그래프) 포함 여부"},
    },
    "required": ["qnum", "points", "stem", "choices", "intent",
                 "solution", "answer", "has_figure"],
}

PROMPT = (
    "이 문제 사진을 위 스키마대로 구조화해 추출하세요.\n"
    "- 수식은 반드시 $...$ 로 감싼 LaTeX로 옮깁니다. 예: 수열 $\\{a_n\\}$에 대하여 "
    "$\\sum_{k=1}^{4}(2a_k-k)=0$.\n"
    "- 한글 텍스트는 그대로 둡니다.\n"
    "- 선택지는 원문자 번호를 포함해 각각 하나의 문자열로.\n"
    "- 정답풀이는 수식 전개를 줄 단위로 나눠 배열에.\n"
    "- 그림(빗면·도르래·그래프·도형 등)이 있으면 has_figure=true.\n"
    "- 확실하지 않은 항목은 비워 두세요(빈 문자열/빈 배열)."
)

_client = None


def _get_client():
    global _client
    if _client is None:
        from anthropic import Anthropic  # 지연 import: UI만 띄울 때 불필요
        _client = Anthropic()            # ANTHROPIC_API_KEY 자동 사용
    return _client


def extract(image_bytes: bytes, media_type: str = "image/jpeg") -> dict:
    """이미지 바이트 → 구조화 dict. 스키마 강제라 파싱 안전."""
    b64 = base64.b64encode(image_bytes).decode()
    resp = _get_client().messages.create(
        model=MODEL,
        max_tokens=4000,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64",
                                         "media_type": media_type, "data": b64}},
            {"type": "text", "text": PROMPT},
        ]}],
    )
    # 텍스트 블록을 이어붙여 JSON 파싱
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    return json.loads(text)