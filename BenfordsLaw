import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 페이지 설정
st.set_page_config(page_title="벤포드의 법칙 시뮬레이터", layout="wide")

st.title("📊 지수 증가 데이터와 벤포드의 법칙 테스트")
st.markdown("""
이 앱은 일정한 비율로 증가하는 지수함수 데이터($y = b^x$)에서 무작위로 샘플을 추출했을 때, 
**첫째 자리 숫자(1~9)**의 등장 빈도가 **벤포드의 법칙**을 따르는지 실시간으로 시각화하고 검증합니다.
""")

# 사이드바 컨트롤러 구성
st.sidebar.header("⚙️ 시뮬레이션 설정")

# 1. 지수함수의 밑 (b) 입력
base = st.sidebar.number_input(
    "지수함수의 밑 (b) 입력 (예: b^x)", 
    min_value=1.001, 
    max_value=10.0, 
    value=1.01, 
    step=0.01,
    format="%.3f"
)

# 2. 데이터 범위 설정 (x의 최대치)
max_x = st.sidebar.slider("데이터 생성 범위 (x의 최대값)", min_value=100, max_value=10000, value=2000, step=100)

# 3. 추출할 샘플 개수 단위 및 횟수 설정
sample_unit = st.sidebar.selectbox(
    "한 번에 뽑을 개수 단위", 
    options=[1, 10, 100, 1000, 5000], 
    index=2
)
sample_clicks = st.sidebar.number_input("추출 횟수 (반복)", min_value=1, max_value=100, value=1)
total_to_sample = sample_unit * sample_clicks

# --- 벤포드의 법칙 이론적 확률 정의 ---
digits = np.arange(1, 10)
theoretical_probs = np.log10(1 + 1 / digits)
theoretical_df = pd.DataFrame({
    'Digit': digits,
    '이론적 확률 (%)': theoretical_probs * 100
}).set_index('Digit')

# --- 세션 상태(Session State)를 활용한 데이터 누적 ---
if 'sampled_digits' not in st.session_state:
    st.session_state.sampled_digits = []

# 버튼 레이아웃
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    generate_btn = st.button("🎲 샘플 추출하기", type="primary")
with col_btn2:
    reset_btn = st.button("🔄 초기화")

if reset_btn:
    st.session_state.sampled_digits = []
    st.rerun()

# --- 데이터 생성 및 샘플링 로직 ---
# 지수함수 데이터 기반 생성 (y = base^x)
x_values = np.arange(1, max_x + 1)
population_data = base ** x_values

if generate_btn:
    # 무작위 샘플 추출
    sampled_data = np.random.choice(population_data, size=total_to_sample, replace=True)
    
    # 첫째 자리 숫자 추출 함수
    def get_first_digit(num):
        s = f"{num:.10e}".strstrip().replace('.', '') # 과학적 표기법 변환 후 앞자리 추출
        for char in s:
            if char in '123456789':
                return int(char)
        return None

    first_digits = [get_first_digit(n) for n in sampled_data]
    # 세션에 누적 데이터 추가
    st.session_state.sampled_digits.extend([d for d in first_digits if d is not None])

# --- 결과 시각화 및 분석 ---
st.subheader("📈 시뮬레이션 결과")

if len(st.session_state.sampled_digits) > 0:
    total_samples = len(st.session_state.sampled_digits)
    
    # 빈도 계산
    counts = pd.Series(st.session_state.sampled_digits).value_counts().reindex(digits, fill_value=0)
    actual_probs = (counts / total_samples) * 100
    
    # 데이터프레임 병합
    result_df = theoretical_df.copy()
    result_df['실제 추출 빈도 (개)'] = counts
    result_df['실제 비율 (%)'] = actual_probs
    result_df['오차 (%p)'] = (result_df['실제 비율 (%)'] - result_df['이론적 확률 (%)']).round(2)
    
    # 대시보드 메트릭 상단 표시
    m1, m2 = st.columns(2)
    m1.metric("총 누적 샘플 수", f"{total_samples} 개")
    m2.metric("설정된 지수식", f"y = {base}^{{x}}")
    
    # 그래프 시각화 (matplotlib)
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 막대그래프: 실제 비율
    ax.bar(digits - 0.2, result_df['실제 비율 (%)'], width=0.4, label=f'실제 비율 ({total_samples}개)', color='#4682B4', alpha=0.8)
    # 꺾은선그래프: 이론적 확률
    ax.plot(digits, result_df['이론적 확률 (%)'], marker='o', color='#FF4500', linewidth=2, label='벤포드 이론 확률')
    
    ax.set_xticks(digits)
    ax.set_xlabel('첫째 자리 숫자 (First Digit)', fontsize=12)
    ax.set_ylabel('비율 (%)', fontsize=12)
    ax.set_title('벤포드 법칙 이론값 vs 실제 추출 데이터 비교', fontsize=14, pad=15)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(fontsize=11)
    
    # 스트림릿에 그래프 출력
    st.pyplot(fig)
    
    # 데이터 표 출력
    st.subheader("📋 상세 통계 데이터")
    st.dataframe(result_df.style.format({
        '이론적 확률 (%)': '{:.2f}%',
        '실제 추출 빈도 (개)': '{:,.0f}개',
        '실제 비율 (%)': '{:.2f}%',
        '오차 (%p)': '{:+.2f}%p'
    }), use_container_width=True)
    
else:
    st.info("👈 왼쪽 사이드바에서 설정을 마친 후 [🎲 샘플 추출하기] 버튼을 눌러 시뮬레이션을 시작하세요!")
