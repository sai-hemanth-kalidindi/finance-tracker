import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Finance Instructions & Follow-ups", layout="wide")

st.title("Finance Instructions & Follow-ups")
st.write("Central tracker for finance instructions and tasks.")

# Sample data to make the dashboard functional right away
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Type", "Amount", "Vendor / Customer", "Project", "Description", "Status", "Assignee"
    ])

# Sidebar Data Entry Form
with st.sidebar:
    st.header("➕ Add New Entry")
    with st.form("entry_form"):
        entry_type = st.selectbox("Type", ["Vendor Payment", "Purchase Order"])
        amount = st.number_input("Amount", min_value=0.0, step=100.0)
        vendor = st.text_input("Vendor / Customer")
        project = st.selectbox("Project", ["AEC-7", "V-64", "ID-32", "AD-8"])
        description = st.text_area("Description")
        status = st.selectbox("Status", ["Open", "Done"])
        assignee = st.selectbox("Assignee", ["Financial Operations", "HARSHA DIMMALA", "SC"])
        
        submitted = st.form_submit_button("Save Entry")
        if submitted:
            new_row = {
                "Type": entry_type,
                "Amount": amount,
                "Vendor / Customer": vendor,
                "Project": project,
                "Description": description,
                "Status": status,
                "Assignee": assignee
            }
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Added successfully!")

# Main Dashboard View
st.subheader("Transaction Tracker")
if not st.session_state.data.empty:
    st.dataframe(st.session_state.data, use_container_width=True)
else:
    st.info("No entries yet. Use the sidebar to add your first transaction!")
