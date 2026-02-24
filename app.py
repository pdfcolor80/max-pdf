import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 여백 최소화 및 한 줄 버튼 디자인 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    
    * { font-family: 'Noto Sans KR', sans-serif !important; }
    header { visibility: hidden; height: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    
    /* 상단 여백 극단적 제거 */
    .main .block-container { 
        padding-top: 10px !important; 
        margin-top: -60px !important; 
    }

    /* 상황 박스 슬림화 */
    .context-box {
        background: #1e1e1e;
        color: white;
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 5px;
        text-align: center;
        font-size: 0.9rem;
    }

    /* 한 줄 버튼 스타일: 간격 좁히고 크기 최적화 */
    div.stButton > button {
        width: 100% !important;
        background-color: #ffffff !important;
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
        padding: 6px 10px !important;
        margin-bottom: -18px !important; /* 버튼 간격 밀착 */
        text-align: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    }
    
    div.stButton > button:active {
        background-color: #f0f7ff !important;
        border-color: #007BFF !important;
    }

    /* 다음 버튼 전용 스타일 */
    .next-area div.stButton > button {
        background-color: #E53935 !important;
        color: white !important;
        height: 48px !important;
        border-radius: 24px !important;
        margin-top: 20px !important;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    all_rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 4: all_rows.append(p)
    return all_rows

all_data = load_data()

def init_quiz(cat):
    # 1. 정답 후보군 (패턴 제외)
    quiz_pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not quiz_pool: quiz_pool = [r for r in all_data if r[0] != "패턴"]
    
    # 정답 결정
    st.session_state.quiz_data = random.choice(quiz_pool)
    correct_eng = st.session_state.quiz_data[1]
    
    # 2. 오답 보기 풀: 무조건 '숙어' 카테고리에서만 추출 (패턴 영어 배제)
    distractor_pool = [r for r in all_data if r[0] == "숙어" and r[1] != correct_eng]
    
    # 만약 숙어 데이터가 부족할 경우를 대비한 안전장치
    if len(distractor_pool) < 5:
        distractor_pool = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]

    # 보기 6개 구성 (정답 1 + 숙어 오답 5)
    st.session_state.forest_items = random.sample(distractor_pool, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    
    st.session_state.phase = "forest"

# 카테고리 선택
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

@st.dialog("📚 단어 복습")
def show_word_popup():
    # 팝업도 숙어나 패턴에서 랜덤하게
    words = [r for r in all_data if r[0] in ["숙어", "패턴"]]
    w = random.choice(words) if words else all_data[0]
    st.markdown(f"<h3 style='text-align:center; color:#007BFF; margin-bottom:5px;'>{w[1]}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:1.1rem; color:#444;'><b>{w[3]}</b></p>", unsafe_allow_html=True)
    st.info(f"발음: {w[2]}")
    if st.button("다음 문제 시작!", use_container_width=True):
        init_quiz(selected_cat)
        st.rerun()

@st.dialog("💡 오답")
def show_wrong(item):
    st.write(f"**{item[1]}**")
    st.write(f"뜻: {item[3]}")
    if st.button("다시 시도"): st.rerun()

# --- 화면 출력 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f'<div class="context-box"><b>{cat_name}</b><br>{target_context} ({target_mean})</div>', unsafe_allow_html=True)

if st.session_state.phase == "forest":
    for i, item in enumerate(st.session_state.forest_items):
        # 버튼에 영어 문장과 발음을 같이 표시
        label = f"{item[1]}  /  {item[2]}"
        if st.button(label, key=f"btn_{i}"):
            if item[1] == target_eng:
                st.session_state.phase = "solved"
            else:
                show_wrong(item)
            st.rerun()

elif st.session_state.phase == "solved":
    st.markdown(f"""
        <div style="text-align:center;">
            <h2 style="color:#007BFF; margin-bottom:0;">{target_eng}</h2>
            <p style="font-size:1.2rem; color:#E53935; font-weight:700; margin-top:5px;">{target_sound}</p>
            <h4 style="color:#444;">{target_mean}</h4>
            <hr style="margin:10px 0;">
            <p id="status" style="font-weight:800; color:#333;">🔊 쉐도잉 5회 반복 중...</p>
        </div>
    """, unsafe_allow_html=True)

    st.components.v1.html(f"""
        <script>
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{target_eng.replace("'","")}");
            ut.lang = 'en-US'; ut.rate = 0.85;
            ut.onend = () => {{ loop++; if(loop < 5) setTimeout(play, 700); }};
            window.speechSynthesis.speak(ut);
        }}
        play();
        </script>
    """, height=0)

    st.markdown('<div class="next-area">', unsafe_allow_html=True)
    if st.button("다음 문제 👉", key="next"):
        show_word_popup()
    st.markdown('</div>', unsafe_allow_html=True)