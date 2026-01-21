import streamlit as st
from datetime import time
from .config_manager import load_config

def init_session_state():
    """Initialize session state variables."""
    loaded_config = None
    if 'sf_config' not in st.session_state or 'etl_config' not in st.session_state:
        loaded_config = load_config()

    if 'sf_config' not in st.session_state:
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
        if loaded_config and 'etl_config' in loaded_config:
            config = loaded_config['etl_config']
            # Migration logic: If old format (no mappings), convert to new format
            if 'mappings' not in config:
                mappings = []
                if config.get('selected_object'):
                    mappings.append({
                        'object': config['selected_object'],
                        'fields': config.get('selected_fields', [])
                    })
                config['mappings'] = mappings
                # Remove old keys if you want to clean up, or keep them ignored
                config.pop('selected_object', None)
                config.pop('selected_fields', None)
            
            st.session_state['etl_config'] = config
        else:
            st.session_state['etl_config'] = {
                'mappings': [],
                'batch_size': 1000
            }

    if 'schedule_config' not in st.session_state:
        if loaded_config and 'schedule_config' in loaded_config:
            sc = loaded_config['schedule_config']
            # Convert run_time string back to time object if it's a string
            if isinstance(sc.get('run_time'), str):
                from datetime import datetime
                try:
                    sc['run_time'] = datetime.strptime(sc['run_time'], "%H:%M:%S").time()
                except:
                    sc['run_time'] = time(9, 0)
            st.session_state['schedule_config'] = sc
        else:
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
