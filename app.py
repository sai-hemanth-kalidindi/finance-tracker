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
    "Central tracker for finance instructions, vendor payments, and follow-ups."
)

# Initialize session state dataframe and unique ID counter if they don't exist
if "data" not in st.session_state:
  st.session_state.data = pd.DataFrame(
      columns=[
          "ID",
          "Type & Vendor/Customer",
          "Amount (₹)",
          "Description File",
          "Description Path",
          "Project",
          "Status",
          "Receipt Status",
          "Receipt Path",
          "Due Date",
          "Admin Creating",
          "Created Time",
          "Last Edited",
          "Assignee",
      ]
  )
if "next_id" not in st.session_state:
  st.session_state.next_id = 1

if "editing_row_id" not in st.session_state:
  st.session_state.editing_row_id = None

# Safety check: Ensure all necessary columns exist even if session state is old
required_columns = [
    "ID",
    "Type & Vendor/Customer",
    "Amount (₹)",
    "Description File",
    "Description Path",
    "Project",
    "Status",
    "Receipt Status",
    "Receipt Path",
    "Due Date",
    "Admin Creating",
    "Created Time",
    "Last Edited",
    "Assignee",
]
for col in required_columns:
  if col not in st.session_state.data.columns:
    st.session_state.data[col] = ""

