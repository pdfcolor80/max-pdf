import streamlit as st
import os
import random

# 파일 및 이미지 경로 설정
DATA_FILE = "sentences.txt"
IMAGE_DIR = "images" 

st.set_page_config(page_title="영어 이미지 연상 학습", layout="centered")

# --- CSS: 스마트폰 가독성 및 UI 최적화 ---
st.markdown("""
    <style>
    .main { background-color: #fdfdfd; }
    .study-card {
        background-color: #ffffff;
        padding: 20px 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        min-height: 500px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        border: 1px solid #eee;
    }
    
    .image-container {
        width: 100%;
        height: 200px; /* 스마트폰 높이 고려 */
        background-color: #f9f9f9;
        border-radius: 15px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    
    .eng-text-container { display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 8px; margin-bottom: 10px; }
    .word-box { display: flex; align-items: baseline; }
    .char-normal { color: #333; font-size: 1.6rem; font-weight: 500; }
    .char-accent { color: #E53935; font-size: 1.9rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #666; font-size: 1rem; margin-bottom: 10px; font-style: italic; }
    .hidden-content { display: none !important; }
    
    .mean-box { margin-top: auto; padding: 15px; border-top: 1px solid #f0f0f0; background-color: #f8faff; border-radius: 15px; }
    .mean-text { color: #1a73e8; font-size: 1.5rem; font-weight: bold; }
    
    .status-info { margin-top: 15px; font-size: 1rem; color: #d32f2f; font-weight: bold; }
    
    /* 스마트폰 버튼 크게 */
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 12px; font-weight: bold; font-size: 1.2rem !important;
        background-color: #333 !important; color: white !important; 
    }
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
    st.header("🎯 학습 메뉴")
    study_mode = st.radio("학습 단계", ["1단계: 핵심 숙어 마스터", "2단계: 패턴 영어 완성"])
    st.session_state.drive_mode = st.toggle("🚗 운전 모드", value=st.session_state.get('drive_mode', False))
    target_cat = "숙어" if "1단계" in study_mode else "패턴"
    filtered_data = [s for s in all_sentences if s[0] == target_cat]

if filtered_data:
    if "current_idx" not in st.session_state or st.session_state.get('last_cat') != target_cat:
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.session_state.last_cat = target_cat

    idx = st.session_state.current_idx
    _, eng, sound, mean = filtered_data[idx]
    
    # 이미지 표시 로직
    img_filename = eng.lower().replace(" ", "_").replace("'", "") + ".jpg"
    img_path = os.path.join(IMAGE_DIR, img_filename)
    
    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # 🖼️ 이미지 영역
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.markdown(f'<div class="image-container" style="color:#ccc;">이미지 준비 중<br>({img_filename})</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
        <div id="display-sound" class="sound-text">[{sound}]</div>
        <div class="mean-box"><div class="mean-text">{mean}</div></div>
        <div id="status-box" class="status-info">시작하려면 아래 버튼 클릭</div>
    </div>
    """, unsafe_allow_html=True)

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
                    msg.rate = 0.5;
                    statusEl.innerText = "Step 1: 느리게 (" + (count+1) + "/13)";
                }} else if (count < 10) {{
                    msg.rate = 0.8;
                    statusEl.innerText = "Step 2: 정상 반복 (" + (count+1) + "/13)";
                }} else {{
                    msg.rate = 0.8;
                    engEl.classList.add('hidden-content');
                    soundEl.classList.add('hidden-content');
                    statusEl.innerText = "Step 3: 가리고 말하기 (" + (count+1) + "/13)";
                }}

                msg.onend = function() {{
                    count++;
                    if (count < 13) {{
                        setTimeout(speak, 1500);
                    }} else {{
                        statusEl.innerText = isDrive ? "🚗 다음 문장 이동..." : "✅ 학습 완료";
                        if(isDrive) {{
                            setTimeout(() => {{
                                const buttons = window.parent.document.querySelectorAll('button');
                                for (let btn of buttons) {{
                                    if (btn.innerText.includes("다음")) {{
                                        btn.click();
                                        break;
                                    }}
                                }
                            }}, 3000);
                        }}
                    }}
                }};
                window.speechSynthesis.speak(msg);
            }}
            speak();
        }}
        
        // 버튼 클릭 감지
        window.parent.document.querySelectorAll('button').forEach(btn => {{
            if (btn.innerText.includes("다음")) {{
                btn.onclick = () => {{ setTimeout(start, 500); }};
            }
        }});
        </script>
    """, height=0)

    if st.button("다음 랜덤 문장 👉 (학습 시작)", type="primary"):
        st.session_state.current_idx = random.randint(0, len(filtered_data) - 1)
        st.rerun()