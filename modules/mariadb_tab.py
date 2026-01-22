import streamlit as st
from .config_manager import save_app_config

def render_mariadb_tab():
    st.subheader("🗄️ MariaDB Connection Settings")
    st.markdown("Enter your MariaDB/MySQL database connection details.")

    # Get current config
    config = st.session_state.get('mariadb_config', {
        'host': '',
        'port': 3306,
        'user': '',
        'password': '',
        'database': ''
    })

    col1, col2 = st.columns(2)

    with col1:
        host = st.text_input("Host", value=config.get('host', ''), placeholder="localhost or IP address")
        port = st.number_input("Port", value=int(config.get('port', 3306)), min_value=1, max_value=65535)
        user = st.text_input("Username", value=config.get('user', ''), placeholder="root")

    with col2:
        password = st.text_input("Password", value=config.get('password', ''), type="password")
        database = st.text_input("Database Name", value=config.get('database', ''), placeholder="my_database")

    # Update session state
    st.session_state['mariadb_config'] = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }

    if st.button("Save MariaDB Configuration", type="primary"):
        save_app_config()
        st.success("MariaDB configuration saved successfully!")
        st.toast("Configuration saved to config.json", icon="💾")

    # Placeholder for test connection logic
    if st.button("Test Connection (Demo)"):
        st.info("Connection testing is currently a placeholder. Ensure 'mysql-connector-python' is installed to implement actual connectivity.")
        if host and user and database:
            st.write(f"Connecting to {user}@{host}:{port}/{database}...")
            # Simulate success
            st.success("Connection parameters look valid (UI test only).")
        else:
            st.error("Please fill in Host, Username, and Database name.")
