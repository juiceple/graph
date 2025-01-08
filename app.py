import streamlit as st
import pandas as pd
import plotly.express as px
import random

# --------------------------
# 초기 페이지 설정
# --------------------------
st.set_page_config(page_title="학습 유형 진단 및 성과 분석", layout="wide")

# --------------------------
# 페이지 분할
# --------------------------
if "diagnosis_completed" not in st.session_state:
    st.session_state.diagnosis_completed = False

if not st.session_state.diagnosis_completed:
    # --------------------------
    # 학습 유형 진단 페이지
    # --------------------------
    st.title("📚 학습 유형 진단 테스트")
    st.write("아래 질문에 응답하여 본인의 학습 유형을 파악하세요.")

    # 질문 리스트
    questions = [
        ("매일 공부할 시간을 미리 계획표로 작성하나요?", "타임 마스터"),
        ("학습 중 방해 요소에도 스트레스를 받는 편인가요?", "타임 마스터"),
        ("계획표에 따라 공부하는 것이 성취감을 줍니까?", "타임 마스터"),
        ("중요한 시험 전, 마지막 주간 계획을 꼼꼼히 세우는 편인가요?", "타임 마스터"),
        ("한 가지 과목에 깊게 몰두하는 것을 좋아하나요?", "몰입 장인"),
        ("관심 있는 주제를 공부할 땐 시간 가는 줄 모르나요?", "몰입 장인"),
        ("수업 시간 외에도 자발적으로 추가 학습을 하나요?", "몰입 장인"),
        ("과목별로 몰입할 날을 정해 그날은 해당 과목만 공부하나요?", "몰입 장인"),
        ("필기 노트를 반복해서 읽는 걸 선호하나요?", "반복 머신"),
        ("같은 문제를 여러 번 풀어 개념을 숙달하나요?", "반복 머신"),
        ("틀린 문제를 여러 번 복습하며 재풀이 하나요?", "반복 머신"),
        ("복습을 하지 않으면 불안함을 느끼나요?", "반복 머신"),
        ("모의고사와 기출 문제 풀이를 자주 하나요?", "모의고사 전설"),
        ("시험 환경을 재현하며 연습한 적이 있나요?", "모의고사 전설"),
        ("시간을 재며 문제를 푸는 연습을 하나요?", "모의고사 전설"),
        ("실전 문제 풀이에 강한 자신감을 느끼나요?", "모의고사 전설"),
        ("문제를 보고 답이 직관적으로 떠오르는 편인가요?", "직관 천재"),
        ("모르는 문제도 감으로 맞출 때가 있나요?", "직관 천재"),
        ("패턴을 빨리 캐치하여 문제를 해결하나요?", "직관 천재"),
        ("문제 풀이 후, 맞춘 이유를 설명하기 어려울 때가 있나요?", "직관 천재")
    ]

    # --------------------------
    # 질문 순서 셔플 및 유지
    # --------------------------
    if "shuffled_questions" not in st.session_state:
        random.shuffle(questions)
        st.session_state.shuffled_questions = questions

    # 유형별 점수 초기화
    scores = {"타임 마스터": 0, "몰입 장인": 0, "반복 머신": 0, "모의고사 전설": 0, "직관 천재": 0}

    # --------------------------
    # 1. 질문 출력 (radio 버튼으로 변경)
    # --------------------------
    for i, (question, category) in enumerate(st.session_state.shuffled_questions):
        # 질문 번호는 작게 표시
        st.markdown(f"<h4 style='font-size:24px;'>질문 {i + 1}</h4>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='font-size:24px;'>{question}</h4>", unsafe_allow_html=True)

        selected_value = st.radio(
            label=f"질문 {i + 1} 선택지",
            options=["매우 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"],
            index=2,  # 기본값: "보통이다"
            key=f"radio_{i}"
        )

        st.markdown("---")  # 구분선

    # --------------------------
    # 2. 학습 유형 결과 계산
    # --------------------------
    if st.button("결과 확인하기"):
        max_score = max(scores.values())
        dominant_type = [k for k, v in scores.items() if v == max_score][0]

        st.session_state.diagnosis_result = dominant_type
        st.session_state.diagnosis_completed = True
        st.success(f"당신의 학습 유형은 **{dominant_type}** 입니다!")

        # 페이지 이동
        st.write("학습 진단이 완료되었습니다. 아래 버튼을 눌러 학습 성과 분석으로 이동하세요.")
        if st.button("학습 성과 분석 페이지로 이동"):
            st.experimental_rerun()

