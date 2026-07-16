"""문제 사진 복원 웹 서비스 (Render 배포용).

사진 업로드 → Claude 추출(extract.py) → MathJax 웹페이지로 깨끗하게 렌더.
AI는 추출 1회만, 렌더는 브라우저(MathJax)·서버 로직으로 무료.
"""
import io
import os

from flask import Flask, render_template, request

import extract

app = Flask(__name__)
MAX_EDGE = 1568  # 업로드 사진 다운스케일 (비전 토큰·업로드 크기 절감)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/healthz")
def healthz():
    return "ok", 200


@app.route("/restore", methods=["POST"])
def restore():
    f = request.files.get("photo")
    if not f or not f.filename:
        return render_template("index.html", error="사진을 선택하세요."), 400
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(f.read())).convert("RGB")
        img.thumbnail((MAX_EDGE, MAX_EDGE))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        data = extract.extract(buf.getvalue(), "image/jpeg")
    except Exception as e:  # noqa: BLE001 - 사용자에게 원인 노출
        return render_template("index.html", error=f"복원 실패: {e}"), 500
    return render_template("result.html", d=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))