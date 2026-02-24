import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 한 화면에 2열 배치 및 여백 박멸 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 및 헤더 완전 박멸 */
    header {visibility: hidden; height: 0px !important;}
    [data-testid="stHeader"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .main .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: -55px !important;
    }

    /* 2. 카드형 버튼 (영어+발음 세트) */
    div.stButton > button {
        background-color: #ffffff !important;
        border: 1px solid #eee !important;
        border-radius: 12px !important;
        padding: 5px !important;
        width: 100% !important;
        min-height: 65px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #007BFF !important;
        background-color: #f0f7ff !important;
    }
    
    /* 버튼 내부 텍스트 스타일 제어 (st.button 꼼수) */
    div.stButton > button p {
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    /* 3. 상황 박스 (슬림 그라데이션) */
    .context-box {
        background: linear-gradient(135deg, #222 0%, #444 100%);
        color: white;
        border-radius: 12px;
        padding: 10px 15px;
        margin-bottom: 8px;
        text-align: center;
    }

    /* 4. 발음 강조 스타일 (정답 화면용) */
    .sound-acc { color: #E53935; font-size: 1.1rem; font-weight: 900; text-decoration: underline; }
    .sound-base { color: #333333; font-size: 1rem; font-weight: 600; }

    /* 5. 하단 다음 버튼 전용 */
    .next-btn-style > div > button {
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.3rem !important;
        height: 55px !important;
        font-weight: 800 !important;
        margin-top: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 발음 강조 HTML 생성 (정답 화면용)
def get_sound_html(sound_text, is_big=False):
    words = sound_text.split()
    b_size = "font-size: 1.6rem;" if is_big else ""
    a_size = "font-size: 1.9rem;" if is_big else ""
    html = '<div style="display:flex; justify-content:center; gap:3px; flex-wrap:wrap;">'
    for word in words:
        if len(word) > 0:
            html += f'<span><span class="sound-acc" style="{a_size}">{word[0]}</span><span class="sound-base" style="{b_size}">{word[1:]}</span></span>'
    html += '</div>'
    return html

# 데이터 로딩
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
categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어", "💡 기타 일상"]])))
categories = ["💡 전체보기"] + categories

# 상단 선택박스
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

def init_quiz(cat):
    pool = [r for r in all_data if r[0] != "패턴"] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not pool: pool = [r for r in all_data if r[0] != "패턴"]
    st.session_state.quiz_data = random.choice(pool)
    correct_eng = st.session_state.quiz_data[1]
    others = [r for r in all_data if r[0] != "패턴" and r[1] != correct_eng]
    st.session_state.forest_items = random.sample(others, 11) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.forest_items)
    st.session_state.choice_items = random.sample(others, min(len(others), 3)) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.choice_items)
    patterns = [r for r in all_data if r[0] == "패턴"]
    st.session_state.bonus_pattern = random.choice(patterns) if patterns else None
    st.session_state.phase = "forest"

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

# --- 퀴즈 화면 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f'<div class="context-box"><div style="font-size:0.7rem; color:#ffeb3b;">{cat_name}</div><div style="font-size:1.1rem; font-weight:700;">{target_context}</div></div>', unsafe_allow_html=True)

def draw_quiz_grid(items):
    # 2열 배치를 위해 columns(2) 사용
    cols = st.columns(2)
    for i, item in enumerate(items):
        with cols[i % 2]:
            # 영어 문장과 발음을 버튼 텍스트로 합침 (줄바꿈 포함)
            # Streamlit 버튼은 내부 HTML이 제한적이므로 특수문자로 구분
            btn_label = f"🔵 {item[1]}\n({item[2]})"
            if st.button(btn_label, key=f"q_{i}"):
                if item[1] == target_eng: st.session_state.phase = "solved"
                else: st.session_state.phase = "choices"
                st.rerun()

if st.session_state.phase == "forest":
    draw_quiz_grid(st.session_state.forest_items)

elif st.session_state.phase == "choices":
    st.error("아쉬워요! 다시 한 번 골라보세요.")
    draw_quiz_grid(st.session_state.choice_items)

elif st.session_state.phase == "solved":
    st.markdown(f'<div style="text-align:center;"><div style="font-size:2.2rem; font-weight:900; color:#007BFF;">{target_eng}</div>', unsafe_allow_html=True)
    st.markdown(get_sound_html(target_sound, is_big=True), unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#444; margin-top:5px;">{target_mean}</div>', unsafe_allow_html=True)
    st.markdown('<div id="shadow-status" style="color:#E53935; font-weight:800; margin-top:8px; font-size:0.9rem;">🔊 쉐도잉 반복 중...</div></div>', unsafe_allow_html=True)

    if st.session_state.bonus_pattern:
        _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
        st.markdown(f"""
            <div style="background-color:#f0f7ff; border-left:4px solid #007BFF; border-radius:10px; padding:10px; margin-top:10px;">
                <div style="color:#007BFF; font-weight:800; font-size:0.7rem;">📍 보너스 패턴</div>
                <div style="font-size:1rem; font-weight:800; color:#222;">{p_eng}</div>
                <div style="font-size:0.8rem; color:#666;">{p_sound} | {p_mean}</div>
            </div>
        """, unsafe_allow_html=True)

    # JS TTS
    js_target = target_eng.replace("'","")
    js_pattern = st.session_state.bonus_pattern[1].replace("'","").replace("(","").replace(")","") if st.session_state.bonus_pattern else ""
    st.components.v1.html(f"""
        <script>
        const status = window.parent.document.getElementById('shadow-status');
        window.speechSynthesis.cancel();
        let loop = 0;
        function play() {{
            let ut = new SpeechSynthesisUtterance("{js_target}");
            ut.lang = 'en-US'; ut.rate = 0.85;
            status.innerText = "🗣️ 따라하기 (" + (loop+1) + "/5)";
            ut.onend = () => {{
                loop++;
                if(loop < 5) setTimeout(play, 800);
                else if("{js_pattern}") {{
                    status.innerText = "📍 패턴 문장 듣기...";
                    let put = new SpeechSynthesisUtterance("{js_pattern}");
                    put.lang = 'en-US';
                    put.onend = () => status.innerText = "✅ 미션 완료!";
                    window.speechSynthesis.speak(put);
                }}
            }};
            window.speechSynthesis.speak(ut);
        }}
        setTimeout(play, 300);
        </script>
    """, height=0)

    st.markdown('<div class="next-btn-style">', unsafe_allow_html=True)
    if st.button("다음 문제 👉"):
        init_quiz(selected_cat)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)