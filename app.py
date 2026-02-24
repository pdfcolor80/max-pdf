import streamlit as st
import os
import random

# 파일 경로
DATA_FILE = "sentences.txt"

# 페이지 설정
st.set_page_config(page_title="현실 영어 쉐도잉", layout="centered")

# --- CSS: 보기 간격 밀착 및 디자인 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif !important; }
    header { visibility: hidden; height: 0px !important; }
    [data-testid="stHeader"] { display: none !important; }
    .main .block-container { padding-top: 10px !important; margin-top: -60px !important; }

    .context-box {
        background: #1e1e1e; color: white; border-radius: 12px;
        padding: 15px 12px; margin-bottom: 15px; text-align: center; 
        font-size: 1.1rem; line-height: 1.5; border: 2px solid #444;
    }

    .stButton > button {
        width: 100% !important; margin-bottom: 8px !important;
        border-radius: 12px !important; background-color: white !important;
        border: 1px solid #ddd !important; height: 52px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }

    div[data-testid="stButton"] button p {
        font-size: 1.05rem !important; font-weight: 600 !important; color: #333;
        margin: 0 !important;
    }

    .next-area button {
        background-color: #E53935 !important; color: white !important;
        height: 60px !important; border-radius: 30px !important;
        font-weight: 800 !important; font-size: 1.2rem !important;
    }
    
    .punishment-box {
        background-color: #FFEBEE; padding: 20px; border-radius: 15px;
        border: 3px solid #D32F2F; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    all_rows = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                p = line.strip().split("|")
                if len(p) >= 5: all_rows.append(p)
    return all_rows

all_data = load_data()

# --- 퀴즈 초기화 ---
def init_quiz(cat):
    quiz_pool = [r for r in all_data if r[0] not in ["패턴", "숙어", "단어"]] if cat == "💡 전체보기" else [r for r in all_data if r[0] == cat]
    if not quiz_pool: quiz_pool = [r for r in all_data if r[0] not in ["패턴", "숙어", "단어"]]
    
    st.session_state.quiz_data = random.choice(quiz_pool)
    correct_eng = st.session_state.quiz_data[1]
    distractor_pool = [r for r in all_data if r[0] == "단어" and r[1] != correct_eng]
    if len(distractor_pool) < 5: distractor_pool = [r for r in all_data if r[1] != correct_eng]
    
    st.session_state.current_options = random.sample(distractor_pool, 5) + [st.session_state.quiz_data]
    random.shuffle(st.session_state.current_options)
    st.session_state.phase = "forest"
    st.session_state.wrong_count = 0 
    st.session_state.force_study = False
    st.session_state.show_effect = False

if "phase" not in st.session_state: st.session_state.phase = "forest"

categories = sorted(list(set([r[0] for r in all_data if r[0] not in ["패턴", "숙어", "단어"]])))
categories = ["💡 전체보기"] + categories
selected_cat = st.selectbox("", categories, label_visibility="collapsed")

if "quiz_data" not in st.session_state or st.session_state.get("last_cat") != selected_cat:
    st.session_state.last_cat = selected_cat
    init_quiz(selected_cat)

def play_sound(sound_type):
    if sound_type == "success":
        js_code = """
        <script>
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        function noise(dur) {
            const b = ctx.createBuffer(1, ctx.sampleRate * dur, ctx.sampleRate);
            const d = b.getChannelData(0);
            for (let i = 0; i < b.length; i++) { d[i] = Math.random() * 2 - 1; }
            const s = ctx.createBufferSource(); s.buffer = b;
            const g = ctx.createGain(); g.gain.setValueAtTime(0.05, ctx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + dur);
            s.connect(g); g.connect(ctx.destination); s.start();
        }
        for(let i=0; i<15; i++) { setTimeout(() => noise(0.2), i * 60); }
        </script>
        """
    else:
        js_code = "<script>const ctx=new(window.AudioContext||window.webkitAudioContext)();function b(f,d,s){const o=ctx.createOscillator();const g=ctx.createGain();o.type='sawtooth';o.frequency.value=f;g.gain.setValueAtTime(0.05,ctx.currentTime);o.connect(g);g.connect(ctx.destination);o.start(ctx.currentTime+s);o.stop(ctx.currentTime+s+d);}b(880,0.1,0);b(1100,0.2,0.15);</script>"
    st.components.v1.html(js_code, height=0)

# --- 다이얼로그: 차수별 멘트 대방출 ---
@st.dialog("😈 약올리기 알림")
def show_wrong_dialog(item):
    st.session_state.wrong_count += 1
    count = st.session_state.wrong_count
    
    insults_1 = [
        "풉! 1번 틀림 😏 보기를 3개로 줄여줄게.", "오답 레이더 발동! 🤣 정답 피해가기 장인이시네.", 
        "지금 졸고 계신 건 아니죠? 🥱", "실수인가요? 아니면 실력인가요? 1차 경고!",
        "손가락이 미끄러진 거라고 믿어드릴게. 딱 한 번만.", "안타깝네요. 뇌가 잠시 외출 중?",
        "괜찮아요, 아직은 그럴 수 있어요. (비웃음)", "어허, 집중 안 하십니까? 🧐",
        "틀리는 것도 재능이라면 당신은 천재!", "삐빅- 오답입니다. 삐빅-"
    ]
    insults_2 = [
        "진심이야? 🤡 반반 확률인데 틀리겠어?", "비행기 티켓 취소할까요? 국제 미아 확정!",
        "와... 이건 지능 문제인데? 🤣 이제 그냥 찍어봐!", "뇌 세포들이 단체로 파업 중인가요? 🧠🚫",
        "거의 정답을 떠먹여 주는데도 뱉어버리네... 대단하다!", "두 번 틀리는 건 과학입니다. IQ 테스트 시급!",
        "이 정도면 일부러 틀리는 수준인데? 🤨", "와우, 창의적으로 오답을 고르시네요!",
        "포기하면 편해요. 하지만 전 계속 괴롭힐 겁니다.", "영어 말고 몸짓 발짓을 연마하시는 게 어떨까요? 🤸"
    ]
    insults_3 = [
        "공부 접으세요 그냥 ⛔", "자존심 상해도 정답은 봐야지? 강제 암기 모드 당첨!",
        "벽이랑 대화하는 게 빠를지도... 😏 정답이나 보세요.", "영어 말고 파파고랑 베프 하세요 🤡",
        "오늘 공부는 여기까지... 뇌가 폭발했습니다. 🧠💥", "자, 정답 들어갑니다. 입이라도 벌리세요!",
        "인내심 테스트 중인가요? 제가 졌습니다. 🏳️", "그냥 한국어로만 사시는 걸 추천합니다. 🇰🇷",
        "예술적인 오답 행진이네요. 박수를 드립니다. 👏", "다음 생에는 원어민으로 태어나시길 기도할게요."
    ]

    msg = random.choice(insults_1 if count == 1 else insults_2 if count == 2 else insults_3)
    reduce_to = 3 if count == 1 else 2 if count == 2 else 0

    st.markdown(f"<h3 style='text-align:center;'>{count}차 굴욕 🤡</h3>", unsafe_allow_html=True)
    st.error(f"고른 것: {item[1]}\n(뜻: {item[3]})")
    st.warning(f"**{msg}**")

    if reduce_to > 0:
        correct_item = st.session_state.quiz_data
        others = [opt for opt in st.session_state.current_options if opt[1] != correct_item[1]]
        st.session_state.current_options = random.sample(others, reduce_to - 1) + [correct_item]
        random.shuffle(st.session_state.current_options)
    else: st.session_state.force_study = True
    
    play_sound("fail")
    if st.button("다시 도전" if reduce_to > 0 else "강제 암기하러 가기 (굴욕)", use_container_width=True):
        if reduce_to == 0: 
            st.session_state.phase = "solved"
            st.session_state.show_effect = True
        st.rerun()

@st.dialog("🔥 강제 암기: 10회 반복")
def show_force_study_dialog(item):
    st.markdown("""<div class="punishment-box"><h3 style="color:#D32F2F; margin:0;">🚨 비상! 지능 저하 감지</h3><p>이 문장은 당신 머리에 박힐 때까지 못 나갑니다.</p></div>""", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; margin-top:15px;'>{item[1]}</h2>", unsafe_allow_html=True)
    st.write("🔊 10번 연속 재생됩니다. 입으로 따라 하세요!")
    clean_text = item[1].replace("'", "")
    st.components.v1.html(f"<script>window.speechSynthesis.cancel();let c=0;function p(){{let u=new SpeechSynthesisUtterance('{clean_text}');u.lang='en-US';u.rate=0.8;u.onend=()=>{ { 'c++; if(c<10) setTimeout(p, 600);' } };window.speechSynthesis.speak(u);}}p();</script>", height=0)
    if st.button("10번 다 따라했습니다 (양심선언)", use_container_width=True):
        init_quiz(selected_cat)
        st.rerun()

@st.dialog("📚 단어 복습")
def show_review_dialog():
    review_pool = [r for r in all_data if r[0] == "단어"]
    w = random.choice(review_pool) if review_pool else all_data[0]
    st.markdown(f"<h3 style='text-align:center; color:#E53935;'>[{w[1]}]</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center;'>뜻: {w[3]}</h4>", unsafe_allow_html=True)
    if st.button("완벽히 외웠음! 다음 문제 👉", use_container_width=True):
        init_quiz(selected_cat)
        st.rerun()

# --- 메인 화면 ---
curr = st.session_state.quiz_data
cat_name, target_eng, target_sound, target_mean, target_context = curr[:5]

st.markdown(f'<div class="context-box"><b>[{cat_name}]</b><br>{target_context}<br>({target_mean})</div>', unsafe_allow_html=True)

if st.session_state.phase == "forest":
    if "current_options" in st.session_state:
        for i, item in enumerate(st.session_state.current_options):
            if st.button(f"{item[1]} / {item[2]}", key=f"ans_{i}"):
                if item[1] == target_eng:
                    st.session_state.phase = "solved"
                    st.session_state.show_effect = True
                    st.rerun()
                else: show_wrong_dialog(item)

elif st.session_state.phase == "solved":
    if st.session_state.show_effect and not st.session_state.get("force_study"):
        if random.choice([True, False]): st.balloons()
        else: st.snow()
        play_sound("success")
        st.session_state.show_effect = False 

    if st.session_state.get("force_study"):
        st.markdown("<h3 style='text-align:center; color:#D32F2F;'>겨우 맞혔네요... ㅉㅉ 🤡</h3>", unsafe_allow_html=True)
    else:
        success_msgs = [
            "천재신가요? 한 방에 맞히다니! 🎉", "폼 미쳤다! 🔥", "원어민 빙의 완료! 👍", "뇌가 아주 섹시하시군요? 🧠✨",
            "한 방에 맞히다니, 대박! ⭐", "오~ 좀 치시는데요? 폼 살아있네!", "완벽합니다! 칭찬 스티커 100개!",
            "굿잡! 원어민도 울고 갈 실력이에요.", "영어 마스터가 멀지 않았습니다! 🚀", "와우! 당신의 기억력에 치얼스! 🥂",
            "전생에 미국인이셨나요? 🇺🇸", "이 속도라면 다음 달에 이민 가셔도 될 듯!", "와, 소름 돋는 정답입니다! 😎"
        ]
        st.markdown(f"<h3 style='text-align:center; color:#2E7D32;'>{random.choice(success_msgs)}</h3>", unsafe_allow_html=True)

    st.markdown(f"<div style='text-align:center;'><h2 style='color:#007BFF; margin-top:10px;'>{target_eng}</h2><p style='font-size:1.4rem; color:#E53935; font-weight:700;'>{target_sound}</p><h3>{target_mean}</h3><hr><p style='font-weight:800; color:#333;'>🔊 5회 반복 쉐도잉</p></div>", unsafe_allow_html=True)
    clean_target = target_eng.replace("'", "")
    st.components.v1.html(f"<script>window.speechSynthesis.cancel();let l=0;function p(){{let u=new SpeechSynthesisUtterance('{clean_target}');u.lang='en-US';u.rate=0.85;u.onend=()=>{{l++;if(l<5)setTimeout(p,700);}};window.speechSynthesis.speak(u);}}p();</script>", height=0)
    
    st.markdown('<div class="next-area">', unsafe_allow_html=True)
    if st.button("다음 문제 👉", key="next"):
        if st.session_state.get("force_study"): show_force_study_dialog(st.session_state.quiz_data)
        else: show_review_dialog()
    st.markdown('</div>', unsafe_allow_html=True)