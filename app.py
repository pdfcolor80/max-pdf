import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 문구 자체를 버튼화 & 부드러운 UI ---
st.markdown("""
    <style>
    /* 폰트 설정 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
    }

    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    .main .block-container {
        padding-top: 0rem !important;
        margin-top: -65px !important;
    }

    /* 1. 문구 카드(버튼) 디자인: 테두리 색은 연하게, 글자색은 선명하게 */
    div.stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #f2f2f2 !important; /* 테두리는 거의 안보이게 */
        border-radius: 20px !important;
        padding: 10px 5px !important;
        width: 100% !important;
        min-height: 80px !important;
        margin-bottom: -15px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; /* 부드러운 그림자 */
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        border-color: #007BFF !important;
        background-color: #f0f7ff !important;
        transform: translateY(-2px);
    }

    /* 2. 카드 내 텍스트 스타일 */
    .btn-eng-text { 
        color: #007BFF; 
        font-size: 1.1rem; 
        font-weight: 800; 
        display: block; 
        margin-bottom: 3px;
    }
    .btn-sound-text {
        font-size: 0.9rem;
        font-weight: 500;
        color: #333;
    }

    /* 3. 상황 박스 (다크 모드 느낌으로 문구 강조) */
    .context-box {
        background: #1e1e1e;
        color: #ffffff;
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 10px;
        text-align: center;
    }

    /* 4. 정답 화면 큰 글씨 */
    .res-eng-big { font-size: 2.5rem; font-weight: 900; color: #007BFF; line-height: 1.1; }
    
    /* 컬럼 간격 */
    [data-testid="column"] { padding: 0 5px !important; }
    </style>
    """, unsafe_allow_html=True)

# 발음 강조 HTML
def get_accent_html(sound_text, is_big=False):
    words = sound_text.split()
    b_size = "font-size: 1.6rem;" if is_big else "font-size: 0.9rem;"
    a_size = "font-size: 1.9rem;" if is_big else "font-size: 1rem;"
    html = '<div style="display:flex; justify-content:center; gap:3px; flex-wrap:wrap; pointer-events:none;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span style="color:#E53935; font-weight:900; text-decoration:underline; {a_size}">{word[0]}</span><span style="color:#333; font-weight:600; {b_size}">{word[1:]}</span></span>'
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
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어"]])))
categories = ["💡 전체보기"] + categories

selected_cat = st.selectbox("", categories, label_visibility="collapsed")

def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    others = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.choice_items = random.sample(others, min(len(others), 2)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

@st.dialog("💡 오답 확인")
def show_wrong_answer(item):
    st.markdown(f"### `{item[1]}`")
    st.markdown(f"**뜻:** {item[3]}")
    st.info(f"**상황:** {item[4]}")
    if st.button("다시 도전하기"): st.rerun()

# --- 화면 렌더링 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f"""
    <div class="context-box">
        <div style="font-size:0.75rem; color:#ffeb3b; font-weight:800; margin-bottom:3px;">{cat_name}</div>
        <div style="font-size:1.15rem; font-weight:500; line-height:1.3;">{target_context}</div>
    </div>
""", unsafe_allow_html=True)

def draw_cards(items):
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            # 버튼 배경 위에 글자를 띄우는 방식 (z-index 활용)
            st.markdown(f"""
                <div style="text-align:center; margin-bottom:-48px; position:relative; z-index:1; pointer-events:none;">
                    <div class="btn-eng-text">{item[1]}</div>
                    {get_accent_html(item[2])}
                </div>
            """, unsafe_allow_html=True)
            if st.button("", key=f"btn_{i}"):
                if item[1] == target_eng: st.session_state.phase = "solved"
                else: show_wrong_answer(item); st.session_state.phase = "choices"
                st.rerun()

if st.session_state.phase == "forest":
    draw_cards(st.session_state.forest_items)

elif st.session_state.phase == "choices":
    st.write("<p style='text-align:center; color:#E53935; font-weight:700;'>🎯 정답을 다시 골라보세요 (3개)</p>", unsafe_allow_html=True)
    draw_cards(st.session_state.choice_items)

elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div class="res-eng-big">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_accent_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#444; margin:8px 0;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="status" style="color:#E53935; font-weight:800;">🔊 쉐도잉 5회 반복 중...</div></div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f"""
            <div style="background-color:#f0f7ff; border-left:5px solid #007BFF; border-radius:15px; padding:12px; margin-top:15px;">
                <div style="color:#007BFF; font-weight:800; font-size:0.8rem;">📍 연관 패턴 학습</div>
                <div style="font-size:1.1rem; font-weight:800;">{p_eng}</div>
                <div style="font-size:0.9rem; color:#555;">{p_mean}</div>
            </div>
        """, unsafe_allow_html=True)

    # JS TTS
    js_target = target_eng.replace("'","")
    js_pattern = st.session_state.bonus_pattern[1].replace("'","").replace("(","").replace(")","") if st.session_state.bonus_pattern else ""
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('status');
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{js_target}");
            ut.lang = 'en-US'; ut.rate = 0.85;
            status.innerText = "🗣️ 따라하기 (" + (loop+1) + "/5)";
            ut.onend = () => {{
                loop++;
                if(loop < 5) setTimeout(play, 750);
                else if("{js_pattern}") {{
                    status.innerText = "✅ 패턴 예문 듣기...";
                    let put = new SpeechSynthesisUtterance("{js_pattern}");
                    put.lang = 'en-US';
                    put.onend = () => status.innerText = "🙌 미션 완료!";
                    window.speechSynthesis.speak(put);
                }}
            }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(play, 300);
        </script>
    """, height=0)

    if st.button("다음 문제 👉", key="next_q"):
        init_quiz(selected_cat)
        st.rerun()