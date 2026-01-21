import streamlit as st
import pandas as pd

def render_extract_tab():
    if not st.session_state['is_connected']:
        st.warning("🔒 Please login in the 'Connection' tab to access these settings.")
    else:
        st.subheader("Object & Fields Selection")

        sf = st.session_state['sf_client']

        # 1. Object 선택 (Dynamic)
        if 'sf_objects_list' not in st.session_state:
            with st.spinner("Fetching Salesforce Objects..."):
                try:
                    # Use EntityDefinition to filter objects
                    # Conditions provided: IsApexTriggerable, IsCustomizable, IsProcessEnabled
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
        
        # Create a mapping for display
        obj_map = {f"{x['label']} ({x['name']})": x['name'] for x in st.session_state['sf_objects_list']}
        obj_display_options = list(obj_map.keys())

        # Callback to handle selection change
        def on_object_change():
            selected_display = st.session_state._object_selector
            if selected_display in obj_map:
                new_obj = obj_map[selected_display]
                # Update config only if changed
                if new_obj != st.session_state['etl_config']['selected_object']:
                    st.session_state['etl_config']['selected_object'] = new_obj
                    st.session_state['etl_config']['selected_fields'] = [] # Reset fields

        # Determine current index
        current_obj_name = st.session_state['etl_config']['selected_object']
        current_index = 0
        if current_obj_name:
            # Find the display string that matches the current name
            match = next((k for k, v in obj_map.items() if v == current_obj_name), None)
            if match:
                current_index = obj_display_options.index(match)

        st.selectbox(
            "Select Salesforce Object", 
            options=obj_display_options,
            index=current_index,
            key='_object_selector',
            on_change=on_object_change,
            placeholder="Choose an object..."
        )
        
        st.divider()
        
        # 2. Field 선택 (Dynamic)
        selected_obj = st.session_state['etl_config']['selected_object']
        
        if selected_obj:
            field_map = {}
            try:
                # We intentionally don't cache fields in session_state globally to avoid memory bloat,
                # but we could cache per object if needed. For now, fetch on selection.
                with st.spinner(f"Fetching fields for {selected_obj}..."):
                    # Object Describe
                    obj_desc = getattr(sf, selected_obj).describe()
                    fields_data = [
                        {'label': f['label'], 'name': f['name']} 
                        for f in obj_desc['fields']
                    ]
                    fields_data.sort(key=lambda x: x['name']) # Sort by API Name usually better for devs, or Label for users.
                    
                    field_map = {f"{f['name']} ({f['label']})": f['name'] for f in fields_data}
            
            except Exception as e:
                st.error(f"Could not describe object {selected_obj}: {e}")
            
            field_display_options = list(field_map.keys())
            
            # Map currently selected API names back to display names
            default_display = []
            for f_name in st.session_state['etl_config']['selected_fields']:
                # Find key for this value
                match = next((k for k, v in field_map.items() if v == f_name), None)
                if match:
                    default_display.append(match)

            selected_fds_display = st.multiselect(
                "Select Fields to Extract",
                options=field_display_options,
                default=default_display,
                placeholder="Select one or more fields",
                key='_field_selector',
                on_change=lambda: st.session_state['etl_config'].update({
                    'selected_fields': [field_map[d] for d in st.session_state._field_selector]
                })
            )
            
            # Preview Logic
            if st.button("Preview Data (Top 5 Rows)"):
                if not st.session_state['etl_config']['selected_fields']:
                    st.warning("Select at least one field.")
                else:
                    try:
                        sf = st.session_state['sf_client']
                        fields_to_query = st.session_state['etl_config']['selected_fields']
                        q = f"SELECT {','.join(fields_to_query)} FROM {selected_obj} LIMIT 5"
                        
                        with st.spinner("Executing SOQL..."):
                            data = sf.query(q)
                            records = data.get('records', [])
                            
                            if records:
                                # Clean up attributes
                                clean_records = []
                                for r in records:
                                    r_clean = {k: v for k, v in r.items() if k != 'attributes'}
                                    clean_records.append(r_clean)
                                
                                df = pd.DataFrame(clean_records)
                                st.dataframe(df, use_container_width=True)
                                st.caption(f"Showing 5 of {data.get('totalSize', '?')} records")
                            else:
                                st.info("No records found.")
                    except Exception as e:
                        st.error(f"Query failed: {e}")
