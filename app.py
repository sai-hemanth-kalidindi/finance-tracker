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
  st.write("Click **✏️ Edit** on any row below to drop down its update form:")

  # Render each entry as an interactive card row with an inline Edit button
  for _, row in df.iterrows():
    row_id = row["ID"]

    with st.container(border=True):
      c1, c2, c3, c4 = st.columns([2.5, 2, 1.2, 0.8])
      with c1:
        st.markdown(f"**ID {row_id}: {row['Type & Vendor/Customer']}**")
        st.caption(f"Project: `{row['Project']}` | Due: {row['Due Date']}")
      with c2:
        st.markdown(
            f"💰 **₹{float(row['Amount (₹)']) if pd.notna(row['Amount (₹)']) else 0.0:,.2f}**"
        )
        st.markdown(f"Status: **{row['Status']}**")
      with c3:
        # File preview indicators
        desc_file = str(row["Description File"])
        desc_p = str(row["Description Path"]) if pd.notna(row["Description Path"]) else ""
        if desc_p and os.path.exists(desc_p):
          with st.popover("📁 Desc File"):
            st.write(f"**Description:** {desc_file}")
            if desc_p.endswith((".png", ".jpg", ".jpeg")):
              st.image(desc_p, use_column_width=True)
            else:
              with open(desc_p, "rb") as f:
                st.download_button(
                    "📥 Download/Open PDF", f, file_name=desc_file
                )
        else:
          st.caption("Desc: None")

        rec_p = str(row["Receipt Path"]) if pd.notna(row["Receipt Path"]) else ""
        if rec_p and os.path.exists(rec_p):
          with st.popover("📄 Receipt"):
            st.write(f"**Receipt:** {row['Receipt Status']}")
            if rec_p.endswith((".png", ".jpg", ".jpeg")):
              st.image(rec_p, use_column_width=True)
            else:
              with open(rec_p, "rb") as f:
                st.download_button(
                    "📥 Download/Open PDF Receipt", f, file_name="receipt.pdf"
                )
        else:
          st.caption("Receipt: ⏳ Pending")

      with c4:
        is_editing = st.session_state.editing_row_id == row_id
        button_label = "❌ Close" if is_editing else "✏️ Edit"
        if st.button(button_label, key=f"edit_btn_{row_id}", use_container_width=True):
          if is_editing:
            st.session_state.editing_row_id = None
          else:
            st.session_state.editing_row_id = row_id
          st.rerun()

    # --- DROP-DOWN EDIT FORM (APPEARS DIRECTLY BELOW THE CLICKED ROW) ---
    if st.session_state.editing_row_id == row_id:
      with st.form(f"edit_form_{row_id}", clear_on_submit=False):
        st.markdown(f"### ⚙️ Editing Entry ID: `{row_id}`")
        ec1, ec2, ec3 = st.columns(3)

        with ec1:
          edit_type_vendor = st.text_input(
              "Type & Vendor/Customer",
              value=row["Type & Vendor/Customer"],
              key=f"ev_{row_id}",
          )
          edit_amount = st.number_input(
              "Amount (₹)",
              value=float(row["Amount (₹)"]),
              min_value=0.0,
              step=1000.0,
              format="%.2f",
              key=f"ea_{row_id}",
          )
          edit_project = st.text_input(
              "Project", value=row["Project"], key=f"ep_{row_id}"
          )

        with ec2:
          status_list = ["To be done", "In process", "Done"]
          curr_status = row["Status"]
          c_idx = (
              status_list.index(curr_status)
              if curr_status in status_list
              else 0
          )
          edit_status = st.selectbox(
              "Status", status_list, index=c_idx, key=f"es_{row_id}"
          )

          try:
            parsed_date = datetime.strptime(
                str(row["Due Date"]), "%Y-%m-%d"
            ).date()
          except Exception:
            parsed_date = datetime.today().date()
          edit_due_date = st.date_input(
              "Due Date", value=parsed_date, key=f"ed_{row_id}"
          )

          edit_assignee = st.text_input(
              "Assign (Reviewer Name)",
              value=row["Assignee"],
              key=f"eass_{row_id}",
          )

        with ec3:
          st.caption(f"Current Desc: **{row['Description File']}**")
          new_desc_file = st.file_uploader(
              "Replace Description File",
              type=["pdf", "png", "jpg"],
              key=f"new_desc_{row_id}",
          )

          st.caption(f"Current Receipt: **{row['Receipt Status']}**")
          new_receipt_file = st.file_uploader(
              "Upload/Replace Payment Receipt",
              type=["pdf", "png", "jpg"],
              key=f"new_rec_{row_id}",
          )

        update_submitted = st.form_submit_button(
            "💾 Save Changes & Update", use_container_width=True
        )

        if update_submitted:
          row_idx = df.index[df["ID"] == row_id][0]
          updated_receipt_status = row["Receipt Status"]
          updated_receipt_path = row["Receipt Path"]
          if new_receipt_file is not None:
            updated_receipt_status = "📄 View / Attached"
            updated_receipt_path = os.path.join(
                "uploads/receipts", new_receipt_file.name
            )
            with open(updated_receipt_path, "wb") as f:
              f.write(new_receipt_file.getbuffer())

          updated_desc_name = row["Description File"]
          updated_desc_path = row["Description Path"]
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
          st.session_state.data.at[row_idx, "Description File"] = (
              updated_desc_name
          )
          st.session_state.data.at[row_idx, "Description Path"] = (
              updated_desc_path
          )
          st.session_state.data.at[row_idx, "Project"] = edit_project
          st.session_state.data.at[row_idx, "Status"] = edit_status
          st.session_state.data.at[row_idx, "Receipt Status"] = (
              updated_receipt_status
          )
          st.session_state.data.at[row_idx, "Receipt Path"] = (
              updated_receipt_path
          )
          st.session_state.data.at[row_idx, "Due Date"] = str(edit_due_date)
          st.session_state.data.at[row_idx, "Assignee"] = edit_assignee
          st.session_state.data.at[row_idx, "Last Edited"] = (
              datetime.now().strftime("%Y-%m-%d %I:%M %p")
          )

          st.session_state.editing_row_id = None
          st.success(f"Entry ID {row_id} updated successfully!")
          st.rerun()

else:
  st.info(
      "No entries found yet. Use the sidebar form on the left to add your first"
      " finance instruction!"
  )
