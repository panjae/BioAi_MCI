# app.py — MCI DTx HF 설문 (완성본)
# 실행: streamlit run app.py
# 필요: pip install streamlit matplotlib numpy

import streamlit as st
import random
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager, rcParams
from collections import defaultdict

st.set_page_config(page_title="MCI DTx – HF 설문", page_icon="🧠", layout="centered")
st.title("🧠 MCI 디지털 테라피 – HF(개인맞춤) 설문")

# ----------------------------
# 한글 폰트 설정(레이더 라벨 깨짐 방지)
# ----------------------------
def set_korean_font():
    preferred = ["Malgun Gothic", "AppleGothic", "NanumGothic",
                 "Noto Sans CJK KR", "Noto Sans KR", "DejaVu Sans"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            rcParams["font.family"] = name
            break
    rcParams["axes.unicode_minus"] = False

set_korean_font()

# ----------------------------
# 세션 상태
# ----------------------------
if "hf_phase" not in st.session_state:
    st.session_state.hf_phase = "intro"   # intro -> style -> topic -> result
if "style_order" not in st.session_state:
    st.session_state.style_order = None
if "topic_order" not in st.session_state:
    st.session_state.topic_order = None
if "style_index" not in st.session_state:
    st.session_state.style_index = 0
if "topic_index" not in st.session_state:
    st.session_state.topic_index = 0
if "style_answers" not in st.session_state:
    st.session_state.style_answers = {}   # {qid: label}
if "topic_answers" not in st.session_state:
    st.session_state.topic_answers = {}
if "hf_profile" not in st.session_state:
    st.session_state.hf_profile = {}

# ----------------------------
# 문항 정의 (유형 표시는 내부용)
# ----------------------------
STYLE_TYPES = ["공감형", "격려형", "논리형", "창의형", "차분형", "직설형"]
TOPIC_TYPES = ["자기인식", "대인관계", "회복력", "긍정습관", "인지기능", "마음챙김"]

STYLE_QUESTIONS = [
    # 공감형 (1–5)
    ("S01", "상대가 내 감정을 이해해줄 때 마음이 가장 편안하다.", "공감형"),
    ("S02", "누군가 조언보다 내 이야기를 조용히 들어줄 때 위로가 된다.", "공감형"),
    ("S03", "감정 표현을 잘 들어주는 사람을 신뢰하게 된다.", "공감형"),
    ("S04", "대화 중 상대가 '그럴 수 있어요'라고 공감해주면 안도감을 느낀다.", "공감형"),
    ("S05", "감정이 진심으로 존중받는 느낌이 중요하다.", "공감형"),
    # 격려형 (6–10)
    ("S06", "‘할 수 있다’는 말을 들으면 실제로 의욕이 생긴다.", "격려형"),
    ("S07", "작은 성취도 인정받을 때 더 노력하고 싶다.", "격려형"),
    ("S08", "상대의 밝은 톤과 웃음이 나에게도 힘이 준다.", "격려형"),
    ("S09", "격려와 칭찬이 내 행동을 바꾸는 가장 큰 요인이다.", "격려형"),
    ("S10", "비판보다 긍정적인 피드백이 훨씬 도움이 된다.", "격려형"),
    # 논리형 (11–15)
    ("S11", "감정 위로보다 문제의 원인을 함께 분석해주는 것이 좋다.", "논리형"),
    ("S12", "감정적인 이야기보다는 현실적인 조언이 더 도움이 된다.", "논리형"),
    ("S13", "논리적 근거가 있는 말이 신뢰감을 준다.", "논리형"),
    ("S14", "대화가 감정적일 때보다 객관적일 때 더 집중된다.", "논리형"),
    ("S15", "상담자는 따뜻함보다는 이성적인 시각을 유지해야 한다고 생각한다.", "논리형"),
    # 창의형 (16–20)
    ("S16", "감정을 색깔이나 이미지로 표현하면 마음이 편해진다.", "창의형"),
    ("S17", "상상이나 은유로 이야기하면 감정이 더 잘 풀린다.", "창의형"),
    ("S18", "예술, 그림, 음악 같은 이야기가 감정 표현에 도움이 된다.", "창의형"),
    ("S19", "‘만약에’로 시작하는 상상 대화가 흥미롭다.", "창의형"),
    ("S20", "감정을 창의적인 방식으로 표현하는 상담을 선호한다.", "창의형"),
    # 차분형 (21–25)
    ("S21", "조용하고 천천히 말하는 상담자가 좋다.", "차분형"),
    ("S22", "말을 급하게 몰아붙이는 대화는 불편하다.", "차분형"),
    ("S23", "상대가 나를 재촉하지 않을 때 마음이 놓인다.", "차분형"),
    ("S24", "차분한 분위기에서 감정을 이야기하기가 쉽다.", "차분형"),
    ("S25", "짧은 침묵이 있어도 어색하지 않게 느껴진다.", "차분형"),
    # 직설형 (26–30)
    ("S26", "돌려 말하지 않고 솔직하게 표현하는 대화를 선호한다.", "직설형"),
    ("S27", "감정적인 위로보다 현실적인 해결책이 더 낫다.", "직설형"),
    ("S28", "상대가 단도직입적으로 말해도 기분이 나쁘지 않다.", "직설형"),
    ("S29", "불편한 사실이라도 바로 지적해주는 것이 좋다.", "직설형"),
    ("S30", "문제를 직면하게 도와주는 대화가 가장 효과적이라고 생각한다.", "직설형"),
]

TOPIC_QUESTIONS = [
    # 자기인식 (1–5)
    ("T01", "내 감정의 원인을 탐색하는 대화가 도움이 된다.", "자기인식"),
    ("T02", "내가 왜 이런 기분인지 스스로 이해하는 게 중요하다.", "자기인식"),
    ("T03", "대화 속에서 내 생각 습관을 돌아볼 때 성장감을 느낀다.", "자기인식"),
    ("T04", "감정을 억누르기보다 솔직히 표현할 수 있을 때 편하다.", "자기인식"),
    ("T05", "내 감정을 구체적인 단어로 표현하는 연습이 필요하다고 느낀다.", "자기인식"),
    # 대인관계 (6–10)
    ("T06", "사람들과의 관계 이야기를 나누는 게 가장 현실적이다.", "대인관계"),
    ("T07", "관계 갈등을 해결하는 조언이 도움이 된다.", "대인관계"),
    ("T08", "내 인간관계 패턴을 분석해보는 것이 흥미롭다.", "대인관계"),
    ("T09", "가족, 친구, 동료와의 관계를 되돌아보는 시간이 필요하다.", "대인관계"),
    ("T10", "사회적 소속감이나 유대감에 대한 이야기가 마음을 안정시킨다.", "대인관계"),
    # 회복력 (11–15)
    ("T11", "힘든 경험을 어떻게 이겨낼지 이야기할 때 위로가 된다.", "회복력"),
    ("T12", "실패나 후회를 재해석하는 대화를 좋아한다.", "회복력"),
    ("T13", "역경 속에서도 성장할 수 있다는 이야기가 힘이 된다.", "회복력"),
    ("T14", "문제를 극복한 사례나 전략을 듣는 게 도움이 된다.", "회복력"),
    ("T15", "‘다시 시작할 수 있다’는 메시지를 자주 듣고 싶다.", "회복력"),
    # 긍정습관 (16–20)
    ("T16", "운동이나 수면 습관처럼 일상 루틴을 다루는 대화가 좋다.", "긍정습관"),
    ("T17", "작은 목표라도 꾸준히 실천하는 방법에 관심이 있다.", "긍정습관"),
    ("T18", "생활습관 개선을 위한 실질적인 조언이 필요하다.", "긍정습관"),
    ("T19", "계획 세우기나 시간 관리에 관한 이야기가 유익하다.", "긍정습관"),
    ("T20", "규칙적인 생활이 마음의 안정을 가져온다고 느낀다.", "긍정습관"),
    # 인지기능 (21–25)
    ("T21", "기억력이나 집중력을 향상시키는 훈련에 흥미가 있다.", "인지기능"),
    ("T22", "퍼즐이나 언어 문제처럼 생각을 자극하는 과제가 좋다.", "인지기능"),
    ("T23", "뇌 건강이나 인지 기능 관련 이야기를 자주 듣고 싶다.", "인지기능"),
    ("T24", "인지 기능 향상이 삶의 질에 직접적인 영향을 준다고 믿는다.", "인지기능"),
    ("T25", "단순한 대화보다 생각을 요하는 질문이 더 흥미롭다.", "인지기능"),
    # 마음챙김 (26–30)
    ("T26", "호흡이나 명상을 주제로 한 대화가 도움이 된다.", "마음챙김"),
    ("T27", "지금 이 순간에 집중하는 연습이 나에게 맞는다.", "마음챙김"),
    ("T28", "마음의 평화를 찾는 주제의 이야기를 좋아한다.", "마음챙김"),
    ("T29", "감각(냄새, 소리, 빛 등)을 인식하는 대화가 안정감을 준다.", "마음챙김"),
    ("T30", "불안하거나 긴장될 때 마음챙김이 효과적이라고 느낀다.", "마음챙김"),
]

STYLE_DICT = {qid: (text, cat) for qid, text, cat in STYLE_QUESTIONS}
TOPIC_DICT = {qid: (text, cat) for qid, text, cat in TOPIC_QUESTIONS}

# 선택지 문구
ANSWER_LABELS = ["매우 아니다", "대체로 아니다", "보통이다", "대체로 그렇다", "매우 그렇다"]

# ----------------------------
# 헬퍼
# ----------------------------
def start_style_phase():
    if st.session_state.style_order is None:
        order = [qid for qid, _, _ in STYLE_QUESTIONS]
        random.shuffle(order)
        st.session_state.style_order = order
    st.session_state.style_index = 0
    st.session_state.hf_phase = "style"

def start_topic_phase():
    if st.session_state.topic_order is None:
        order = [qid for qid, _, _ in TOPIC_QUESTIONS]
        random.shuffle(order)
        st.session_state.topic_order = order
    st.session_state.topic_index = 0
    st.session_state.hf_phase = "topic"

def compute_scores(answer_map, question_dict, type_labels):
    scores = defaultdict(int)
    for qid, ans_label in answer_map.items():
        score = ANSWER_LABELS.index(ans_label) + 1  # 1~5
        _, cat = question_dict[qid]
        scores[cat] += score
    for t in type_labels:
        scores[t] += 0
    return dict(scores)

def render_single_question(phase: str):
    if phase == "style":
        order = st.session_state.style_order
        idx = st.session_state.style_index
        qdict = STYLE_DICT
        answers = st.session_state.style_answers
        total = len(order)
        title = "💬 HF ① – 대화방식 검사"
    else:
        order = st.session_state.topic_order
        idx = st.session_state.topic_index
        qdict = TOPIC_DICT
        answers = st.session_state.topic_answers
        total = len(order)
        title = "🧠 HF ② – 선호 대화주제 검사"

    st.subheader(title)

    qid = order[idx]
    text, _ = qdict[qid]

    st.caption(f"진행도: {idx+1}/{total}")
    st.progress((idx+1)/total)

    # 질문(크게)
    st.markdown(f"<h4 style='font-size:20px; font-weight:600; line-height:1.4;'>{text}</h4>",
                unsafe_allow_html=True)

    current = answers.get(qid, None)
    chosen = st.radio(
        label="",
        options=ANSWER_LABELS,
        index=None if current is None else ANSWER_LABELS.index(current),
        horizontal=True,
        key=f"radio_{phase}_{qid}",
    )

    cols = st.columns(3)
    with cols[0]:
        if st.button("← 이전", disabled=(idx == 0), use_container_width=True):
            if chosen:
                answers[qid] = chosen
            if phase == "style":
                st.session_state.style_index -= 1
            else:
                st.session_state.topic_index -= 1
            st.rerun()

    with cols[2]:
        next_label = "다음 →" if idx < total - 1 else "완료 →"
        if st.button(next_label, disabled=(chosen is None), use_container_width=True):
            answers[qid] = chosen
            if idx < total - 1:
                if phase == "style":
                    st.session_state.style_index += 1
                else:
                    st.session_state.topic_index += 1
                st.rerun()
            else:
                if phase == "style":
                    st.session_state.hf_profile["style_scores"] = compute_scores(
                        answers, STYLE_DICT, STYLE_TYPES
                    )
                    start_topic_phase()
                    st.rerun()
                else:
                    st.session_state.hf_profile["topic_scores"] = compute_scores(
                        answers, TOPIC_DICT, TOPIC_TYPES
                    )
                    st.session_state.hf_phase = "result"
                    st.rerun()

# ----------------------------
# 레이더 차트
# ----------------------------
def plot_radar(scores: dict, categories: list, title: str, color: str):
    values = [scores.get(cat, 0) for cat in categories]
    N = len(categories)
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, N + 1)

    fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax.plot(angles, values, color=color, linewidth=2)
    ax.fill(angles, values, color=color, alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_title(title, size=14, pad=20)
    fig.tight_layout()
    return fig

# ----------------------------
# 화면 렌더링
# ----------------------------
if st.session_state.hf_phase == "intro":
    st.markdown(
        """
        ### 👋 HF 테스트 시작
        당신에게 맞는 **대화방식**과 **대화주제**를 알아보는 1~5점 문항 검사입니다.  
        문항은 한 번에 하나씩 표시되며, 순서는 무작위입니다.
        """
    )
    if st.button("🟢 상담 시작하기"):
        start_style_phase()
        st.rerun()

elif st.session_state.hf_phase == "style":
    if st.session_state.style_order is None:
        start_style_phase()
    render_single_question("style")

elif st.session_state.hf_phase == "topic":
    if st.session_state.topic_order is None:
        start_topic_phase()
    render_single_question("topic")

elif st.session_state.hf_phase == "result":
    st.subheader("📊 HF 결과 요약")

    style_scores = st.session_state.hf_profile.get("style_scores", {})
    topic_scores = st.session_state.hf_profile.get("topic_scores", {})

    def top2(d):
        items = sorted(d.items(), key=lambda x: x[1], reverse=True)
        return (items[0] if items else (None, 0)), (items[1] if len(items) > 1 else (None, 0))

    s1, s2 = top2(style_scores)
    t1, t2 = top2(topic_scores)

    if s1[0]:
        st.write(f"### 🗣️ 대화 스타일: **{s1[0]}**" + (f" (보조: {s2[0]})" if s2[0] else ""))
    if t1[0]:
        st.write(f"### 💭 선호 주제: **{t1[0]}**" + (f" (보조: {t2[0]})" if t2[0] else ""))

    st.divider()
    st.write("### 📈 시각화 – 성향 분포")
    c1, c2 = st.columns(2)
    with c1:
        fig1 = plot_radar(style_scores, STYLE_TYPES, "대화방식", "#4CAF50")
        st.pyplot(fig1)
    with c2:
        fig2 = plot_radar(topic_scores, TOPIC_TYPES, "대화주제", "#2196F3")
        st.pyplot(fig2)

    st.divider()
    if st.button("🔁 다시 시작"):
        for k in [
            "hf_phase", "style_order", "topic_order", "style_index",
            "topic_index", "style_answers", "topic_answers"
        ]:
            st.session_state.pop(k, None)
        st.rerun()

st.caption("© 2025 MCI DTx – HF 설문 모듈 (완성본)")
