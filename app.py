
import json
from datetime import date, datetime
from typing import List, Dict, Optional

import gradio as gr

# --------------------
# Simple JSON "storage"
# --------------------
PROFILE_PATH = "profile.json"
INGREDIENTS_PATH = "ingredients.json"
LOGS_PATH = "logs.json"

def _load(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default

def _save(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Initialize files if missing
if not os.path.exists(PROFILE_PATH):
    _save(PROFILE_PATH, {"bmr": 0, "goal_cal": 1800, "allergies": [], "conditions": []})
if not os.path.exists(INGREDIENTS_PATH):
    _save(INGREDIENTS_PATH, [])
if not os.path.exists(LOGS_PATH):
    _save(LOGS_PATH, [])

# --------------------
# Helpers
# --------------------
def calc_bmr(sex: str, weight_kg: float, height_cm: float, age: int) -> int:
    # Mifflin-St Jeor
    if sex.lower() in ["male", "m", "남", "남성"]:
        bmr = 10*weight_kg + 6.25*height_cm - 5*age + 5
    else:
        bmr = 10*weight_kg + 6.25*height_cm - 5*age - 161
    return int(round(bmr))

def add_profile(sex, weight, height, age, goal_cal, allergies_text, conditions_text):
    bmr = calc_bmr(sex, weight, height, age)
    allergies = [a.strip() for a in allergies_text.split(",") if a.strip()]
    conditions = [c.strip() for c in conditions_text.split(",") if c.strip()]
    profile = {
        "bmr": bmr,
        "goal_cal": int(goal_cal),
        "allergies": allergies,
        "conditions": conditions,
        "sex": sex,
        "weight_kg": weight,
        "height_cm": height,
        "age": age,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    _save(PROFILE_PATH, profile)
    return f"✅ 프로필 저장 완료! (BMR={bmr}kcal)", json.dumps(profile, ensure_ascii=False, indent=2)

def list_profile():
    prof = _load(PROFILE_PATH, {})
    return json.dumps(prof, ensure_ascii=False, indent=2)

def add_ingredient(name, quantity, unit, expires_on):
    data = _load(INGREDIENTS_PATH, [])
    item = {
        "name": name.strip(),
        "quantity": float(quantity) if quantity else 0.0,
        "unit": unit.strip(),
        "expires_on": expires_on if expires_on else None,
        "added_at": datetime.now().isoformat(timespec="seconds"),
    }
    if not item["name"]:
        return "❗이름은 필수입니다.", json.dumps(data, ensure_ascii=False, indent=2)
    data.append(item)
    _save(INGREDIENTS_PATH, data)
    return "✅ 재료 추가!", json.dumps(data, ensure_ascii=False, indent=2)

def remove_ingredient(name):
    data = _load(INGREDIENTS_PATH, [])
    new_data = [i for i in data if i.get("name","").lower() != name.strip().lower()]
    _save(INGREDIENTS_PATH, new_data)
    return f"🗑️ '{name}' 삭제(이름 일치 항목).", json.dumps(new_data, ensure_ascii=False, indent=2)

def clear_ingredients():
    _save(INGREDIENTS_PATH, [])
    return "🧹 재료 목록 초기화.", "[]"

def list_ingredients():
    data = _load(INGREDIENTS_PATH, [])
    # sort by expiry soonest first
    def sort_key(i):
        ex = i.get("expires_on")
        try:
            return datetime.fromisoformat(ex) if ex else datetime.max
        except Exception:
            return datetime.max
    data = sorted(data, key=sort_key)
    return json.dumps(data, ensure_ascii=False, indent=2)

# Very simple rules for "recommendations"
# You can enrich later with nutrition, tags, embeddings, etc.
RULES = [
    {
        "name": "아보카도 에그볼",
        "need": ["아보카도", "계란"],
        "avoid_any": [],
        "kcal": 420,
        "desc": "아보카도와 삶은 계란, 소금 한 꼬집, 올리브오일로 간단하게."
    },
    {
        "name": "토마토 모짜렐라 샐러드",
        "need": ["토마토", "모짜렐라"],
        "avoid_any": ["유당불내증"],
        "kcal": 350,
        "desc": "토마토+모짜렐라+올리브오일. 바질이 있다면 더 좋아요."
    },
    {
        "name": "관찰레 스크램블 라이스",
        "need": ["관찰레", "계란", "밥"],
        "avoid_any": ["저탄수"],
        "kcal": 650,
        "desc": "관찰레와 계란을 스크램블로, 밥과 함께 한 그릇."
    },
    {
        "name": "요거트&복숭아 볼",
        "need": ["요거트", "복숭아"],
        "avoid_any": ["유당불내증"],
        "kcal": 300,
        "desc": "무가당 요거트에 복숭아 다이스를 올려 상큼하게."
    },
]

def recommend():
    prof = _load(PROFILE_PATH, {})
    inv = _load(INGREDIENTS_PATH, [])
    have = {i["name"] for i in inv}
    allergies = set(prof.get("allergies", []))
    conditions = set(prof.get("conditions", []))
    avoid_keys = allergies | conditions

    candidates = []
    for r in RULES:
        if not set(r["need"]).issubset(have):
            continue
        if any(x in avoid_keys for x in r["avoid_any"]):
            continue
        # crude goal_cal proximity score
        goal = prof.get("goal_cal", 1800)
        score = abs(goal/3 - r["kcal"])  # assume ~1식
        candidates.append((score, r))

    if not candidates:
        return "😿 조건에 맞는 추천이 없어요. 재료를 더 추가해보세요.", ""

    candidates.sort(key=lambda x: x[0])
    best = candidates[0][1]

    # log selection
    logs = _load(LOGS_PATH, [])
    logs.append({
        "date": datetime.now().date().isoformat(),
        "chosen_recipe": best["name"],
        "kcal": best["kcal"],
    })
    _save(LOGS_PATH, logs)

    detail = {
        "recipe": best["name"],
        "kcal": best["kcal"],
        "desc": best["desc"],
        "used": best["need"],
        "profile_goal_cal": prof.get("goal_cal", 1800),
    }
    return f"🍽️ 오늘의 추천: {best['name']}", json.dumps(detail, ensure_ascii=False, indent=2)

def show_logs():
    logs = _load(LOGS_PATH, [])
    return json.dumps(logs, ensure_ascii=False, indent=2)

# --------------------
# UI
# --------------------
with gr.Blocks(title="FridgeGenie (MVP)") as demo:
    gr.Markdown("# 🧊 FridgeGenie\n간단 냉장고+프로필 기반 추천 MVP")

    with gr.Tab("1) 프로필"):
        sex = gr.Radio(choices=["여성", "남성"], value="여성", label="성별")
        weight = gr.Number(value=60, label="체중(kg)")
        height = gr.Number(value=165, label="키(cm)")
        age = gr.Number(value=35, label="나이")
        goal_cal = gr.Number(value=1800, label="목표 칼로리(kcal/day)")
        allergies_text = gr.Textbox(label="알러지(쉼표로 구분)", placeholder="예: 우유, 땅콩")
        conditions_text = gr.Textbox(label="기저질환/상태(쉼표 구분)", placeholder="예: 저탄수, 유당불내증")
        prof_btn = gr.Button("프로필 저장")
        prof_status = gr.Markdown()
        prof_view = gr.Code(label="현재 프로필(JSON)", language="json")

        prof_btn.click(add_profile, [sex, weight, height, age, goal_cal, allergies_text, conditions_text],
                       [prof_status, prof_view])
        gr.Button("프로필 불러오기").click(list_profile, [], [prof_view])

    with gr.Tab("2) 재료"):
        name = gr.Textbox(label="재료명", placeholder="예: 토마토")
        quantity = gr.Number(value=1, label="수량")
        unit = gr.Textbox(label="단위", value="개")
        expires = gr.Textbox(label="소진/유통기한(YYYY-MM-DD)", placeholder="예: 2025-08-31")
        add_btn = gr.Button("재료 추가")
        del_name = gr.Textbox(label="삭제할 재료명", placeholder="예: 토마토")
        del_btn = gr.Button("이름으로 삭제")
        clear_btn = gr.Button("전체 초기화")
        inv_view = gr.Code(label="재료 목록(JSON)", language="json")

        add_btn.click(add_ingredient, [name, quantity, unit, expires], [gr.Markdown(), inv_view])
        del_btn.click(remove_ingredient, [del_name], [gr.Markdown(), inv_view])
        clear_btn.click(clear_ingredients, [], [gr.Markdown(), inv_view])
        gr.Button("재료 불러오기").click(list_ingredients, [], [inv_view])

    with gr.Tab("3) 추천"):
        rec_btn = gr.Button("오늘의 추천 뽑기")
        rec_status = gr.Markdown()
        rec_detail = gr.Code(label="추천 결과 상세(JSON)", language="json")
        rec_btn.click(recommend, [], [rec_status, rec_detail])

    with gr.Tab("4) 기록"):
        gr.Button("로그 보기").click(show_logs, [], [gr.Code(label="로그(JSON)", language="json")])

if __name__ == "__main__":
    demo.launch()
