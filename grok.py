import json
from datetime import datetime
from pathlib import Path
import streamlit as st

# 🎨 가독성 개선 + 라운지 배너 예외
st.markdown("""
    <style>
        /* 전체 텍스트 밝고 크게 */
        html, body, [class*="css"] {
            color: #fffdf5;
            font-size: 18px;
            font-weight: 500;
        }

        /* 제목 크고 진하게 */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 700;
        }

        /* 설명글도 밝게 */
        p, span, label {
            color: #fefefe !important;
        }

        /* 라운지 배너만 예외 (배경이 밝으니 어두운 글씨) */
        .css-1n76uvr, .css-1n76uvr p, .css-1n76uvr h1, .css-1n76uvr h2 {
            color: #1e3d2f !important; /* 짙은 초록 */
            font-weight: 700;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        /* 전체 텍스트 색과 크기 */
        html, body, [class*="css"] {
            color: #fffdf5; /* 크림빛 흰색 */
            font-size: 18px; /* 기본 글씨 크기 업 */
            font-weight: 500;
        }

        /* 제목 스타일 */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 700;
        }

        /* 작은 설명글도 밝게 */
        p, span, label {
            color: #fefefe !important;
        }
    </style>
""", unsafe_allow_html=True)

# 상단 배경(연두 톤)
bg_color = "#E5F9E0"   # 연한 연두

# 메인 텍스트 색
main_text_color = "#3B5D2A"  # 진한 숲 초록

# 서브 텍스트 색
sub_text_color = "#5F7A4B"   # 부드러운 카키

# 카드 배경(베이지 톤)
card_bg_color = "#FFF5E1"    # 크림 베이지

# 우드톤 포인트 (버튼, 테두리)
wood_color = "#A47149"       # 브라운

# 버튼 호버시 연한 베이지
hover_color = "#FFEED6"

st.markdown(f"""
    <style>
        .stApp {{
            background-color: {bg_color};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {main_text_color};
        }}
        p {{
            color: {sub_text_color};
        }}
        /* 카드 스타일 */
        .card {{
            background-color: {card_bg_color};
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid {wood_color};
            box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
        }}
        /* 버튼 스타일 */
        .stButton > button {{
            background-color: {wood_color};
            color: white;
            border-radius: 8px;
            border: none;
            box-shadow: 0px 3px 6px rgba(0,0,0,0.2);
            transition: all 0.2s ease-in-out;
        }}
        .stButton > button:hover {{
            background-color: {hover_color};
            color: {main_text_color};
            box-shadow: 0px 5px 10px rgba(0,0,0,0.3);
            transform: translateY(-2px);
        }}
    </style>
""", unsafe_allow_html=True)

# 파일 경로
USER_DATA_FILE = Path('user_data.json')
FRIDGE_FILE = Path('fridge.json')

# 데이터 로더

def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default

# 점수 계산(간단 근사)

def compute_scores(user: dict, fridge: dict):
    body = 70
    mind = 70
    life = 70

    # BMI
    try:
        h = float(user.get('height', 0))
        w = float(user.get('weight', 0))
        if h > 0 and w > 0:
            bmi = w / ((h/100)**2)
            if 18.5 <= bmi <= 23:
                body += 10
            elif bmi < 18.5 or bmi > 27.5:
                body -= 10
            else:
                body -= 5
    except Exception:
        pass

    # 수면/컨디션 → 마음 점수
    sleep = user.get('sleep_hours')
    cond = user.get('condition_score', 5)
    if isinstance(sleep, (int, float)) and sleep:
        if 7 <= sleep <= 9:
            mind += 10
        elif sleep < 5:
            mind -= 10
        else:
            mind -= 2
    if isinstance(cond, (int, float)):
        mind += (cond - 5) * 2

    # 냉장고→생활 점수
    if isinstance(fridge, dict) and fridge:
        life += min(10, len(fridge))

    clamp = lambda x: int(max(0, min(100, round(x))))
    return clamp(body), clamp(mind), clamp(life)

# 페이지 설정
st.set_page_config(page_title="🌿 웰니스 라운지 · 홈", page_icon="🌿", layout="wide")