# --- SIDEBAR: ADD NEW ENTRY FORM ---
with st.sidebar:
  st.header("➕ Add New Instruction")
  with st.form("entry_form", clear_on_submit=True):
    type_vendor = st.text_input(
        "1. Type & Vendor/Customer Name",
        placeholder="e.g., Vendor Payment - UDL Building",
    )
    amount = st.number_input(
        "2. Amount (₹)", min_value=0.0, step=1000.0, format="%.2f"
    )

    st.markdown("---")
    st.markdown("**3. Description Details**")
    description_text = st.text_area(
        "Description Text", placeholder="Details of work or material..."
    )
    description_file = st.file_uploader(
        "Upload Description File (PDF/Image)",
        type=["pdf", "png", "jpg"],
        key="desc_file",
    )

    st.markdown("---")
    project = st.text_input("4. Project", placeholder="e.g., AEC-7 or V-64")
    status = st.selectbox("5. Status", ["To be done", "In process", "Done"])

    receipt_file = st.file_uploader(
        "6. Files (Payment Receipt in PDF) - *Optional for now*",
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
      desc_file_name = "None"
      desc_path = ""
      if description_file is not None:
        desc_file_name = description_file.name
        desc_path = os.path.join(
            "uploads/descriptions", description_file.name
        )
        with open(desc_path, "wb") as f:
          f.write(description_file.getbuffer())

      receipt_status = "⏳ Pending"
      receipt_path = ""
      if receipt_file is not None:
        receipt_status = "📄 View / Attached"
        receipt_path = os.path.join("uploads/receipts", receipt_file.name)
        with open(receipt_path, "wb") as f:
          f.write(receipt_file.getbuffer())

      current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

      new_row = {
          "ID": st.session_state.next_id,
          "Type & Vendor/Customer": type_vendor,
          "Amount (₹)": float(amount),
          "Description File": desc_file_name,
          "Description Path": desc_path,
          "Project": project,
          "Status": status,
          "Receipt Status": receipt_status,
          "Receipt Path": receipt_path,
          "Due Date": str(due_date),
          "Admin Creating": admin_name,
          "Created Time": current_time,
          "Last Edited": current_time,
          "Assignee": assignee,
      }

      st.session_state.next_id += 1
      st.session_state.data = pd.concat(
          [st.session_state.data, pd.DataFrame([new_row])], ignore_index=True
      )
      st.success("Entry added successfully!")
      st.rerun()

# --- MAIN DASHBOARD VIEW ---
st.subheader("📋 Finance Tracker Dashboard")

df = st.session_state.data

if not df.empty:
  # Clean display dataframe (hiding local file paths from direct table view for neatness)
  view_df = df.drop(columns=["Description Path", "Receipt Path"])

  st.dataframe(view_df, use_container_width=True, hide_index=True)

  st.markdown("---")
  st.subheader("✏️ Edit Entry & Upload Receipts")
  st.write(
      "Select an **ID** below to update details, change status, or upload"
      " payment receipts:"
  )

  # Dropdown selector for editing (works flawlessly on mobile and desktop)
  row_options = []
  for _, row in df.iterrows():
    label = (
        f"ID {row['ID']}: {row['Type & Vendor/Customer']} | Project:"
        f" {row['Project']} | Status: {row['Status']}"
    )
    row_options.append(label)

  selected_option = st.selectbox("Select Entry to Edit:", row_options)
  selected_id = int(selected_option.split(":")[0].replace("ID ", ""))

  row_idx = df.index[df["ID"] == selected_id][0]
  current_row = df.loc[row_idx]

  with st.form("edit_entry_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
      edit_type_vendor = st.text_input(
          "Type & Vendor/Customer", value=current_row["Type & Vendor/Customer"]
      )
      edit_amount = st.number_input(
          "Amount (₹)",
          value=float(current_row["Amount (₹)"]),
          min_value=0.0,
          step=1000.0,
          format="%.2f",
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
      st.caption(f"Current Description File: **{current_row['Description File']}**")
      new_desc_file = st.file_uploader(
          "Replace Description File",
          type=["pdf", "png", "jpg"],
          key=f"edit_desc_{selected_id}",
      )

      st.caption(f"Current Receipt Status: **{current_row['Receipt Status']}**")
      new_receipt_file = st.file_uploader(
          "Upload / Replace Payment Receipt (PDF)",
          type=["pdf", "png", "jpg"],
          key=f"edit_receipt_{selected_id}",
      )

    update_submitted = st.form_submit_button(
        "💾 Save Changes", use_container_width=True
    )

    if update_submitted:
      updated_receipt_status = current_row["Receipt Status"]
      updated_receipt_path = current_row["Receipt Path"]
      if new_receipt_file is not None:
        updated_receipt_status = "📄 View / Attached"
        updated_receipt_path = os.path.join(
            "uploads/receipts", new_receipt_file.name
        )
        with open(updated_receipt_path, "wb") as f:
          f.write(new_receipt_file.getbuffer())

      updated_desc_name = current_row["Description File"]
      updated_desc_path = current_row["Description Path"]
      if new_desc_file is not None:
        updated_desc_name = new_desc_file.name
        updated_desc_path = os.path.join(
            "uploads/descriptions", new_desc_file.name
        )
        with open(updated_desc_path, "wb") as f:
          f.write(new_desc_file.getbuffer())

      st.session_state.data.at[row_idx, "Type & Vendor/Customer"] = (
          edit_type_vendor
      )
      st.session_state.data.at[row_idx, "Amount (₹)"] = float(edit_amount)
      st.session_state.data.at[row_idx, "Description File"] = updated_desc_name
      st.session_state.data.at[row_idx, "Description Path"] = updated_desc_path
      st.session_state.data.at[row_idx, "Project"] = edit_project
      st.session_state.data.at[row_idx, "Status"] = edit_status
      st.session_state.data.at[row_idx, "Receipt Status"] = updated_receipt_status
      st.session_state.data.at[row_idx, "Receipt Path"] = updated_receipt_path
      st.session_state.data.at[row_idx, "Due Date"] = str(edit_due_date)
      st.session_state.data.at[row_idx, "Assignee"] = edit_assignee
      st.session_state.data.at[row_idx, "Last Edited"] = (
          datetime.now().strftime("%Y-%m-%d %I:%M %p")
      )

      st.success(f"Entry ID {selected_id} updated successfully!")
      st.rerun()

else:
  st.info(
      "No entries found yet. Use the sidebar form on the left to add your first"
      " finance instruction!"
  )
