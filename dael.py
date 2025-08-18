import json
from datetime import datetime, date, timedelta
from pathlib import Path
import streamlit as st

USER_DATA_FILE = Path('user_data.json')
FRIDGE_FILE = Path('fridge.json')

# JSON 데이터 입출력
def load_data(path: Path, default):
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

def save_data(path: Path, data):
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# BMI/BMR 계산
def calculate_inbody(user):
    try:
        height = float(user.get('height', 0))
        weight = float(user.get('weight', 0))
        age = int(user.get('age', 0))
        gender = str(user.get('gender', 'female')).lower()
        if height <= 0 or weight <= 0 or age <= 0:
            return None
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        if gender == 'male':
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        return {"bmi": round(bmi, 2), "bmr": round(bmr, 2)}
    except Exception:
        return None

# 레시피 DB
def get_recipe_db():
    return {
        '샐러드': {'ingredients': ['상추', '토마토', '닭가슴살'], 'calories': 320, 'desc': '저칼로리 단백질 샐러드'},
        '토마토 파스타': {'ingredients': ['토마토', '파스타', '올리브오일'], 'calories': 550, 'desc': '간단 파스타'},
        '야채 수프': {'ingredients': ['양파', '당근', '감자'], 'calories': 200, 'desc': '따뜻한 수프'},
    }

# 레시피 매칭
def match_recipes(fridge, user, target_min=None, target_max=None):
    recipes = get_recipe_db()
    user_conditions = set(user.get('conditions', []))
    fridge_items = set(fridge.keys())
    matched = []
    for name, info in recipes.items():
        ingredients = set(info['ingredients'])
        match_rate = int(len(ingredients & fridge_items) / len(ingredients) * 100)
        # 알레르기/기저질환 필터
        if user_conditions & ingredients:
            continue
        # 칼로리 필터
        if target_min is not None and target_max is not None:
            if not (target_min <= info['calories'] <= target_max):
                continue
        matched.append({
            'name': name,
            'match_rate': match_rate,
            'calories': info['calories'],
            'desc': info['desc']
        })
    matched.sort(key=lambda x: x['match_rate'], reverse=True)
    return matched

# 세션 상태 초기화
if 'user' not in st.session_state:
    st.session_state.user = load_data(USER_DATA_FILE, default={})
if 'fridge' not in st.session_state:
    st.session_state.fridge = load_data(FRIDGE_FILE, default={})

st.set_page_config(page_title="건강/냉장고/솔루션", page_icon="🥗", layout="centered")

st.title("🥗 건강·냉장고·솔루션 앱")
menu = st.sidebar.radio("메뉴", ["몸 상태 입력", "활력징후 입력", "냉장고 관리", "유통기한 체크", "솔루션 추천"])

if menu == "몸 상태 입력":
    st.subheader("🧍 신체 정보")
    user = st.session_state.user
    with st.form("body_form"):
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("키 (cm)", min_value=0.0, step=0.1, value=float(user.get('height', 0)))
            age = st.number_input("나이 (세)", min_value=0, step=1, value=int(user.get('age', 0)))
        with col2:
            weight = st.number_input("체중 (kg)", min_value=0.0, step=0.1, value=float(user.get('weight', 0)))
            gender = st.selectbox("성별", ["female", "male"], index=(1 if str(user.get('gender', 'female')).lower()=='male' else 0))
        conditions_in = st.text_input("기저질환 (콤마 구분)", value=", ".join(user.get('conditions', [])))
        meds_in = st.text_input("복용중인 약 (콤마 구분)", value=", ".join(user.get('meds', [])))
        submitted = st.form_submit_button("저장")
    if submitted:
        st.session_state.user = {
            'height': height,
            'weight': weight,
            'age': int(age),
            'gender': gender,
            'conditions': [s.strip() for s in conditions_in.split(',') if s.strip()],
            'meds': [s.strip() for s in meds_in.split(',') if s.strip()],
        }
        save_data(USER_DATA_FILE, st.session_state.user)
        st.success("신체 정보 저장 완료!")
    stats = calculate_inbody(st.session_state.user)
    if stats:
        st.info(f"현재 BMI: {stats['bmi']}, BMR: {stats['bmr']} kcal")

