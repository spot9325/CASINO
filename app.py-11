
import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="K-Casino Tourism Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = "casino.db"

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0B1020 0%, #111827 45%, #F8FAFC 45%, #F8FAFC 100%);
}
.block-container {padding-top: 2.2rem; padding-bottom: 3rem;}
h1, h2, h3 {letter-spacing: -0.03em;}
.hero {
    padding: 1.7rem 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #111827 0%, #1F2937 58%, #7C2D12 100%);
    color: white;
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0 18px 45px rgba(15,23,42,0.32);
}
.hero h1 {font-size: 2.15rem; margin: 0 0 0.4rem 0;}
.hero p {font-size: 1rem; color: #CBD5E1; margin: 0;}
.metric-card {
    padding: 1.1rem 1.2rem;
    border-radius: 18px;
    background: white;
    border: 1px solid #E5E7EB;
    box-shadow: 0 12px 28px rgba(15,23,42,0.08);
}
.metric-label {font-size: 0.86rem; color:#64748B;}
.metric-value {font-size: 1.55rem; font-weight: 750; color:#111827; margin-top:0.25rem;}
.chart-card {
    padding: 1.25rem;
    border-radius: 22px;
    background: white;
    border: 1px solid #E5E7EB;
    box-shadow: 0 12px 30px rgba(15,23,42,0.08);
    margin-bottom: 1.2rem;
}
.sql-box {
    border-radius: 14px;
    border: 1px solid #E5E7EB;
    background: #F8FAFC;
    padding: 0.85rem;
}
.insight-box {
    border-left: 4px solid #92400E;
    background: #FFFBEB;
    padding: 0.9rem 1rem;
    border-radius: 12px;
    color: #1F2937;
}
.small-note {font-size:0.86rem; color:#64748B;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>K-Casino Tourism Intelligence Dashboard</h1>
  <p>공공 카지노·관광 데이터를 연결해 방한 관광 회복, 카지노 수요 전환, 사업장별 수익 구조, 국적 포트폴리오를 분석합니다.</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# DB 확인 및 공통 함수
# =========================================================
if not os.path.exists(DB_PATH):
    st.error("데이터베이스 파일을 찾을 수 없습니다.")
    st.warning("app.py와 같은 폴더에 'CASINO.db.db' 파일이 있는지 확인해 주세요.")
    st.stop()

@st.cache_data
def run_query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
    finally:
        conn.close()
    return df

def show_sql_and_insight(sql: str, insight: str):
    with st.expander("사용한 SQL 보기", expanded=False):
        st.code(sql.strip(), language="sql")
    st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

def comma(x):
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return "-"

# =========================================================
# 사이드바
# =========================================================
st.sidebar.header("대시보드 구성")
st.sidebar.write("사용 테이블")
st.sidebar.markdown("""
- 연도별 외국인 관광객
- 연도별 관광 대비 외화수입
- 카지노 이용고객 및 매출
- 카지노 외국인 국가
""")
st.sidebar.divider()
st.sidebar.write("분석 초점")
st.sidebar.markdown("""
1. 관광 회복이 카지노 수요로 전환되는가  
2. 고객 수와 매출은 같은 방향으로 움직이는가  
3. 외국인 카지노 수요는 어느 국가에 집중되는가
""")

# =========================================================
# 핵심 지표
# =========================================================
kpi_sql = """
SELECT
    A."연 도" AS "연도",
    CAST(REPLACE(A."외래 방한객", ',', '') AS INTEGER) AS "외래방한객",
    CAST(REPLACE(A."카지노 이용객", ',', '') AS INTEGER) AS "카지노이용객",
    CAST(REPLACE(B."카지노 외화수입", ',', '') AS INTEGER) AS "카지노외화수입",
    CAST(B."점유율(%)" AS REAL) AS "카지노외화수입점유율"
FROM "연도별 외국인 관광객" A
JOIN "연도별 관광 대비 외화수입" B
  ON CAST(A."연 도" AS INTEGER) = CAST(B."연 도" AS INTEGER)
ORDER BY "연도" DESC
LIMIT 1
"""
kpi = run_query(kpi_sql).iloc[0]

casino_total_sql = """
SELECT
    SUM(CAST(REPLACE("‘25매출액", ',', '') AS INTEGER)) AS "총매출액",
    SUM(CAST(REPLACE("‘25입장객", ',', '') AS INTEGER)) AS "총입장객"
FROM "카지노 이용고객 및 매출"
"""
casino_total = run_query(casino_total_sql).iloc[0]

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>2025 외래 방한객</div><div class='metric-value'>{comma(kpi['외래방한객'])}명</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>2025 카지노 이용객</div><div class='metric-value'>{comma(kpi['카지노이용객'])}명</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>2025 카지노 외화수입 점유율</div><div class='metric-value'>{kpi['카지노외화수입점유율']:.1f}%</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>2025 사업장 총매출액</div><div class='metric-value'>{comma(casino_total['총매출액'])}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# 차트 1
# =========================================================
sql_1 = """
SELECT
    A."연 도" AS "연도",
    CAST(REPLACE(A."외래 방한객", ',', '') AS INTEGER) AS "외래방한객",
    CAST(REPLACE(A."카지노 이용객", ',', '') AS INTEGER) AS "카지노이용객",
    ROUND(
        CAST(REPLACE(A."카지노 이용객", ',', '') AS REAL)
        / NULLIF(CAST(REPLACE(A."외래 방한객", ',', '') AS REAL), 0) * 100, 2
    ) AS "카지노전환율",
    CAST(REPLACE(B."카지노 외화수입", ',', '') AS INTEGER) AS "카지노외화수입",
    CAST(B."점유율(%)" AS REAL) AS "카지노외화수입점유율"
FROM "연도별 외국인 관광객" A
JOIN "연도별 관광 대비 외화수입" B
  ON CAST(A."연 도" AS INTEGER) = CAST(B."연 도" AS INTEGER)
ORDER BY "연도";
"""
df_1 = run_query(sql_1)
st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("1. 방한 관광 회복은 카지노 수요 회복으로 이어졌는가")
left, right = st.columns([1.65, 1])
with left:
    fig1 = px.line(
        df_1,
        x="연도",
        y=["외래방한객", "카지노이용객"],
        markers=True,
        title="연도별 외래 방한객과 카지노 이용객 추이"
    )
    fig1.update_layout(
        height=420,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend_title_text="구분",
        margin=dict(l=20, r=20, t=55, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)
with right:
    insight_1 = """
    <b>인사이트</b><br>
    2020~2021년에는 전체 방한객이 급감했지만 카지노 전환율은 비정상적으로 높아져, 단순한 관광객 규모보다 ‘입국자 구성’이 더 중요하게 작동했음을 보여준다. 
    2023년 이후 방한객과 카지노 이용객은 함께 회복되지만, 2025년 전환율은 약 18.45% 수준으로 팬데믹 특수 구간보다 낮다. 
    따라서 카지노 산업은 관광객 총량 회복만으로 설명하기 어렵고, 카지노 이용 가능성이 높은 세그먼트를 별도로 추적해야 한다.
    """
    show_sql_and_insight(sql_1, insight_1)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 차트 2
# =========================================================
sql_2 = """
SELECT
    "카지노명",
    CAST(REPLACE("‘25매출액", ',', '') AS INTEGER) AS "매출액",
    CAST(REPLACE("‘25입장객", ',', '') AS INTEGER) AS "입장객",
    ROUND(
        CAST(REPLACE("‘25매출액", ',', '') AS REAL)
        / NULLIF(CAST(REPLACE("‘25입장객", ',', '') AS REAL), 0), 3
    ) AS "입장객당매출"
FROM "카지노 이용고객 및 매출"
ORDER BY "매출액" DESC;
"""
df_2 = run_query(sql_2)
top_n = st.slider("차트 2 표시 사업장 수", min_value=5, max_value=len(df_2), value=10)
df_2_view = df_2.head(top_n).sort_values("매출액", ascending=True)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("2. 카지노 사업장별 매출 집중도와 고객당 수익성은 어떻게 다른가")
left, right = st.columns([1.65, 1])
with left:
    fig2 = px.bar(
        df_2_view,
        x="매출액",
        y="카지노명",
        orientation="h",
        hover_data=["입장객", "입장객당매출"],
        title="2025 카지노 사업장별 매출액 상위 구조"
    )
    fig2.update_layout(
        height=500,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="매출액",
        yaxis_title="카지노명",
        margin=dict(l=20, r=20, t=55, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)
with right:
    top3_share = df_2.sort_values("매출액", ascending=False).head(3)["매출액"].sum() / df_2["매출액"].sum() * 100
    insight_2 = f"""
    <b>인사이트</b><br>
    2025년 매출은 상위 3개 사업장에 약 {top3_share:.1f}%가 집중되어 있어, 카지노 시장이 균등 분산형이 아니라 대형 거점 중심 구조임을 보여준다. 
    특히 강원랜드는 입장객과 매출 규모가 모두 크지만, 고객당 매출 기준에서는 파라다이스시티·드림타워 등 복합리조트형 사업장의 수익성이 더 두드러진다. 
    즉 ‘많이 오는 카지노’와 ‘한 명당 지출이 큰 카지노’는 다르며, 대시보드에서는 규모성과 수익성을 분리해 해석해야 한다.
    """
    show_sql_and_insight(sql_2, insight_2)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 차트 3
# =========================================================
sql_3 = """
SELECT
    "국가명",
    SUM(CAST(REPLACE("외국인 입장객 수", ',', '') AS INTEGER)) AS "외국인입장객수"
FROM "카지노 외국인 국가"
GROUP BY "국가명"
ORDER BY "외국인입장객수" DESC
LIMIT 15;
"""
df_3 = run_query(sql_3).sort_values("외국인입장객수", ascending=True)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.subheader("3. 외국인 카지노 수요는 어느 국가에 집중되어 있는가")
left, right = st.columns([1.65, 1])
with left:
    fig3 = px.bar(
        df_3,
        x="외국인입장객수",
        y="국가명",
        orientation="h",
        title="국가별 외국인 카지노 입장객 상위 15개국"
    )
    fig3.update_layout(
        height=500,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="외국인 입장객 수",
        yaxis_title="국가명",
        margin=dict(l=20, r=20, t=55, b=20)
    )
    st.plotly_chart(fig3, use_container_width=True)
with right:
    country_total_sql = """
    SELECT
        SUM("국가별합계") AS "전체합계"
    FROM (
        SELECT
            "국가명",
            SUM(CAST(REPLACE("외국인 입장객 수", ',', '') AS INTEGER)) AS "국가별합계"
        FROM "카지노 외국인 국가"
        GROUP BY "국가명"
    );
    """
    total_foreign = run_query(country_total_sql).iloc[0]["전체합계"]
    top5_share = run_query("""
    SELECT
        SUM("외국인입장객수") AS "상위5합계"
    FROM (
        SELECT
            "국가명",
            SUM(CAST(REPLACE("외국인 입장객 수", ',', '') AS INTEGER)) AS "외국인입장객수"
        FROM "카지노 외국인 국가"
        GROUP BY "국가명"
        ORDER BY "외국인입장객수" DESC
        LIMIT 5
    );
    """).iloc[0]["상위5합계"] / total_foreign * 100

    insight_3 = f"""
    <b>인사이트</b><br>
    국가별 입장객은 중국이 압도적으로 크고, 홍콩·미국·태국·대만이 뒤를 잇는다. 상위 5개 국가가 전체의 약 {top5_share:.1f}%를 차지해 수요 포트폴리오가 매우 집중되어 있다. 
    이는 마케팅 효율성 측면에서는 핵심국가 집중 전략이 유리하다는 뜻이지만, 특정 국가의 경기·환율·출입국 정책 변화에 취약하다는 리스크도 함께 의미한다. 
    따라서 카지노 관광 전략은 중국권 의존도를 관리하면서 미국·동남아권을 보완 시장으로 확장하는 방향이 타당하다.
    """
    show_sql_and_insight(sql_3, insight_3)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 데이터 미리보기 및 배포 안내
# =========================================================
with st.expander("원본 데이터 테이블 미리보기"):
    tab1, tab2, tab3, tab4 = st.tabs(["연도별 외국인 관광객", "연도별 관광 대비 외화수입", "카지노 이용고객 및 매출", "카지노 외국인 국가"])
    with tab1:
        st.dataframe(run_query('SELECT * FROM "연도별 외국인 관광객"'), use_container_width=True)
    with tab2:
        st.dataframe(run_query('SELECT * FROM "연도별 관광 대비 외화수입"'), use_container_width=True)
    with tab3:
        st.dataframe(run_query('SELECT * FROM "카지노 이용고객 및 매출"'), use_container_width=True)
    with tab4:
        st.dataframe(run_query('SELECT * FROM "카지노 외국인 국가"'), use_container_width=True)

st.divider()
st.markdown("""
### GitHub 및 Streamlit 배포 안내
1. GitHub Repository를 만들고 `app.py`, `requirements.txt`, `CASINO.db.db`를 같은 위치에 업로드한다.  
2. Streamlit Community Cloud에서 GitHub Repository를 연결하고 Main file path를 `app.py`로 지정한다.  
3. 배포 후 생성된 사이트 주소와 GitHub 주소를 과제 제출란에 함께 제출한다.  
4. README.md에는 사용한 프롬프트, 데이터 전처리 방식, 차트별 SQL과 인사이트를 정리한다.
""")
