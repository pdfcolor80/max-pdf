import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어", layout="centered")

# --- CSS: 한 화면(One-Screen) 레이아웃 최적화 ---
st.markdown("""
    <style>
    /* 1. 기본 여백 및 헤더 제거 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 0px !important;
        max-width: 500px; /* 모바일 스타일 너비 제한 */
    }
    
    /* 2. 전체 카드 컨테이너 (스크롤 방지) */
    .quiz-card {
        display: flex;
        flex-direction: column;
        height: 85vh; /* 화면의 대부분을 사용 */
        justify-content: flex-start;
    }

    /* 상황 박스 */
    .context-box {
        background: linear-gradient(135deg, #222 0%, #444 100%);
        color: #ffffff;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
    .cat-tag { font-size: 0.7rem; color: #ffeb3b; font-weight: 800; }
    .context-text { font-size: 1rem; font-weight: 700; }

    /* 버튼 스타일 및 간격 축소 */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 2px !important;
        min-height: 40px;
        margin-bottom: -5px;
    }
    
    /* 결과 텍스트 크기 조절 */
    .res-eng { font-size: 1.8rem; font-weight: 900; color: #007BFF; margin-top: 10px; }
    .res-mean { font-size: 1rem; color: #555; font-weight: 600; }

    /* 패턴 박스 슬림화 */
    .pattern-box {
        background-color: #f0f7ff;
        border-left: 4px solid #007BFF;
        border-radius: 8px;
        padding: 8px;
        margin-top: 10px;
    }

    /* 하단 다음 버튼 고정 느낌 */
    .next-btn-container {
        margin-top: auto; /* 맨 아래로 밀기 */
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 한글 강조 함수
def get_accent_html(sound_text, is_big=False):
    words = sound_text.split()
    e_size = "font-size: 1.1rem;" if is_big else "font-size: 0.8rem;"
    a_size = "font-size: 1.3rem;" if is_big else "font-size: 0.9rem;"
    html = '<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:3px;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="accent-red" style="{a_size} color:#E53935; font-weight:900;">{word[0]}</span><span class="sound-black" style="{e_size} font-weight:600;">{word[1:]}</span></span>'
    html += '</div>'
    return html

# 데이터 로딩 (가상 데이터 예시 포함)
@st.cache_data
def load_data():
    all_rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 4: all_rows.append(p)
    else:
        # 파일이 없을 경우를 대비한 샘플 데이터
        all_rows = [["인사", "Hello", "헬로우", "안녕", "처음 만날 때"], ["패턴", "I am (name)", "아이 엠", "나는 ~야", "자기소개"]]
    return all_rows

all_data = load_data()
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴"]])))
categories = ["💡 전체보기"] + categories

# 퀴즈 초기화 함수
def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    st.session_state.quiz_data = random.choice(pool)
    st.session_state.phase = "forest"
    
    # 선택지 생성 (중복 방지)
    others = [r for r in all_data if r[1] != st.session_state.quiz_data[1]]
    st.session_state.forest_items = random.sample(others, min(len(others), 11)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None

# 선택바
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 메인 렌더링 ---
st.markdown('<div class="quiz-card">', unsafe_allow_html=True)

curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

# 1. 상황 정보
st.markdown(f'<div class="context-box"><div class="cat-tag">{cat_name}</div><div class="context-text">{target_context}</div></div>', unsafe_allow_html=True)

# 2. 퀴즈/결과 영역
if st.session_state.phase == "forest":
    cols = st.columns(2)
    for i, item in enumerate(st.session_state.forest_items):
        with cols[i % 2]:
            if st.button(f"{item[1]}\n{item[2]}", key=f"f_{i}"):
                st.session_state.phase = "solved"
                st.rerun()

elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div class="res-eng">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_accent_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div class="res-mean">뜻: {target_mean}</div></div>', unsafe_allow_html=True)
    
    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f'<div class="pattern-box"><div style="color:#007BFF; font-weight:800; font-size:0.7rem;">📍 패턴</div><div style="font-weight:800;">{p_eng}</div><div style="font-size:0.8rem;">{p_sound} | {p_mean}</div></div>', unsafe_allow_html=True)

    # TTS 로직 생략 (기존 코드와 동일)
    st.markdown('<div id="shadow-status" style="color:#E53935; font-weight:800; text-align:center; margin-top:10px;">🔊 쉐도잉 시작...</div>', unsafe_allow_html=True)

# 3. 하단 버튼 (공통)
st.markdown('<div class="next-btn-container">', unsafe_allow_html=True)
if st.button("다음 문제 👉", use_container_width=True):
    init_quiz(selected_cat)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)