import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="벤포드 시뮬레이터", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    iframe { height: 410px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 벤포드의 법칙 & 지수함수 발표 대시보드")

st.sidebar.header("⚙️ 설정")
base = st.sidebar.number_input("지수함수의 밑 (b)", min_value=1.001, max_value=2.0, value=1.01, step=0.001, format="%.3f")
max_x = st.sidebar.slider("데이터 생성 범위 (x의 최대값)", 100, 5000, 1000)

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

colors = ['#3182bd', '#6baed6', '#9ecae1', '#e6550d', '#fd8d3c', '#fdae6b', '#31a354', '#74c476', '#a1d99b']
color_map = {d: colors[d-1] for d in range(1, 10)}

x_curve = np.arange(1, max_x + 1)
y_curve = base ** x_curve
digits_curve = np.array([int(str(f"{y:e}")[0]) for y in y_curve])

col_left, col_right = st.columns(2)

with col_left:
    fig_curve = go.Figure()
    for d in range(1, 10):
        mask = (digits_curve == d)
        if np.any(mask):
            x_seg = np.where(mask, x_curve, np.nan)
            y_seg = np.where(mask, y_curve, np.nan)
            fig_curve.add_trace(go.Scatter(
                x=x_seg, y=y_seg,
                mode='lines',
                name=f"앞자리 {d}",
                line=dict(color=color_map[d], width=4),
                connectgaps=False
            ))
    fig_curve.update_layout(
        title=f"지수함수 곡선의 앞자리 숫자별 구간 ($y = {base}^x$)",
        xaxis=dict(title="x"),
        yaxis=dict(title="y (데이터 값)"),
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )
    st.plotly_chart(fig_curve, use_container_width=True)

with col_right:
    digits = np.arange(1, 10)
    theoretical = np.log10(1 + 1/digits) * 100
    
    if len(st.session_state.data_log) > 0:
        total_samples = len(st.session_state.data_log)
        counts = pd.Series(st.session_state.data_log).value_counts().reindex(digits, fill_value=0)
        actual_pct = (counts / total_samples) * 100
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=digits, y=actual_pct,
            name="실제 비율",
            text=[f"{c}개<br>({p:.1f}%)" for c, p in zip(counts, actual_pct)],
            textposition='auto',
            marker_color=colors,
            marker_line_color='#333333', marker_line_width=1.5
        ))
        fig_bar.add_trace(go.Scatter(
            x=digits, y=theoretical,
            name="이론적 곡선",
            mode='lines+markers',
            line=dict(color='firebrick', width=4),
            marker=dict(size=8, color='firebrick')
        ))
        fig_bar.update_layout(
            title=f"첫째 자리 추출 결과 (총 샘플: {total_samples}개)",
            xaxis=dict(title="첫째 자리 숫자", tickmode='linear', tick0=1, dtick=1),
            yaxis=dict(title="비율 (%)", range=[0, max(45, max(actual_pct) + 5)]),
            bargap=0,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(x=0.65, y=0.95)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("사이드바에서 [샘플 추출] 버튼을 클릭하면 통계 데이터 그래프가 나타납니다.")

if len(st.session_state.data_log) > 0:
    df_res = pd.DataFrame({
        "숫자": digits,
        "이론 확률": [f"{t:.1f}%" for t in theoretical],
        "실제 개수": [f"{c}개" for c in counts],
        "실제 비율": [f"{p:.1f}%" for p in actual_pct],
        "오차": [f"{p-t:+.1f}%p" for p, t in zip(actual_pct, theoretical)]
    }).set_index("숫자")
    st.dataframe(df_res.T, use_container_width=True)
