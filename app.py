import streamlit as st
import os
import random

# 파일 경로 설정
DATA_FILE = "sentences.txt"

st.set_page_config(page_title="영어 시네마 쉐도잉", layout="centered")

# --- CSS: 다크 모드 및 레드 강조 UI ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    .study-card {
        background-color: #1c1e21;
        padding: 15px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        border: 1px solid #333;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 85vh; 
    }
    
    .video-container {
        width: 100%;
        border-radius: 15px;
        margin-bottom: 15px;
        overflow: hidden;
        border: 2px solid #444;
        background-color: #000;
    }
    
    .eng-text-container { 
        display: flex; flex-wrap: wrap; align-items: center; justify-content: center; 
        gap: 5px; margin-bottom: 10px; 
    }
    .char-normal { color: #eee; font-size: 1.5rem; font-weight: 500; }
    /* 강조 표시 레드(#E53935)로 수정 */
    .char-accent { color: #E53935; font-size: 1.8rem; font-weight: 800; text-decoration: underline; }
    
    .sound-text { color: #aaa; font-size: 1rem; margin-bottom: 10px; font-style: italic; }
    
    .mean-box { 
        padding: 15px; 
        background-color: #2c2f33; 
        border-radius: 15px;
        margin-bottom: 15px;
    }
    .mean-text { color: #4dabf7; font-size: 1.4rem; font-weight: bold; }
    
    .status-info { font-size: 1rem; color: #E53935; font-weight: bold; margin-bottom: 10px; }
    
    .stButton>button { 
        width: 100%; height: 4.5rem; border-radius: 12px; font-weight: bold; font-size: 1.2rem !important;
        background-color: #E53935 !important; color: white !important; border: none;
    }
    
    /* 유튜브 검색 보조 버튼 스타일 */
    .yt-link {
        display: inline-block; padding: 8px 15px; background-color: #333; color: #ff4d4d;
        text-decoration: none; border-radius: 8px; font-size: 0.8rem; margin-top: 5px;
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
    st.header("🎬 쉐도잉 설정")
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
    yt_id = row[4] if len(row) > 4 else None

    st.markdown('<div class="study-card">', unsafe_allow_html=True)
    
    # --- 영상 영역: 임베딩 방식 개선 ---
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    if yt_id:
        st.video(f"https://www.youtube.com/watch?v={yt_id}")
    else:
        # 유튜브 검색 결과를 직접 보여주기보다, 검색어로 임베딩을 시도하거나 링크 제공
        # 자동 검색 임베딩이 차단될 경우를 대비해 검색 링크를 함께 표시
        st.video(f"https://www.youtube.com/embed?q={eng.replace(' ', '+')}+movie+scene")
        st.markdown(f'<a href="https://www.youtube.com/results?search_query={eng}+movie+scene" target="_blank" class="yt-link">📺 영상이 안 나오면 클릭해서 검색결과 보기</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 텍스트 정보 영역
    st.markdown(f"""
        <div>
            <div id="display-eng" class="eng-text-container">{get_accented_html(eng)}</div>
            <div id="display-sound" class="sound-text">[{sound}]</div>
            <div class="mean-box"><div class="mean-text">{mean}</div></div>
            <div id="status-box" class="status-info">쉐도잉 준비 완료</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # JS 학습 로직 (음성 반복 및 가림 효과)
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
                    statusEl.innerText = "Step 1: 반복 청취 (" + (count+1) + "/13)"; 
                }} else if (count < 10) {{ 
                    msg.rate = 0.9; 
                    statusEl.innerText = "Step 2: 집중 반복 (" + (count+1) + "/13)"; 
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
                        statusEl.innerText = isDrive ? "🚗 다음 장면으로 이동 중..." : "✅ 학습 완료";
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