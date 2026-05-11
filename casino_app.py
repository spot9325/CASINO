
import os
import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. 기본 설정
# ============================================================
DB_PATH = "casino.db"

st.set_page_config(
    page_title="카지노 산업 통계 데이터 분석 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. 블랙 & 골드 테마 CSS
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f17;
        color: #f5f5f5;
    }
    h1, h2, h3 {
        color: #d4af37 !important;
        font-weight: 800 !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    [data-testid="stMetric"] {
        background-color: #1b222d;
        border: 1px solid #d4af37;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 0 12px rgba(212, 175, 55, 0.12);
    }
    [data-testid="stMetricLabel"] {
        color: #c9c9c9;
        font-size: 0.95rem;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 2rem;
    }
    .insight-box {
        background-color: #151b24;
        border-left: 5px solid #d4af37;
        border-radius: 8px;
        padding: 16px 18px;
        margin: 12px 0 24px 0;
        color: #e8e8e8;
        line-height: 1.65;
    }
    .sql-box {
        margin-top: 8px;
    }
    .small-note {
        color: #a8a8a8;
        font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 3. DB 연결 및 데이터 로드 함수
# ============================================================
if not os.path.exists(DB_PATH):
    st.error("⚠️ casino.db 파일을 찾을 수 없습니다. app.py와 casino.db가 같은 폴더에 있는지 확인해 주세요.")
    st.stop()


@st.cache_data
def load_data(query: str) -> pd.DataFrame:
    """SQLite 쿼리 결과를 DataFrame으로 불러오는 함수"""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df


def to_number(series: pd.Series) -> pd.Series:
    """쉼표, %, 공백 등이 포함된 문자열 숫자를 안전하게 숫자로 변환"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip(),
        errors="coerce"
    )


def fmt_num(value, suffix=""):
    if pd.isna(value):
        return "-"
    return f"{int(round(value)):,}{suffix}"


def fmt_float(value, digits=1, suffix=""):
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}{suffix}"


# ============================================================
# 4. 제목
# ============================================================
st.title("🎰 카지노 산업 통계 데이터 분석 대시보드")
st.markdown(
    "공공데이터를 기반으로 **국내 카지노 산업의 성장**, **관광산업과의 관계**, "
    "**국가별 외국인 입장객 구조**를 분석합니다."
)

# ============================================================
# 5. 사용할 SQL
# ============================================================

# 주의: DB의 실제 테이블명과 컬럼명에 띄어쓰기가 있으므로 큰따옴표("")로 감쌉니다.
sql_growth = """
SELECT
    "연 도" AS 연도,
    "외래 방한객" AS 외래방한객,
    "카지노 이용객" AS 카지노이용객
FROM "연도별 외국인 관광객"
ORDER BY "연 도"
"""

sql_revenue = """
SELECT
    "연 도" AS 연도,
    "관광 외화수입" AS 관광외화수입,
    "카지노 외화수입" AS 카지노외화수입,
    "점 유율(%)" AS 점유율
FROM "연도별 관광 대비 외화수입"
ORDER BY "연 도"
"""

sql_country = """
SELECT
    "국가명" AS 국가명,
    CAST(REPLACE("외국인 입장객 수", ',', '') AS INTEGER) AS 외국인입장객수
FROM "카지노 외국인 국가"
ORDER BY CAST(REPLACE("외국인 입장객 수", ',', '') AS INTEGER) DESC
LIMIT 10
"""

sql_store = """
SELECT
    "카지노명" AS 카지노명,
    "25매출액" AS 매출액,
    "25입장객" AS 입장객
FROM "카지노 이용고객 및 매출"
"""


# ============================================================
# 6. 데이터 불러오기 및 숫자 변환
# ============================================================
try:
    df_growth = load_data(sql_growth)
    df_revenue = load_data(sql_revenue)
    df_country = load_data(sql_country)
    df_store = load_data(sql_store)
except Exception as e:
    st.error("DB 테이블명 또는 컬럼명이 app.py의 SQL과 다를 수 있습니다.")
    st.exception(e)
    st.stop()

df_growth["연도"] = to_number(df_growth["연도"])
df_growth["외래방한객"] = to_number(df_growth["외래방한객"])
df_growth["카지노이용객"] = to_number(df_growth["카지노이용객"])

df_revenue["연도"] = to_number(df_revenue["연도"])
df_revenue["관광외화수입"] = to_number(df_revenue["관광외화수입"])
df_revenue["카지노외화수입"] = to_number(df_revenue["카지노외화수입"])
df_revenue["점유율"] = to_number(df_revenue["점유율"])

df_country["외국인입장객수"] = to_number(df_country["외국인입장객수"])

df_store["매출액"] = to_number(df_store["매출액"])
df_store["입장객"] = to_number(df_store["입장객"])


# ============================================================
# 7. KPI 카드
# ============================================================
st.subheader("📊 주요 지표")

latest_growth = df_growth.dropna(subset=["연도"]).sort_values("연도").iloc[-1]
top_country_row = df_country.sort_values("외국인입장객수", ascending=False).iloc[0]
latest_revenue = df_revenue.dropna(subset=["연도"]).sort_values("연도").iloc[-1]
top_store_row = df_store.sort_values("입장객", ascending=False).iloc[0] if len(df_store) > 0 else None

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "최근 연도 카지노 이용객",
        fmt_num(latest_growth["카지노이용객"], "명")
    )
with col2:
    st.metric(
        "외국인 입장객 1위 국가",
        top_country_row["국가명"]
    )
with col3:
    st.metric(
        "최근 카지노 외화수입",
        fmt_num(latest_revenue["카지노외화수입"])
    )
with col4:
    if top_store_row is not None:
        st.metric(
            "입장객 최다 카지노",
            str(top_store_row["카지노명"])
        )
    else:
        st.metric("입장객 최다 카지노", "-")

st.markdown("---")


# ============================================================
# 차트 1. 한국 카지노 산업은 어떻게 성장해왔는가?
# ============================================================
st.header("1. 한국 카지노 산업은 어떻게 성장해왔는가?")
st.markdown('<p class="small-note">연도별 외래 방한객과 카지노 이용객 변화를 함께 비교합니다.</p>', unsafe_allow_html=True)

df_growth_plot = df_growth.dropna(subset=["연도"]).sort_values("연도")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=df_growth_plot["연도"],
    y=df_growth_plot["외래방한객"],
    mode="lines+markers",
    name="외래 방한객",
    line=dict(color="#d4af37", width=3)
))
fig1.add_trace(go.Scatter(
    x=df_growth_plot["연도"],
    y=df_growth_plot["카지노이용객"],
    mode="lines+markers",
    name="카지노 이용객",
    line=dict(color="#ffffff", width=3)
))
fig1.update_layout(
    title="연도별 외래 방한객과 카지노 이용객 변화",
    template="plotly_dark",
    paper_bgcolor="#0b0f17",
    plot_bgcolor="#0b0f17",
    xaxis_title="연도",
    yaxis_title="인원 수",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig1, use_container_width=True)

# 동적 인사이트
min_casino = df_growth_plot.loc[df_growth_plot["카지노이용객"].idxmin()]
max_casino = df_growth_plot.loc[df_growth_plot["카지노이용객"].idxmax()]
latest = df_growth_plot.iloc[-1]
first = df_growth_plot.iloc[0]
casino_change = ((latest["카지노이용객"] - first["카지노이용객"]) / first["카지노이용객"] * 100) if first["카지노이용객"] else None

st.markdown(
    f"""
    <div class="insight-box">
    <b>데이터 인사이트</b><br>
    - 카지노 이용객이 가장 많았던 시점은 <b>{int(max_casino['연도'])}년</b>으로, 약 <b>{fmt_num(max_casino['카지노이용객'], '명')}</b>입니다. 반대로 가장 낮았던 시점은 <b>{int(min_casino['연도'])}년</b>으로 나타납니다.<br>
    - 최근 연도 기준 카지노 이용객은 약 <b>{fmt_num(latest['카지노이용객'], '명')}</b>이며, 첫 관측 연도 대비 변화율은 <b>{fmt_float(casino_change, 1, '%')}</b>입니다.<br>
    - 외래 방한객과 카지노 이용객을 함께 보면, 카지노 산업은 외국인 관광 흐름의 영향을 받지만 두 지표가 항상 같은 폭으로 움직이지는 않아 카지노 자체의 수요 구조도 함께 확인할 필요가 있습니다.
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("사용한 SQL 보기"):
    st.code(sql_growth, language="sql")


# ============================================================
# 차트 2. 카지노 산업은 관광산업과 얼마나 연결되어 있는가?
# ============================================================
st.header("2. 카지노 산업은 관광산업과 얼마나 연결되어 있는가?")
st.markdown('<p class="small-note">관광 외화수입과 카지노 외화수입을 비교해 카지노 산업의 관광산업 내 위치를 확인합니다.</p>', unsafe_allow_html=True)

df_revenue_plot = df_revenue.dropna(subset=["연도"]).sort_values("연도")
df_revenue_long = df_revenue_plot.melt(
    id_vars="연도",
    value_vars=["관광외화수입", "카지노외화수입"],
    var_name="구분",
    value_name="외화수입"
)

fig2 = px.bar(
    df_revenue_long,
    x="연도",
    y="외화수입",
    color="구분",
    barmode="group",
    title="연도별 관광 외화수입과 카지노 외화수입 비교",
    color_discrete_map={
        "관광외화수입": "#d4af37",
        "카지노외화수입": "#8b7355"
    }
)
fig2.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f17",
    plot_bgcolor="#0b0f17",
    xaxis_title="연도",
    yaxis_title="외화수입",
    legend_title_text=""
)
st.plotly_chart(fig2, use_container_width=True)

max_share = df_revenue_plot.loc[df_revenue_plot["점유율"].idxmax()]
latest_rev = df_revenue_plot.iloc[-1]
avg_share = df_revenue_plot["점유율"].mean()
casino_rev_change = ((latest_rev["카지노외화수입"] - df_revenue_plot.iloc[0]["카지노외화수입"]) / df_revenue_plot.iloc[0]["카지노외화수입"] * 100) if df_revenue_plot.iloc[0]["카지노외화수입"] else None

st.markdown(
    f"""
    <div class="insight-box">
    <b>데이터 인사이트</b><br>
    - 카지노 외화수입 점유율이 가장 높았던 연도는 <b>{int(max_share['연도'])}년</b>이며, 점유율은 <b>{fmt_float(max_share['점유율'], 1, '%')}</b>입니다.<br>
    - 전체 기간 평균 카지노 외화수입 점유율은 약 <b>{fmt_float(avg_share, 1, '%')}</b>로, 카지노가 관광 외화수입의 일부를 꾸준히 구성하고 있음을 보여줍니다.<br>
    - 최근 연도 카지노 외화수입은 약 <b>{fmt_num(latest_rev['카지노외화수입'])}</b>이며, 첫 관측 연도 대비 변화율은 <b>{fmt_float(casino_rev_change, 1, '%')}</b>입니다. 이는 카지노 산업이 관광객 수뿐 아니라 고부가가치 소비와도 연결될 수 있음을 시사합니다.
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("사용한 SQL 보기"):
    st.code(sql_revenue, language="sql")


# ============================================================
# 차트 3. 어떤 국가의 관광객이 한국 카지노 산업을 주도하는가?
# ============================================================
st.header("3. 어떤 국가의 관광객이 한국 카지노 산업을 주도하는가?")
st.markdown('<p class="small-note">외국인 카지노 입장객 수 상위 10개 국가를 비교합니다.</p>', unsafe_allow_html=True)

df_country_plot = df_country.sort_values("외국인입장객수", ascending=True)

fig3 = px.bar(
    df_country_plot,
    x="외국인입장객수",
    y="국가명",
    orientation="h",
    title="외국인 카지노 입장객 수 TOP 10 국가",
    color="외국인입장객수",
    color_continuous_scale=["#4a4a4a", "#d4af37"]
)
fig3.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b0f17",
    plot_bgcolor="#0b0f17",
    xaxis_title="외국인 입장객 수",
    yaxis_title="국가명",
    coloraxis_showscale=False
)
st.plotly_chart(fig3, use_container_width=True)

top1 = df_country.sort_values("외국인입장객수", ascending=False).iloc[0]
top2 = df_country.sort_values("외국인입장객수", ascending=False).iloc[1] if len(df_country) > 1 else None
top10_total = df_country["외국인입장객수"].sum()
top1_share = top1["외국인입장객수"] / top10_total * 100 if top10_total else None
gap = top1["외국인입장객수"] - top2["외국인입장객수"] if top2 is not None else None

st.markdown(
    f"""
    <div class="insight-box">
    <b>데이터 인사이트</b><br>
    - TOP10 국가 중 외국인 카지노 입장객 수가 가장 많은 국가는 <b>{top1['국가명']}</b>이며, 입장객 수는 <b>{fmt_num(top1['외국인입장객수'], '명')}</b>입니다.<br>
    - 1위 국가가 TOP10 전체에서 차지하는 비중은 약 <b>{fmt_float(top1_share, 1, '%')}</b>입니다. 특정 국가 의존도가 높다면 해당 국가의 관광 규제, 환율, 항공 노선 변화가 카지노 산업에 직접적인 영향을 줄 수 있습니다.<br>
    - 1위와 2위 국가 간 입장객 격차는 약 <b>{fmt_num(gap, '명')}</b>으로, 국가별 수요가 균등하기보다는 일부 국가에 집중되는 구조를 보입니다.
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("사용한 SQL 보기"):
    st.code(sql_country, language="sql")


# ============================================================
# 마무리 안내
# ============================================================
st.markdown("---")
st.info(
    "GitHub에는 app.py, requirements.txt, casino.db를 같은 저장소에 업로드합니다. "
    "Streamlit Community Cloud에서 해당 GitHub 저장소를 연결하고 Main file path를 app.py로 설정하면 배포할 수 있습니다. "
    "코드를 수정한 뒤 GitHub에 commit & push하면 Streamlit 앱에도 자동 반영됩니다."
)
