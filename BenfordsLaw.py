import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="벤포드 시뮬레이터", layout="wide")

st.title("📈 벤포드 법칙 시각화 시뮬레이터")
st.markdown("""
사용자의 요구사항을 반영하여, 일반적인 막대그래프 대신 **영역 차트(Area Chart)**를 활용하여 실제 데이터 분포와 이상적 분포 곡선을 겹쳐서 보여줍니다.
데이터가 누적됨에 따라 실제 분포가 어떻게 이상적 분포에 수렴하는지 직관적으로 확인할 수 있습니다.
""")

# 사이드바: 컨트롤러
st.sidebar.header("⚙️ 시뮬레이션 설정")
base = st.sidebar.number_input("지수함수의 밑 (b)", min_value=1.001, max_value=2.0, value=1.01, step=0.001, format="%.3f")
max_x = st.sidebar.slider("데이터 생성 범위 (x의 최대값)", 100, 10000, 2000)

st.sidebar.subheader("🎲 샘플링 설정")
sample_size = st.sidebar.selectbox("한 번에 뽑을 개수", [1, 10, 100, 1000, 5000], index=2)

# 세션 상태 초기화 (누적 데이터 저장)
if 'data_log' not in st.session_state:
    st.session_state.data_log = []

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("샘플 추출", type="primary"):
        # 데이터 생성: y = b^x
        x_vals = np.arange(1, max_x + 1)
        population = base ** x_vals
        
        # 무작위 샘플링
        samples = np.random.choice(population, size=sample_size, replace=True)
        
        # 첫째 자리 추출 로직
        def get_first_digit(n):
            return int(str(f"{n:e}")[0])
        
        new_digits = [get_first_digit(s) for s in samples]
        st.session_state.data_log.extend(new_digits)

with col_btn2:
    if st.button("초기화"):
        st.session_state.data_log = []
        st.rerun()

# --- 통계 계산 ---
digits = np.arange(1, 10)
# 이상적 벤포드 분포 계산
theoretical = np.log10(1 + 1/digits) * 100

if len(st.session_state.data_log) > 0:
    counts = pd.Series(st.session_state.data_log).value_counts().reindex(digits, fill_value=0)
    actual_pct = (counts / len(st.session_state.data_log)) * 100

    # --- Plotly 시각화 (혼합 차트) ---
    fig = go.Figure()

    # 1. 실제 데이터 분포 (영역 차트)
    fig.add_trace(go.Scatter(
        x=digits,
        y=actual_pct,
        mode='lines',
        name=f"실제 분포 ({len(st.session_state.data_log)}개)",
        fill='tozeroy',  # Y축 0까지 채우기
        fillcolor='rgba(96, 125, 139, 0.5)', # 반투명한 색상
        line=dict(color='#607d8b', width=2)
    ))

    # 2. 이상적 벤포드 분포 곡선 (점선)
    fig.add_trace(go.Scatter(
        x=digits,
        y=theoretical,
        name="벤포드 곡선 (이론치)",
        mode='lines',
        line=dict(color='firebrick', width=4, dash='dash')  # 대시 선
    ))

    fig.update_layout(
        title=f"첫째 자리 숫자 분포 비교 (누적 샘플: {len(st.session_state.data_log)}개)",
        xaxis=dict(title="첫째 자리 숫자", tickmode='linear', tick0=1, dtick=1),
        yaxis=dict(title="비율 (%)", range=[0, 45]),
        legend=dict(x=0.7, y=0.9),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # 상세 데이터 테이블
    st.subheader("📋 상세 분석 데이터")
    df_res = pd.DataFrame({
        "숫자": digits,
        "이론적 확률 (%)": theoretical.round(2),
        "실제 추출 비율 (%)": actual_pct.values.round(2),
        "오차 (%p)": (actual_pct.values - theoretical).round(2)
    }).set_index("숫자")
    st.table(df_res)

else:
    st.info("사이드바에서 [샘플 추출] 버튼을 클릭하여 시뮬레이션을 시작하세요.")

이 코드를 사용하여 앱을 실행하면, 사용자의 손그림처럼 전체적인 분포의 윤곽을 보여주는 직관적인 시각화를 얻을 수 있습니다.