# 데이터
user = load_json(USER_DATA_FILE, {})
fridge = load_json(FRIDGE_FILE, {})
body, mind, life = compute_scores(user, fridge)

# 커스텀 CSS (그린 + 우드톤)
st.markdown(
    """
    <style>
      /* 배경: 은은한 우드 패턴 + 그린 그라디언트 오버레이 */
      .stApp {
        background: linear-gradient(135deg, rgba(54, 179, 126, 0.10), rgba(99, 164, 255, 0.06)),
                    repeating-linear-gradient( 90deg, #f5efe6 0px, #f5efe6 12px, #f2ebdf 12px, #f2ebdf 24px );
      }
      /* 카드 스타일 */
      .card {
        border-radius: 20px; padding: 20px; background: #ffffffcc; backdrop-filter: blur(6px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
      }
      .hero {
        border-radius: 24px; padding: 32px; 
        background: radial-gradient(1200px 400px at 10% -10%, rgba(102, 187, 106, 0.25), transparent),
                    radial-gradient(1200px 400px at 100% 0%, rgba(72, 150, 111, 0.20), transparent),
                    linear-gradient(135deg, #edf7ee 0%, #eef6fb 100%);
        border: 1px solid rgba(0,0,0,0.05);
      }
      .kicker {font-size: 15px; color: #4f6f52; letter-spacing: 0.06em; text-transform: uppercase;}
      .headline {font-size: 32px; font-weight: 800; line-height: 1.25; color: #2d3a2f;}
      .subline {font-size: 16px; color: #5c6f62; margin-top: 6px;}
      .score {font-size: 24px; font-weight: 700; color: #2d3a2f;}
      .wood-title {color: #3f4f3f; font-weight: 700;}
      .btn-hollow {border: 1px solid #87a27e; padding: 10px 14px; border-radius: 12px;}
    </style>
    """, unsafe_allow_html=True
)

# 헤더 히어로 섹션
st.markdown(
    f"""
    <div class="hero">
      <div class="kicker">WELCOME TO YOUR WELLNESS LOUNGE</div>
      <div class="headline">내 몸을 돌보는 게 곧 나의 삶이다.</div>
      <div class="subline">내 몸과 마음을 다스려 완전한 나로 거듭나자.</div>
    </div>
    """, unsafe_allow_html=True
)

st.write("")

# 3개 지표 카드 (몸/마음/삶)
col1, col2, col3 = st.columns(3)
for col, label, emoji, score in [
    (col1, "몸", "🪵", body),
    (col2, "마음", "🍃", mind),
    (col3, "삶", "🌞", life),
]:
    with col:
        st.markdown(f"<div class='card'><div class='wood-title'>{emoji} {label}</div>", unsafe_allow_html=True)
        st.progress(score/100)
        st.markdown(f"<div class='score'>{score} / 100</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# 오늘의 안내 문구 & 액션
with st.container():
    c1, c2 = st.columns([3,2])
    with c1:
        st.markdown("### 오늘의 한마디 ✨")
        quotes = [
            ("숲의 바람처럼, 천천히. 그러나 꾸준히.", "라운지"),
            ("작은 루틴이 큰 평온을 만든다.", "라운지"),
            ("몸을 돌보면 마음이 따라오고, 마음이 평온하면 삶이 반짝여.", "라운지"),
        ]
        q, a = quotes[datetime.now().day % len(quotes)]
        st.markdown(f"> {q}\n\n— *{a}*")
    with c2:
        st.markdown("### 오늘의 시작")
        st.button("바디 체크룸 열기 🧍", use_container_width=True)
        st.button("바이탈 스테이션 열기 💓", use_container_width=True)
        st.button("푸드 스테이션 열기 🧊", use_container_width=True)
        st.button("케어 플래너 열기 🍱", use_container_width=True)
        st.caption("*멀티페이지 연결 전: 사이드바에서 메뉴를 선택해줘*")

# 푸터
st.write("")
st.caption("© 웰니스 라운지 · 초록&우드톤 테마 — 따뜻한 일상을 위한 루루 전용")
