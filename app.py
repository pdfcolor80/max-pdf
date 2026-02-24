import streamlit as st
import os
import random
import requests

# 파일 경로 및 GIPHY 설정
DATA_FILE = "sentences.txt"
GIPHY_API_KEY = "여기에_발급받은_API_키를_넣으세요" 

st.set_page_config(page_title="영어 시네마 쉐도잉", layout="centered")

# --- CSS: 상단 공백 및 모든 여백 강제 제거 ---
st.markdown("""
    <style>
    /* 1. 최상위 루트 컨테이너 여백 제거 */
    .main .block-container {
        padding-top: 0px !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        padding-bottom: 0px !important;
    }
    
    /* 2. 스트림릿 기본 헤더/푸터/메뉴 숨기기 및 높이 제거 */
    header { visibility: hidden; height: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    /* 3. 앱 배경 설정 */
    .main { 
        background-color: #ffffff; 
    }

    /* 4. 학습 카드 스타일: 상단 밀착 */
    .study-card {
        background-color: #ffffff;
        padding: 5px 15px; 
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        min-height: 95vh;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        margin-top: 0px !important;
    }

    /* 5. 미디어(GIF) 영역: 상단 여백 최소화 */
    .media-container {
        width: 100%;
        height: 240px;
        border-radius: 15px;
        overflow: hidden;
        background-color: #f9f9f9;
        margin-top: 5px; /* 위쪽 여백 최소화 */
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .media-container img { width: 100%; height: 100%; object-fit: contain; }
    
    .eng-text-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 5px; margin-bottom: 5px; }
    .char-normal { color: #000000; font-size: 1.6rem; font-weight: 500; }
    .char-accent { color: #E53935; font-size: 1.9rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #666; font-size: 1.1rem; margin-bottom: 10px; font-style: italic; }
    .mean-box { padding: 12px; background-color: #f8f9fa; border-radius: 15px; border: 1px solid #eee; margin-bottom: 10px; }
    .mean-text { color: #222; font-size: 1.4rem; font-weight: bold; }
    .status-info { font-size: 1.1rem; color: #E53935; font-weight: bold; margin-bottom: 10px; }
    
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 15px; font-weight: bold; font-size: 1.3rem !important;
        background-color: #E53935 !important; color: white !important; border: none;
        margin-top: auto; 
    }
    </style>
    """, unsafe_allow_html=True)

def get_giphy_url(keyword):
    try:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={keyword}+movie&limit=1&rating=g"
        response = requests.get(url, timeout=5).json()
        if 'data' in response and len(response['data']) > 0:
            return response['data'][0]['images']['original']['url']
        return "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueXF3eHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpxeHpx/3o7TKunv7I79U/giphy.gif"
    except:
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

    # 실제 카드 렌더링 시작
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    gif_url = get_giphy_url(eng)
    st.markdown(f'<div class="media-container"><img src="{gif_url}"></div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">쉐도잉 대기 중</div>
        </div>
    """, unsafe_allow_html=True)

    # JavaScript 학습 로직
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
    
    st.markdown('</div>', unsafe_allow_html=True)