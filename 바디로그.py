import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional

st.set_page_config(page_title="개인 건강기록 로그", page_icon="🩺", layout="centered")

# -----------------------------
# 기본 정의
# -----------------------------
ALL_METRICS = ["혈압", "심박수", "체온", "호흡수", "SPO2", "혈당", "체중", "BMI", "허리둘레"]
UNIT_COLUMNS = {
    "체온": "체온_단위",
    "혈당": "혈당_단위",
    "체중": "체중_단위",
    "허리둘레": "허리둘레_단위",
    "키": "키_단위",
}
BASE_COLUMNS = ["날짜", "시간"] + ALL_METRICS + list(UNIT_COLUMNS.values())

LABELS = {
    "혈압": "혈압(수축/이완) — mmHg",
    "심박수": "심박수(bpm)",
    "체온": "체온(℃)",
    "혈당": "혈당(mg/dL)",
    "SPO2": "SpO₂(%)",
    "호흡수": "호흡수(RR /min)",
    "체중": "체중(kg)",
    "허리둘레": "허리둘레(cm)",
    "BMI": "BMI(kg/m²)"
}

if "health_log" not in st.session_state:
    st.session_state.health_log = pd.DataFrame(columns=BASE_COLUMNS)
if "selected_metrics" not in st.session_state:
    st.session_state.selected_metrics = ["체중", "허리둘레", "BMI"]
if "view" not in st.session_state:
    st.session_state.view = "record"  # record | data

# -----------------------------
# 상단 네비게이션
# -----------------------------
st.title("🩺 개인 건강 기록 로그 (커스텀)")
nav1, nav2 = st.columns(2)
with nav1:
    if st.button("📝 기록하기", use_container_width=True):
        st.session_state.view = "record"
with nav2:
    if st.button("📦 데이터 관리실", use_container_width=True):
        st.session_state.view = "data"

# -----------------------------
# 사이드바: '추적 지표 설정' (이미지처럼)
# -----------------------------
with st.sidebar:
    st.markdown("### 🧭 추적 지표 설정")

    with st.form("metric_prefs", clear_on_submit=False):
        left, right = st.columns(2)
        with left:
            st.markdown("**기본 바이탈**")
            cb_bp   = st.checkbox(LABELS["혈압"], value=("혈압" in st.session_state.selected_metrics))
            cb_hr   = st.checkbox(LABELS["심박수"], value=("심박수" in st.session_state.selected_metrics))
            cb_temp = st.checkbox(LABELS["체온"], value=("체온" in st.session_state.selected_metrics))
            cb_glu  = st.checkbox(LABELS["혈당"], value=("혈당" in st.session_state.selected_metrics))
        with right:
            st.markdown("**옵션**")
            cb_spo2 = st.checkbox(LABELS["SPO2"], value=("SPO2" in st.session_state.selected_metrics))
            cb_rr   = st.checkbox(LABELS["호흡수"], value=("호흡수" in st.session_state.selected_metrics))
            cb_wt   = st.checkbox(LABELS["체중"], value=("체중" in st.session_state.selected_metrics))
            cb_wc   = st.checkbox(LABELS["허리둘레"], value=("허리둘레" in st.session_state.selected_metrics))
            cb_bmi  = st.checkbox(LABELS["BMI"], value=("BMI" in st.session_state.selected_metrics))

        saved = st.form_submit_button("저장(지표 설정)")
        if saved:
            sel = []
            if cb_bp: sel.append("혈압")
            if cb_hr: sel.append("심박수")
            if cb_temp: sel.append("체온")
            if cb_glu: sel.append("혈당")
            if cb_spo2: sel.append("SPO2")
            if cb_rr: sel.append("호흡수")
            if cb_wt: sel.append("체중")
            if cb_wc: sel.append("허리둘레")
            if cb_bmi: sel.append("BMI")
            st.session_state.selected_metrics = sel
            st.success("지표 설정이 저장됐습니다 ✅")

# -----------------------------
# 도우미: BMI 계산(단위 변환)
# -----------------------------
def compute_bmi(height_val: Optional[float], height_unit: str,
                weight_val: Optional[float], weight_unit: str) -> Optional[float]:
    if not height_val or not weight_val or height_val <= 0 or weight_val <= 0:
        return None
    h_m = height_val/100.0 if height_unit == "cm" else height_val*0.0254
    w_kg = weight_val if weight_unit == "kg" else weight_val*0.45359237
    return round(w_kg/(h_m*h_m), 2)

