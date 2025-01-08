import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
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

    grade = st.sidebar.slider(
        f"{subject} 등급 (1=최고, 9=최하):",
        min_value=1, max_value=9, value=5,
        key=f"{subject}_grade"
    )
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

st.title("종합 학습 진단 보고서 (화면 + PDF)")

# --------------------------
# 3) (A) 각 과목별: 레이더 차트 + 세부 피드백
# --------------------------
st.header("1. 과목별 대단원 점수 (Radar) & 피드백")

for subject, info in all_subject_data.items():
    # (1) 레이더 차트
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

    # (2) 과목별 세부 피드백
    st.markdown(f"### ▶ {subject} 세부 피드백")
    grade = info["grade"]
    time = info["study_time"]
    st.write(f"- **등급**: {grade}, **공부 시간**: {time}시간")

    # 간단 등급 코멘트
    if grade <= 3:
        st.write("  - 우수한 편입니다. 다른 과목과 균형 있게 유지하세요.")
    elif grade <= 6:
        st.write("  - 중간 정도이므로 취약 대단원 보충을 권장합니다.")
    else:
        st.write("  - 등급이 낮습니다. 추가 시간 투자와 기초 개념 정리가 필요합니다.")

    # 공부시간이 2시간 미만 && 등급이 7~9 => 경고
    if grade >= 7 and time < 2:
        st.warning("  공부 시간이 부족해 보입니다. 하루 1~2시간 이상 추가 확보를 권장합니다.")

    # 대단원별 점수 피드백
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

# --------------------------
# 3) (B) 등급 대비 공부 시간 투자 점수 (Radar Chart) - 새 계산식
# --------------------------
st.header("2. 등급 대비 공부 시간 투자 점수 (Radar Chart)")

def calc_new_invest_score(grade, study_time):
    """
    개선된 투자 점수 계산 예시:
    - 개선 요구도(improvement_need) = max(0, (grade - 5))
      (등급 1~5는 0~4까지 0~… 음수가 나올 수 있으나 음수는 0 처리)
      예) grade=9 => improvement_need=4, grade=7 => 2, grade=5 => 0, grade=1 => 0
    - 투자 점수 = improvement_need * (study_time^1.0)
      (등급이 낮을수록, 공부 시간이 많을수록 점수 ↑)
    """
    improvement_need = max(0, grade - 5)  # grade=9 => 4, grade=6 => 1, grade=4 => -1 => 0 처리
    return improvement_need * study_time

# 과목별 새 투자점수
invest_list = []
for subj, info in all_subject_data.items():
    g = info["grade"]
    t = info["study_time"]
    score_val = calc_new_invest_score(g, t)
    invest_list.append({"과목": subj, "투자점수": score_val})

invest_df = pd.DataFrame(invest_list)

# Radar Chart
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
- **계산식 예시**: 개선 필요도 = max(0, (등급 - 5)),  
  투자 점수 = 개선 필요도 × 공부 시간  
- 따라서 등급이 5 이하인 과목(=상대적으로 괜찮은 과목)은 투자 점수가 0이거나 낮게 계산됩니다.
- 등급이 9(=가장 낮은 편)이고 공부 시간이 많다면 높은 '투자점수'를 얻게 됩니다.
""")

# --------------------------
# 4) 종합 평가 등급 & 이유
# --------------------------
st.header("3. 종합 평가")

# (A) '투자점수' 총합
score_sum = invest_df["투자점수"].sum() if not invest_df.empty else 0

# (B) score_sum을 1~9등급으로 매핑 (예시)
def map_score_sum_to_grade(score_sum):
    # 임의 구간 예시
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

overall_score = map_score_sum_to_grade(score_sum)

# (C) 결과 표시
st.subheader(f"종합 학습 점수: {overall_score}등급")
st.write(f"- '등급 대비 공부 시간 투자' 총합 점수: {score_sum:.2f}")

reason_text = f"""
이번 종합 학습 점수는 {overall_score}등급입니다.
새로운 계산식에 따라, '등급이 낮을수록(grade>5) 더 많이 공부했는지'를 정량화한 점수 합계가 {score_sum:.2f}으로 측정되었기 때문입니다.
(점수가 높을수록 낮은 등급 과목에 적극 투자했다고 판단)
"""
st.write(reason_text)

# --------------------------
# 5) PDF 생성
# --------------------------
FONT_PATH = "C:/Windows/Fonts/malgun.ttf"  # Windows 예시

class PDFReport(FPDF):
    def header(self):
        self.set_font('malgun', '', 16)
        self.cell(0, 10, "종합 학습 진단 보고서", align='C', ln=True)
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('malgun', '', 14)
        self.cell(0, 10, title, ln=True)
        self.ln(2)

    def add_text(self, text):
        self.set_font('malgun', '', 12)
        self.multi_cell(0, 7, text)
        self.ln(2)

def create_pdf(all_subject_data, invest_df, overall_score, score_sum):
    pdf = PDFReport()
    pdf.add_font('malgun', '', FONT_PATH, uni=True)
    pdf.add_page()

    # 1) 종합 평가
    pdf.chapter_title("1. 종합 평가")
    pdf.add_text(f"• 종합 학습 점수: {overall_score}등급")
    pdf.add_text(f"• 투자 점수 합계: {score_sum:.2f}")
    explain = (
        f"'등급이 낮을수록(>5) 더 많이 공부했는지'를 정량화한 결과, "
        f"점수 합계가 {score_sum:.2f}이므로 {overall_score}등급으로 평가되었습니다."
    )
    pdf.add_text(explain)

    # 2) 과목별 '등급 대비 공부 시간 투자 점수'
    pdf.chapter_title("2. (새) 등급 대비 공부 시간 투자 점수")
    for idx, row in invest_df.iterrows():
        subj = row["과목"]
        sc = row["투자점수"]
        pdf.add_text(f"- {subj}: {sc:.2f}")

    pdf.add_text("(점수가 높을수록 낮은 등급 과목에 공부 시간을 많이 투자했다는 의미)")

    # 3) 과목별 상세 피드백
    pdf.chapter_title("3. 과목별 상세 피드백")

    for subject, info in all_subject_data.items():
        pdf.add_text(f"▶ {subject}")
        pdf.add_text(f"- 등급: {info['grade']}, 공부 시간: {info['study_time']}시간")

        # 등급 간단 피드백
        if info["grade"] <= 3:
            pdf.add_text("  우수한 편입니다. 다른 과목과 균형 있게 유지하세요.")
        elif info["grade"] <= 6:
            pdf.add_text("  중간 정도이므로 취약 대단원 보충을 권장합니다.")
        else:
            pdf.add_text("  등급이 낮습니다. 추가 시간 투자와 기초 개념 정리가 필요합니다.")

        # 대단원별 점수 피드백
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
            pdf.add_text(feed)

        pdf.ln(3)

    return pdf

# --------------------------
# 6) PDF 다운로드 버튼
# --------------------------
if st.button("PDF 다운로드"):
    if len(all_subject_data) == 0:
        st.error("과목 정보가 없습니다. 사이드바에서 과목을 입력해 주세요.")
    else:
        pdf = create_pdf(all_subject_data, invest_df, overall_score, score_sum)
        pdf_buffer = io.BytesIO()
        pdf.output(pdf_buffer, dest='S')
        pdf_buffer.seek(0)
        
        st.download_button(
            label="📄 종합 보고서 다운로드",
            data=pdf_buffer,
            file_name="종합_학습진단보고서.pdf",
            mime="application/pdf"
        )
