from datetime import datetime
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Finance Instructions & Follow-ups", layout="wide"
)

# Create local folders for uploaded PDF files
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
          "Project",
          "Status",
          "Payment Receipt PDF",
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
      desc_file_name = description_file.name if description_file else "None"
      if description_file:
        with open(
            os.path.join("uploads/descriptions", description_file.name), "wb"
        ) as f:
          f.write(description_file.getbuffer())

      receipt_file_name = receipt_file.name if receipt_file else "Pending Payment / No Receipt Yet"
      if receipt_file:
        with open(
            os.path.join("uploads/receipts", receipt_file.name), "wb"
        ) as f:
          f.write(receipt_file.getbuffer())

      current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

      new_row = {
          "ID": st.session_state.next_id,
          "Type & Vendor/Customer": type_vendor,
          "Amount": float(amount),
          "Description Text": description_text,
          "Description File": desc_file_name,
          "Project": project,
          "Status": status,
          "Payment Receipt PDF": receipt_file_name,
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
  # Render table rows with an inline Edit Action column
  st.write("Click a row's **Edit / Upload** button below to open its update form:")
  
  for _, row in df.iterrows():
    col_a, col_b, col_c, col_d, col_e, col_f, col_g = st.columns([0.6, 1.5, 1, 1.2, 1, 1, 0.8])
    col_a.write(f"**ID {row['ID']}**")
    col_b.write(row['Type & Vendor/Customer'])
    col_c.write(f"${row['Amount']:,.2f}")
    col_d.write(row['Project'])
    col_e.write(row['Status'])
    col_f.write(row['Payment Receipt PDF'])
    
    with col_g:
      if st.button("✏️ Edit", key=f"edit_btn_{row['ID']}"):
        st.session_state.editing_row_id = row['ID']

    st.divider()

  # If an entry is selected for editing, show its form right here
  if st.session_state.editing_row_id is not None:
    edit_id = st.session_state.editing_row_id
    row_idx = df.index[df["ID"] == edit_id][0]
    current_row = df.loc[row_idx]

    st.markdown(f"### ⚙️ Editing Entry ID: `{edit_id}` ({current_row['Type & Vendor/Customer']})")

    with st.form(f"edit_form_{edit_id}"):
      c1, c2, c3 = st.columns(3)

      with c1:
        edit_type_vendor = st.text_input(
            "Type & Vendor/Customer", value=current_row["Type & Vendor/Customer"]
        )
        edit_amount = st.number_input(
            "Amount",
            value=float(current_row["Amount"]),
            min_value=0.0,
            step=100.0,
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
      cancel_clicked = st.form_submit_button("❌ Cancel Editing", use_container_width=False)

      if update_submitted:
        updated_receipt_name = current_row["Payment Receipt PDF"]
        if new_receipt_file is not None:
          updated_receipt_name = new_receipt_file.name
          with open(
              os.path.join("uploads/receipts", new_receipt_file.name), "wb"
          ) as f:
            f.write(new_receipt_file.getbuffer())

        updated_desc_name = current_row["Description File"]
        if new_desc_file is not None:
          updated_desc_name = new_desc_file.name
          with open(
              os.path.join("uploads/descriptions", new_desc_file.name), "wb"
          ) as f:
            f.write(new_desc_file.getbuffer())

        st.session_state.data.at[row_idx, "Type & Vendor/Customer"] = edit_type_vendor
        st.session_state.data.at[row_idx, "Amount"] = float(edit_amount)
        st.session_state.data.at[row_idx, "Description Text"] = edit_desc_text
        st.session_state.data.at[row_idx, "Description File"] = updated_desc_name
        st.session_state.data.at[row_idx, "Project"] = edit_project
        st.session_state.data.at[row_idx, "Status"] = edit_status
        st.session_state.data.at[row_idx, "Payment Receipt PDF"] = updated_receipt_name
        st.session_state.data.at[row_idx, "Due Date"] = str(edit_due_date)
        st.session_state.data.at[row_idx, "Assignee"] = edit_assignee
        st.session_state.data.at[row_idx, "Last Edited"] = datetime.now().strftime(
            "%Y-%m-%d %I:%M %p"
        )

        st.session_state.
