import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 설정 (와이드 레이아웃)
st.set_page_config(page_title="카지노 산업 분석 대시보드", layout="wide")

# 2. 고급스러운 블랙 & 골드 테마 적용 (Custom CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stMetric { background-color: #1f2630; padding: 20px; border-radius: 10px; border: 1px solid #d4af37; }
    h1, h2, h3 { color: #d4af37 !important; }
    .stMarkdown { color: #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# 3. SQLite 연결 함수 (캐싱 적용)
@st.cache_data
def load_data(query):
    if not os.path.exists('casino.db'):
        return None
    conn = sqlite3.connect('casino.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# DB 파일 존재 여부 확인 후 진행
if not os.path.exists('casino.db'):
    st.error("⚠️ 'casino.db' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요.")
    st.stop()

# --- 대시보드 시작 ---
st.title("🎰 카지노 산업 통계 데이터 분석 대시보드")
st.markdown("공공데이터를 기반으로 대한민국 카지노 산업의 현황과 성장 추이를 분석합니다.")

# --- 상단 KPI 카드 ---
st.subheader("📊 주요 지표 (KPI)")
col1, col2, col3 = st.columns(3)

# 데이터 불러오기 (KPI용)
df_kpi_tourist = load_data("SELECT SUM(카지노이용객) as total_users FROM 연도별_외국인_관광객")
df_kpi_country = load_data("SELECT 국가명 FROM 카지노_외국인_국가 ORDER BY 외국인입장객수 DESC LIMIT 1")

with col1:
    total_users = df_kpi_tourist['total_users'].iloc[0]
    st.metric("누적 총 카지노 이용객", f"{total_users:,} 명")

with col2:
    top_country = df_kpi_country['국가명'].iloc[0]
    st.metric("최대 이용 국가", top_country)

with col3:
    st.metric("산업 테마", "Premium Gold")

st.divider()

# --- 차트 1: 한국 카지노 산업 성장 추이 ---
st.header("1. 한국 카지노 산업 성장 추이")
sql1 = "SELECT 연도, 외래방한객, 카지노이용객 FROM 연도별_외국인_관광객"
df1 = load_data(sql1)

if df1 is not None:
    fig1 = px.line(df1, x='연도', y=['외래방한객', '카지노이용객'], 
                  title="연도별 외래방한객과 카지노이용객 변화",
                  markers=True, color_discrete_sequence=['#d4af37', '#ffffff'])
    fig1.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig1, use_container_width=True)
    
    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(sql1, language='sql')
        st.write("💡 **인사이트:** 전체 외래 방한객의 증감 추세와 카지노 이용객의 상관관계를 보여줍니다. 특정 시점의 급격한 변화는 대외 경제 상황이나 정책 변화를 반영합니다.")

# --- 차트 2: 카지노 산업과 관광산업 관계 분석 ---
st.header("2. 카지노 산업과 관광산업 관계 분석")
sql2 = "SELECT 연도, 관광외화수입, 카지노외화수입 FROM 연도별_관광_대비_외화수입"
df2 = load_data(sql2)

if df2 is not None:
    # 텍스트 형태의 수입 데이터를 숫자로 변환 (천 단위 콤마 제거 등)
    df2['관광외화수입'] = df2['관광외화수입'].str.replace(',', '').astype(float)
    df2['카지노외화수입'] = df2['카지노외화수입'].str.replace(',', '').astype(float)
    
    fig2 = px.bar(df2, x='연도', y=['관광외화수입', '카지노이외화수입'], 
                 title="관광외화수입과 카지노외화수입 비교",
                 barmode='group', color_discrete_sequence=['#8b7355', '#d4af37'])
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(sql2, language='sql')
        st.write("💡 **인사이트:** 전체 관광 외화 수입 중 카지노가 기여하는 비중을 확인할 수 있습니다. 카지노는 고부가가치 관광 산업으로서 중요한 위치를 차지합니다.")

# --- 차트 3: 국가별 외국인 카지노 이용객 분석 ---
st.header("3. 국가별 외국인 카지노 이용객 분석")
sql3 = "SELECT 국가명, 외국인입장객수 FROM 카지노_외국인_국가 ORDER BY 외국인입장객수 DESC LIMIT 10"
df3 = load_data(sql3)

if df3 is not None:
    fig3 = px.bar(df3, x='외국인입장객수', y='국가명', orientation='h',
                 title="외국인입장객수 상위 10개 국가",
                 color='외국인입장객수', color_continuous_scale=['#444444', '#d4af37'])
    fig3.update_layout(template="plotly_dark", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("사용한 SQL 및 인사이트 보기"):
        st.code(sql3, language='sql')
        st.write("💡 **인사이트:** 특정 국가(예: 중국, 일본 등)에 대한 의존도를 파악할 수 있습니다. 마케팅 전략 수립 시 타겟 국가를 선정하는 핵심 지표가 됩니다.")

st.info("본 데이터는 공공데이터 포털의 카지노 산업 통계를 바탕으로 구성되었습니다.")
