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
