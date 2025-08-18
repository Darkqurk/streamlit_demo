
# FridgeGenie (MVP) — Gradio

간단한 **냉장고 관리 + 개인 프로필 기반 '오늘의 추천'** 웹앱(Gradio 버전)입니다.

## 로컬 실행
```bash
pip install -r requirements.txt
python app.py
```
브라우저에서 표시되는 로컬 URL로 접속하세요.

## 배포(가장 쉬운 방법: Hugging Face Spaces)
1. 이 폴더의 파일들을 깃 저장소에 올립니다.
2. https://huggingface.co/spaces 에서 New Space → SDK는 **Gradio** 선택.
3. 방금 만든 깃 저장소를 연결하면 자동으로 배포됩니다.

## 폴더/파일
- `app.py` : Gradio UI + 간단 로직
- `requirements.txt` : 필요한 라이브러리
- `profile.json`/`ingredients.json`/`logs.json` : JSON 저장소(없으면 자동 생성)
