import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 데이터 파일 경로
DATA_FILE = "vital_data.json"

# 데이터 로드 함수
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# 데이터 저장 함수
def save_data(data):
    # 2년치 데이터만 유지 (730일)
    cutoff_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    filtered_data = {k: v for k, v in data.items() if k >= cutoff_date}
    
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

# 바이탈 데이터 입력 함수
def add_vital_data(date_str, time_str, systolic, diastolic, pulse, temperature, blood_sugar, spo2):
    data = load_data()
    
    if date_str not in data:
        data[date_str] = []
    
    vital_entry = {
        "time": time_str,
        "systolic": systolic,
        "diastolic": diastolic,
        "pulse": pulse,
        "temperature": temperature,
        "blood_sugar": blood_sugar,
        "spo2": spo2,
        "timestamp": datetime.now().isoformat()
    }
    
    data[date_str].append(vital_entry)
    save_data(data)
    return True

# 데이터 조회 함수
def get_data_range(start_date, end_date):
    data = load_data()
    result = {}
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str in data:
            result[date_str] = data[date_str]
        current_date += timedelta(days=1)
    
    return result

# DataFrame 변환 함수
def data_to_dataframe(data):
    rows = []
    for date_str, entries in data.items():
        for entry in entries:
            row = {
                '날짜': date_str,
                '시간': entry['time'],
                '수축기혈압': entry['systolic'],
                '이완기혈압': entry['diastolic'],
                '맥박': entry['pulse'],
                '체온': entry['temperature'],
                '혈당': entry['blood_sugar'],
                'SPO2': entry['spo2']
            }
            rows.append(row)
    
    return pd.DataFrame(rows)

# Streamlit 앱 시작
st.set_page_config(page_title="바이탈 입력 로그", page_icon="🏥", layout="wide")

st.title("🏥 바이탈 입력 로그 시스템")
st.markdown("---")

# 사이드바 메뉴
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["📝 데이터 입력", "📊 데이터 조회", "📈 차트 분석", "🗃️ 데이터 관리"]
)

