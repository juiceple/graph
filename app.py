import streamlit as st

st.set_page_config(page_title="학습 유형 진단", layout="centered")

# --------------------------
# 세션 스테이트 초기화
# --------------------------
if "question_idx" not in st.session_state:
    st.session_state.question_idx = 0  # 현재 문항 인덱스
if "survey_completed" not in st.session_state:
    st.session_state.survey_completed = False  # 모든 문항 답변 완료 여부
if "score_dict" not in st.session_state:
    st.session_state.score_dict = {
        "WP": 0,  # 완벽주의 미루기형
        "PB": 0,  # 과유불급 문제풀이형
        "FE": 0,  # 감 잡고 끝내기형
        "FA": 0,  # 열심히 하는 척만 하는 형
        "SC": 0,  # 모르면 다른 과목으로 도망가는 형
    }
if "diagnosis_result" not in st.session_state:
    st.session_state.diagnosis_result = None

# --------------------------
# 질문 목록 (5유형 × 4문항 = 20문항)
# --------------------------
questions = [
    # 완벽주의 미루기형(WP)
    ("조금이라도 이해가 덜 되면, 진도를 미루고 다시 처음부터 공부하려 한다.", "WP"),
    ("개념을 100% 완벽히 이해하지 못하면, 문제풀이로 넘어갈 수 없다.", "WP"),
    ("공부 중 작은 실수도 용납하기 싫어 시간 관리를 망치는 편이다.", "WP"),
    ("조금이라도 허술하면 안 된다는 압박으로 인해 학습이 더디게 진행된다.", "WP"),

    # 과유불급 문제풀이형(PB)
    ("개념서 보는 것보다 다양한 문제를 많이 푸는 편이 성적에 더 도움이 된다고 믿는다.", "PB"),
    ("틀린 문제를 오랜 시간 복기하기보다, 새로운 문제를 더 푸는 데 집중한다.", "PB"),
    ("문제 풀이량이 많으면 실전 감각은 자연스럽게 올라간다고 생각한다.", "PB"),
    ("복잡한 이론 정리보다는, 문제 해설을 보며 이해하는 편이 더 낫다고 본다.", "PB"),

    # 감 잡고 끝내기형(FE)
    ("시험에 자주 나오는 ‘핵심 포인트’만 골라 집중 학습하는 편이다.", "FE"),
    ("새로운 개념도 일단 요점만 파악하면, 세부 내용은 대충 넘어간다.", "FE"),
    ("문제를 풀 때 논리적 근거보다는 ‘감으로 때려 맞히는’ 경우가 종종 있다.", "FE"),
    ("교재 전체를 꼼꼼히 공부하기보다는, 출제 빈도가 높아 보이는 부분 위주로 마무리한다.", "FE"),

    # 열심히 하는 척만 하는 형(FA)
    ("스터디 카페에서 하루 종일 앉아 있어도, 막상 공부한 내용이 거의 없다.", "FA"),
    ("공부 계획은 세우지만, 실제로는 대부분 핸드폰이나 딴짓으로 시간을 보낸다.", "FA"),
    ("‘오늘도 도서관에 갔으니 나는 열심히 공부했다’고 스스로 위안 삼는다.", "FA"),
    ("학습 시간을 확보해도 집중력이 너무 낮아 진도가 나가지 않는다.", "FA"),

    # 모르면 다른 과목으로 도망가는 형(SC)
    ("어려운 문제나 취약 과목을 만나면, 바로 다른 과목으로 넘어간다.", "SC"),
    ("계속 틀리는 단원은 ‘나중에 하자’며 넘어가고, 수월한 부분만 먼저 공부한다.", "SC"),
    ("싫어하는 과목은 최대한 뒤로 미루며, 자신 있는 과목만 붙잡고 있는다.", "SC"),
    ("취약점 보완이 아니라, 잘하는 파트나 과목을 반복해 공부하는 편이다.", "SC"),
]

# --------------------------
# 유형 코드 → 실제 유형명
# --------------------------
type_name_map = {
    "WP": "완벽주의 미루기형",
    "PB": "과유불급 문제풀이형",
    "FE": "감 잡고 끝내기형",
    "FA": "열심히 하는 척만 하는 형",
    "SC": "모르면 다른 과목으로 도망가는 형"
}

