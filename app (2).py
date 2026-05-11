import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# =============================
# 1. 페이지 설정
# =============================
st.set_page_config(page_title="카지노 산업 분석 대시보드", layout="wide")

# =============================
# 2. 블랙 & 골드 테마 CSS
# =============================
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stMetric {
        background-color: #1f2630;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #d4af37;
    }
    h1, h2, h3 {
        color: #d4af37 !important;
    }
    .stMarkdown, p, div {
        color: #e6e6e6;
    }
</style>
""", unsafe_allow_html=True)

# =============================
# 3. DB 확인 및 연결 함수
# =============================
DB_PATH = "casino.db"

if not os.path.exists(DB_PATH):
    st.error("⚠️ 'casino.db' 파일을 찾을 수 없습니다. app.py와 같은 폴더에 casino.db가 있는지 확인해주세요.")
    st.stop()

@st.cache_data
def load_data(query: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def to_number(series: pd.Series) -> pd.Series:
    """콤마, %, 공백 등이 섞인 숫자형 문자를 안전하게 숫자로 변환"""
    return pd.to_numeric(
        series.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip(),
        errors="coerce"
    )

# =============================
# 4. 대시보드 제목
# =============================
st.title("🎰 카지노 산업 통계 데이터 분석 대시보드")
st.markdown("공공데이터를 기반으로 국내 카지노 산업과 관광산업의 관계를 분석합니다.")

# =============================
# 5. KPI 카드
# =============================
st.subheader("📊 주요 지표")

kpi_sql_total = """
SELECT SUM("카지노 이용객") AS total_users
FROM "연도별 외국인 관광객"
"""

kpi_sql_country = """
SELECT "국가명" AS 국가명, "외국인 입장객 수" AS 입장객수
FROM "카지노 외국인 국가"
ORDER BY "외국인 입장객 수" DESC
LIMIT 1
"""

kpi_sql_revenue = """
SELECT SUM(CAST(REPLACE("카지노 외화수입", ',', '') AS REAL)) AS total_casino_revenue
FROM "연도별 관광 대비 외화수입"
"""

try:
    df_kpi_total = load_data(kpi_sql_total)
    df_kpi_country = load_data(kpi_sql_country)
    df_kpi_revenue = load_data(kpi_sql_revenue)

    total_users = int(df_kpi_total["total_users"].iloc[0])
    top_country = df_kpi_country["국가명"].iloc[0]
    total_casino_revenue = df_kpi_revenue["total_casino_revenue"].iloc[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("누적 카지노 이용객", f"{total_users:,}명")
    with col2:
        st.metric("외국인 입장객 1위 국가", top_country)
    with col3:
        st.metric("누적 카지노 외화수입", f"{total_casino_revenue:,.0f}")
except Exception as e:
    st.warning("KPI 계산 중 오류가 발생했습니다. DB의 테이블명과 컬럼명을 확인해주세요.")
    st.exception(e)

st.divider()

# =============================
# 차트 1. 한국 카지노 산업 성장 추이
# =============================
st.header("1. 한국 카지노 산업은 어떻게 변화했는가?")
st.caption("연도별 외래 방한객과 카지노 이용객 변화를 비교합니다.")

sql1 = """
SELECT
    "연 도" AS 연도,
    "외래 방한객" AS 외래방한객,
    "카지노 이용객" AS 카지노이용객
FROM "연도별 외국인 관광객"
ORDER BY "연 도"
"""

df1 = load_data(sql1)
df1["외래방한객"] = to_number(df1["외래방한객"])
df1["카지노이용객"] = to_number(df1["카지노이용객"])

fig1 = px.line(
    df1,
    x="연도",
    y=["외래방한객", "카지노이용객"],
    markers=True,
    title="연도별 외래 방한객과 카지노 이용객 변화",
    color_discrete_sequence=["#d4af37", "#ffffff"]
)
fig1.update_layout(template="plotly_dark", hovermode="x unified")
st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql1, language="sql")
    st.info(
        "외래 방한객과 카지노 이용객의 흐름을 함께 보면 카지노 산업이 관광객 유입 변화에 얼마나 민감하게 반응하는지 확인할 수 있습니다. "
        "특정 연도의 급감 또는 회복 구간은 관광산업 전반의 충격과 카지노 산업의 회복 속도를 비교하는 근거가 됩니다."
    )

st.divider()

# =============================
# 차트 2. 카지노 산업과 관광산업 관계 분석
# =============================
st.header("2. 카지노 산업은 관광산업과 얼마나 연결되어 있는가?")
st.caption("관광 외화수입과 카지노 외화수입을 비교합니다.")

sql2 = """
SELECT
    "연 도" AS 연도,
    "관광 외화수입" AS 관광외화수입,
    "카지노 외화수입" AS 카지노외화수입,
    "점 유율(%)" AS 점유율
FROM "연도별 관광 대비 외화수입"
ORDER BY "연 도"
"""

df2 = load_data(sql2)
df2["관광외화수입"] = to_number(df2["관광외화수입"])
df2["카지노외화수입"] = to_number(df2["카지노외화수입"])
df2["점유율"] = to_number(df2["점유율"])

fig2 = px.bar(
    df2,
    x="연도",
    y=["관광외화수입", "카지노외화수입"],
    barmode="group",
    title="관광 외화수입과 카지노 외화수입 비교",
    color_discrete_sequence=["#8b7355", "#d4af37"]
)
fig2.update_layout(template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql2, language="sql")
    st.info(
        "전체 관광 외화수입과 카지노 외화수입을 함께 비교하면 카지노가 관광산업 안에서 어느 정도의 경제적 비중을 갖는지 파악할 수 있습니다. "
        "점유율 변화를 함께 보면 카지노 산업이 단순 이용객 수뿐 아니라 외화 획득 측면에서도 어떤 역할을 했는지 해석할 수 있습니다."
    )

st.divider()

# =============================
# 차트 3. 국가별 외국인 카지노 이용객 분석
# =============================
st.header("3. 어떤 국가의 관광객이 한국 카지노 산업을 주도하는가?")
st.caption("외국인 입장객 수 상위 10개 국가를 확인합니다.")

sql3 = """
SELECT
    "국가명" AS 국가명,
    "외국인 입장객 수" AS 외국인입장객수
FROM "카지노 외국인 국가"
ORDER BY "외국인 입장객 수" DESC
LIMIT 10
"""

df3 = load_data(sql3)
df3["외국인입장객수"] = to_number(df3["외국인입장객수"])

fig3 = px.bar(
    df3,
    x="외국인입장객수",
    y="국가명",
    orientation="h",
    title="외국인 카지노 입장객 수 TOP 10 국가",
    color="외국인입장객수",
    color_continuous_scale=["#444444", "#d4af37"]
)
fig3.update_layout(template="plotly_dark", yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig3, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(sql3, language="sql")
    st.info(
        "국가별 입장객 수를 보면 한국 카지노 산업이 특정 국가 관광객에게 얼마나 의존하고 있는지 확인할 수 있습니다. "
        "상위 국가에 이용객이 집중되어 있다면 향후 관광 마케팅이나 카지노 산업 전략이 국가별로 세분화될 필요가 있습니다."
    )

st.divider()
st.info("※ SQLite 테이블명과 컬럼명에 띄어쓰기가 포함되어 있어, SQL문에서 큰따옴표를 사용했습니다.")
