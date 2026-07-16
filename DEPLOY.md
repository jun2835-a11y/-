# Render 배포 가이드

문제 사진 복원 웹 서비스를 Render에 올리는 방법. 코드는 준비돼 있고,
아래는 **회원님 Render 계정에서** 하실 단계입니다.

## 구성
```
사진 업로드 → Flask(app.py) → Claude 추출(extract.py) → MathJax 웹페이지(templates/result.html)
```
- AI 호출은 **문제당 1회**(사진 이해). 렌더는 브라우저 MathJax·서버 로직 → 무료.
- Node·Docker·서버 폰트 **불필요** (수식은 브라우저에서 렌더).

## 로컬에서 먼저 실행
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # Windows PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."
python app.py                              # http://localhost:5000
```

## Render 배포 (2가지 방법)

### 방법 A — Blueprint (render.yaml 자동 인식, 추천)
1. 이 리포를 GitHub에 push.
2. Render 대시보드 → **New → Blueprint** → 이 리포 선택.
3. `render.yaml`이 서비스를 자동 구성. **ANTHROPIC_API_KEY** 값만 입력하라고 물어봅니다.
4. **Apply** → 빌드·배포. 끝나면 `https://problem-restore.onrender.com` 형태 URL 발급.

### 방법 B — 수동 (Web Service)
1. Render 대시보드 → **New → Web Service** → 리포 선택.
2. 설정:
   - Runtime: **Python**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120`
3. **Environment** 탭에서 환경변수 추가:
   - `ANTHROPIC_API_KEY` = `sk-ant-...` (비밀)
   - `MODEL` = `claude-opus-4-8` (선택; 저렴하게 하려면 `claude-haiku-4-5`)
4. **Create Web Service** → 배포.

## 비용
- 사진 1건 추출 ≈ ₩10~70 (모델에 따라). 렌더는 무료.
- Render 무료 플랜: 유휴 15분 후 잠들고 첫 요청 시 ~30초 깨어남. 상시 가동은 유료 플랜.

## 보안
- **API 키는 코드·리포에 절대 넣지 않습니다.** Render 환경변수로만 주입.
- `.gitignore`에 `.env` 포함 여부 확인.

## 다음 증분
- 그림 문제(Track B): `physlib.scene.render_scene`로 SVG 생성해 결과 페이지에 삽입.
- PNG/HWP 자산 내려받기: 서버 래스터화(resvg + NanumGothic) 추가 시 Docker 이미지로 전환.