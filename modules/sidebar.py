import streamlit as st
from .config_manager import load_config, save_config

def render_sidebar():
    st.header("⚙️ Configuration")
    
    st.info("Heroku 환경에서는 DB를 연동하여 설정을 영구 저장해야 합니다. 현재는 세션 상태(임시)로 동작합니다.")
    
    # 설정 불러오기 (Mock -> Real Local)
    if st.button("Reload Config from File"):
        cfg = load_config()
        if cfg:
            st.session_state['sf_config'] = cfg.get('sf_config', st.session_state['sf_config'])
            # Explicitly update widget keys to reflect new config in UI
            st.session_state['u_username'] = st.session_state['sf_config']['username']
            st.session_state['u_password'] = st.session_state['sf_config']['password']
            st.session_state['u_token'] = st.session_state['sf_config']['security_token']
            st.session_state['u_domain'] = st.session_state['sf_config']['domain']
            
            st.toast("Configuration reloaded from config.json", icon="🔄")
            st.rerun()
        else:
            st.error("config.json not found.")
    
    # 설정 저장하기 (Mock -> Real Local)
    if st.button("Save Settings to File", type="primary"):
        save_data = {
            "sf_config": st.session_state['sf_config'],
            "etl_config": st.session_state['etl_config'],
            "schedule_config": {
                # Time objects are not JSON serializable, convert to string
                "frequency": st.session_state['schedule_config']['frequency'],
                "run_time": st.session_state['schedule_config']['run_time'].strftime("%H:%M:%S"),
                "is_active": st.session_state['schedule_config']['is_active']
            }
        }
        # Note: We are saving password in plain text for this local prototype.
        save_config(save_data)
        st.success("Configuration saved to config.json!")