# --------------------------
# 유형별 결과 데이터 (조언 부분 제외)
# --------------------------
type_info = {
    "완벽주의 미루기형": {
        "장점": [
            "철저한 개념 이해: 기초가 탄탄하고, 응용 문제에 강합니다.",
            "체계적인 학습: 학습 계획과 정리가 체계적이며 복습 효율이 높습니다.",
            "장기적인 학습 효과: 깊이 있게 학습한 내용이 오래 유지됩니다."
        ],
        "단점": [
            "진도 지연: 모든 내용을 완벽히 이해하려다 보니 학습 속도가 느립니다.",
            "실전 경험 부족: 이론에 치중해 문제풀이 속도, 전략 면에서 약점을 보일 수 있습니다.",
            "완벽주의 스트레스: 작은 오류에도 크게 스트레스를 받을 수 있습니다.",
            "유연성 부족: 계획에 변경이 생기면 쉽게 당황할 수 있습니다."
        ]
    },

    "과유불급 문제풀이형": {
        "장점": [
            "실전 감각 우수: 다양한 문제로 시험 환경에 익숙합니다.",
            "응용력과 속도 강점: 빠른 패턴 파악과 풀이로 효율적인 문제 해결 가능.",
            "시간 관리 능력: 문제 풀이 위주의 빠른 진도로 시험 대비 속도가 좋습니다."
        ],
        "단점": [
            "기초 개념 부족: 새로운 유형이나 응용 문제에서 취약.",
            "틀린 문제 반복: 오답 복기가 부족해 같은 실수를 반복할 위험이 큼.",
            "학습의 비효율성: 문제 풀이만으로는 장기적으로 약점이 드러날 수 있습니다.",
            "시험 범위 누락 위험: 자주 다뤄지지 않는 중요 개념을 놓칠 수 있습니다."
        ]
    },

    "감 잡고 끝내기형": {
        "장점": [
            "효율적인 학습: 핵심 포인트를 빠르게 파악해 시간 대비 성과가 높습니다.",
            "빠른 의사결정 능력: 중요하지 않다고 판단한 부분에 시간을 낭비하지 않습니다.",
            "시험 적응력 우수: 자주 출제되는 영역을 잘 캐치해 점수 상승 속도가 빠릅니다."
        ],
        "단점": [
            "기초 부족: 세부 이해가 부족해 새로운 유형에서 점수가 흔들릴 수 있습니다.",
            "학습의 일관성 부족: 중요하지 않다고 느낀 부분을 통째로 스킵하기도 합니다.",
            "깊이 없는 학습: 포인트 위주로 공부해 응용력, 논리적 사고가 약할 수 있습니다.",
            "자기 과신: 충분히 공부했다고 착각해 예상 밖의 문제에 당황할 수 있습니다."
        ]
    },

    "열심히 하는 척만 하는 형": {
        "장점": [
            "외적인 모범생 이미지: 공부 장소에 자주 가고 오래 머물러 동기 부여가 쉬움.",
            "꾸준한 학습 환경 유지: 스터디 카페, 도서관에 가는 습관이 있음.",
            "시간 관리 경험: 최소한의 공부 시간은 확보해둔다는 강점이 있음."
        ],
        "단점": [
            "집중력 부족: SNS나 딴짓으로 실제 학습 시간이 매우 적음.",
            "성과 부재: 오랜 공부 시간에도 실질 성과가 나오지 않음.",
            "방향성 부족: 명확한 목표 없이 앉아있어, 필요한 내용을 충분히 학습하지 못함.",
            "자기만족과 정체: '공부했다'는 기분만 쌓여 발전이 더딜 수 있음."
        ]
    },

    "모르면 다른 과목으로 도망가는 형": {
        "장점": [
            "빠른 상황 대처: 어려운 문제에 붙잡히지 않고 다른 과목으로 전환해 시간 활용 가능.",
            "스트레스 관리: 부담이 큰 과목에 매달리지 않아 학습 스트레스를 덜 느낌.",
            "폭넓은 학습 경험: 여러 과목을 고르게 다뤄 전반적 학습량을 확보할 수 있음."
        ],
        "단점": [
            "문제 해결력 부족: 까다로운 문제나 새로운 유형을 회피해 해결 경험이 적음.",
            "취약 과목 고착화: 반복적 회피로 약점이 해소되지 않고 계속 남음.",
            "학습의 깊이 부족: 어려운 개념을 건너뛰어 기초가 탄탄치 않을 수 있음.",
            "자신감 저하: 특정 과목에서 성과를 못 내 스스로 부족함을 느낄 수 있음."
        ]
    }
}

