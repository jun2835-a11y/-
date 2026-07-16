# TikZ 렌더용 LaTeX 툴체인 포함 이미지 (Render Docker 배포)
FROM python:3.12-slim

# xelatex + tikz/pgfplots/tikz-3dplot + 한글(kotex) + pdftocairo(poppler)
RUN apt-get update && apt-get install -y --no-install-recommends \
      texlive-xetex texlive-latex-extra texlive-pictures texlive-science \
      texlive-lang-korean texlive-fonts-recommended \
      poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --timeout 180 --workers 1"]