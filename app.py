import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="영어 시네마 쉐도잉", layout="centered")

# --- CSS: 상단 여백 완전 제거 및 UI 최적화 ---
st.markdown("""
    <style>
    /* 1. 상단 여백 및 헤더 강제 제거 */
    [data-testid="stAppViewContainer"] {
        padding-top: 0px !important;
    }
    [data-testid="stHeader"] {
        display: none !important;
    }
    .main .block-container {
        padding-top: 0px !important;
        margin-top: -60px !important; /* 상단 여백을 더 강력하게 끌어올림 */
    }
    
    .main { background-color: #ffffff; }

    /* 2. 카드 디자인 */
    .study-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        min-height: 85vh;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }

    /* 3. 검색 영역 (GIPHY 검색 버튼 박스) */
    .search-box {
        width: 100%;
        height: 160px;
        border-radius: 15px;
        background-color: #f1f3f5;
        border: 2px dashed #dee2e6;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    
    .giphy-btn {
        display: inline-block;
        padding: 12px 25px;
        background-color: #000000; /* GIPHY 블랙 */
        color: #00ff99 !important; /* GIPHY 네온 그린 */
        text-decoration: none !important;
        border-radius: 10px;
        font-weight: 900;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(0,255,153,0.2);
        text-transform: uppercase;
    }
    
    /* 텍스트 스타일: 블랙 & 레드 */
    .eng-text-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; margin-bottom: 5px; }
    .char-normal { color: #000000; font-size: 1.8rem; font-weight: 500; }
    .char-accent { color: #E53935; font-size: 2.1rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #666; font-size: 1.2rem; margin-bottom: 10px; font-style: italic; }
    .mean-box { padding: 15px; background-color: #f8f9fa; border-radius: 15px; border: 1px solid #eee; margin-bottom: 15px; }
    .mean-text { color: #222; font-size: 1.5rem; font-weight: bold; }
    .status-info { font-size: 1.1rem; color: #E53935; font-weight: bold; margin-bottom: 15px; }
    
    /* 하단 메인 버튼 */
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 15px; font-weight: bold; font-size: 1.3rem !important;
        background-color: #E53935 !important; color: white !important; border: none;
        margin-top: auto;
    }
    </style>
    """, unsafe_allow_html=True)

def get_accented_html(text):
    words = text.split()
    vowels = "aeiouAEIOU"
    html_output = ""
    for word in words:
        html_output += '<div class="word-box">'
        accented = False
        for char in word:
            if not accented and char in vowels and len(word) > 2:
                html_output += f'<span class="char-accent">{char}</span>'
                accented = True
            else:
                html_output += f'<span class="char-normal">{char}</span>'
        html_output += '</div>'
    return html_output

def load_sentences():
    if not os.path.exists(DATA_FILE): return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip().split("|") for line in f if len(line.strip().split("|")) >= 4]

all_sentences = load_sentences()

with st.sidebar:
    st.header("⚙️ 앱 설정")
    study_mode = st.radio("학습 대상", ["1단계: 숙어", "2단계: 패턴"])
    st.session_state.drive_mode = st.toggle("🚗 운전 모드 (자동 넘김)", False)
    target_cat = "숙어" if "숙어" in study_mode else "패턴"
    filtered_data = [s for s in all_sentences if s[0] == target_cat]

if filtered_data:
    if "current_idx" not in st.session_state or st.session_state.get('last_cat') != target_cat:
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.session_state.last_cat = target_cat

    idx = st.session_state.current_idx
    _, eng, sound, mean = filtered_data[idx]

    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # --- 상단 GIPHY 검색 영역 ---
    # 검색어 뒤에 'movie'를 붙여서 상황에 맞는 움짤이 더 잘 나오게 설정
    giphy_search_url = f"https://giphy.com/search/{eng.replace(' ', '-')}-movie"
    st.markdown(f"""
        <div class="search-box">
            <p style="color:#444; margin-bottom:12px; font-weight:bold; font-size:0.9rem;">상황에 맞는 움짤을 찾아보세요</p>
            <a href="{giphy_search_url}" target="_blank" class="giphy-btn">⚡ GIPHY 움짤 검색</a>
        </div>
    """, unsafe_allow_html=True)

    # 텍스트 영역
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">쉐도잉 대기 중</div>
        </div>
    """, unsafe_allow_html=True)

    # JS 로직 (생략 없이 포함)
    is_drive = "true" if st.session_state.drive_mode else "false"
    clean_eng = eng.replace('"', '').replace("'", "")
    
    st.components.v1.html(f"""
        <script>
        function start() {{
            const engEl = window.parent.document.getElementById('display-eng');
            const soundEl = window.parent.document.getElementById('display-sound');
            const statusEl = window.parent.document.getElementById('status-box');
            engEl.classList.remove('hidden-content');
            soundEl.classList.remove('hidden-content');
            window.speechSynthesis.cancel();
            
            let count = 0;
            const isDrive = {is_drive};
            function speak() {{
                let msg = new SpeechSynthesisUtterance("{clean_eng}");
                msg.lang = 'en-US';
                if (count < 5) {{ msg.rate = 0.6; statusEl.innerText = "Step 1: 저속 반복 (" + (count+1) + "/13)"; }}
                else if (count < 10) {{ msg.rate = 0.9; statusEl.innerText = "Step 2: 정상 반복 (" + (count+1) + "/13)"; }}
                else {{ 
                    msg.rate = 0.9; engEl.classList.add('hidden-content'); soundEl.classList.add('hidden-content'); 
                    statusEl.innerText = "Step 3: 장면 연상 (" + (count+1) + "/13)"; 
                }}
                msg.onend = function() {{
                    count++;
                    if (count < 13) {{ setTimeout(speak, 1500); }}
                    else {{
                        statusEl.innerText = isDrive ? "🚗 자동 이동 중..." : "✅ 학습 완료";
                        if(isDrive) {{
                            setTimeout(() => {{
                                const buttons = window.parent.document.querySelectorAll('button');
                                for (let btn of buttons) {{ if (btn.innerText.includes("다음")) {{ btn.click(); break; }} }}
                            }}, 3000);
                        }}
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}
            speak();
        }}
        window.parent.document.querySelectorAll('button').forEach(btn => {{
            if (btn.innerText.includes("다음")) {{ btn.onclick = () => {{ setTimeout(start, 500); }}; }}
        }});
        </script>
    """, height=0)

    if st.button("다음 랜덤 장면 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)