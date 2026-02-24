import streamlit as st
import os
import random
import time

# --- 파일 및 설정 ---
DATA_FILE = "sentences.txt"
st.set_page_config(page_title="영어 수용소 V3", layout="centered")

# --- CSS: 킹받는 UI 및 애니메이션 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; }
    .main-title { font-family: 'Black Han Sans', sans-serif; color: #ff4b4b; text-align: center; font-size: 3rem; }
    .context-box { background: #1e1e1e; color: #00ff00; border-radius: 15px; padding: 25px; margin-bottom: 20px; text-align: center; border: 3px solid #444; font-size: 1.3rem; line-height: 1.6; }
    .prison-mode { background: #4a0000; color: #ff0000; padding: 40px; border-radius: 20px; text-align: center; border: 10px double #ff0000; animation: shake 0.5s infinite; }
    @keyframes shake { 0% { transform: translate(1px, 1px) rotate(0deg); } 10% { transform: translate(-1px, -2px) rotate(-1deg); } 20% { transform: translate(-3px, 0px) rotate(1deg); } 100% { transform: translate(1px, -2px) rotate(-1deg); } }
    .stButton > button { width: 100%; height: 60px; border-radius: 15px; font-weight: 700; font-size: 1.1rem; transition: 0.3s; }
    .pattern-card { background: #f0f2f6; border-left: 10px solid #ff4b4b; padding: 20px; margin: 10px 0; border-radius: 10px; color: #31333F; }
    </style>
    """, unsafe_allow_html=True)

# --- 효과음 및 TTS 로직 (Web Audio API) ---
def play_sound(type):
    sound_js = {
        "success": "let c=new AudioContext(); let o=c.createOscillator(); let g=c.createGain(); o.connect(g); g.connect(c.destination); o.type='triangle'; o.frequency.setValueAtTime(523.25, c.currentTime); g.gain.setValueAtTime(0.1, c.currentTime); o.start(); o.stop(c.currentTime+0.2); setTimeout(()=>{let o2=c.createOscillator(); o2.connect(g); o2.type='triangle'; o2.frequency.setValueAtTime(659.25, c.currentTime); o2.start(); o2.stop(c.currentTime+0.2);}, 200);",
        "wrong": "let c=new AudioContext(); let o=c.createOscillator(); o.connect(c.destination); o.type='sawtooth'; o.frequency.setValueAtTime(150, c.currentTime); o.start(); o.stop(c.currentTime+0.3);",
        "prison": "let c=new AudioContext(); let o=c.createOscillator(); let g=c.createGain(); o.connect(g); g.connect(c.destination); o.type='square'; setInterval(()=>{o.frequency.exponentialRampToValueAtTime(800, c.currentTime+0.5); o.frequency.exponentialRampToValueAtTime(400, c.currentTime+1);}, 1000); o.start();",
        "popup": "let c=new AudioContext(); let o=c.createOscillator(); let g=c.createGain(); o.connect(g); g.connect(c.destination); o.frequency.setValueAtTime(100, c.currentTime); o.frequency.exponentialRampToValueAtTime(1000, c.currentTime+0.2); o.start(); o.stop(c.currentTime+0.2);"
    }
    st.components.v1.html(f"<script>{sound_js.get(type, '')}</script>", height=0)

def play_tts(text, count=1):
    js = f"""<script>window.speechSynthesis.cancel(); let l=0; function p(){{ let u=new SpeechSynthesisUtterance("{text.replace('"', '')}"); u.lang='en-US'; u.rate=0.8; u.onend=()=>{{ l++; if(l<{count}) setTimeout(p, 300); }}; window.speechSynthesis.speak(u); }} p();</script>"""
    st.components.v1.html(js, height=0)

# --- 데이터 로드 ---
@st.cache_data
def load_all_data():
    data = {"quiz": [], "pattern": [], "word": []}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) < 5: continue
                if "패턴" in p[0]: data["pattern"].append(p)
                elif "단어" in p[0]: data["word"].append(p)
                else: data["quiz"].append(p)
    return data

db = load_all_data()

# --- 세션 초기화 ---
if "mode" not in st.session_state: st.session_state.mode = "HOME"
if "wrong_log" not in st.session_state: st.session_state.wrong_log = {}
if "attempt" not in st.session_state: st.session_state.attempt = 1

# --- 멘트 리스트 ---
praises = ["와... 뇌 섹시미 폭발! ✨", "유전자 자체가 영어 최적화인가요? ⚡", "방금 발음, 구글 번역기 의문의 1패! 🎙️", "천재인가? 뇌 세포들이 단체로 열일 중!"]
insults_1 = ["손가락이 미끄러진 거죠? 🤨", "에이, 일부러 틀린 거 다 알아요. 그쵸?", "뇌가 잠시 로그아웃 하셨나요?"]
insults_2 = ["와, 진심인가요? 찍기 전용 뇌를 따로 쓰시나... 🤡", "지능이 아니라 운에 맡기고 계시죠? 보기 줄여드릴게요.", "AI인 저도 당황스럽네요. 데이터 오류인가?"]

# --- 팝업: 랜덤 단어 학습 ---
@st.dialog("🎁 보너스! 랜덤 단어 복습")
def word_popup():
    play_sound("popup")
    st.write("다음 문제로 가기 전, 뇌를 더 섹시하게 만드세요!")
    targets = random.sample(db["word"], min(len(db["word"]), 2))
    for t in targets:
        st.markdown(f"### **{t[1]}**")
        st.write(f"뜻: {t[4]} (발음: {t[2]})")
        st.write("---")
    if st.button("암기 완료! 다음으로 👉"):
        st.session_state.phase = "IDLE"
        st.rerun()

# --- 메인 화면 로직 ---
if st.session_state.mode == "HOME":
    st.markdown("<h1 class='main-title'>ENGLISH PRISON V3</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔥 숙어/단어 퀴즈 (수용소)"):
            st.session_state.mode = "QUIZ"
            st.session_state.phase = "IDLE"
            st.rerun()
    with col2:
        if st.button("📐 패턴 영어 (응용 학습)"):
            st.session_state.mode = "PATTERN"
            st.rerun()

elif st.session_state.mode == "QUIZ":
    if st.session_state.phase == "IDLE":
        st.session_state.q = random.choice(db["quiz"])
        st.session_state.attempt = 1
        st.session_state.phase = "ASKING"
        # 보기 생성
        ans = st.session_state.q
        others = random.sample([x for x in db["quiz"] if x[1] != ans[1]], 5)
        st.session_state.opts = others + [ans]
        random.shuffle(st.session_state.opts)
        st.rerun()

    q = st.session_state.q
    st.markdown(f"<div class='context-box'><b>[{q[0]}]</b><br>{q[4]}<br>({q[3]})</div>", unsafe_allow_html=True)
    
    # 단계별 보기 제한
    current_opts = st.session_state.opts
    if st.session_state.attempt == 2:
        st.warning(random.choice(insults_1))
        current_opts = [o for o in st.session_state.opts if o[1] == q[1]] + random.sample([o for o in st.session_state.opts if o[1] != q[1]], 2)
        random.shuffle(current_opts)
    elif st.session_state.attempt == 3:
        st.error(random.choice(insults_2))
        current_opts = [o for o in st.session_state.opts if o[1] == q[1]] + random.sample([o for o in st.session_state.opts if o[1] != q[1]], 1)
        random.shuffle(current_opts)

    for o in current_opts:
        if st.button(f"{o[1]} : {o[2]}"):
            if o[1] == q[1]:
                play_sound("success")
                st.success(random.choice(praises))
                play_tts(q[1], 5)
                time.sleep(2)
                word_popup()
            else:
                play_sound("wrong")
                st.session_state.attempt += 1
                st.session_state.wrong_log[q[1]] = st.session_state.wrong_log.get(q[1], 0) + 1
                if st.session_state.wrong_log[q[1]] >= 2 and st.session_state.attempt > 3:
                    st.session_state.phase = "PRISON"
                elif st.session_state.attempt > 3:
                    st.session_state.phase = "IDLE"
                st.rerun()

    if st.session_state.get("phase") == "PRISON":
        st.markdown(f"<div class='prison-mode'><h1>🚨 강제 암기 수용소 🚨</h1><h3>벌써 몇 번째 틀리는 거죠? 붕어인가요?</h3><h2>{q[1]}</h2><p>10번 연속 청취 중... 도망칠 수 없습니다.</p></div>", unsafe_allow_html=True)
        play_sound("prison")
        play_tts(q[1], 10)
        if st.button("반성합니다. 탈옥하겠습니다."):
            st.session_state.wrong_log[q[1]] = 0
            st.session_state.phase = "IDLE"
            st.rerun()

elif st.session_state.mode == "PATTERN":
    st.markdown("## 📐 패턴 응용 엔진")
    pat = random.choice(db["pattern"])
    st.markdown(f"<div class='pattern-card'><h3>핵심 패턴: {pat[1]}</h3><p>의미: {pat[4]}</p></div>", unsafe_allow_html=True)
    st.info("이 패턴의 리듬을 몸에 익히세요. (자동 발음 실행)")
    play_tts(pat[1], 3)
    
    if st.button("다른 패턴 공부하기"): st.rerun()
    if st.button("메인으로"): st.session_state.mode = "HOME"; st.rerun()