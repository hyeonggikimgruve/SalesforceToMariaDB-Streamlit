import streamlit as st
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed
from .config_manager import save_config

def attempt_login(silent=False):
    """Attempts to login with current session state credentials."""
    # Sync widgets to config before login attempt just in case
    
    if not st.session_state['sf_config']['username'] or not st.session_state['sf_config']['password']:
        if not silent: st.error("Please enter Username and Password.")
        return

    container = st.empty()
    if not silent:
        spinner = container.spinner("Connecting to Salesforce...")
    else:
        # Create a dummy context manager for silent mode
        from contextlib import nullcontext
        spinner = nullcontext()

    with spinner:
        try:
            sf = Salesforce(
                username=st.session_state['sf_config']['username'],
                password=st.session_state['sf_config']['password'],
                security_token=st.session_state['sf_config']['security_token'],
                domain=st.session_state['sf_config']['domain']
            )
            st.session_state['sf_client'] = sf
            st.session_state['is_connected'] = True
            
            # Clear cached objects if new login happens
            if 'sf_objects' in st.session_state:
                del st.session_state['sf_objects']
            
            if not silent:
                st.success("Connection Successful!")
            else:
                st.toast("Auto-login successful!", icon="✅")
            
            # Fetch and display Org/User info
            return True

        except SalesforceAuthenticationFailed as e:
            if not silent:
                st.error("Authentication Failed.")
                with st.expander("See Error Details"):
                    st.code(str(e))
            st.session_state['is_connected'] = False
            return False
        except Exception as e:
            if not silent:
                st.error(f"An error occurred: {str(e)}")
            st.session_state['is_connected'] = False
            return False

def render_auth_tab():
    st.subheader("Salesforce Authentication")
    
    if not st.session_state.get('is_connected', False):
        # Login Form
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Username", 
                key="u_username",
                value=st.session_state['sf_config'].get('username', ""),
                placeholder="user@example.com"
            )
            st.text_input(
                "Password", 
                type="password",
                value=st.session_state['sf_config'].get('password', ""),
                key="u_password"
            )
        
        with col2:
            st.text_input(
                "Security Token", 
                type="password",
                value=st.session_state['sf_config'].get('security_token', ""),
                key="u_token",
                help="Salesforce Security Token is required for API access."
            )
            st.selectbox(
                "Environment", 
                options=["login", "test"], 
                index=0 if st.session_state['sf_config'].get('domain') == "login" else 1,
                key="u_domain",
                format_func=lambda x: "Production (login.salesforce.com)" if x == "login" else "Sandbox (test.salesforce.com)"
            )
        
        # Sync widgets back to sf_config
        st.session_state['sf_config']['username'] = st.session_state['u_username']
        st.session_state['sf_config']['password'] = st.session_state['u_password']
        st.session_state['sf_config']['security_token'] = st.session_state['u_token']
        st.session_state['sf_config']['domain'] = st.session_state['u_domain']

        remember_me = st.checkbox("Remember Me (Save credentials to config.json)", value=True)

        if st.button("Login & Connect", type="primary"):
            if attempt_login(silent=False):
                if remember_me:
                    # Save only auth config for now
                    save_data = {
                        "sf_config": st.session_state['sf_config']
                    }
                    save_config(save_data)
                    st.toast("Credentials saved to config.json", icon="💾")
                st.rerun()
    else:
        # Connected State
        try:
            sf = st.session_state['sf_client']
            # Cache info in session state to avoid re-querying on every rerun
            if 'org_info' not in st.session_state:
                st.session_state['org_info'] = sf.query("SELECT Id, Name, OrganizationType, IsSandbox FROM Organization")['records'][0]
                del st.session_state['org_info']['attributes']
                
                user_query = f"SELECT Id, Name, Profile.Name, Email FROM User WHERE Username = '{st.session_state['sf_config']['username']}'"
                st.session_state['user_info'] = sf.query(user_query)['records'][0]
                del st.session_state['user_info']['attributes']

            org_info = st.session_state['org_info']
            user_info = st.session_state['user_info']
            
            st.success("✅ **Connected to Salesforce**")
            
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.markdown(f"**🏢 Organization:** {org_info['Name']}")
                st.caption(f"Org ID: {org_info['Id']} | Type: {org_info['OrganizationType']} | Sandbox: {org_info['IsSandbox']}")
            
            with info_col2:
                st.markdown(f"**👤 User:** {user_info['Name']}")
                st.caption(f"Profile: {user_info['Profile']['Name']} | Email: {user_info['Email']}")

        except Exception as info_err:
            st.warning(f"Connected, but failed to fetch details: {info_err}")

        if st.button("Logout", type="secondary"):
            st.session_state['sf_client'] = None
            st.session_state['is_connected'] = False
            if 'sf_objects' in st.session_state:
                del st.session_state['sf_objects']
            if 'org_info' in st.session_state:
                del st.session_state['org_info']
            if 'user_info' in st.session_state:
                del st.session_state['user_info']
            st.rerun()
