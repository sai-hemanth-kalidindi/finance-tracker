from datetime import datetime
import time
import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Finance Instructions & Follow-ups", layout="wide"
)

# Connect to Supabase using Streamlit Secrets
@st.cache_resource
def init_supabase() -> Client:
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)


supabase = init_supabase()
BUCKET_NAME = "finance-files"


def upload_pdf_to_supabase(uploaded_file, folder: str) -> str:
  """Uploads a file to Supabase Storage and returns its public URL."""
  if uploaded_file is None:
    return ""
  clean_name = f"{int(time.time())}_{uploaded_file.name.replace(' ', '_')}"
  storage_path = f"{folder}/{clean_name}"
  file_bytes = uploaded_file.getvalue()

  supabase.storage.from_(BUCKET_NAME).upload(
      path=storage_path,
      file=file_bytes,
      file_options={"content-type": uploaded_file.type, "upsert": "true"},
  )
  return supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)


def fetch_data() -> pd.DataFrame:
  response = (
      supabase.table("transactions").select("*").order("id", desc=True).execute()
  )
  if response.data:
    return pd.DataFrame(response.data)
  return pd.DataFrame(
      columns=[
          "id",
          "type_vendor",
          "amount",
          "description_text",
          "description_file_url",
          "project",
          "status",
          "receipt_file_url",
          "due_date",
          "admin_creating",
          "created_time",
          "last_edited",
          "assignee",
      ]
  )


st.title("Finance Instructions & Follow-ups")
st.write(
    "Central tracker for finance instructions, vendor payments, and follow-ups."
)

# Load live data from Supabase
df = fetch_data()

# --- SIDEBAR: ADD NEW ENTRY FORM (Receipt is optional here) ---
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
    
    # Optional on creation (can be uploaded later once payment is done)
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
      with st.spinner("Saving to cloud database..."):
        desc_url = upload_pdf_to_supabase(description_file, "descriptions")
        # If receipt is left blank, it saves as empty string so it can be added later
        receipt_url = upload_pdf_to_supabase(receipt_file, "receipts") if receipt_file else ""
        current_time = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        new_record = {
            "type_vendor": type_vendor,
            "amount": float(amount),
            "description_text": description_text,
            "description_file_url": desc_url,
            "project": project,
            "status": status,
            "receipt_file_url": receipt_url,
            "due_date": str(due_date),
            "admin_creating": admin_name,
            "created_time": current_time,
            "last_edited": current_time,
            "assignee": assignee,
        }

        supabase.table("transactions").insert(new_record).execute()
      st.success("Saved permanently to cloud!")
      st.rerun()

# --- MAIN DASHBOARD VIEW ---
st.subheader("📋 Finance Tracker Dashboard")

