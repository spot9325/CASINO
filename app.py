import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="Casino Analytics Dashboard",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 반드시 실제 업로드한 DB 파일명과 동일해야 함
DB_PATH = "casino.db"

# =========================================================
# CSS: 사진과 같은 다크 네이비 + 골드 + 퍼플 테마
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800;900&display=swap');

/* Streamlit 기본 UI/하단 배포 안내 숨김 */
#MainMenu {visibility: hidden;}
footer {visibility: hidden; height: 0;}
header {visibility: hidden; height: 0;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
[data-testid="stStatusWidget"] {display: none !important;}
[data-testid="collapsedControl"] {display: none !important;}

:root {
    --bg0: #050b16;
    --bg1: #071426;
    --card: rgba(8, 25, 45, 0.92);
    --line: rgba(106, 170, 230, 0.34);
    --gold: #f1b93e;
    --gold2: #ffd77b;
    --purple: #8e5ce6;
    --purple2: #b888ff;
    --text: #f8fbff;
    --muted: #c8d3e3;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 78% 4%, rgba(241,185,62,0.18) 0, rgba(241,185,62,0.05) 23%, transparent 42%),
        radial-gradient(circle at 20% 8%, rgba(142,92,230,0.18) 0, transparent 35%),
        linear-gradient(180deg, #06101f 0%, #061426 42%, #040914 100%);
}

.block-container {
    max-width: 1240px;
    padding: 2.1rem 1.4rem 2.4rem !important;
}

/* 상단 */
.top-wrap {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1.2rem;
    margin-bottom: 1.35rem;
}
.title-area h1 {
    margin: 0;
    font-size: 2.15rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    color: var(--gold2);
    text-shadow: 0 0 18px rgba(241,185,62,0.18);
}
.title-area p {
    margin: .45rem 0 0;
    color: var(--muted);
    font-size: 1.05rem;
}
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(145px, 1fr));
    gap: .8rem;
    min-width: 560px;
}
.kpi-card {
    border: 1px solid rgba(130, 180, 235, .45);
    border-radius: 12px;
    background: linear-gradient(180deg, rgba(13,31,56,.96), rgba(8,23,43,.96));
    box-shadow: 0 12px 28px rgba(0,0,0,.28), inset 0 0 22px rgba(117,160,255,.05);
    padding: .82rem 1rem;
    text-align: center;
}
.kpi-label {font-size: .82rem; color: #d8e4f4; margin-bottom: .25rem;}
.kpi-value {font-size: 1.55rem; font-weight: 900; color: #fff; letter-spacing: -.02em;}
.kpi-icon {color: var(--gold); font-size: 1.35rem; margin-right:.35rem;}

/* 섹션 카드 */
.section-card {
    border: 1px solid rgba(105, 170, 230, .38);
    border-radius: 10px;
    background: linear-gradient(180deg, rgba(6,20,39,.94), rgba(5,17,32,.94));
    box-shadow: 0 18px 38px rgba(0,0,0,.28);
    padding: 1.05rem 1.08rem 1rem;
    margin-bottom: .95rem;
}
.section-title-row {
    display: flex;
    gap: .8rem;
    align-items: flex-start;
    margin-bottom: 1rem;
}
.badge {
    width: 46px; height: 46px; min-width: 46px;
    border-radius: 8px;
    border: 1px solid rgba(178, 136, 255, .72);
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, rgba(87,52,150,.95), rgba(35,42,97,.94));
    color: #ffe481;
    font-weight: 900;
    font-size: 1.45rem;
    box-shadow: inset 0 0 18px rgba(184,136,255,.2);
}
.section-title h2 {
    margin: 0;
    color: var(--gold2);
    font-size: 1.62rem;
    font-weight: 900;
    letter-spacing: -.05em;
}
.section-title p {
    margin: .12rem 0 0;
    color: #d1dbea;
    font-size: .98rem;
}

/* Plotly 카드와 SQL 카드 */
.viz-card, .sql-panel, .insight-box {
    border: 1px solid rgba(105,170,230,.36);
    border-radius: 9px;
    background: rgba(5, 18, 34, .78);
    overflow: hidden;
}
.viz-card {padding: .75rem .85rem .2rem;}
.viz-title {font-weight: 800; font-size: 1.02rem; margin: 0 0 .25rem; color:#fff;}
.sql-panel {border-color: rgba(178,136,255,.62);}
.sql-head {
    background: linear-gradient(90deg, rgba(50,39,98,.96), rgba(39,35,86,.92));
    padding: .72rem .95rem;
    color: #f7f2ff;
    font-weight: 800;
    border-bottom: 1px solid rgba(178,136,255,.34);
}
.sql-body {padding: .8rem .9rem;}
.stCodeBlock, pre, code {
    background: transparent !important;
    color: #f5f7ff !important;
    font-size: .82rem !important;
}

.insight-box {
    margin-top: .85rem;
    padding: .85rem 1rem;
    border-color: rgba(178,136,255,.65);
    background: linear-gradient(90deg, rgba(45,28,74,.92), rgba(22,28,66,.88));
    color: #fff;
}
.insight-title {
    color: var(--gold2);
    font-weight: 900;
    font-size: 1.02rem;
    margin-bottom: .25rem;
}
.insight-box ul {margin: .2rem 0 0 1.2rem; padding:0;}
.insight-box li {margin: .14rem 0; color:#fff7dc; line-height:1.55;}

/* Streamlit 자체 요소 색 보정 */
[data-testid="stVerticalBlock"] {gap: .85rem;}
.stSlider label, .stExpander, .stDataFrame {color: #fff !important;}
[data-testid="stExpander"] {
    background: rgba(6,20,39,.72);
    border: 1px solid rgba(105,170,230,.35);
    border-radius: 10px;
}
hr {border-color: rgba(105,170,230,.22);}

@media (max-width: 950px) {
    .top-wrap {display:block;}
    .kpi-grid {min-width: 0; grid-template-columns: 1fr; margin-top: 1rem;}
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DB 확인 및 공통 함수
# =========================================================
if not os.path.exists(DB_PATH):
    st.error("데이터베이스 파일을 찾을 수 없습니다.")
    st.warning("app.py와 같은 폴더에 반드시 `casino.db` 파일을 업로드해 주세요. 파일명은 대소문자까지 맞아야 합니다.")
    st.stop()

@st.cache_data
def run_query(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        return pd.read_sql_query(sql, conn)
    finally:
        conn.close()

def comma(x):
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return "-"

def trillion_from_eok(x):
    try:
        return f"{float(x) / 10000:.2f}조원"
    except Exception:
        return "-"

def chart_layout(fig, height=360, legend=True):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f7fbff", family="Noto Sans KR"),
        title_font=dict(color="#ffffff", size=16),
        margin=dict(l=26, r=26, t=38, b=28),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=.5,
            font=dict(color="#dfe8f5", size=11)
        ) if legend else None,
        hoverlabel=dict(bgcolor="#101a2e", font_color="#ffffff", bordercolor="#8e5ce6")
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(160,190,230,.16)", zeroline=False,
        color="#e9f0fb", linecolor="rgba(210,225,245,.22)", tickfont=dict(size=11)
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(160,190,230,.16)", zeroline=False,
        color="#e9f0fb", linecolor="rgba(210,225,245,.22)", tickfont=dict(size=11)
    )
    return fig

def sql_box(sql: str):
    st.markdown("<div class='sql-panel'><div class='sql-head'>사용한 SQL</div><div class='sql-body'>", unsafe_allow_html=True)
    st.code(sql.strip(), language="sql")
    st.markdown("</div></div>", unsafe_allow_html=True)

def insight_box(items):
    lis = "".join([f"<li>{item}</li>" for item in items])
    st.markdown(f"<div class='insight-box'><div class='insight-title'>💡 인사이트</div><ul>{lis}</ul></div>", unsafe_allow_html=True)

def section_open(num, title, subtitle):
    st.markdown(f"""
    <div class='section-card'>
      <div class='section-title-row'>
        <div class='badge'>{num}</div>
        <div class='section-title'>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
    """, unsafe_allow_html=True)

def section_close():
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 상단 KPI
# =========================================================
kpi_sql = """
SELECT
    A."연 도" AS year,
    CAST(REPLACE(A."외래 방한객", ',', '') AS INTEGER) AS foreigner,
    CAST(REPLACE(A."카지노 이용객", ',', '') AS INTEGER) AS casino_visitors,
    CAST(REPLACE(B."카지노 외화수입", ',', '') AS INTEGER) AS casino_fx_revenue
FROM "연도별 외국인 관광객" A
JOIN "연도별 관광 대비 외화수입" B
  ON CAST(A."연 도" AS INTEGER) = CAST(B."연 도" AS INTEGER)
ORDER BY year DESC
LIMIT 1;
"""
kpi = run_query(kpi_sql).iloc[0]

casino_total_sql = """
SELECT
    COUNT(*) AS business_count,
    SUM(CAST(REPLACE("‘25매출액", ',', '') AS INTEGER)) AS total_revenue,
    SUM(CAST(REPLACE("‘25입장객", ',', '') AS INTEGER)) AS total_visitors
FROM "카지노 이용고객 및 매출";
"""
casino_total = run_query(casino_total_sql).iloc[0]

st.markdown(f"""
<div class='top-wrap'>
  <div class='title-area'>
    <h1>👑 Casino Analytics Dashboard</h1>
    <p>공공데이터로 보는 국내 카지노 산업 인사이트</p>
  </div>
  <div class='kpi-grid'>
    <div class='kpi-card'><div class='kpi-label'>총 카지노 사업장</div><div class='kpi-value'><span class='kpi-icon'>🏛️</span>{comma(casino_total['business_count'])}개소</div></div>
    <div class='kpi-card'><div class='kpi-label'>2025년 총 매출</div><div class='kpi-value'><span class='kpi-icon'>₩</span>{trillion_from_eok(casino_total['total_revenue'])}</div></div>
    <div class='kpi-card'><div class='kpi-label'>2025년 총 입장객</div><div class='kpi-value'><span class='kpi-icon'>👥</span>{comma(casino_total['total_visitors'] / 10000)}만명</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 1. 관광 회복 vs 카지노 입장객
# =========================================================
sql_1 = """
SELECT
    v.year,
    v.foreigner AS 외래_방한객수,
    c.total_visitors AS 카지노_입장객수
FROM visitor v
LEFT JOIN (
    SELECT
        year,
        SUM(visitors) AS total_visitors
    FROM casino_yearly
    GROUP BY year
) c ON v.year = c.year
ORDER BY v.year;
"""

# 현재 DB의 한글 테이블명 기준으로도 실행되도록 동일 결과를 만드는 쿼리 사용
sql_1_run = """
SELECT
    A."연 도" AS year,
    CAST(REPLACE(A."외래 방한객", ',', '') AS INTEGER) AS 외래_방한객수,
    CAST(REPLACE(A."카지노 이용객", ',', '') AS INTEGER) AS 카지노_입장객수
FROM "연도별 외국인 관광객" A
ORDER BY CAST(A."연 도" AS INTEGER);
"""
df_1 = run_query(sql_1_run)

section_open("1", "방한 관광 회복은 카지노 수요 회복으로 이어졌는가?", "외래 방한객 수와 카지노 입장객 수 추이 비교")
left, right = st.columns([1.9, 1.05])
with left:
    st.markdown("<div class='viz-card'><div class='viz-title'>연도별 외래 방한객 수 vs 카지노 입장객 수</div>", unsafe_allow_html=True)
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=df_1["year"], y=df_1["외래_방한객수"], name="외래 방한객 수(명)",
        marker_color="#8759d9", opacity=.9,
        hovertemplate="연도=%{x}<br>외래 방한객=%{y:,}명<extra></extra>"
    ))
    fig1.add_trace(go.Scatter(
        x=df_1["year"], y=df_1["카지노_입장객수"], name="카지노 입장객 수(명)",
        mode="lines+markers", marker=dict(size=9, color="#f1b93e"),
        line=dict(width=2.5, color="#f1b93e"), yaxis="y2",
        hovertemplate="연도=%{x}<br>카지노 입장객=%{y:,}명<extra></extra>"
    ))
    fig1.update_layout(
        yaxis=dict(title="외래 방한객 수(명)", tickformat="~s"),
        yaxis2=dict(title="카지노 입장객 수(명)", overlaying="y", side="right", tickformat="~s", color="#f1b93e")
    )
    st.plotly_chart(chart_layout(fig1, height=355), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    sql_box(sql_1)
insight_box([
    "2020~2021년 전체 방한객은 급감했지만 카지노 이용객 감소폭은 상대적으로 작아, 카지노 수요층의 회복력이 더 빠르게 나타났습니다.",
    "2023년 이후 방한객과 카지노 이용객은 함께 회복세를 보였지만, 단순 관광객 증가만으로 카지노 수요를 설명하기는 어렵습니다.",
    "이는 카지노 산업이 관광객 총량보다 ‘카지노 이용 가능성이 높은 고객층’ 변화에 더 민감하게 반응함을 시사합니다."
])
section_close()

# =========================================================
# 2. 사업장별 매출과 입장객당 매출
# =========================================================
sql_2 = """
SELECT
    business_name AS 사업장명,
    revenue AS 매출액_억원,
    CASE
        WHEN visitors > 0
        THEN ROUND((revenue * 100000000) / visitors, 0)
        ELSE NULL
    END AS 입장객당_매출_원
FROM casino_2025
WHERE revenue IS NOT NULL
ORDER BY revenue DESC
LIMIT 10;
"""
sql_2_run = """
SELECT
    "카지노명" AS 사업장명,
    CAST(REPLACE("‘25매출액", ',', '') AS INTEGER) AS 매출액_억원,
    CAST(REPLACE("‘25입장객", ',', '') AS INTEGER) AS 입장객수,
    CASE
        WHEN CAST(REPLACE("‘25입장객", ',', '') AS INTEGER) > 0
        THEN ROUND((CAST(REPLACE("‘25매출액", ',', '') AS REAL) * 100000000) / CAST(REPLACE("‘25입장객", ',', '') AS REAL), 0)
        ELSE NULL
    END AS 입장객당_매출_원
FROM "카지노 이용고객 및 매출"
WHERE "‘25매출액" IS NOT NULL
ORDER BY 매출액_억원 DESC
LIMIT 10;
"""
df_2 = run_query(sql_2_run).sort_values("매출액_억원", ascending=True)

section_open("2", "카지노 사업장별 매출 집중도와 고객당 수익성은 어떻게 다른가?", "2025년 사업장별 매출과 입장객당 매출(효율성) 비교")
left, right = st.columns([1.9, 1.05])
with left:
    st.markdown("<div class='viz-card'><div class='viz-title'>2025년 사업장별 매출 및 입장객당 매출(Top 10)</div>", unsafe_allow_html=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=df_2["사업장명"], x=df_2["매출액_억원"], name="매출액(억원)", orientation="h",
        marker_color="#8e5ce6", opacity=.92,
        text=df_2["매출액_억원"].map(lambda x: f"{x:,.0f}"), textposition="outside",
        hovertemplate="사업장=%{y}<br>매출액=%{x:,}억원<extra></extra>"
    ))
    fig2.add_trace(go.Scatter(
        y=df_2["사업장명"], x=df_2["입장객당_매출_원"], name="입장객당 매출(원)",
        mode="lines+markers", marker=dict(size=8, color="#f1b93e"),
        line=dict(width=2, color="#f1b93e"), xaxis="x2",
        hovertemplate="사업장=%{y}<br>입장객당 매출=%{x:,.0f}원<extra></extra>"
    ))
    fig2.update_layout(
        xaxis=dict(title="매출액(억원)", range=[0, max(df_2["매출액_억원"]) * 1.18]),
        xaxis2=dict(title="입장객당 매출(원)", overlaying="x", side="top", showgrid=False, color="#f1b93e"),
        yaxis=dict(title="사업장명")
    )
    st.plotly_chart(chart_layout(fig2, height=365), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    sql_box(sql_2)
insight_box([
    "2025년 매출은 상위 3개 사업장에 약 66%가 집중되어 있어, 카지노 시장이 대형 거점 중심 구조임을 보여줍니다.",
    "강원랜드는 입장객과 매출 규모 모두 압도적이지만, 고객당 매출 기준에서는 파라다이스시티·드림타워 등 복합리조트형 카지노의 수익성이 더 높게 나타납니다.",
    "즉 ‘많이 방문하는 카지노’와 ‘고객당 소비가 큰 카지노’는 다르며, 규모성과 수익성을 분리해 해석할 필요가 있습니다."
])
section_close()

# =========================================================
# 3. 외국인 카지노 수요 국가 집중도
# =========================================================
sql_3 = """
SELECT
    country AS 국가,
    SUM(visitors) AS 입장객수
FROM casino_country_2025
GROUP BY country
ORDER BY 입장객수 DESC
LIMIT 10;
"""
sql_3_run = """
SELECT
    "국가명" AS 국가,
    SUM(CAST(REPLACE("외국인 입장객 수", ',', '') AS INTEGER)) AS 입장객수
FROM "카지노 외국인 국가"
GROUP BY "국가명"
ORDER BY 입장객수 DESC
LIMIT 10;
"""
df_3 = run_query(sql_3_run).sort_values("입장객수", ascending=True)

section_open("3", "외국인 카지노 수요는 어느 국가에 집중되어 있는가?", "2025년 기준 국가별 카지노 입장객 수 (Top 10)")
left, right = st.columns([1.9, 1.05])
with left:
    st.markdown("<div class='viz-card'><div class='viz-title'>국가별 카지노 입장객 수 (Top 10)</div>", unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        y=df_3["국가"], x=df_3["입장객수"], orientation="h", name="입장객 수(명)",
        marker_color="#8e5ce6",
        text=df_3["입장객수"].map(lambda x: f"{x:,.0f}"), textposition="outside",
        hovertemplate="국가=%{y}<br>입장객=%{x:,}명<extra></extra>"
    ))
    fig3.update_layout(xaxis=dict(title="입장객 수(명)", tickformat="~s"), yaxis=dict(title=""))
    st.plotly_chart(chart_layout(fig3, height=360, legend=False), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
with right:
    sql_box(sql_3)
    insight_box([
        "중국·홍콩·미국·태국·대만 등 상위 5개 국가가 전체 카지노 외국인 수요의 대부분을 차지해 국가별 집중도가 매우 높게 나타납니다.",
        "특히 중국 의존도가 압도적으로 높아, 카지노 산업은 특정 국가의 경기·환율·출입국 정책 변화에 영향을 크게 받을 가능성이 있습니다.",
        "따라서 핵심 국가 집중 전략은 유지하되, 미국·동남아권 등 신규 수요 시장을 함께 확대하는 전략이 필요합니다."
    ])
section_close()

# =========================================================
# 원본 데이터 미리보기: 배포 안내 문구는 완전 삭제
# =========================================================
with st.expander("원본 데이터 테이블 미리보기", expanded=False):
    tab1, tab2, tab3, tab4 = st.tabs(["연도별 외국인 관광객", "연도별 관광 대비 외화수입", "카지노 이용고객 및 매출", "카지노 외국인 국가"])
    with tab1:
        st.dataframe(run_query('SELECT * FROM "연도별 외국인 관광객"'), use_container_width=True)
    with tab2:
        st.dataframe(run_query('SELECT * FROM "연도별 관광 대비 외화수입"'), use_container_width=True)
    with tab3:
        st.dataframe(run_query('SELECT * FROM "카지노 이용고객 및 매출"'), use_container_width=True)
    with tab4:
        st.dataframe(run_query('SELECT * FROM "카지노 외국인 국가"'), use_container_width=True)
