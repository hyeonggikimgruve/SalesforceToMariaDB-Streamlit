import streamlit as st
from .config_manager import save_app_config

def render_schedule_tab():
    if not st.session_state['is_connected']:
        st.warning("🔒 Please login in the 'Connection' tab to access schedule settings.")
    else:
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
            
            if st.button("💾 Save Schedule", type="primary"):
                save_app_config()
                st.success("Schedule saved!")
                
        with col_sch2:
            st.info(f"""
            **Current Schedule Status:**
            - Active: {'✅ Yes' if st.session_state['schedule_config']['is_active'] else '❌ No'}
            - Frequency: {st.session_state['schedule_config']['frequency']}
            - Next Run: (Calculated based on timezone)
            """)
            
            st.warning("Heroku Free/Eco Dynos sleep after 30 mins of inactivity. For reliable scheduling, use 'Heroku Scheduler' add-on or a dedicated worker dyno.")
