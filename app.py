import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --------------------------
# 1) 과목별 대단원 리스트
# --------------------------
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

# --------------------------
# 2) 사이드바: 모든 과목 입력
# --------------------------
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

# 평균 등급 계산 및 목표 등급 설정
average_grade = sum(total_grades) / len(total_grades) if total_grades else 5.0

# --------------------------
# 3) 종합 평가 및 등급 대비 시간 시각화
# --------------------------
st.title("종합 학습 진단 보고서")

# (A) 투자 점수 계산 함수
def calc_new_invest_score(grade, study_time, target_grade=average_grade, max_time=5, weight=1):
    improvement_need = max(0, grade - target_grade)
    time_coefficient = min(1, max_time / study_time) if study_time > 0 else 0
    invest_score = weight * (improvement_need / target_grade) * study_time * time_coefficient
    return invest_score

# 과목별 새 투자점수 및 데이터 정리
invest_list = []
for subj, info in all_subject_data.items():
    g = info["grade"]
    t = info["study_time"]
    score_val = calc_new_invest_score(g, t)
    invest_list.append({"과목": subj, "투자점수": score_val, "등급": g, "공부시간": t})

invest_df = pd.DataFrame(invest_list)

# (B) 총합 점수 계산 및 등급 매핑
def map_score_sum_to_grade(score_sum):
    if score_sum < 1:
        return 9
    elif score_sum < 2:
        return 8
    elif score_sum < 4:
        return 7
    elif score_sum < 6:
        return 6
    elif score_sum < 9:
        return 5
    elif score_sum < 12:
        return 4
    elif score_sum < 16:
        return 3
    elif score_sum < 20:
        return 2
    else:
        return 1

score_sum = invest_df["투자점수"].sum() if not invest_df.empty else 0
overall_score = map_score_sum_to_grade(score_sum)

# 종합 평가 결과
st.subheader(f"종합 학습 점수: {overall_score}등급")
st.write(f"- '등급 대비 공부 시간 투자' 총합 점수: {score_sum:.2f}")
reason_text = f"""
이번 종합 학습 점수는 {overall_score}등급입니다.
현재 평균 등급({average_grade:.2f})을 목표 등급으로 설정하여 계산되었습니다.
점수 합계가 {score_sum:.2f}로 측정되었기 때문입니다.
(점수가 높을수록 낮은 등급 과목에 적극 투자했다고 판단)
"""
st.write(reason_text)

# --------------------------
# 4) 과목별 등급 및 공부 시간 막대 그래프
# --------------------------
st.header("1. 과목별 등급 및 공부 시간 시각화")
bar_fig = px.bar(
    invest_df, x="과목", y=["등급", "공부시간"],
    barmode="group",
    title="과목별 등급 및 공부 시간",
    labels={"value": "값", "variable": "항목"}
)
st.plotly_chart(bar_fig)

# --------------------------
# 5) (Radar Chart) 등급 대비 공부 시간 투자 점수
# --------------------------
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

# --------------------------
# 6) 과목별 피드백
# --------------------------
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
