import json
import os
import streamlit as st

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from local JSON file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Failed to load config file: {e}")
    return None

def save_config(config_data):
    """Save configuration to local JSON file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        st.error(f"Failed to save config file: {e}")

def save_app_config():
    """Helper to save all relevant session state to config.json."""
    save_data = {
        "sf_config": st.session_state.get('sf_config', {}),
        "mariadb_config": st.session_state.get('mariadb_config', {}),
        "etl_config": st.session_state.get('etl_config', {}),
        "schedule_config": {
            "frequency": st.session_state['schedule_config']['frequency'],
            "run_time": st.session_state['schedule_config']['run_time'].strftime("%H:%M:%S") if hasattr(st.session_state['schedule_config']['run_time'], 'strftime') else st.session_state['schedule_config']['run_time'],
            "is_active": st.session_state['schedule_config']['is_active']
        }
    }
    save_config(save_data)