else:
    # --------------------------
    # 학습 성과 분석 페이지
    # --------------------------
    st.title("📊 학습 성과 분석 및 종합 평가")
    st.write(f"학습 유형 진단 결과: **{st.session_state.diagnosis_result}**")

    subject_units = {
        "국어": ["듣기·말하기", "읽기", "쓰기", "문법", "문학"],
        "수학": ["다항식의 연산", "방정식과 부등식", "함수", "수열", "확률"],
        "영어": ["듣기와 말하기", "읽기와 쓰기", "언어와 문화"],
        "한국사": [
            "선사 시대와 고조선의 형성", "삼국의 발전과 통일", "고려의 성립과 발전",
            "조선의 건국과 발전", "근대 국가 수립 운동과 국권 수호 운동",
            "일제 강점기와 민족 운동", "대한민국의 발전과 현대 사회"
        ],
        "통합사회": [
            "인간, 사회, 환경과 행복", "자연환경과 인간", "생활 공간과 사회",
            "인권과 법", "정치 과정과 민주주의", "시장 경제와 금융",
            "사회 정의와 복지", "세계화와 평화"
        ],
        "통합과학": ["물질과 규칙성", "시스템과 상호작용", "변화와 다양성", "환경과 에너지"],
        "과학탐구실험": ["과학 탐구의 본성", "탐구 설계와 수행", "자료 해석과 결론 도출"]
    }

    st.sidebar.title("학습 데이터 입력 (모든 과목)")
    all_subject_data = {}
    total_grades = []

    for subject, units in subject_units.items():
        st.sidebar.subheader(f"[{subject}] 대단원별 점수 입력 (0~100)")
        unit_scores = {}
        for unit in units:
            score = st.sidebar.slider(
                f"{subject} - {unit} 점수:",
                min_value=0, max_value=100, value=50,
                key=f"{subject}_{unit}"
            )
            unit_scores[unit] = score

        grade = st.sidebar.number_input(
            f"{subject} 등급 (1~9, 소수점 허용):",
            min_value=1.0, max_value=9.0, value=5.0, step=0.1,
            key=f"{subject}_grade"
        )
        total_grades.append(grade)

        study_time = st.sidebar.number_input(
            f"{subject} 공부 시간 (시간):",
            min_value=0.0, value=1.0, step=0.5,
            key=f"{subject}_time"
        )

        all_subject_data[subject] = {
            "unit_scores": unit_scores,
            "grade": grade,
            "study_time": study_time
        }

    average_grade = sum(total_grades) / len(total_grades) if total_grades else 5.0

    def calc_new_invest_score(grade, study_time, target_grade=average_grade, max_time=5, weight=1):
        improvement_need = max(0, grade - target_grade)
        time_coefficient = min(1, max_time / study_time) if study_time > 0 else 0
        return weight * (improvement_need / target_grade) * study_time * time_coefficient

    invest_list = []
    for subj, info in all_subject_data.items():
        g = info["grade"]
        t = info["study_time"]
        score_val = calc_new_invest_score(g, t)
        invest_list.append({"과목": subj, "투자점수": score_val, "등급": g, "공부시간": t})

    invest_df = pd.DataFrame(invest_list)

    st.header("1. 과목별 등급 및 공부 시간 시각화")
    bar_fig = px.bar(
        invest_df, x="과목", y=["등급", "공부시간"],
        barmode="group",
        title="과목별 등급 및 공부 시간",
        labels={"value": "값", "variable": "항목"}
    )
    st.plotly_chart(bar_fig)

    st.header("2. 등급 대비 공부 시간 투자 점수 (Radar Chart)")
    radar_invest_fig = px.line_polar(
        invest_df,
        r="투자점수",
        theta="과목",
        line_close=True,
        range_r=[0, invest_df["투자점수"].max() * 1.2 if not invest_df.empty else 1],
        title="(새) 등급 대비 공부 시간 투자 점수"
    )
    radar_invest_fig.update_traces(fill='toself')
    st.plotly_chart(radar_invest_fig)

    st.write("""
    - **계산식 예시**: 개선 필요도 = max(0, (등급 - 평균 등급)),  
      투자 점수 = 개선 필요도 × 공부 시간 × 시간 보정 계수  
    - 평균 등급을 목표로 설정하여, 상대적으로 낮은 등급인 과목에 투자했는지를 평가합니다.
    """)

    st.header("3. 과목별 상세 피드백")
    for subject, info in all_subject_data.items():
        unit_df = pd.DataFrame({
            "대단원": list(info["unit_scores"].keys()),
            "점수": list(info["unit_scores"].values())
        })
        radar_fig = px.line_polar(
            unit_df, 
            r="점수", 
            theta="대단원", 
            line_close=True, 
            range_r=[0, 100],
            title=f"[{subject}] 대단원 점수"
        )
        radar_fig.update_traces(fill='toself')
        st.plotly_chart(radar_fig)

        st.markdown(f"### ▶ {subject} 세부 피드백")
        grade = info["grade"]
        time = info["study_time"]
        st.write(f"- **등급**: {grade}, **공부 시간**: {time}시간")

        if grade <= 3:
            st.write("  - 우수한 편입니다. 다른 과목과 균형 있게 유지하세요.")
        elif grade <= 6:
            st.write("  - 중간 정도이므로 취약 대단원 보충을 권장합니다.")
        else:
            st.write("  - 등급이 낮습니다. 추가 시간 투자와 기초 개념 정리가 필요합니다.")

        if grade >= 7 and time < 2:
            st.warning("  공부 시간이 부족해 보입니다. 하루 1~2시간 이상 추가 확보를 권장합니다.")

        for unit, score in info["unit_scores"].items():
            if score < 50:
                feed = f"❗ {unit}({score}점): 매우 낮음, 기초 개념 보충 필요!"
            elif score < 70:
                feed = f"⚠️ {unit}({score}점): 중간 이하, 복습 권장."
            elif score < 85:
                feed = f"✅ {unit}({score}점): 중간 이상, 조금 더 보완하세요."
            elif score < 95:
                feed = f"✨ {unit}({score}점): 우수, 실력 유지."
            else:
                feed = f"⭐ {unit}({score}점): 거의 만점, 훌륭합니다!"
            st.write("-", feed)
        st.write("---")
