from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Finance Instructions & Follow-ups", layout="wide"
)

# Create local folders for uploaded files if they don't exist
os.makedirs("uploads/descriptions", exist_ok=True)
os.makedirs("uploads/receipts", exist_ok=True)

st.title("Finance Instructions & Follow-ups")
st.write(
    "Central tracker for finance instructions, tracking vendor payments and"
    " tasks."
)

# Initialize session state dataframe if it doesn't exist
if "data" not in st.session_state:
  st.session_state.data = pd.DataFrame(
      columns=[
          "Type & Vendor/Customer",
          "Amount",
          "Description Text",
          "Description File (PDF)",
          "Project",
          "Status",
          "Payment Receipt (PDF)",
          "Due Date",
          "Admin Creating",
          "Created Time",
          "Last Edited",
          "Assignee",
      ]
  )

# --- SIDEBAR: ADD NEW ENTRY FORM ---
with st.sidebar:
  st.header("➕ Add New Instruction")
  with st.form("entry_form", clear_on_submit=True):
    type_vendor = st.text_input(
        "1. Type & Vendor/Customer Name",
        placeholder="e.g., Vendor Payment - UDL Building",
    )
    amount = st.number_input("2. Amount", min_value=0.0, step=100.0)

    # 3. Description: Text input OR PDF upload option
    st.markdown("---")
    st.markdown("**3. Description Details**")
    description_text = st.text_area(
        "Description Text", placeholder="Details of work or material..."
    )
    description_file = st.file_uploader(
        "Upload Description File (PDF/Doc)", type=["pdf", "png", "jpg"], key="desc_file"
    )

    st.markdown("---")
    project = st.text_input(
        "4. Project", placeholder="e.g., AEC-7 or V-64"
    )
    status = st.selectbox("5. Status", ["To be done", "In process", "Done"])
    receipt_file = st.file_uploader(
        "6. Files (Payment Receipt in PDF)", type=["pdf", "png", "jpg"], key="receipt_file"
    )
    due_date = st.date_input("7. Due Date")
    admin_name = st.text_input("8. Admin Name Creating", placeholder="e.g., Sai")
    assignee = st.text_input("11. Assign (Reviewer Name)", placeholder="e.g., Harsha")

    submitted = st.form_submit_button("Save Entry", use_container_width=True)

    if submitted:
      # Handle Description PDF upload
      desc_file_name = "No File"
      if description_file is not None:
        desc_file_name = description_file.name
        with open(os.path.join("uploads/descriptions", desc_file_name), "wb") as f:
          f.write(description_file.getbuffer())

      # Handle Payment Receipt PDF upload
      receipt_file_name = "No File"
      if receipt_file is not None:
        receipt_file_name = receipt_file.name
        with open(os.path.join("uploads/receipts", receipt_file_name), "wb") as f:
          f.write(receipt_file.getbuffer())

      current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

      new_row = {
          "Type & Vendor/Customer": type_vendor,
          "Amount": amount,
          "Description Text": description_text,
          "Description File (PDF)": desc_file_name,
          "Project": project,
          "Status": status,
          "Payment Receipt (PDF)": receipt_file_name,
          "Due Date": str(due_date),
          "Admin Creating": admin_name,
          "Created Time": current_time,
          "Last Edited": current_time,
          "Assignee": assignee,
      }

      # Append to dataframe
      st.session_state.data = pd.concat(
          [st.session_state.data, pd.DataFrame([new_row])], ignore_index=True
      )
      st.success("Entry added successfully!")
      st.rerun()

# --- MAIN DASHBOARD VIEW & EDITING ---
st.subheader("📋 Finance Tracker Dashboard")

if not st.session_state.data.empty:
  # Display interactive table with editing enabled
  edited_df = st.data_editor(
      st.session_state.data,
      use_container_width=True,
      num_rows="dynamic",
      key="tracker_editor",
  )

  # Check if user edited the table, and update the 'Last Edited' timestamp automatically
  if not edited_df.equals(st.session_state.data):
    current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    edited_df["Last Edited"] = current_time
    st.session_state.data = edited_df
    st.rerun()

  # Quick Summary Metrics
  st.divider()
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Entries", len(st.session_state.data))
  col2.metric(
      "To Be Done",
      len(st.session_state.data[st.session_state.data["Status"] == "To be done"]),
  )
  col3.metric(
      "In Process",
      len(
          st.session_state.data[st.session_state.data["Status"] == "In process"]
      ),
  )
  col4.metric(
      "Done", len(st.session_state.data[st.session_state.data["Status"] == "Done"])
  )

else:
  st.info(
      "No entries found yet. Use the sidebar form on the left to add your first"
      " finance instruction!"
  )
