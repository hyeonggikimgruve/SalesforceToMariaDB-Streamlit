import streamlit as st
from .config_manager import save_app_config

def render_load_tab():
    st.subheader("🚀 Data Load Order Settings")
    st.markdown("데이터를 로드할 순서를 설정합니다. (예: Account -> Case -> Opportunity)")

    etl_config = st.session_state.get('etl_config', {})
    mappings = etl_config.get('mappings', [])
    transformations = etl_config.get('transformations', {})

    # Only include objects that have a target table assigned in the Transform tab
    objects_to_load = [
        obj['object'] for obj in mappings 
        if obj['object'] in transformations and transformations[obj['object']].get('target_table')
    ]

    if not objects_to_load:
        st.warning("⚠️ No valid target mappings found. Please configure **Target Tables** in the **'Transform'** tab first.")
        return

    # Initialize load_order if empty or if objects changed
    current_load_order = etl_config.get('load_order', [])
    
    # Filter: Keep only objects that are currently valid to load
    current_load_order = [obj for obj in current_load_order if obj in objects_to_load]
    
    # Add: New objects that are now valid but not yet in the order list
    for obj in objects_to_load:
        if obj not in current_load_order:
            current_load_order.append(obj)
            
    st.session_state['etl_config']['load_order'] = current_load_order

    st.info("아래 목록에서 화살표 버튼을 사용하여 로드 순서를 조정하고, 각 개체별 적재 방식을 설정하세요.")

    # Reorder and Strategy UI
    for i, obj_name in enumerate(current_load_order):
        with st.container(border=True):
            col_order, col_info, col_strategy, col_options = st.columns([0.1, 0.3, 0.3, 0.3])
            
            with col_order:
                st.write(f"### {i+1}")
                if st.button("🔼", key=f"up_{obj_name}_{i}", disabled=(i == 0), use_container_width=True):
                    current_load_order[i], current_load_order[i-1] = current_load_order[i-1], current_load_order[i]
                    st.session_state['etl_config']['load_order'] = current_load_order
                    st.rerun()
                if st.button("🔽", key=f"down_{obj_name}_{i}", disabled=(i == len(current_load_order)-1), use_container_width=True):
                    current_load_order[i], current_load_order[i+1] = current_load_order[i+1], current_load_order[i]
                    st.session_state['etl_config']['load_order'] = current_load_order
                    st.rerun()
            
            with col_info:
                target_table = transformations[obj_name].get('target_table', 'Unknown')
                st.markdown(f"**Source:** `{obj_name}`")
                st.markdown(f"**Target:** `{target_table}`")
                field_count = len([v for v in transformations[obj_name].get('field_map', {}).values() if v])
                st.caption(f"📍 {field_count} fields mapped")

            with col_strategy:
                strategies = ["INSERT", "BULK LOAD / COPY", "MERGE (UPSERT)", "OVERWRITE"]
                current_strategy = transformations[obj_name].get('load_strategy', "INSERT")
                if current_strategy not in strategies: current_strategy = "INSERT"
                
                new_strategy = st.selectbox(
                    "적재 방식 (Strategy)",
                    options=strategies,
                    index=strategies.index(current_strategy),
                    key=f"strat_{obj_name}"
                )
                transformations[obj_name]['load_strategy'] = new_strategy

            with col_options:
                if new_strategy == "MERGE (UPSERT)":
                    # Get list of target columns that are mapped
                    field_map = transformations[obj_name].get('field_map', {})
                    target_columns = sorted(list(set([v for v in field_map.values() if v])))
                    
                    if not target_columns:
                        st.error("❌ No mapped fields found. Please map fields in the 'Transform' tab.")
                        transformations[obj_name]['match_key'] = None
                    else:
                        current_match_key = transformations[obj_name].get('match_key', "")
                        
                        match_key = st.selectbox(
                            "매칭 키 (Match Key)",
                            options=target_columns,
                            index=target_columns.index(current_match_key) if current_match_key in target_columns else 0,
                            key=f"match_{obj_name}",
                            help="UPSERT 수행 시 중복 체크의 기준이 되는 컬럼을 선택하세요."
                        )
                        transformations[obj_name]['match_key'] = match_key
                elif new_strategy == "BULK LOAD / COPY":
                    st.info("🚀 High-speed loading enabled.")
                elif new_strategy == "OVERWRITE":
                    st.warning("⚠️ Truncates table before load.")
                else:
                    st.caption("Standard row-by-row insertion.")

    st.divider()

    # Global Load Settings
    st.subheader("⚙️ Global Load Settings")
    col_batch, _ = st.columns([0.3, 0.7])
    with col_batch:
        batch_size = st.number_input(
            "Batch Size",
            min_value=1,
            max_value=10000,
            value=etl_config.get('batch_size', 1000),
            step=100,
            help="한 번에 처리할 레코드 수를 설정합니다. (MariaDB 성능에 영향)"
        )
        st.session_state['etl_config']['batch_size'] = batch_size

    # Visual representation of the flow
    st.markdown("### 🔄 Planned Execution Flow")
    flow_items = []
    for obj in current_load_order:
        strat = transformations[obj].get('load_strategy', 'INSERT')
        flow_items.append(f"**{obj}** ({strat})")
    
    flow_str = " ➡️ ".join(flow_items)
    st.info(flow_str)

    # Save Action
    if st.button("💾 Save Load Settings", type="primary", use_container_width=True):
        st.session_state['etl_config']['load_order'] = current_load_order
        st.session_state['etl_config']['transformations'] = transformations
        save_app_config()
        st.success("Load settings and strategies saved successfully!")
