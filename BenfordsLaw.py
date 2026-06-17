import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="벤포드 시뮬레이터", layout="wide")

st.title("📊 벤포드의 법칙 시각화 시뮬레이터")

st.sidebar.header("⚙️ 설정")
base = st.sidebar.number_input("지수함수의 밑 (b)", min_value=1.001, max_value=2.0, value=1.01, step=0.001, format="%.3f")
max_x = st.sidebar.slider("데이터 생성 범위 (x의 최대값)", 100, 10000, 2000)

st.sidebar.subheader("🎲 샘플링")
sample_size = st.sidebar.selectbox("한 번에 뽑을 개수", [1, 10, 100, 1000, 5000], index=2)

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
    counts = pd.Series(st.session_state.data_log).value_counts().reindex(digits, fill_value=0)
    actual_pct = (counts / len(st.session_state.data_log)) * 100

    fig = go.Figure()

    # 막대가 서로 빈틈없이 붙도록 bargap=0 설정
    fig.add_trace(go.Bar(
        x=digits,
        y=actual_pct,
        name=f"실제 비율 ({len(st.session_state.data_log)}개)",
        marker_color='rgba(55, 83, 109, 0.7)',
        marker_line_color='rgba(55, 83, 109, 1.0)',
        marker_line_width=1.5
    ))

    fig.add_trace(go.Scatter(
        x=digits,
        y=theoretical,
        name="벤포드 법칙 (이론치)",
        mode='lines+markers',
        line=dict(color='firebrick', width=4),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title=f"첫째 자리 숫자 분포 (총 누적 샘플: {len(st.session_state.data_log)}개)",
        xaxis=dict(title="첫째 자리 숫자", tickmode='linear', tick0=
