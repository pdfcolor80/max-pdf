import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="현실 영어 무한 쉐도잉", layout="centered")

# --- CSS: 상단 여백 제거 및 UI 디자인 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 및 헤더 완전 제거 */
    [data-testid="stAppViewContainer"] { padding-top: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 0px !important; margin-top: -85px !important; }
    
    .main { background-color: #ffffff; }

    /* 퀴즈 카드 디자인 */
    .quiz-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 25px;
        text-align: center;
        box-shadow: 0 4px 30px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
    }

    /* 상황 설명 상자 */
    .context-box {
        background-color: #000000;
        color: #ffffff;
        border-radius: 20px;
        padding: 20px 15px;
        margin-bottom: 20px;
    }
    .context-text { font-size: 1.3rem; font-weight: 700; line-height: 1.4; word-break: keep-all; }

    /* 영어 문장 스타일 */
    .eng-text-container { font-size: 2.2rem; font-weight: 800; color: #000000; margin-bottom: 5px; }
    
    /* 한글 발음 첫 글자 강조 (레드 + 밑줄) */
    .sound-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; margin-bottom: 10px; }
    .sound-word { font-size: 1.5rem; font-weight: 600; color: #444; }
    .sound-accent { color: #E53935; font-size: 1.8rem; font-weight: 900; text-decoration: underline; }
    
    /* 패턴 학습 박스 */
    .pattern-box {
        background-color: #fef2f2;
        border: 2px dashed #E53935;
        border-radius: 15px;
        padding: 15px;
        margin-top: 20px;
        text-align: left;
    }
    .pattern-tag { color: #E53935; font-weight: 800; font-size: 0.9rem; margin-bottom: 5px; }
    .pattern-text { color: #1a1a1a; font-size: 1.2rem; font-weight: 700; font-style: italic; }

    .mean-text { color: #666; font-size: 1.2rem; margin-bottom: 10px; font-weight: 500; }
    .status-info { font-size: 1.1rem; color: #E53935; font-weight: bold; margin-bottom: 10px; }

    /* 버튼 스타일 */
    .stButton>button { border-radius: 10px; font-weight: bold; width: 100%; }
    .next-btn>div .stButton>button {
        height: 4rem;
        background-color: #E53935 !important;
        color: white !important;
        font-size: 1.3rem !important;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_accented_sound_html(sound_text):
    """한글 발음의 각 단어 첫 글자만 빨간색 강조"""
    words = sound_text.split()
    html_output = '<div class="sound-container">'
    for word in words:
        if len(word) > 0:
            html_output += f'<div style="display:flex; align-items:baseline;">'
            html_output += f'<span class="sound-accent">{word[0]}</span>'
            if len(word) > 1:
                html_output += f'<span class="sound-word">{word[1:]}</span>'
            html_output += '</div>&nbsp;'
    html_output += '</div>'
    return html_output

def load_data():
    idioms, patterns = [], []
    if not os.path.exists(DATA_FILE): return idioms, patterns
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            p = line.strip().split("|")
            if p[0] == "숙어" and len(p) >= 5: idioms.append(p)
            elif p[0] == "패턴" and len(p) >= 4: patterns.append(p)
    return idioms, patterns

# 데이터 로드
idioms, patterns = load_data()

if idioms:
    # --- 퀴즈 세션 관리 ---
    if "quiz_idx" not in st.session_state:
        st.session_state.quiz_idx = random.randint(0, len(idioms) - 1)
        st.session_state.phase = "forest"  # forest(1단계) -> choices(2단계) -> solved(완료)
        
        # 보기 생성
        correct_eng = idioms[st.session_state.quiz_idx][1]
        others = [d[1] for d in idioms if d[1] != correct_eng]
        st.session_state.forest_opts = random.sample(others, 11) + [correct_eng]
        random.shuffle(st.session_state.forest_opts)
        st.session_state.choice_opts = random.sample(others, 3) + [correct_eng]
        random.shuffle(st.session_state.choice_opts)
        
        # 보너스 패턴 (패턴 리스트에서 랜덤)
        st.session_state.bonus_pattern = random.choice(patterns) if patterns else None

    curr = idioms[st.session_state.quiz_idx]
    cat, eng, sound, mean, context = curr[:5]

    st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
    
    # 1. 상황 설명 (무조건 상단 고정)
    st.markdown(f'<div class="context-box"><div class="context-text">💡 {context}</div></div>', unsafe_allow_html=True)

    # 2. 퀴즈 단계별 화면
    if st.session_state.phase == "forest":
        st.write("🌳 **1단계: 단어 숲에서 정답을 찾아보세요!**")
        cols = st.columns(3)
        for i, opt in enumerate(st.session_state.forest_opts):
            if cols[i % 3].button(opt, key=f"f_{i}"):
                if opt == eng:
                    st.session_state.phase = "solved"
                    st.session_state.msg = "🎯 대단해요! 한 번에 맞췄어요!"
                else:
                    st.session_state.phase = "choices"
                st.rerun()

    elif st.session_state.phase == "choices":
        st.warning("⚠️ 틀렸습니다! 다시 기회를 드릴게요.")
        st.write("❓ **2단계: 4개 중에서 골라보세요**")
        for i, opt in enumerate(st.session_state.choice_opts):
            if st.button(opt, key=f"c_{i}"):
                st.session_state.phase = "solved"
                st.session_state.msg = "✅ 정답 확인!"
                st.rerun()

    # 3. 정답 노출 및 쉐도잉 + 패턴 연계
    elif st.session_state.phase == "solved":
        st.subheader(st.session_state.msg)
        st.markdown(f"""
            <div style="margin-top:15px;">
                <div class="eng-text-container">{eng}</div>
                {get_accented_sound_html(sound)}
                <div class="mean-text">뜻: {mean}</div>
                <div id="status-box" class="status-info">쉐도잉 반복 중 (5회)</div>
            </div>
        """, unsafe_allow_html=True)

        # 보너스 패턴 박스
        if st.session_state.bonus_pattern:
            _, p_eng, p_sound, p_mean = st.session_state.bonus_pattern[:4]
            st.markdown(f"""
                <div class="pattern-box">
                    <div class="pattern-tag">📍 보너스 패턴 공부</div>
                    <div class="pattern-text">"{p_eng}"</div>
                    <div style="color:#666; font-size:0.9rem; margin-top:5px;">{p_sound} | {p_mean}</div>
                </div>
            """, unsafe_allow_html=True)

        # TTS 로직: 숙어 5번 + 패턴 1번
        p_eng_clean = st.session_state.bonus_pattern[1].replace("(", "").replace(")", "").replace("'", "")
        clean_eng = eng.replace("'", "")
        
        st.components.v1.html(f"""
            <script>
            function start() {{
                const statusEl = window.parent.document.getElementById('status-box');
                window.speechSynthesis.cancel();
                let count = 0;
                function speak() {{
                    let msg = new SpeechSynthesisUtterance("{clean_eng}");
                    msg.lang = 'en-US';
                    msg.rate = 0.8;
                    statusEl.innerText = "🗣️ 소리내어 따라하세요 (" + (count+1) + "/5)";
                    msg.onend = () => {{
                        count++;
                        if (count < 5) setTimeout(speak, 1000);
                        else {{
                            statusEl.innerText = "📍 마지막으로 패턴 문장 듣기...";
                            let p_msg = new SpeechSynthesisUtterance("{p_eng_clean}");
                            p_msg.lang = 'en-US';
                            p_msg.onend = () => {{ statusEl.innerText = "✅ 마스터 완료!"; }};
                            setTimeout(() => window.speechSynthesis.speak(p_msg), 800);
                        }}
                    }};
                    window.speechSynthesis.speak(msg);
                }}
                setTimeout(speak, 500);
            }}
            start();
            </script>
        """, height=0)

        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button("다음 문제 👉"):
            for key in ["quiz_idx", "phase", "forest_opts", "choice_opts", "msg", "bonus_pattern"]:
                if key in st.session_state: del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)