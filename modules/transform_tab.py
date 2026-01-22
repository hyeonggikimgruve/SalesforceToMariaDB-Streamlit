import streamlit as st
import json
from .config_manager import save_app_config

# Constants for Transformations
TRANSFORM_TYPES = ["None", "To Number", "To Date", "To DateTime", "To Boolean", "Enum Mapping"]
DATE_FORMATS = ["YYYY-MM-DD", "YYYYMMDD", "YYYY/MM/DD", "ISO8601", "Manual"]
TIMEZONES = ["UTC", "Asia/Seoul", "US/Eastern", "US/Pacific", "Europe/London"]

# Dummy MariaDB Schema
MARIADB_SCHEMA = {
    "stg_sf_account": ["id", "sf_id", "name", "type", "industry", "phone", "website", "created_at"],
    "stg_sf_contact": ["id", "sf_id", "first_name", "last_name", "email", "phone", "account_id", "created_at"],
    "stg_sf_opportunity": ["id", "sf_id", "name", "amount", "stage", "close_date", "account_id", "created_at"],
    "stg_sf_lead": ["id", "sf_id", "name", "company", "email", "status", "source", "created_at"],
    "stg_sf_case": ["id", "sf_id", "subject", "status", "priority", "description", "account_id", "created_at"],
    "stg_sf_user": ["id", "sf_id", "username", "email", "full_name", "is_active", "profile_id", "created_at"]
}

