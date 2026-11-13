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
          "Amount",
          "Description Text",
          "Description File",
          "Description Path",
          "Project",
          "Status",
          "Payment Receipt PDF",
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
    "Amount",
    "Description Text",
    "Description File",
    "Description Path",
    "Project",
    "Status",
    "Payment Receipt PDF",
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

      receipt_file_name = "Pending Payment / No Receipt Yet"
      receipt_path = ""
      if receipt_file is not None:
        receipt_file_name = receipt_file.name
        receipt_path = os.path.join("uploads/receipts", receipt_file.name)
        with open(receipt_path, "wb") as f:
          f.write(receipt_file.getbuffer())

      current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

      new_row = {
          "ID": st.session_state.next_id,
          "Type & Vendor/Customer": type_vendor,
          "Amount": float(amount),
          "Description Text": description_text,
          "Description File": desc_file_name,
          "Description Path": desc_path,
          "Project": project,
          "Status": status,
          "Payment Receipt PDF": receipt_file_name,
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
  # Table Header
  st.markdown("---")
  header_cols = st.columns(
      [0.4, 1.2, 0.9, 0.9, 0.9, 1.1, 0.7, 0.7, 0.8, 0.8, 0.8, 0.5]
  )
  header_cols[0].markdown("**ID**")
  header_cols[1].markdown("**Type & Vendor**")
  header_cols[2].markdown("**Amount (₹)**")
  header_cols[3].markdown("**Desc File**")
  header_cols[4].markdown("**Project**")
  header_cols[5].markdown("**Status**")
  header_cols[6].markdown("**Receipt**")
  header_cols[7].markdown("**Due Date**")
  header_cols[8].markdown("**Admin**")
  header_cols[9].markdown("**Created**")
  header_cols[10].markdown("**Assignee**")
  header_cols[11].markdown("**Action**")
  st.markdown("---")

  # Render each row with preview triggers
  for _, row in df.iterrows():
    row_cols = st.columns(
        [0.4, 1.2, 0.9, 0.9, 0.9, 1.1, 0.7, 0.7, 0.8, 0.8, 0.8, 0.5]
    )
    row_cols[0].write(str(row["ID"]))
    row_cols[1].write(str(row["Type & Vendor/Customer"]))
    row_cols[2].write(
        f"₹{float(row['Amount']) if pd.notna(row['Amount']) else 0.0:,.2f}"
    )

    # Description File preview column
    desc_display = str(row["Description File"])
    desc_p = str(row["Description Path"]) if pd.notna(row["Description Path"]) else ""
    if desc_p and os.path.exists(desc_p):
      with row_cols[3]:
        with st.popover(f"📁 {desc_display[:10]}..."):
          st.write(f"**Description File:** {desc_display}")
          if desc_p.endswith((".png", ".jpg", ".jpeg")):
            st.image(desc_p, use_column_width=True)
          else:
            with open(desc_p, "rb") as f:
              st.download_button(
                  "📥 Download/Open PDF", f, file_name=desc_display
              )
    else:
      row_cols[3].write(desc_display if desc_display != "nan" else "None")

    row_cols[4].write(str(row["Project"]))
    row_cols[5].write(str(row["Status"]))

    # Receipt preview column
    receipt_display = str(row["Payment Receipt PDF"])
    receipt_p = str(row["Receipt Path"]) if pd.notna(row["Receipt Path"]) else ""
    if receipt_p and os.path.exists(receipt_p):
      with row_cols[6]:
        with st.popover("📄 View Receipt"):
          st.write(f"**Receipt File:** {receipt_display}")
          if receipt_p.endswith((".png", ".jpg", ".jpeg")):
            st.image(receipt_p, use_column_width=True)
          else:
            with open(receipt_p, "rb") as f:
              st.download_button(
                  "📥 Download/Open PDF Receipt", f, file_name=receipt_display
              )
    else:
      row_cols[6].write("⏳ Pending")

    row_cols[7].write(str(row["Due Date"]))
    row_cols[8].write(str(row["Admin Creating"]))
    row_cols[9].write(str(row["Created Time"]))
    row_cols[10].write(str(row["Assignee"]))

    with row_cols[11]:
      if st.button("✏️", key=f"edit_btn_{row['ID']}"):
        st.session_state.editing_row_id = row["ID"]

    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)

  # If an entry is selected for editing, show its form right here
  if st.session_state.editing_row_id is not None:
    edit_id = st.session_state.editing_row_id
    row_idx = df.index[df["ID"] == edit_id][0]
    current_row = df.loc[row_idx]

    st.markdown(
        f"### ⚙️ Editing Entry ID: `{edit_id}`"
        f" ({current_row['Type & Vendor/Customer']})"
    )

    with st.form(f"edit_form_{edit_id}"):
      c1, c2, c3 = st.columns(3)

      with c1:
        edit_type_vendor = st.text_input(
            "Type & Vendor/Customer", value=current_row["Type & Vendor/Customer"]
        )
        edit_amount = st.number_input(
            "Amount (₹)",
            value=float(current_row["Amount"]),
            min_value=0.0,
            step=1000.0,
            format="%.2f",
        )
        edit_project = st.text_input(
            "Project", value=current_row["Project"]
        )

      with c2:
        status_list = ["To be done", "In process", "Done"]
        current_status_idx = (
            status_list.index(current_row["Status"])
            if current_row["Status"] in status_list
            else 0
        )
        edit_status = st.selectbox(
            "Status", status_list, index=current_status_idx
        )

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
        st.caption(f"Current Receipt: **{current_row['Payment Receipt PDF']}**")
        new_receipt_file = st.file_uploader(
            "Upload Payment Receipt (PDF)",
            type=["pdf", "png", "jpg"],
            key=f"edit_receipt_{edit_id}",
        )
        new_desc_file = st.file_uploader(
            "Replace Description File (PDF)",
            type=["pdf", "png", "jpg"],
            key=f"edit_desc_{edit_id}",
        )

      update_submitted = st.form_submit_button(
          "💾 Save Changes & Upload Receipt", use_container_width=True
      )
      cancel_clicked = st.form_submit_button(
          "❌ Cancel Editing", use_container_width=False
      )

      if update_submitted:
        updated_receipt_name = current_row["Payment Receipt PDF"]
        updated_receipt_path = current_row["Receipt Path"]
        if new_receipt_file is not None:
          updated_receipt_name = new_receipt_file.name
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
        st.session_state.data.at[row_idx, "Amount"] = float(edit_amount)
        st.session_state.data.at[row_idx, "Description Text"] = edit_desc_text
        st.session_state.data.at[row_idx, "Description File"] = (
            updated_desc_name
        )
        st.session_state.data.at[row_idx, "Description Path"] = (
            updated_desc_path
        )
        st.session_state.data.at[row_idx, "Project"] = edit_project
        st.session_state.data.at[row_idx, "Status"] = edit_status
        st.session_state.data.at[row_idx, "Payment Receipt PDF"] = (
            updated_receipt_name
        )
        st.session_state.data.at[row_idx, "Receipt Path"] = updated_receipt_path
        st.session_state.data.at[row_idx, "Due Date"] = str(edit_due_date)
        st.session_state.data.at[row_idx, "Assignee"] = edit_assignee
        st.session_state.data.at[row_idx, "Last Edited"] = (
            datetime.now().strftime("%Y-%m-%d %I:%M %p")
        )

        st.session_state.editing_row_id = None
        st.success(f"Entry ID {edit_id} updated successfully!")
        st.rerun()

      if cancel_clicked:
        st.session_state.editing_row_id = None
        st.rerun()

  # Summary Metrics in Rupees
  st.markdown("---")
  total_sum = pd.to_numeric(df["Amount"], errors="coerce").sum()

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Amount (₹)", f"₹{total_sum:,.2f}")
  col2.metric("To Be Done", len(df[df["Status"] == "To be done"]))
  col3.metric("Done", len(df[df["Status"] == "Done"]))

else:
  st.info(
      "No entries found yet. Use the sidebar form on the left to add your first"
      " finance instruction!"
  )
