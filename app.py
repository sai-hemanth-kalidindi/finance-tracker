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

    st.markdown("---")
    st.markdown("**3. Description Details**")
    description_text = st.text_area(
        "Description Text", placeholder="Details of work or material..."
    )
    description_file = st.file_uploader(
        "Upload Description File (PDF/Doc)",
        type=["pdf", "png", "jpg"],
        key="desc_file",
    )

    st.markdown("---")
    project = st.text_input("4. Project", placeholder="e.g., AEC-7 or V-64")
    status = st.selectbox("5. Status", ["To be done", "In process", "Done"])
    receipt_file = st.file_uploader(
        "6. Files (Payment Receipt in PDF)",
        type=["pdf", "png", "jpg"],
        key="receipt_file",
    )
    due_date = st.date_input("7. Due Date")
    admin_name = st.text_input("8. Admin Name Creating", placeholder="e.g., Sai")
    assignee = st.text_input(
        "11. Assign (Reviewer Name)", placeholder="e.g., Harsha"
    )

    submitted = st.form_submit_button("Save Entry", use_container_width=True)

    if submitted:
      desc_file_name = "No File"
      if description_file is not None:
        desc_file_name = description_file.name
        with open(
            os.path.join("uploads/descriptions", desc_file_name), "wb"
        ) as f:
          f.write(description_file.getbuffer())

      receipt_file_name = "No File"
      if receipt_file is not None:
        receipt_file_name = receipt_file.name
        with open(
            os.path.join("uploads/receipts", receipt_file_name), "wb"
        ) as f:
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

      st.session_state.data = pd.concat(
          [st.session_state.data, pd.DataFrame([new_row])], ignore_index=True
      )
      st.success("Entry added successfully!")
      st.rerun()

# --- MAIN DASHBOARD VIEW ---
st.subheader("📋 Finance Tracker Dashboard")

if not st.session_state.data.empty:
  st.dataframe(st.session_state.data, use_container_width=True)

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Entries", len(st.session_state.data))
  col2.metric(
      "To Be Done",
      len(
          st.session_state.data[st.session_state.data["Status"] == "To be done"]
      ),
  )
  col3.metric(
      "In Process",
      len(
          st.session_state.data[st.session_state.data["Status"] == "In process"]
      ),
  )
  col4.metric(
      "Done",
      len(st.session_state.data[st.session_state.data["Status"] == "Done"]),
  )

  st.divider()

  # --- EDIT EXISTING ENTRY SECTION ---
  st.subheader("✏️ Edit an Existing Entry / Upload Payment Receipt")

  row_options = []
  for idx, row in st.session_state.data.iterrows():
    option_label = f"Row {idx}: {row['Type & Vendor/Customer']} | Project: {row['Project']} | Amount: {row['Amount']}"
    row_options.append(option_label)

  selected_option = st.selectbox("Select Entry to Edit:", row_options)
  selected_idx = int(selected_option.split(":")[0].replace("Row ", ""))
  current_row = st.session_state.data.loc[selected_idx]

  with st.form("edit_entry_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
      edit_type_vendor = st.text_input(
          "Type & Vendor/Customer",
          value=current_row["Type & Vendor/Customer"],
      )
      edit_amount = st.number_input(
          "Amount", value=float(current_row["Amount"]), min_value=0.0, step=100.0
      )
      edit_project = st.text_input("Project", value=current_row["Project"])

    with c2:
      status_list = ["To be done", "In process", "Done"]
      current_status_idx = (
          status_list.index(current_row["Status"])
          if current_row["Status"] in status_list
          else 0
      )
      edit_status = st.selectbox("Status", status_list, index=current_status_idx)

      try:
        parsed_date = datetime.strptime(
            str(current_row["Due Date"]), "%Y-%m-%d"
        ).date()
      except Exception:
        parsed_date = datetime.today().date()
      edit_due_date = st.date_input("Due Date", value=parsed_date)

      edit_assignee = st.text_input(
          "Assign (Reviewer Name)", value=current_row["Assignee"]
      )

    with c3:
      edit_desc_text = st.text_area(
          "Description Text", value=current_row["Description Text"]
      )
      st.caption(
          f"Current Payment Receipt: **{current_row['Payment Receipt (PDF)']}**"
      )
      new_receipt_file = st.file_uploader(
          "Upload / Replace Payment Receipt (PDF)",
          type=["pdf", "png", "jpg"],
          key="edit_receipt",
      )
      st.caption(
          f"Current Description File: **{current_row['Description File (PDF)']}**"
      )
      new_desc_file = st.file_uploader(
          "Upload / Replace Description File (PDF)",
          type=["pdf", "png", "jpg"],
          key="edit_desc",
      )

    update_submitted = st.form_submit_button(
        "Update Entry", use_container_width=True
    )

    if update_submitted:
      updated_receipt_name = current_row["Payment Receipt (PDF)"]
      if new_receipt_file is not None:
        updated_receipt_name = new_receipt_file.name
        with open(
            os.path.join("uploads/receipts", updated_receipt_name), "wb"
        ) as f:
          f.write(new_receipt_file.getbuffer())

      updated_desc_name = current_row["Description File (PDF)"]
      if new_desc_file is not None:
        updated_desc_name = new_desc_file.name
        with open(
            os.path.join("uploads/descriptions", updated_desc_name), "wb"
        ) as f:
          f.write(new_desc_file.getbuffer())

      st.session_state.data.at[selected_idx, "Type & Vendor/Customer"] = (
          edit_type_vendor
      )
      st.session_state.data.at[selected_idx, "Amount"] = edit_amount
      st.session_state.data.at[selected_idx, "Description Text"] = edit_desc_text
      st.session_state.data.at[selected_idx, "Description File (PDF)"] = (
          updated_desc_name
      )
      st.session_state.data.at[selected_idx, "Project"] = edit_project
      st.session_state.data.at[selected_idx, "Status"] = edit_status
      st.session_state.data.at[selected_idx, "Payment Receipt (PDF)"] = (
          updated_receipt_name
      )
      st.session_state.data.at[selected_idx, "Due Date"] = str(edit_due_date)
      st.session_state.data.at[selected_idx, "Assignee"] = edit_assignee
      st.session_state.data.at[selected_idx, "Last Edited"] = (
          datetime.now().strftime("%Y-%m-%d %I:%M %p")
      )

      st.success(f"Row {selected_idx} updated successfully!")
      st.rerun()

else:
  st.info(
      "No entries found yet. Use the sidebar form on the left to add your first"
      " finance instruction!"
  )
