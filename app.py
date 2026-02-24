import streamlit as st
import os
import random
import requests

# 파일 경로 및 GIPHY 설정
DATA_FILE = "sentences.txt"
# 발급받은 'Beta Key'를 여기에 넣으세요!
GIPHY_API_KEY = "kTRDpyAZYcdXvcVCN7ZnwNjZM9dvJuCT "

st.set_page_config(page_title="영어 시네마 쉐도잉", layout="centered")

# --- CSS: 블랙 & 레드 테마 UI ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; color: #000000; }
    .study-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .media-container {
        width: 100%;
        height: 250px;
        border-radius: 15px;
        overflow: hidden;
        background-color: #f9f9f9;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .media-container img { width: 100%; height: 100%; object-fit: contain; }
    
    /* 텍스트 스타일: 기본 블랙, 강조 레드 */
    .eng-text-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; margin-bottom: 10px; }
    .char-normal { color: #000000; font-size: 1.6rem; font-weight: 500; }
    .char-accent { color: #E53935; font-size: 1.9rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #666; font-size: 1.1rem; margin-bottom: 10px; font-style: italic; }
    .mean-box { padding: 15px; background-color: #f8f9fa; border-radius: 15px; border: 1px solid #eee; }
    .mean-text { color: #222; font-size: 1.5rem; font-weight: bold; }
    .status-info { font-size: 1.1rem; color: #E53935; font-weight: bold; margin-bottom: 15px; }
    
    /* 메인 버튼 레드 */
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 15px; font-weight: bold; font-size: 1.3rem !important;
        background-color: #E53935 !important; color: white !important; border: none;
    }
    .hidden-content { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

def get_giphy_url(keyword):
    """GIPHY API 실시간 검색 (에러 방지 로직 포함)"""
    try:
        # 검색어 뒤에 'movie'를 붙이면 더 적절한 장면이 나옵니다.
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={keyword}+movie&limit=1&rating=g"
        response = requests.get(url, timeout=5).json()
        if 'data' in response and len(response['data']) > 0:
            return response['data'][0]['images']['original']['url']
        return "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueXF3eHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpx/3o7TKunv7I79U/giphy.gif"
    except Exception as e:
        return "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueXF3eHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpx/3o7TKunv7I79U/giphy.gif"

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

# 사이드바 설정
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
    
    # GIPHY 이미지 로드
    gif_url = get_giphy_url(eng)
    st.markdown(f'<div class="media-container"><img src="{gif_url}"></div>', unsafe_allow_html=True)

    # 텍스트 영역
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">쉐도잉 시작</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # TTS & 스크립트
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
                    statusEl.innerText = "Step 3: 장면 연상 쉐도잉 (" + (count+1) + "/13)"; 
                }}
                msg.onend = function() {{
                    count++;
                    if (count < 13) {{ setTimeout(speak, 1500); }}
                    else {{
                        statusEl.innerText = isDrive ? "🚗 다음 장면으로..." : "✅ 학습 완료!";
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