if not df.empty:
  # Map empty receipt URLs to a readable message in the table
  display_df = df.copy()
  display_df["receipt_file_url"] = display_df["receipt_file_url"].apply(
      lambda x: x if (x and str(x).startswith("http")) else "Pending Payment / No Receipt Yet"
  )

  display_df = display_df.rename(
      columns={
          "id": "ID",
          "type_vendor": "Type & Vendor/Customer",
          "amount": "Amount",
          "description_text": "Description Text",
          "description_file_url": "Payment Receipt PDF",
          "description_file_url": "Description PDF",
          "project": "Project",
          "status": "Status",
          "receipt_file_url": "Payment Receipt PDF",
          "due_date": "Due Date",
          "admin_creating": "Admin Creating",
          "created_time": "Created Time",
          "last_edited": "Last Edited",
          "assignee": "Assignee",
      }
  )

  st.dataframe(
      display_df,
      use_container_width=True,
      hide_index=True,
      column_config={
          "Payment Receipt PDF": st.column_config.LinkColumn(
              "Payment Receipt PDF", display_text="Open Receipt"
          ),
      },
  )

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Total Entries", len(df))
  col2.metric("To Be Done", len(df[df["status"] == "To be done"]))
  col3.metric("In Process", len(df[df["status"] == "In process"]))
  col4.metric("Done", len(df[df["status"] == "Done"]))

  st.divider()

  # --- EDIT EXISTING ENTRY SECTION (Upload receipt here later) ---
  st.subheader("✏️ Edit an Existing Entry / Upload Payment Receipt")

  row_options = []
  for _, row in df.iterrows():
    receipt_status = "✅ Has Receipt" if row["receipt_file_url"] else "⏳ Pending Receipt"
    label = (
        f"ID {row['id']}: {row['type_vendor']} | Project: {row['project']} |"
        f" Amount: {row['amount']} [{receipt_status}]"
    )
    row_options.append(label)

  selected_option = st.selectbox("Select Entry to Edit:", row_options)
  selected_id = int(selected_option.split(":")[0].replace("ID ", ""))
  current_row = df[df["id"] == selected_id].iloc[0]

  with st.form("edit_entry_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
      edit_type_vendor = st.text_input(
          "Type & Vendor/Customer", value=current_row["type_vendor"] or ""
      )
      edit_amount = st.number_input(
          "Amount",
          value=float(current_row["amount"] or 0.0),
          min_value=0.0,
          step=100.0,
      )
      edit_project = st.text_input(
          "Project", value=current_row["project"] or ""
      )

    with c2:
      status_list = ["To be done", "In process", "Done"]
      current_status_idx = (
          status_list.index(current_row["status"])
          if current_row["status"] in status_list
          else 0
      )
      edit_status = st.selectbox("Status", status_list, index=current_status_idx)

      try:
        parsed_date = datetime.strptime(
            str(current_row["due_date"]), "%Y-%m-%d"
        ).date()
      except Exception:
        parsed_date = datetime.today().date()
      edit_due_date = st.date_input("Due Date", value=parsed_date)

      edit_assignee = st.text_input(
          "Assign (Reviewer Name)", value=current_row["assignee"] or ""
      )

    with c3:
      edit_desc_text = st.text_area(
          "Description Text", value=current_row["description_text"] or ""
      )
      st.caption(
          "Receipt Status: **Uploaded** ✅"
          if current_row["receipt_file_url"]
          else "Receipt Status: **Pending Payment (No receipt yet)** ⏳"
      )
      new_receipt_file = st.file_uploader(
          "Upload / Attach Payment Receipt (PDF)",
          type=["pdf", "png", "jpg"],
          key="edit_receipt",
      )
      new_desc_file = st.file_uploader(
          "Upload / Replace Description File (PDF)",
          type=["pdf", "png", "jpg"],
          key="edit_desc",
      )

    update_submitted = st.form_submit_button(
        "Update Entry / Save Receipt", use_container_width=True
    )

    if update_submitted:
      with st.spinner("Updating cloud record..."):
        # Keep existing receipt if no new file is chosen, otherwise upload the new one
        updated_receipt_url = current_row["receipt_file_url"] or ""
        if new_receipt_file is not None:
          updated_receipt_url = upload_pdf_to_supabase(
              new_receipt_file, "receipts"
          )

        updated_desc_url = current_row["description_file_url"] or ""
        if new_desc_file is not None:
          updated_desc_url = upload_pdf_to_supabase(
              new_desc_file, "descriptions"
          )

        updated_record = {
            "type_vendor": edit_type_vendor,
            "amount": float(edit_amount),
            "description_text": edit_desc_text,
            "description_file_url": updated_desc_url,
            "project": edit_project,
            "status": edit_status,
            "receipt_file_url": updated_receipt_url,
            "due_date": str(edit_due_date),
            "assignee": edit_assignee,
            "last_edited": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
        }

        supabase.table("transactions").update(updated_record).eq(
            "id", selected_id
        ).execute()

      st.success(f"Entry ID {selected_id} updated successfully!")
      st.rerun()

else:
  st.info(
      "No entries found yet. Use the sidebar form on the left to add your first"
      " finance instruction!"
  )
