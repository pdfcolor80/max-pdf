import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"
IMAGE_DIR = "images" # GIF 파일을 저장할 폴더

st.set_page_config(page_title="영어 시네마 쉐도잉", layout="centered")

# --- CSS: 블랙 & 레드 테마 UI ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; color: #000000; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    .study-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 85vh; 
    }
    
    /* GIF/이미지 영역 */
    .media-container {
        width: 100%;
        height: 220px;
        border-radius: 15px;
        margin-bottom: 15px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #f9f9f9;
    }
    .media-container img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }
    
    .eng-text-container { 
        display: flex; flex-wrap: wrap; align-items: center; justify-content: center; 
        gap: 5px; margin-bottom: 10px; 
    }
    /* 단어 기본색: 블랙 */
    .char-normal { color: #000000; font-size: 1.5rem; font-weight: 500; }
    /* 강조색: 레드 */
    .char-accent { color: #E53935; font-size: 1.8rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #666; font-size: 1rem; margin-bottom: 10px; font-style: italic; }
    
    .mean-box { 
        padding: 15px; 
        background-color: #f8f9fa; 
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #eee;
    }
    .mean-text { color: #222; font-size: 1.4rem; font-weight: bold; }
    
    .status-info { font-size: 1rem; color: #E53935; font-weight: bold; margin-bottom: 10px; }
    
    /* 메인 버튼: 레드 */
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 12px; font-weight: bold; font-size: 1.2rem !important;
        background-color: #E53935 !important; color: white !important; border: none;
    }
    
    /* 유튜브 검색 버튼 스타일 */
    .yt-search-btn {
        display: block; width: 100%; padding: 10px; margin-top: 5px;
        background-color: #f1f1f1; color: #cc0000; text-decoration: none;
        border-radius: 10px; font-size: 0.9rem; font-weight: bold;
        border: 1px solid #ddd;
    }

    .hidden-content { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

def get_accented_html(text):
    words = text.split()
    vowels = "aeiouAEIOU"
    html_output = ""
    for word in words:
        html_output += '<div class="word-box">'
        accent_done = False
        for char in word:
            if not accent_done and char in vowels and len(word) > 2:
                html_output += f'<span class="char-accent">{char}</span>'
                accent_done = True
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
    st.header("⚙️ 설정")
    study_mode = st.radio("단계", ["1단계: 숙어", "2단계: 패턴"])
    st.session_state.drive_mode = st.toggle("🚗 운전 모드", value=st.session_state.get('drive_mode', False))
    target_cat = "숙어" if "숙어" in study_mode else "패턴"
    filtered_data = [s for s in all_sentences if s[0] == target_cat]

if filtered_data:
    if "current_idx" not in st.session_state or st.session_state.get('last_cat') != target_cat:
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.session_state.last_cat = target_cat

    idx = st.session_state.current_idx
    row = filtered_data[idx]
    cat, eng, sound, mean = row[0], row[1], row[2], row[3]

    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # --- 미디어 영역: GIF 우선 표시 ---
    gif_filename = eng.lower().replace(" ", "_").replace("'", "") + ".gif"
    gif_path = os.path.join(IMAGE_DIR, gif_filename)
    
    st.markdown('<div class="media-container">', unsafe_allow_html=True)
    if os.path.exists(gif_path):
        st.image(gif_path)
    else:
        st.markdown(f'<div style="color:#999; font-size:0.9rem;">이미지(GIF)를 images 폴더에<br>{gif_filename} 이름으로 넣어주세요</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 텍스트 정보 영역
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">쉐도잉 시작</div>
            <a href="https://www.youtube.com/results?search_query={eng}+movie+scene" target="_blank" class="yt-search-btn">🎬 관련 영상 유튜브에서 검색하기</a>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # JS 학습 로직
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
                
                if (count < 5) {{ 
                    msg.rate = 0.6; 
                    statusEl.innerText = "Step 1: 저속 듣기 (" + (count+1) + "/13)"; 
                }} else if (count < 10) {{ 
                    msg.rate = 0.9; 
                    statusEl.innerText = "Step 2: 정상 반복 (" + (count+1) + "/13)"; 
                }} else {{ 
                    msg.rate = 0.9; 
                    engEl.classList.add('hidden-content'); 
                    soundEl.classList.add('hidden-content'); 
                    statusEl.innerText = "Step 3: 장면 연상 쉐도잉 (" + (count+1) + "/13)"; 
                }}

                msg.onend = function() {{
                    count++;
                    if (count < 13) {{ 
                        setTimeout(speak, 1500); 
                    }} else {{
                        statusEl.innerText = isDrive ? "🚗 다음 장면 준비 중..." : "✅ 학습 완료";
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
            if (btn.innerText.includes("다음")) {{ 
                btn.onclick = () => {{ setTimeout(start, 500); }}; 
            }}
        }});
        </script>
    """, height=0)

    if st.button("다음 랜덤 장면 👉", type="primary"):
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.rerun()