import streamlit as st
from modules.state_manager import init_session_state, init_widget_state
from modules.auth import attempt_login, render_auth_tab
from modules.sidebar import render_sidebar
from modules.extract_tab import render_extract_tab
from modules.schedule_tab import render_schedule_tab

# 페이지 기본 설정
st.set_page_config(
    page_title="Salesforce ETL Manager",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
init_session_state()

# Attempt auto-login once on startup if config was loaded
if not st.session_state.get('is_connected') and not st.session_state.get('auto_login_attempted'):
    st.session_state['auto_login_attempted'] = True
    if st.session_state['sf_config']['username'] and st.session_state['sf_config']['password']:
        attempt_login(silent=True)

# Helper to sync widget state
init_widget_state()

# 사이드바: 설정 관리
with st.sidebar:
    render_sidebar()

# 메인 타이틀
st.title("☁️ Salesforce Data ETL Manager")
st.markdown("Salesforce 데이터를 추출하고 스케줄링을 관리하는 대시보드입니다.")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["🔐 Connection", "📊 Extract Settings", "⏰ Schedule"])

# --- TAB 1: Salesforce 연결 설정 ---
with tab1:
    render_auth_tab()

# --- TAB 2: 추출 대상 및 필드 설정 ---
with tab2:
    render_extract_tab()

# --- TAB 3: 스케줄 설정 ---
with tab3:
    render_schedule_tab()