if menu == "📝 데이터 입력":
    st.header("바이탈 데이터 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        input_date = st.date_input("날짜", value=date.today())
        input_time = st.time_input("시간", value=datetime.now().time())
        
        st.subheader("혈압")
        systolic = st.number_input("수축기 혈압 (mmHg)", min_value=50, max_value=300, value=120)
        diastolic = st.number_input("이완기 혈압 (mmHg)", min_value=30, max_value=200, value=80)
        
        pulse = st.number_input("맥박 (bpm)", min_value=30, max_value=200, value=72)
    
    with col2:
        temperature = st.number_input("체온 (°C)", min_value=30.0, max_value=45.0, value=36.5, step=0.1)
        blood_sugar = st.number_input("혈당 (mg/dL)", min_value=50, max_value=500, value=100)
        spo2 = st.number_input("SPO2 (%)", min_value=50, max_value=100, value=98)
        
        st.write("")  # 공간 확보
        if st.button("💾 데이터 저장", type="primary"):
            date_str = input_date.strftime('%Y-%m-%d')
            time_str = input_time.strftime('%H:%M')
            
            if add_vital_data(date_str, time_str, systolic, diastolic, pulse, temperature, blood_sugar, spo2):
                st.success("✅ 데이터가 성공적으로 저장되었습니다!")
                st.balloons()
            else:
                st.error("❌ 데이터 저장 중 오류가 발생했습니다.")

elif menu == "📊 데이터 조회":
    st.header("바이탈 데이터 조회")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_type = st.selectbox("조회 기간", ["하루", "일주일", "한달", "사용자 지정"])
    
    if view_type == "하루":
        selected_date = st.date_input("조회할 날짜", value=date.today())
        start_date = end_date = selected_date
    elif view_type == "일주일":
        start_date = date.today() - timedelta(days=6)
        end_date = date.today()
        st.info(f"📅 {start_date} ~ {end_date} (최근 7일)")
    elif view_type == "한달":
        start_date = date.today() - timedelta(days=29)
        end_date = date.today()
        st.info(f"📅 {start_date} ~ {end_date} (최근 30일)")
    else:  # 사용자 지정
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작 날짜", value=date.today() - timedelta(days=7))
        with col2:
            end_date = st.date_input("종료 날짜", value=date.today())
        
        if start_date > end_date:
            st.error("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
            st.stop()
        
        if (end_date - start_date).days > 30:
            st.warning("⚠️ 조회 기간이 30일을 초과합니다. 성능상 30일 이내로 조회하는 것을 권장합니다.")
    
    # 데이터 조회 및 표시
    data = get_data_range(start_date, end_date)
    
    if data:
        df = data_to_dataframe(data)
        
        # 통계 정보
        if not df.empty:
            st.subheader("📈 통계 요약")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("총 측정 횟수", len(df))
                st.metric("평균 수축기혈압", f"{df['수축기혈압'].mean():.1f}")
            
            with col2:
                st.metric("평균 맥박", f"{df['맥박'].mean():.1f}")
                st.metric("평균 이완기혈압", f"{df['이완기혈압'].mean():.1f}")
            
            with col3:
                st.metric("평균 체온", f"{df['체온'].mean():.1f}°C")
                st.metric("평균 혈당", f"{df['혈당'].mean():.1f}")
            
            with col4:
                st.metric("평균 SPO2", f"{df['SPO2'].mean():.1f}%")
        
        st.subheader("📋 상세 데이터")
        
        # 검색 기능
        search_date = st.text_input("🔍 날짜로 검색 (YYYY-MM-DD 형식)", placeholder="2024-01-15")
        
        if search_date:
            filtered_df = df[df['날짜'].str.contains(search_date, na=False)]
            if not filtered_df.empty:
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.info("해당 날짜의 데이터가 없습니다.")
        else:
            st.dataframe(df, use_container_width=True)
    else:
        st.info("해당 기간에 데이터가 없습니다.")

elif menu == "📈 차트 분석":
    st.header("바이탈 데이터 차트 분석")
    
    # 기간 설정
    col1, col2 = st.columns(2)
    with col1:
        chart_start_date = st.date_input("시작 날짜", value=date.today() - timedelta(days=7))
    with col2:
        chart_end_date = st.date_input("종료 날짜", value=date.today())
    
    data = get_data_range(chart_start_date, chart_end_date)
    
    if data:
        df = data_to_dataframe(data)
        df['datetime'] = pd.to_datetime(df['날짜'] + ' ' + df['시간'])
        df = df.sort_values('datetime')
        
        # 차트 옵션
        chart_option = st.selectbox(
            "차트 선택",
            ["혈압 추이", "맥박 추이", "체온 추이", "혈당 추이", "SPO2 추이", "전체 비교"]
        )
        
        if chart_option == "혈압 추이":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['datetime'], y=df['수축기혈압'], 
                                   mode='lines+markers', name='수축기혈압', line=dict(color='red')))
            fig.add_trace(go.Scatter(x=df['datetime'], y=df['이완기혈압'], 
                                   mode='lines+markers', name='이완기혈압', line=dict(color='blue')))
            fig.update_layout(title="혈압 추이", yaxis_title="mmHg")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_option == "맥박 추이":
            fig = px.line(df, x='datetime', y='맥박', title='맥박 추이', markers=True)
            fig.update_layout(yaxis_title="bpm")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_option == "체온 추이":
            fig = px.line(df, x='datetime', y='체온', title='체온 추이', markers=True)
            fig.update_layout(yaxis_title="°C")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_option == "혈당 추이":
            fig = px.line(df, x='datetime', y='혈당', title='혈당 추이', markers=True)
            fig.update_layout(yaxis_title="mg/dL")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_option == "SPO2 추이":
            fig = px.line(df, x='datetime', y='SPO2', title='SPO2 추이', markers=True)
            fig.update_layout(yaxis_title="%")
            st.plotly_chart(fig, use_container_width=True)
            
        elif chart_option == "전체 비교":
            # 정규화된 값으로 모든 지표를 한 차트에
            normalized_df = df.copy()
            for col in ['수축기혈압', '이완기혈압', '맥박', '체온', '혈당', 'SPO2']:
                normalized_df[f'{col}_norm'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 100
            
            fig = go.Figure()
            colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown']
            metrics = ['수축기혈압', '이완기혈압', '맥박', '체온', '혈당', 'SPO2']
            
            for i, metric in enumerate(metrics):
                fig.add_trace(go.Scatter(x=normalized_df['datetime'], 
                                       y=normalized_df[f'{metric}_norm'],
                                       mode='lines+markers', 
                                       name=metric, 
                                       line=dict(color=colors[i])))
            
            fig.update_layout(title="전체 바이탈 비교 (정규화된 값)", yaxis_title="정규화된 값 (%)")
            st.plotly_chart(fig, use_container_width=True)
            st.info("💡 모든 지표를 0-100% 범위로 정규화하여 비교 표시합니다.")
    else:
        st.info("해당 기간에 차트로 표시할 데이터가 없습니다.")

elif menu == "🗃️ 데이터 관리":
    st.header("데이터 관리")
    
    data = load_data()
    total_entries = sum(len(entries) for entries in data.values())
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 저장된 데이터 현황")
        st.metric("총 저장 일수", len(data))
        st.metric("총 측정 기록", total_entries)
        
        if data:
            dates = list(data.keys())
            earliest_date = min(dates)
            latest_date = max(dates)
            st.metric("가장 오래된 기록", earliest_date)
            st.metric("가장 최근 기록", latest_date)
    
    with col2:
        st.subheader("🔧 데이터 관리 도구")
        
        # JSON 다운로드
        if st.button("💾 JSON 파일 다운로드"):
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            st.download_button(
                label="다운로드",
                data=json_str,
                file_name=f"vital_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # 데이터 정리
        if st.button("🧹 오래된 데이터 정리 (2년 이상)", type="secondary"):
            old_count = len(data)
            save_data(data)  # 2년 필터링이 적용됨
            new_data = load_data()
            new_count = len(new_data)
            removed = old_count - new_count
            if removed > 0:
                st.success(f"✅ {removed}일의 오래된 데이터가 정리되었습니다.")
            else:
                st.info("정리할 오래된 데이터가 없습니다.")
        
        # 전체 데이터 삭제 (위험한 작업)
        st.markdown("---")
        st.markdown("**⚠️ 위험한 작업**")
        if st.button("🗑️ 모든 데이터 삭제", type="secondary"):
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            
            if not st.session_state.confirm_delete:
                st.session_state.confirm_delete = True
                st.warning("⚠️ 정말로 모든 데이터를 삭제하시겠습니까? 다시 한 번 버튼을 클릭하세요.")
            else:
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("✅ 모든 데이터가 삭제되었습니다.")
                st.session_state.confirm_delete = False

# 푸터
st.markdown("---")
st.markdown("**💡 사용법:**")
st.markdown("- 좌측 메뉴에서 원하는 기능을 선택하세요")
st.markdown("- 데이터는 자동으로 JSON 형식으로 저장됩니다")
st.markdown("- 최대 2년치 데이터가 보관되며, 그 이후 데이터는 자동 삭제됩니다")
st.markdown("- 차트 분석에서 다양한 시각화를 확인할 수 있습니다")