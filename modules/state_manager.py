import streamlit as st
from datetime import time
from .config_manager import load_config

def init_session_state():
    """Initialize session state variables."""
    if 'sf_config' not in st.session_state:
        # Try to load from file first
        loaded_config = load_config()
        if loaded_config and 'sf_config' in loaded_config:
            st.session_state['sf_config'] = loaded_config['sf_config']
            st.session_state['auto_login_attempted'] = False # Flag to try auto-login once
        else:
            st.session_state['sf_config'] = {
                'username': '',
                'password': '',
                'security_token': '',
                'domain': 'login' # login (Prod) or test (Sandbox)
            }
            st.session_state['auto_login_attempted'] = True # No config, so consider it "attempted" (skipped)

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

    if 'is_connected' not in st.session_state:
        st.session_state['is_connected'] = False

    if 'sf_client' not in st.session_state:
        st.session_state['sf_client'] = None

def init_widget_state():
    """Helper to sync widget state with session state config."""
    if 'u_username' not in st.session_state:
        st.session_state['u_username'] = st.session_state['sf_config']['username']
    if 'u_password' not in st.session_state:
        st.session_state['u_password'] = st.session_state['sf_config']['password']
    if 'u_token' not in st.session_state:
        st.session_state['u_token'] = st.session_state['sf_config']['security_token']
    if 'u_domain' not in st.session_state:
        st.session_state['u_domain'] = st.session_state['sf_config']['domain']