def render_transform_tab():
    st.subheader("🛠️ Data Transformation & Mapping")
    st.markdown("Salesforce의 원본 데이터 필드를 MariaDB(Target)의 테이블 및 컬럼과 매핑하고 데이터 변환 규칙을 설정합니다.")

    if not st.session_state.get('etl_config', {}).get('mappings'):
        st.warning("⚠️ No Extract settings found. Please configure objects and fields in the **'Extract Settings'** tab first.")
        return

    mappings = st.session_state['etl_config']['mappings']
    transformations = st.session_state['etl_config'].get('transformations', {})

    # MariaDB 테이블 목록
    target_tables = list(MARIADB_SCHEMA.keys())

    for idx, mapping in enumerate(mappings):
        obj_name = mapping['object']
        fields = mapping['fields']
        
        with st.expander(f"📦 Mapping: {obj_name} ({len(fields)} fields)", expanded=True):
            col_target_top = st.columns([2, 3])
            
            # 1. Target Table Selection
            current_target = transformations.get(obj_name, {}).get('target_table', None)
            target_idx = target_tables.index(current_target) if current_target in target_tables else None
            
            with col_target_top[0]:
                selected_target = st.selectbox(
                    f"Select Target Table (MariaDB)",
                    options=target_tables,
                    index=target_idx,
                    key=f"target_table_{obj_name}_{idx}",
                    placeholder="Choose a MariaDB Table..."
                )
            
            if not selected_target:
                st.info("Please select a target table to begin field mapping.")
                continue

            # Update state if target table changed
            if obj_name not in transformations:
                transformations[obj_name] = {'target_table': selected_target, 'field_map': {}, 'field_configs': {}}
            elif transformations[obj_name]['target_table'] != selected_target:
                transformations[obj_name]['target_table'] = selected_target
                # Reset field map if table changes? (Decided to keep and let user fix)
            
            if 'field_configs' not in transformations[obj_name]:
                transformations[obj_name]['field_configs'] = {}

            st.divider()
            
            # 2. Field Mapping Header
            h_col1, h_col2, h_col3, h_col4 = st.columns([1.5, 1.5, 1.5, 0.5])
            h_col1.markdown("**SF Field (Source)**")
            h_col2.markdown("**MariaDB Column (Target)**")
            h_col3.markdown("**Transformation**")
            h_col4.markdown("**Status**")

            field_map = transformations[obj_name].get('field_map', {})
            field_configs = transformations[obj_name].get('field_configs', {})
            target_columns = MARIADB_SCHEMA[selected_target]
            
            # 3. Field Mapping Rows
            for f_api in fields:
                r_col1, r_col2, r_col3, r_col4 = st.columns([1.5, 1.5, 1.5, 0.5])
                
                with r_col1:
                    st.code(f_api, language=None)
                
                with r_col2:
                    current_mapped_col = field_map.get(f_api, None)
                    col_idx = target_columns.index(current_mapped_col) if current_mapped_col in target_columns else None
                    
                    selected_col = st.selectbox(
                        f"Map {f_api}",
                        options=["-- Skip --"] + target_columns,
                        index=(col_idx + 1) if col_idx is not None else 0,
                        key=f"map_{obj_name}_{f_api}_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    if selected_col == "-- Skip --":
                        field_map[f_api] = None
                    else:
                        field_map[f_api] = selected_col
                
                with r_col3:
                    current_cfg = field_configs.get(f_api, {"type": "None"})
                    t_idx = TRANSFORM_TYPES.index(current_cfg['type']) if current_cfg['type'] in TRANSFORM_TYPES else 0
                    
                    selected_transform = st.selectbox(
                        f"Transform {f_api}",
                        options=TRANSFORM_TYPES,
                        index=t_idx,
                        key=f"trans_type_{obj_name}_{f_api}_{idx}",
                        label_visibility="collapsed"
                    )
                    
                    if selected_transform != current_cfg['type']:
                        current_cfg = {"type": selected_transform}
                        field_configs[f_api] = current_cfg
                
                with r_col4:
                    if field_map[f_api]:
                        st.success("✅", icon="✔️")
                    else:
                        st.info("⏸️")

                # 4. Advanced Transformation Configuration
                if field_map[f_api] and selected_transform != "None":
                    with st.container(border=True):
                        st.caption(f"⚙️ Config for {f_api} → {field_map[f_api]} ({selected_transform})")
                        c1, c2, c3 = st.columns(3)
                        
                        if selected_transform in ["To Date", "To DateTime"]:
                            with c1:
                                current_cfg['src_fmt'] = st.selectbox("Source Format", DATE_FORMATS, 
                                                                    index=DATE_FORMATS.index(current_cfg.get('src_fmt', 'ISO8601')) if current_cfg.get('src_fmt') in DATE_FORMATS else 3, 
                                                                    key=f"src_fmt_{obj_name}_{f_api}_{idx}")
                            with c2:
                                current_cfg['tgt_fmt'] = st.selectbox("Target Format", DATE_FORMATS, 
                                                                    index=DATE_FORMATS.index(current_cfg.get('tgt_fmt', 'YYYY-MM-DD')) if current_cfg.get('tgt_fmt') in DATE_FORMATS else 0, 
                                                                    key=f"tgt_fmt_{obj_name}_{f_api}_{idx}")
                            with c3:
                                current_cfg['tz_convert'] = st.checkbox("Timezone Convert", value=current_cfg.get('tz_convert', False), key=f"tz_chk_{obj_name}_{f_api}_{idx}")
                                if current_cfg['tz_convert']:
                                    cc1, cc2 = st.columns(2)
                                    with cc1:
                                        current_cfg['src_tz'] = st.selectbox("From", TIMEZONES, index=TIMEZONES.index(current_cfg.get('src_tz', 'UTC')), key=f"src_tz_{obj_name}_{f_api}_{idx}")
                                    with cc2:
                                        current_cfg['tgt_tz'] = st.selectbox("To", TIMEZONES, index=TIMEZONES.index(current_cfg.get('tgt_tz', 'Asia/Seoul')), key=f"tgt_tz_{obj_name}_{f_api}_{idx}")
                        
                        elif selected_transform == "To Number":
                            with c1:
                                current_cfg['decimal_places'] = st.number_input("Decimal Places", min_value=0, max_value=10, value=current_cfg.get('decimal_places', 0), key=f"decimal_{obj_name}_{f_api}_{idx}")
                            with c2:
                                current_cfg['handle_null'] = st.selectbox("Null Strategy", ["Zero", "Keep Null", "Default"], index=0, key=f"null_strat_{obj_name}_{f_api}_{idx}")
                        
                        elif selected_transform == "To Boolean":
                            with c1:
                                current_cfg['true_val'] = st.text_input("True Values (CSV)", value=current_cfg.get('true_val', 'true,1,Y,Yes'), key=f"true_val_{obj_name}_{f_api}_{idx}")
                            with c2:
                                current_cfg['false_val'] = st.text_input("False Values (CSV)", value=current_cfg.get('false_val', 'false,0,N,No'), key=f"false_val_{obj_name}_{f_api}_{idx}")
                        
                        elif selected_transform == "Enum Mapping":
                            mapping_str = current_cfg.get('enum_map', '{"SF_Value": "DB_Value"}')
                            current_cfg['enum_map'] = st.text_area("Mapping Table (JSON)", value=mapping_str, key=f"enum_map_{obj_name}_{f_api}_{idx}", help="Enter a JSON object for value-to-value mapping.")
                        
                        field_configs[f_api] = current_cfg

            transformations[obj_name]['field_map'] = field_map
            transformations[obj_name]['field_configs'] = field_configs

    st.divider()
    
    # Save Action
    if st.button("💾 Save Transform Settings", type="primary", use_container_width=True):
        st.session_state['etl_config']['transformations'] = transformations
        save_app_config()
        st.success("Transformation settings saved successfully!")
