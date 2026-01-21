import streamlit as st
import pandas as pd
import os
import json
from datetime import time

# 페이지 기본 설정
st.set_page_config(
    page_title="Salesforce ETL Manager",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화 (메모리상 임시 저장)
if 'sf_config' not in st.session_state:
    st.session_state['sf_config'] = {
        'username': '',
        'password': '',
        'security_token': '',
        'domain': 'login' # login (Prod) or test (Sandbox)
    }

if 'etl_config' not in st.session_state:
    st.session_state['etl_config'] = {
        'selected_object': '',
        'selected_fields': [],
        'batch_size': 1000
    }

if 'schedule_config' not in st.session_state:
    st.session_state['schedule_config'] = {
        'frequency': 'Daily',
        'run_time': time(9, 0),
        'is_active': False
    }

# 사이드바: 설정 관리
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.info("Heroku 환경에서는 DB를 연동하여 설정을 영구 저장해야 합니다. 현재는 세션 상태(임시)로 동작합니다.")
    
    # 설정 불러오기 (Mock)
    if st.button("Load Settings"):
        st.toast("Settings loaded successfully! (Mock)", icon="✅")
    
    # 설정 저장하기 (Mock)
    if st.button("Save All Settings", type="primary"):
        # 실제 구현시 여기서 DB에 저장
        st.success("Configuration saved to Database! (Mock)")
        st.json({
            "Auth": "********",
            "ETL": st.session_state['etl_config'],
            "Schedule": st.session_state['schedule_config']
        })

# 메인 타이틀
st.title("☁️ Salesforce Data ETL Manager")
st.markdown("Salesforce 데이터를 추출하고 스케줄링을 관리하는 대시보드입니다.")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["🔐 Connection", "📊 Extract Settings", "⏰ Schedule"])

# --- TAB 1: Salesforce 연결 설정 ---
with tab1:
    st.subheader("Salesforce Authentication")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['sf_config']['username'] = st.text_input(
            "Username", 
            value=st.session_state['sf_config']['username'],
            placeholder="user@example.com"
        )
        st.session_state['sf_config']['password'] = st.text_input(
            "Password", 
            type="password",
            value=st.session_state['sf_config']['password']
        )
    
    with col2:
        st.session_state['sf_config']['security_token'] = st.text_input(
            "Security Token", 
            type="password",
            value=st.session_state['sf_config']['security_token'],
            help="Salesforce Security Token is required for API access."
        )
        st.session_state['sf_config']['domain'] = st.selectbox(
            "Environment", 
            options=["login", "test"], 
            index=0 if st.session_state['sf_config']['domain'] == 'login' else 1,
            format_func=lambda x: "Production (login.salesforce.com)" if x == "login" else "Sandbox (test.salesforce.com)"
        )
    
    if st.button("Test Connection"):
        if not st.session_state['sf_config']['username'] or not st.session_state['sf_config']['password']:
            st.error("Please enter Username and Password.")
        else:
            with st.spinner("Connecting to Salesforce..."):
                # 실제 연결 로직은 추후 구현
                import time as t
                t.sleep(1.5) 
                st.success("Connection Successful! (Authenticated as Org ID: 00Dxxx...)")

# --- TAB 2: 추출 대상 및 필드 설정 ---
with tab2:
    st.subheader("Object & Fields Selection")
    
    # 1. Object 선택
    # 실제로는 SF API로 Object 목록을 가져와야 함. 여기서는 샘플 데이터 사용.
    sample_objects = ["Account", "Contact", "Opportunity", "Lead", "Case", "CustomObject__c"]
    
    selected_obj = st.selectbox(
        "Select Salesforce Object", 
        options=sample_objects,
        index=sample_objects.index(st.session_state['etl_config']['selected_object']) if st.session_state['etl_config']['selected_object'] in sample_objects else 0
    )
    st.session_state['etl_config']['selected_object'] = selected_obj
    
    st.divider()
    
    # 2. Field 선택
    # 선택된 Object에 따라 필드 목록을 동적으로 가져와야 함.
    st.write(f"Available Fields for **{selected_obj}**")
    
    sample_fields = {
        "Account": ["Id", "Name", "Type", "BillingCity", "CreatedDate", "LastModifiedDate"],
        "Contact": ["Id", "FirstName", "LastName", "Email", "Phone", "AccountId"],
        "Opportunity": ["Id", "Name", "StageName", "Amount", "CloseDate", "AccountId"]
    }
    
    current_fields_options = sample_fields.get(selected_obj, ["Id", "Name", "CreatedDate", "SystemModstamp"])
    
    selected_fds = st.multiselect(
        "Select Fields to Extract",
        options=current_fields_options,
        default=st.session_state['etl_config']['selected_fields'] if st.session_state['etl_config']['selected_fields'] else ["Id", "Name"]
    )
    st.session_state['etl_config']['selected_fields'] = selected_fds

    # Preview Logic
    if st.button("Preview Data (Top 5 Rows)"):
        st.dataframe(pd.DataFrame(columns=selected_fds, data=[["Sample 1", "Sample 2"] * (len(selected_fds)//2 + 1)]))

# --- TAB 3: 스케줄 설정 ---
with tab3:
    st.subheader("Job Scheduler")
    
    col_sch1, col_sch2 = st.columns([1, 2])
    
    with col_sch1:
        st.write("Schedule Configuration")
        st.session_state['schedule_config']['is_active'] = st.toggle(
            "Activate Schedule", 
            value=st.session_state['schedule_config']['is_active']
        )
        
        freq = st.selectbox(
            "Frequency", 
            ["Daily", "Hourly", "Weekly", "Cron Expression"],
            index=0
        )
        st.session_state['schedule_config']['frequency'] = freq
        
        if freq == "Daily":
            run_time = st.time_input("Run Time (UTC)", value=st.session_state['schedule_config']['run_time'])
            st.session_state['schedule_config']['run_time'] = run_time
        elif freq == "Cron Expression":
            st.text_input("Cron Expression", value="0 9 * * *")
            
    with col_sch2:
        st.info(f"""
        **Current Schedule Status:**
        - Active: {'✅ Yes' if st.session_state['schedule_config']['is_active'] else '❌ No'}
        - Frequency: {st.session_state['schedule_config']['frequency']}
        - Next Run: (Calculated based on timezone)
        """)
        
        st.warning("Heroku Free/Eco Dynos sleep after 30 mins of inactivity. For reliable scheduling, use 'Heroku Scheduler' add-on or a dedicated worker dyno.")

