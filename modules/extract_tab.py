import streamlit as st
import pandas as pd
from .config_manager import save_app_config

def render_extract_tab():
    if not st.session_state.get('is_connected'):
        st.warning("🔒 Please login in the 'Connection' tab to access these settings.")
        return

    st.subheader("Extract Configurations")

    # Ensure mappings list exists
    if 'mappings' not in st.session_state['etl_config']:
        st.session_state['etl_config']['mappings'] = []
    
    mappings = st.session_state['etl_config']['mappings']
    sf = st.session_state['sf_client']

    # --- Manage Editor State ---
    if 'extract_editor_mode' not in st.session_state:
        st.session_state['extract_editor_mode'] = 'add' # 'add' or 'edit'
        st.session_state['extract_editor_idx'] = None

    # --- LIST VIEW ---
    with st.expander("📂 Saved Mappings", expanded=True):
        if not mappings:
            st.info("No mappings saved yet. Add one below.")
        else:
            for i, m in enumerate(mappings):
                col1, col2, col3 = st.columns([6, 1, 1])
                with col1:
                    st.write(f"**{i+1}. {m['object']}** ({len(m['fields'])} fields)")
                with col2:
                    if st.button("✏️", key=f"edit_map_{i}", help="Edit"):
                        st.session_state['extract_editor_mode'] = 'edit'
                        st.session_state['extract_editor_idx'] = i
                        st.session_state['_populate_editor'] = True 
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"del_map_{i}", help="Delete"):
                        mappings.pop(i)
                        save_app_config()
                        # If we deleted the one being edited, reset editor
                        if (st.session_state['extract_editor_mode'] == 'edit' and 
                            st.session_state['extract_editor_idx'] == i):
                            st.session_state['extract_editor_mode'] = 'add'
                            st.session_state['extract_editor_idx'] = None
                            # Clear form
                            if 'editor_selected_obj_display' in st.session_state:
                                del st.session_state['editor_selected_obj_display']
                            if 'editor_selected_fields_display' in st.session_state:
                                del st.session_state['editor_selected_fields_display']
                        st.rerun()

    st.divider()

    # --- EDITOR SECTION ---
    mode = st.session_state['extract_editor_mode']
    header_text = "➕ Add New Mapping" if mode == 'add' else f"✏️ Edit Mapping #{st.session_state['extract_editor_idx']+1}"
    st.subheader(header_text)

    # 1. Fetch Objects
    if 'sf_objects_list' not in st.session_state:
        with st.spinner("Fetching Salesforce Objects..."):
            try:
                query = """
                    SELECT QualifiedApiName, Label
                    FROM EntityDefinition
                    WHERE IsApexTriggerable = true
                      AND IsCustomizable = true
                      AND IsProcessEnabled = true
                    ORDER BY Label
                """
                results = sf.query_all(query)
                st.session_state['sf_objects_list'] = [
                    {'label': rec['Label'], 'name': rec['QualifiedApiName']} 
                    for rec in results['records']
                ]
            except Exception as e:
                st.error(f"Failed to fetch objects: {e}")
                st.session_state['sf_objects_list'] = []

    obj_map = {f"{x['label']} ({x['name']})": x['name'] for x in st.session_state['sf_objects_list']}
    obj_options = list(obj_map.keys())

    # --- Population Logic (Object) ---
    if st.session_state.get('_populate_editor'):
        if mode == 'edit':
            idx = st.session_state['extract_editor_idx']
            if 0 <= idx < len(mappings):
                m = mappings[idx]
                found_disp = next((k for k, v in obj_map.items() if v == m['object']), None)
                if found_disp:
                    st.session_state['editor_selected_obj_display'] = found_disp
                    st.session_state['_need_field_sync'] = True
        st.session_state['_populate_editor'] = False

    # Object Selector
    selected_obj_display = st.selectbox(
        "Select Object",
        options=obj_options,
        key='editor_selected_obj_display',
        index=None,
        placeholder="Choose an object..."
    )

    selected_obj_api = obj_map.get(selected_obj_display) if selected_obj_display else None
    selected_fields_api = []

    if selected_obj_api:
        # Fetch Fields
        cache_key = f"meta_fields_{selected_obj_api}"
        if cache_key in st.session_state:
            fields_data = st.session_state[cache_key]
        else:
            try:
                with st.spinner(f"Fetching fields for {selected_obj_api}..."):
                    obj_desc = getattr(sf, selected_obj_api).describe()
                    fields_data = [{'label': f['label'], 'name': f['name']} for f in obj_desc['fields']]
                    fields_data.sort(key=lambda x: x['name'])
                    st.session_state[cache_key] = fields_data
            except Exception as e:
                st.error(f"Error fetching fields: {e}")
                fields_data = []

        field_map = {f"{f['name']} ({f['label']})": f['name'] for f in fields_data}
        field_options = list(field_map.keys())

        # --- Population Logic (Fields) ---
        if st.session_state.get('_need_field_sync'):
            if mode == 'edit':
                idx = st.session_state['extract_editor_idx']
                if 0 <= idx < len(mappings):
                    m = mappings[idx]
                    disp_fields = [k for k, v in field_map.items() if v in m['fields']]
                    st.session_state['editor_selected_fields_display'] = disp_fields
            st.session_state['_need_field_sync'] = False

        selected_fields_display = st.multiselect(
            "Select Fields",
            options=field_options,
            key='editor_selected_fields_display',
            placeholder="Select one or more fields"
        )
        selected_fields_api = [field_map[d] for d in selected_fields_display]

    else:
        st.info("👈 Select an object to choose fields.")

    # --- Actions ---
    col_actions = st.columns([1, 1, 2])
    
    with col_actions[0]:
        btn_label = "Update Mapping" if mode == 'edit' else "Add Mapping"
        if st.button(btn_label, use_container_width=True, type="primary"):
            if not selected_obj_api or not selected_fields_api:
                st.error("Please select an object and at least one field.")
            else:
                new_mapping = {'object': selected_obj_api, 'fields': selected_fields_api}
                
                if mode == 'edit':
                    mappings[st.session_state['extract_editor_idx']] = new_mapping
                    st.success("Mapping updated!")
                    st.session_state['extract_editor_mode'] = 'add'
                    st.session_state['extract_editor_idx'] = None
                    # Clear inputs
                    if 'editor_selected_obj_display' in st.session_state:
                        del st.session_state['editor_selected_obj_display']
                    if 'editor_selected_fields_display' in st.session_state:
                         del st.session_state['editor_selected_fields_display']
                else:
                    mappings.append(new_mapping)
                    st.success("Mapping added!")
                    if 'editor_selected_fields_display' in st.session_state:
                        del st.session_state['editor_selected_fields_display']
                    # Keep object selected for convenience? No, clear to indicate success.
                    # Actually users might want to add multiple mappings for same object? 
                    # Let's clear for now to follow standard 'form submission' feel.
                    if 'editor_selected_obj_display' in st.session_state:
                         del st.session_state['editor_selected_obj_display']

                save_app_config()
                st.rerun()

    with col_actions[1]:
        if mode == 'edit':
            if st.button("Cancel Edit", use_container_width=True):
                st.session_state['extract_editor_mode'] = 'add'
                st.session_state['extract_editor_idx'] = None
                if 'editor_selected_obj_display' in st.session_state:
                    del st.session_state['editor_selected_obj_display']
                if 'editor_selected_fields_display' in st.session_state:
                    del st.session_state['editor_selected_fields_display']
                st.rerun()
        else:
             if st.button("Clear Form", use_container_width=True):
                if 'editor_selected_obj_display' in st.session_state:
                    del st.session_state['editor_selected_obj_display']
                if 'editor_selected_fields_display' in st.session_state:
                    del st.session_state['editor_selected_fields_display']
                st.rerun()

    # --- Preview ---
    if selected_obj_api and selected_fields_api:
        if st.button("🔍 Preview Data (Current Selection)", type="secondary"):
            try:
                q = f"SELECT {','.join(selected_fields_api)} FROM {selected_obj_api} LIMIT 5"
                with st.spinner("Querying..."):
                    res = sf.query(q)
                    recs = [ {k:v for k,v in r.items() if k!='attributes'} for r in res['records'] ]
                    if recs:
                        st.dataframe(pd.DataFrame(recs))
                    else:
                        st.info("No records found.")
            except Exception as e:
                st.error(f"Preview failed: {e}")