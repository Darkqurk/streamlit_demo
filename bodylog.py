import streamlit as st

st.set_page_config(page_title="바디로그", layout="wide")


# 상단 헤더 HTML
st.markdown("""
    <div style='background: linear-gradient(90deg, #a8e6cf, #dcedc1); padding:20px; border-radius:8px'>
        <h1 style='color:#2e7d32; text-align:center;'>📊 바디로그</h1>
        <p style='color:#388e3c; text-align:center;'>매일 내 몸의 변화를 기록하고 이해하세요</p>
    </div>
""", unsafe_allow_html=True)

# 오늘의 상태
st.write("## 오늘의 상태 요약")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("BMI", "22.4", "-0.2")
col2.metric("혈압", "120/80", "정상")
col3.metric("심박수", "72 bpm", "정상")
col4.metric("체온", "36.5°", "정상")
col5.metric("혈당", "95 mg/dL", "정상")

# 메뉴 버튼
st.write("## 메뉴")
col5, col6, col7 = st.columns(3)
col5.button("데이터입력")
col6.button("상세 데이터 입력")
col7.button("데이터 보기")

# 건강 팁
st.info("💡 오늘의 건강 팁: 아침에 따뜻한 물 한 잔으로 시작하세요!")