# --------------------------
# 설문 진행 함수
# --------------------------
def questionnaire():
    # 질문 개수
    total_q = len(questions)
    current_idx = st.session_state.question_idx

    # 이미 모든 문항을 답했다면
    if current_idx >= total_q:
        st.session_state.survey_completed = True
        st.rerun()  # 결과 페이지로
        st.stop()

    # 진행률 계산
    progress = (current_idx / total_q) * 100
    st.progress(progress / 100.0)
    st.write(f"진행도: {current_idx}/{total_q}")

    # 현재 문항
    q_text, q_type = questions[current_idx]
    st.subheader(q_text)

    # 각 버튼 별 점수 매핑
    score_map = {
        "매우 일치한다": 4,
        "어느정도 일치한다": 3,
        "거의 일치하지 않는다": 2,
        "전혀 일치하지 않는다": 1
    }

    # 한 줄에 2개씩 버튼을 배치 (columns)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("매우 일치한다"):
            st.session_state.score_dict[q_type] += score_map["매우 일치한다"]
            st.session_state.question_idx += 1
            st.rerun()

        if st.button("거의 일치하지 않는다"):
            st.session_state.score_dict[q_type] += score_map["거의 일치하지 않는다"]
            st.session_state.question_idx += 1
            st.rerun()

    with c2:
        if st.button("어느정도 일치한다"):
            st.session_state.score_dict[q_type] += score_map["어느정도 일치한다"]
            st.session_state.question_idx += 1
            st.rerun()

        if st.button("전혀 일치하지 않는다"):
            st.session_state.score_dict[q_type] += score_map["전혀 일치하지 않는다"]
            st.session_state.question_idx += 1
            st.rerun()


# --------------------------
# 결과 페이지 함수
# --------------------------
def results_page():
    final_scores = st.session_state.score_dict
    # 가장 점수가 높은 유형 찾기
    max_type_code = max(final_scores, key=final_scores.get)
    max_type_name = type_name_map[max_type_code]

    st.title("학습 유형 진단 결과")
    st.subheader(f"당신의 학습 유형은 **{max_type_name}** 입니다!")
    st.write("---")

    info = type_info[max_type_name]

    # 장점
    st.markdown("### 장점")
    for adv in info["장점"]:
        st.write("- ", adv)

    # 단점
    st.markdown("### 단점")
    for dis in info["단점"]:
        st.write("- ", dis)

    # --- 홍보용 영역 (조언 대신) ---
    st.write("---")
    st.markdown("<b>검사가 완료되었습니다.</b> 학습 코칭을 통해 학습 습관을 개선해보세요!", unsafe_allow_html=True)

    # 버튼 스타일: 여기서는 간단히 HTML을 사용해 디자인된 버튼을 구현
    st.markdown(
        """
        <br>
        <a href="https://medsky.co.kr/coaching" target="_blank">
            <button style="
                background-color:#000000; 
                color:white; 
                border:none; 
                border-radius:4px; 
                padding: 10px 20px; 
                margin-right:10px; 
                cursor:pointer;
            ">
                학습 코칭 알아보기
            </button>
        </a>
        
        <a href="https://pf.kakao.com/_Zxmxhun" target="_blank">
            <button style="
                background-color:#F7E600; 
                color:black; 
                border:none; 
                border-radius:4px; 
                padding: 10px 20px; 
                cursor:pointer;
            ">
                카카오톡 상담하기
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

# --------------------------
# 메인 로직
# --------------------------
if not st.session_state.survey_completed:
    questionnaire()
else:
    results_page()
