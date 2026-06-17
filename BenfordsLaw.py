import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 스크롤 없이 한 화면에 채우기 위해 전체 화면(wide) 및 상단 여백 제거 설정
st.set_page_config(page_title="벤포드 시뮬레이터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    iframe { height: 420px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 벤포드의 법칙 발표 대시보드")

st.sidebar.header("⚙️ 설정")
base = st.sidebar.number_input("지수함수의 밑 (b)", min_value=1.001, max_value=2.0, value=1.01, step=0.001, format="%.3f")
max_x = st.sidebar.slider("데이터 생성 범위 (x의 최대값)", 100, 10000, 2000)

st.sidebar.subheader("🎲 샘플링")
sample_size = st.sidebar.selectbox("한 번에 뽑을 개수", [1, 10, 100, 1000, 5000], index=3)

if 'data_log' not in st.session_state:
    st.session_state.data_log = []

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("샘플 추출", type="primary"):
        x_vals = np.arange(1, max_x + 1)
        population = base ** x_vals
        samples = np.random.choice(population, size=sample_size, replace=True)
        
        def get_first_digit(n):
            return int(str(f"{n:e}")[0])
        
        new_digits = [get_first_digit(s) for s in samples]
        st.session_state.data_log.extend(new_digits)

with col_btn2:
    if st.button("초기화"):
        st.session_state.data_log = []
        st.rerun()

digits = np.arange(1, 10)
theoretical = np.log10(1 + 1/digits) * 100

if len(st.session_state.data_log) > 0:
    total_samples = len(st.session_state.data_log)
    counts = pd.Series(st.session_state.data_log).value_counts().reindex(digits, fill_value=0)
    actual_pct = (counts / total_samples) * 100

    # 설명 보조 지표 계산 (MSE: 평균제곱오차) - 수렴도 검증용 발표 지표
    mse = np.mean((actual_pct.values - theoretical) ** 2)

    # 화면 분할 (왼쪽: 차트, 오른쪽: 실시간 통계 표) -> 스크롤 방지용 레이아웃
    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        fig = go.Figure()

        # 실제 비율 막대그래프 (내부에 실제 뽑힌 '개수'와 '비율'을 함께 표시)
        fig.add_trace(go.Bar(
            x=digits,
            y=actual_pct,
            name="실제 비율",
            text=[f"{c}개<br>({p:.1f}%)" for c, p in zip(counts, actual_pct)],
            textposition='auto',
            marker_color='rgba(55, 83, 109, 0.7)',
            marker_line_color='rgba(55, 83, 109, 1.0)',
            marker_line_width=1.5
        ))

        # 벤포드 법칙 이론적 곡선
        fig.add_trace(go.Scatter(
            x=digits,
            y=theoretical,
            name="이론적 곡선",
            mode='lines+markers',
            line=dict(color='firebrick', width=4),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=f"첫째 자리 숫자 분포 (총 누적 샘플: {total_samples}개)",
            xaxis=dict(title="첫째 자리 숫자", tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(title="비율 (%)", range=[0, max(45, max(actual_pct) + 5)]),
            bargap=0,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(x=0.75, y=0.95),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        # 발표 시 강조하기 좋은 수렴도 정보 요약 대시보드
        st.markdown(f"### 📈 실시간 수렴도 분석")
        st.metric(label="총 누적 샘플 수", value=f"{total_samples} 개")
        
        # 오차가 작을수록(0에 가까울수록) 이론에 완벽히 부합함을 의미
        st.metric(label="이론치와의 평균 오차 지표 (MSE)", value=f"{mse:.4f}", 
                  delta="수렴 중" if mse < 10 else "데이터 부족", delta_color="normal" if mse < 10 else "inverse")

        # 상세 통계 테이블
        st.markdown("### 📋 수치 데이터")
        df_res = pd.DataFrame({
            "숫자": digits,
            "이론 확률": [f"{t:.1f}%" for t in theoretical],
            "실제 개수": [f"{c}개" for c in counts],
            "실제 비율": [f"{p:.1f}%" for p in actual_pct],
            "오차": [f"{p-t:+.1f}%p" for p, t in zip(actual_pct, theoretical)]
        }).set_index("숫자")
        st.dataframe(df_res, use_container_width=True)

else:
    st.info("사이드바에서 [샘플 추출] 버튼을 클릭하면 발표용 대시보드가 한 화면에 정렬됩니다.")