# ============================================================
# 뷰 1) 기록하기
# ============================================================
if st.session_state.view == "record":
    with st.form("health_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1: date = st.date_input("기록 날짜", datetime.today())
        with c2: time = st.time_input("기록 시간", datetime.now().time())

        st.subheader("데이터 입력")
        inputs, units = {}, {}

        # BMI 자동 계산
        auto_bmi = ("BMI" in st.session_state.selected_metrics) and st.checkbox("BMI 자동 계산(키/몸무게로 계산)", value=False)
        height_val, height_unit = None, "cm"
        if auto_bmi:
            hc1, hc2 = st.columns([2,1])
            with hc1: height_val = st.number_input("키", min_value=0.0, step=0.1, help="BMI 자동 계산용")
            with hc2: height_unit = st.selectbox("키 단위", ["cm", "inch"], index=0)
            inputs["키"] = height_val; units["키"] = height_unit

        def field_with_unit(metric: str):
            if metric == "체온":
                v,u = st.columns([2,1])
                with v: val = st.number_input("체온", min_value=0.0, step=0.1)
                with u: unit = st.selectbox("체온 단위", ["℃","℉"], index=0)
                return val, unit
            if metric == "혈당":
                v,u = st.columns([2,1])
                with v: val = st.number_input("혈당", min_value=0.0, step=1.0)
                with u: unit = st.selectbox("혈당 단위", ["mg/dL","mmol/L"], index=0)
                return val, unit
            if metric == "체중":
                v,u = st.columns([2,1])
                with v: val = st.number_input("체중", min_value=0.0, step=0.1)
                with u: unit = st.selectbox("체중 단위", ["kg","lb"], index=0)
                return val, unit
            if metric == "허리둘레":
                v,u = st.columns([2,1])
                with v: val = st.number_input("허리둘레", min_value=0.0, step=0.1)
                with u: unit = st.selectbox("허리둘레 단위", ["cm","inch"], index=0)
                return val, unit
            if metric == "혈압":
                v,u = st.columns([2,1])
                with v: val = st.text_input("혈압 (예: 120/80)")
                with u: unit = st.text_input("혈압 단위", value="mmHg", disabled=True)
                return val, unit
            if metric == "심박수":
                v,u = st.columns([2,1])
                with v: val = st.number_input("심박수", min_value=0, step=1)
                with u: unit = st.text_input("심박수 단위", value="bpm", disabled=True)
                return val, unit
            if metric == "호흡수":
                v,u = st.columns([2,1])
                with v: val = st.number_input("호흡수", min_value=0, step=1)
                with u: unit = st.text_input("호흡수 단위", value="회/분", disabled=True)
                return val, unit
            if metric == "SPO2":
                v,u = st.columns([2,1])
                with v: val = st.number_input("SpO₂", min_value=0, max_value=100, step=1)
                with u: unit = st.text_input("SpO₂ 단위", value="%", disabled=True)
                return val, unit
            if metric == "BMI":
                v,u = st.columns([2,1])
                with v: val = st.number_input("BMI", min_value=0.0, step=0.1, disabled=auto_bmi)
                with u: unit = st.text_input("BMI 단위", value="kg/m²", disabled=True)
                return val, unit
            return None, None

        for m in st.session_state.selected_metrics:
            val, unit = field_with_unit(m)
            inputs[m] = val
            if m in UNIT_COLUMNS: units[m] = unit

        submitted = st.form_submit_button("저장", use_container_width=True)
        if submitted:
            if "혈압" in st.session_state.selected_metrics and inputs.get("혈압"):
                if "/" not in str(inputs["혈압"]):
                    st.warning("혈압은 '수축기/이완기' 형태(예: 120/80)로 입력해 주세요.")
            new_row = {"날짜": date, "시간": time}

            if "BMI" in st.session_state.selected_metrics and auto_bmi:
                new_row["BMI"] = compute_bmi(
                    height_val=inputs.get("키"), height_unit=units.get("키","cm"),
                    weight_val=inputs.get("체중"), weight_unit=units.get("체중","kg")
                )

            for m in st.session_state.selected_metrics:
                if not (m == "BMI" and auto_bmi):
                    new_row[m] = inputs.get(m)
            # 단위 컬럼
            for metric, unit_col in UNIT_COLUMNS.items():
                if metric == "키" and auto_bmi:
                    new_row[unit_col] = units.get("키")
                elif metric in st.session_state.selected_metrics:
                    new_row[unit_col] = units.get(metric)
                else:
                    new_row[unit_col] = None

            # 누락 컬럼 정합성
            for m in ALL_METRICS:
                new_row.setdefault(m, None)
            for uc in UNIT_COLUMNS.values():
                new_row.setdefault(uc, None)

            st.session_state.health_log = pd.concat(
                [st.session_state.health_log, pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.success("✅ 기록이 저장되었습니다!")

    # 미리보기
    st.subheader("📒 최근 기록 미리보기")
    disp = ["날짜","시간"] + [m for m in ALL_METRICS if m in st.session_state.selected_metrics]
    for m in ["체온","혈당","체중","허리둘레"]:
        if m in st.session_state.selected_metrics:
            disp.append(UNIT_COLUMNS[m])
    for c in disp:
        if c not in st.session_state.health_log.columns:
            st.session_state.health_log[c] = None
    st.dataframe(
        st.session_state.health_log[disp].sort_values(["날짜","시간"], ascending=[False,False]),
        use_container_width=True
    )

# ============================================================
# 뷰 2) 데이터 관리실
# ============================================================
if st.session_state.view == "data":
    st.header("📦 데이터 관리실")
    st.subheader("전체 데이터")
    for c in BASE_COLUMNS:
        if c not in st.session_state.health_log.columns:
            st.session_state.health_log[c] = None
    st.dataframe(
        st.session_state.health_log[BASE_COLUMNS].sort_values(["날짜","시간"], ascending=[False,False]),
        use_container_width=True
    )
    st.markdown("---")
    cdl, cul = st.columns(2)
    with cdl:
        if not st.session_state.health_log.empty:
            st.download_button(
                "⬇️ CSV로 내려받기",
                st.session_state.health_log.to_csv(index=False).encode("utf-8-sig"),
                file_name="health_log.csv",
                mime="text/csv",
                use_container_width=True
            )
    with cul:
        up = st.file_uploader("⬆️ CSV 불러오기", type=["csv"])
        if up is not None:
            try:
                df = pd.read_csv(up)
                for c in BASE_COLUMNS:
                    if c not in df.columns: df[c] = None
                st.session_state.health_log = df[BASE_COLUMNS]
                st.success("CSV 불러오기 완료!")
            except Exception as e:
                st.error(f"불러오는 중 오류: {e}")
