import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 모바일 2열 강제 고정 및 폰트/클릭 최적화 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    
    /* 전체 폰트 적용 */
    html, body, [class*="css"], .stApp {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    .main .block-container { padding-top: 0rem !important; margin-top: -60px !important; }

    /* 2열 그리드 강제 고정 (모바일 포함) */
    .grid-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        width: 100%;
        margin-top: 10px;
    }

    .card-wrapper {
        position: relative;
        width: 100%;
        min-height: 85px;
        background: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        overflow: hidden; /* 버튼이 튀어나가지 않게 */
    }

    /* 문구 스타일 */
    .eng-txt { color: #007BFF; font-size: 0.95rem; font-weight: 800; margin-bottom: 2px; pointer-events: none; }
    .acc-char { color: #E53935; font-weight: 900; text-decoration: underline; font-size: 0.9rem; pointer-events: none; }
    .base-char { color: #333333; font-weight: 600; font-size: 0.85rem; pointer-events: none; }

    /* 스트림릿 버튼을 카드 전체로 확장 (클릭 해결) */
    .stButton > button {
        width: 100% !important;
        height: 85px !important;
        background-color: transparent !important;
        color: transparent !important;
        border: none !important;
        position: absolute !important;
        top: 0; left: 0;
        z-index: 10;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 카드 활성화 효과 */
    .card-wrapper:active { background-color: #f0f7ff; transform: scale(0.98); }

    /* 상황 박스 */
    .context-box {
        background: #1a1a1a;
        color: white;
        border-radius: 15px;
        padding: 12px;
        margin-bottom: 10px;
        text-align: center;
        font-size: 1rem;
    }

    /* 다음 버튼 디자인 */
    .next-btn-style .stButton > button {
        background-color: #E53935 !important;
        color: white !important;
        height: 50px !important;
        border-radius: 25px !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        position: relative !important;
        z-index: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def make_sound_html(sound_text, is_big=False):
    words = sound_text.split()
    b_size = "font-size: 1.6rem;" if is_big else ""
    a_size = "font-size: 1.9rem;" if is_big else ""
    html = '<div style="display:flex; justify-content:center; gap:2px; flex-wrap:wrap; line-height:1;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="acc-char" style="{a_size}">{word[0]}</span><span class="base-char" style="{b_size}">{word[1:]}</span></span>'
    html += '</div>'
    return html

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
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = all_data
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    others = [r for r in all_data if r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.choice_items = random.sample(others, min(len(others), 2)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

@st.dialog("📚 필수 단어 복습")
def show_random_word():
    words_pool = [r for r in all_data if r[0] in ["숙어", "패턴"]]
    word = random.choice(words_pool) if words_pool else all_data[0]
    st.markdown(f"<h2 style='text-align:center; color:#007BFF;'>{word[1]}</h2>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; margin-bottom:15px;'>{make_sound_html(word[2], is_big=True)}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:1.2rem;'><b>뜻: {word[3]}</b></p>", unsafe_allow_html=True)
    st.info(f"**활용 상황:** {word[4]}")
    if st.button("다음 퀴즈 시작! 👉", use_container_width=True):
        init_quiz(selected_cat)
        st.rerun()

@st.dialog("💡 오답 확인")
def show_wrong_answer(item):
    st.markdown(f"### `{item[1]}`")
    st.markdown(f"**뜻:** {item[3]}")
    st.info(f"**상황:** {item[4]}")
    if st.button("다시 도전하기"): st.rerun()

# --- 화면 렌더링 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f"""<div class="context-box"><b>{cat_name}</b><br>{target_context} ({target_mean})</div>""", unsafe_allow_html=True)

if st.session_state.phase in ["forest", "choices"]:
    items = st.session_state.forest_items if st.session_state.phase == "forest" else st.session_state.choice_items
    
    # st.columns 대신 직접 HTML과 st.button 순차 배치
    # CSS에서 이 버튼들을 그리드 형태로 재배치함
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    for i, item in enumerate(items):
        # 개별 카드를 감싸는 컨테이너
        with st.container():
            st.markdown(f"""
                <div class="card-wrapper">
                    <div class="eng-txt">{item[1]}</div>
                    <div class="snd-txt">{make_sound_html(item[2])}</div>
            """, unsafe_allow_html=True)
            if st.button(" ", key=f"btn_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                else:
                    st.session_state.phase = "choices"
                    show_wrong_answer(item)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div style="font-size:2.3rem; font-weight:900; color:#007BFF;">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(make_sound_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#444; margin:10px 0;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="status" style="color:#E53935; font-weight:800;">🔊 따라 읽으세요!</div></div>', unsafe_allow_html=True)

    # JS TTS
    js_target = target_eng.replace("'","")
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('status');
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{js_target}");
            ut.lang = 'en-US'; ut.rate = 0.8;
            status.innerText = "🗣️ 반복 중 (" + (loop+1) + "/5)";
            ut.onend = () => {{ loop++; if(loop < 5) setTimeout(play, 700); else status.innerText = "✅ 완료!"; }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(play, 300);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn-style">', unsafe_allow_html=True)
    if st.button("다음 문제 👉", key="next_main"):
        show_random_word()
    st.markdown('</div>', unsafe_allow_html=True)