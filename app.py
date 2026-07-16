"""문제 사진 복원 웹 서비스 (Render 배포용).

사진 업로드 → Claude 추출(extract.py) → MathJax 웹페이지로 깨끗하게 렌더.
AI는 추출 1회만, 렌더는 브라우저(MathJax)·서버 로직으로 무료.
"""
import base64
import io
import os

from flask import Flask, render_template, request

import extract

app = Flask(__name__)
MAX_EDGE = 1568  # 업로드 사진 다운스케일 (비전 토큰·업로드 크기 절감)


def _crop_figure(img, bbox):
    """추출된 상대좌표(bbox)로 그림 영역만 잘라낸다. 유효하지 않으면 전체."""
    if not bbox:
        return img
    W, H = img.size
    x0, y0 = bbox.get("x0", 0), bbox.get("y0", 0)
    x1, y1 = bbox.get("x1", 0), bbox.get("y1", 0)
    if x1 <= x0 or y1 <= y0:
        return img
    px, py = 0.03 * W, 0.03 * H
    left, top = max(0, int(x0 * W - px)), max(0, int(y0 * H - py))
    right, bot = min(W, int(x1 * W + px)), min(H, int(y1 * H + py))
    if right - left < 24 or bot - top < 24:
        return img
    return img.crop((left, top, right, bot))


def _clean_scan(pil):
    """사진 그림 → 클린 스캔: 배경 종이색·그림자를 흰색으로 평탄화 + 대비 보정."""
    import numpy as np
    from PIL import ImageFilter, Image
    g = pil.convert("L")
    arr = np.asarray(g, dtype=np.float32)
    mid = float(((arr > 70) & (arr < 200)).mean())         # 원본 중간톤 비율
    if mid < 0.18:                                         # 선그림: 배경 평탄화 + 대비강화
        rad = max(8, max(g.size) // 18)
        bg = np.asarray(g.filter(ImageFilter.GaussianBlur(rad)), dtype=np.float32)
        norm = np.clip(arr / (bg + 1.0) * 255.0, 0, 255)
        norm = np.clip((norm - 30.0) / 205.0 * 255.0, 0, 255)
    else:                                                  # 음영/사진: 전역 화이트밸런스만(음영 보존)
        white = float(np.percentile(arr, 96)) or 255.0
        norm = np.clip(arr / white * 255.0, 0, 255)
    return Image.fromarray(norm.astype("uint8"), "L")


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
        jpeg = buf.getvalue()
        data = extract.extract(jpeg, "image/jpeg")
    except Exception as e:  # noqa: BLE001 - 사용자에게 원인 노출
        return render_template("index.html", error=f"복원 실패: {e}"), 500
    # 그림 처리: 원기둥이면 벡터로 재생성, 그 외 그림은 원본을 폴백으로
    figure_svg = None
    tikz_code = None
    figure_err = None
    if data.get("has_figure"):
        try:
            tikz_code = (extract.extract_tikz(jpeg, "image/jpeg") or {}).get("tikz", "").strip()
        except Exception as e:  # noqa: BLE001
            figure_err = f"TikZ 생성 실패: {e}"
        if tikz_code:
            try:
                from tikz import render_tikz
                figure_svg = render_tikz(tikz_code)
            except Exception as e:  # noqa: BLE001 - 코드는 노출해 수정 가능하게
                figure_err = str(e)[:1400]

    return render_template("result.html", d=data, figure_svg=figure_svg,
                           tikz_code=tikz_code, figure_err=figure_err)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))