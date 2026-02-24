import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 모바일 한 줄 고정 및 디자인 최적화 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif !important; }
    header { visibility: hidden; height: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 10px !important; margin-top: -60px !important; }

    .context-box {
        background: #1e1e1e; color: white; border-radius: 12px;
        padding: 8px 12px; margin-bottom: 15px; text-align: center; font-size: 0.85rem;
    }

    /* 버튼 레이아웃 강제 한 줄 고정 (Flex 사용 대신 컬럼 간격 미세 조정) */
    [data-testid="column"] {
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* 보기 버튼 스타일 */
    .stButton > button {
        width: 100% !important;
        margin: 0 !important;
        border-radius: 10px !important;
        background-color: white !important;
        border: 1px solid #ddd !important;
        height: 52px !important;
        display: flex; align-items: center; justify-content: center;
    }

    /* 보기 텍스트 크기 조절 */
    div[data-testid="stButton"] button p {
        font-size: 0.82rem !important;
        line-height: 1.2 !important;
    }

    /* 스피커 아이콘 크기 */
    .spk-btn button p {
        font-size: 1.3rem !important;
    }

    /* 다음 문제 버튼 (하단 고정 느낌) */
    .next-area button {
        background-color: #E53935 !important;
        color: white !important;
        height: 58px !important;
        border-radius: 29px !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
        margin-top: 20px !important;
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
                if len(p) >= 5: all_rows.append(p)
    return all_rows

all_data = load_data()

# 퀴즈 초기화 함수
def init_quiz(cat):
    quiz_pool = [r for r in all_data if r[0] not in ["패턴", "숙어", "단어"]] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not quiz_pool: quiz_pool = [r for r in all_data if r[0] not in ["패턴", "숙어", "단어"]]
    
    st.session_state.quiz_data = random.choice(quiz_pool)
    correct_eng = st.session_state.quiz_data[1]
    
    distractor_pool = [r for r in all_data if r[0] == "단어" and r[1] != correct_eng]
    if len(distractor_pool) < 5: distractor_pool = [r for r in all_data if r[1] != correct_eng]
    
    st.session_state.forest_items = random.sample(distractor_pool, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.phase = "forest"

# --- 다이얼로그 정의 ---

@st.dialog("🤪 풉! 실망이야")
def show_wrong_dialog(item):
    st.markdown(f"<h3 style='text-align:center;'>{item[1]}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-weight:bold; color:#E53935;'>뜻: {item[3]}</p>", unsafe_allow_html=True)
    st.info(f"**상황 설명:** {item[4]}")
    # 비웃음 소리
    st.components.v1.html("<script>const ctx=new(window.AudioContext||window.webkitAudioContext)();function beep(f,d,s){const o=ctx.createOscillator();const g=ctx.createGain();o.type='sawtooth';o.frequency.value=f;g.gain.setValueAtTime(0.05,ctx.currentTime);o.connect(g);g.connect(ctx.destination);o.start(ctx.currentTime+s);o.stop(ctx.currentTime+s+d);}beep(880,0.1,0);beep(1100,0.2,0.15);</script>", height=0)
    if st.button("반성하고 다시 도전 🙇", use_container_width=True):
        st.rerun()

@st.dialog("📚 단어 복습")
def show_review_dialog():
    review_pool = [r for r in all_data if r[0] == "단어"]
    w = random.choice(review_pool) if review_pool else ["단어", "No Data", "", "데이터가 없습니다", ""]
    st.markdown(f"<h3 style='text-align:center;'>{w[1]}</h3>", unsafe_allow_html=True)
    st.write(f"**뜻:** {w[3]}")
    st.write(f"**발음:** {w[2]}")
    st.info(f"**상황:** {w[4]}")
    if st.button("외웠으니 다음 문제!", use_container_width=True):
        init_quiz(selected_cat)
        st.rerun()

# --- 로직 시작 ---
if "phase" not in st.session_state:
    st.session_state.phase = "forest"

categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어", "단어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f'<div class="context-box"><b>{cat_name}</b><br>{target_context} ({target_mean})</div>', unsafe_allow_html=True)

# 1. 문제 풀기 단계
if st.session_state.phase == "forest":
    for i, item in enumerate(st.session_state.forest_items):
        c1, c2 = st.columns([0.83, 0.17])
        with c1:
            if st.button(f"{item[1]} / {item[2]}", key=f"ans_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                    st.rerun()
                else:
                    show_wrong_dialog(item)
        with c2:
            st.markdown('<div class="spk-btn">', unsafe_allow_html=True)
            if st.button("🔊", key=f"spk_{i}"):
                st.components.v1.html(f"<script>window.speechSynthesis.cancel();let ut=new SpeechSynthesisUtterance('{item[1].replace(\"'\",\"\")}');ut.lang='en-US';ut.rate=0.9;window.speechSynthesis.speak(ut);</script>", height=0)
            st.markdown('</div>', unsafe_allow_html=True)

# 2. 정답 맞힌 단계
elif st.session_state.phase == "solved":
    st.balloons()
    st.markdown(f"""
        <div style="text-align:center;">
            <h2 style="color:#007BFF; margin-bottom:0;">{target_eng}</h2>
            <p style="font-size:1.2rem; color:#E53935; font-weight:700;">{target_sound}</p>
            <h4 style="color:#444;">{target_mean}</h4>
            <hr>
            <p style="font-weight:800; color:#333;">🔊 5회 반복 쉐도잉 중...</p>
        </div>
    """, unsafe_allow_html=True)

    st.components.v1.html(f"<script>window.speechSynthesis.cancel();let loop=0;function play(){{let ut=new SpeechSynthesisUtterance('{target_eng.replace(\"'\",\"\")}');ut.lang='en-US';ut.rate=0.85;ut.onend=()=>{ { "loop++; if(loop < 5) setTimeout(play, 700);" } };window.speechSynthesis.speak(ut);}}play();</script>", height=0)

    st.markdown('<div class="next-area">', unsafe_allow_html=True)
    if st.button("다음 문제 👉", key="next_btn"):
        show_review_dialog()
    st.markdown('</div>', unsafe_allow_html=True)