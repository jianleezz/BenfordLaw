import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# 페이지 설정
st.set_page_config(page_title="벤포드 시뮬레이터 V2", layout="wide")

# CSS를 통한 스타일링 (한국어 폰트 안정성 확보)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 벤포드의 법칙 시각화 시뮬레이터")
st.markdown("지수적으로 증가하는 데이터에서 무작위 샘플을 뽑아 **첫째 자리 숫자**의 분포를 확인합니다.")

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
theoretical = np.log10(1 + 1/digits) * 100

if len(st.session_state.data_log) > 0:
    counts = pd.Series(st.session_state.data_log).value_counts().reindex(digits, fill_value=0)
    actual_pct = (counts / len(st.session_state.data_log)) * 100

    # --- Plotly 시각화 (막대 + 선 혼합) ---
    fig = go.Figure()

    # 1. 실제 데이터 막대그래프
    fig.add_trace(go.Bar(
        x=digits,
        y=actual_pct,
        name=f"실제 데이터 ({len(st.session_state.data_log)}개)",
        marker_color='rgb(55, 83, 109)',
        opacity=0.7
    ))

    # 2. 이론적 벤포드 법칙 선 그래프
    fig.add_trace(go.Scatter(
        x=digits,
        y=theoretical,
        name="벤포드 법칙 (이론치)",
        mode='lines+markers',
        line=dict(color='firebrick', width=4),
        marker=dict(size=10)
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

### 📋 `requirements.txt` 업데이트 필수!
Plotly를 새로 사용하므로 깃허브의 `requirements.txt` 파일도 아래와 같이 수정해야 합니다.
```text
streamlit
numpy
pandas
plotly

### 💡 해결된 포인트
1.  **직관적 시각화:** 막대(실제) 위에 빨간 선(이론)이 지나가도록 설계하여 오차를 즉각 확인할 수 있습니다.
2.  **한국어 깨짐 방지:** Plotly는 브라우저 엔진을 사용하므로 별도의 폰트 설정 없이도 한국어가 아주 깔끔하게 출력됩니다.
3.  **동적 시뮬레이션:** 추출할 때마다 누적된 데이터가 반영되어 그래프가 실시간으로 변화하며 이론치에 가까워지는 모습을 볼 수 있습니다.

수정된 코드를 적용해 보시고, 추가로 더 다듬고 싶은 부분이 있다면 말씀해 주세요!