elif menu == "활력징후 입력":
    st.subheader("💓 활력징후")
    user = st.session_state.user.copy()
    with st.form("vitals_form"):
        bp = st.text_input("혈압", value=user.get('blood_pressure', ''))
        hr = st.number_input("심박수", min_value=0, step=1, value=int(user.get('heart_rate', 0)))
        temp = st.number_input("체온", min_value=0.0, step=0.1, value=float(user.get('temperature', 0.0)))
        bs = st.number_input("혈당", min_value=0.0, step=0.1, value=float(user.get('blood_sugar', 0.0)))
        sleep = st.number_input("수면시간", min_value=0.0, step=0.5, value=float(user.get('sleep_hours', 0.0)))
        cond = st.slider("오늘 컨디션", min_value=1, max_value=10, value=int(user.get('condition_score', 5)))
        submitted = st.form_submit_button("저장")
    if submitted:
        user.update({
            'blood_pressure': bp,
            'heart_rate': int(hr),
            'temperature': float(temp),
            'blood_sugar': float(bs),
            'sleep_hours': float(sleep),
            'condition_score': int(cond),
            'vitals_updated_at': datetime.now().isoformat(timespec='seconds')
        })
        st.session_state.user = user
        save_data(USER_DATA_FILE, user)
        st.success("활력징후 저장 완료!")

elif menu == "냉장고 관리":
    st.subheader("🧊 냉장고 재료 관리")
    fridge = st.session_state.fridge
    if fridge:
        st.dataframe([{'재료': k, **v} for k, v in fridge.items()], use_container_width=True)
    with st.form("fridge_form"):
        item = st.text_input("재료 이름")
        quantity = st.text_input("양")
        exp = st.date_input("유통기한", value=date.today())
        action = st.selectbox("작업", ["추가/덮어쓰기", "삭제"])
        submitted = st.form_submit_button("실행")
    if submitted:
        fridge = st.session_state.fridge.copy()
        if action == "삭제":
            fridge.pop(item, None)
        else:
            fridge[item] = {'quantity': quantity, 'exp_date': exp.isoformat()}
        st.session_state.fridge = fridge
        save_data(FRIDGE_FILE, fridge)
        st.success("변경 완료!")

elif menu == "유통기한 체크":
    st.subheader("⏰ 유통기한 체크")
    fridge = st.session_state.fridge
    if not fridge:
        st.info("등록된 재료가 없습니다.")
    else:
        today = datetime.now().date()
        rows = []
        for item, info in fridge.items():
            try:
                exp = datetime.strptime(info['exp_date'], '%Y-%m-%d').date()
                delta = (exp - today).days
                status = "❌ 만료" if delta < 0 else (f"⚠️ 임박 (D-{delta})" if delta <= 3 else f"✅ 여유 (D+{delta})")
                rows.append({'재료': item, '양': info['quantity'], '유통기한': exp.isoformat(), '남은일수': delta, '상태': status})
            except:
                rows.append({'재료': item, '양': info['quantity'], '유통기한': info['exp_date'], '남은일수': None, '상태': '형식 오류'})
        rows.sort(key=lambda r: (r['남은일수'] is None, r['남은일수'] if r['남은일수'] is not None else 10**9))
        st.dataframe(rows, use_container_width=True)

elif menu == "솔루션 추천":
    st.subheader("🧪 솔루션 추천")
    stats = calculate_inbody(st.session_state.user)
    fridge = st.session_state.fridge
    user = st.session_state.user
    if stats:
        st.write(f"**현재 BMI:** {stats['bmi']} | **BMR:** {stats['bmr']} kcal")
        goal = st.selectbox("목표", ["감량", "유지", "증량"], index=0)
        factor = 0.8 if goal == "감량" else (1.0 if goal == "유지" else 1.2)
        target_min = int(stats['bmr'] * (factor - 0.1))
        target_max = int(stats['bmr'] * factor)
        st.write(f"목표 칼로리 범위: {target_min} ~ {target_max} kcal")
        matches = match_recipes(fridge, user, target_min, target_max)
        if matches:
            for m in matches:
                st.markdown(f"**{m['name']}** — {m['match_rate']}% 일치, {m['calories']} kcal\n- {m['desc']}")
        else:
            st.info("조건에 맞는 레시피가 없습니다.")
    else:
        st.info("먼저 '몸 상태 입력'에서 정보를 저장하세요.")

