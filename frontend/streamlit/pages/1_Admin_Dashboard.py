import streamlit as st
import requests
import pandas as pd
import os

# --- Page Configuration and Access Control ---
st.set_page_config(page_title="Admin Dashboard", layout="wide")

if not st.session_state.get('logged_in') or st.session_state.get('role') != 'admin':
    st.error("You do not have permission to view this page. Please log in as an Admin.")
    st.stop()

# --- Shared Variables ---
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
auth = st.session_state.get('auth')

# --- Helper Functions ---
def get_all_users():
    try:
        res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
        if res.status_code == 200:
            return [u['username'] for u in res.json()]
        return []
    except Exception:
        return []

def get_all_pdfs():
    try:
        res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
        if res.status_code == 200:
            return [pdf['filename'] for pdf in res.json().get("pdfs", [])]
        return []
    except Exception:
        return []

# --- Main UI ---
st.title("👑 Admin Dashboard")

menu = st.sidebar.radio("Admin Menu", [
    "User Management",
    "Chat Management",
    "Data Management",
    "VectorDB Management"
])

st.header(menu)

# --- User Management ---
if menu == "User Management":
    tabs = st.tabs(["List Users", "Add User", "Delete User", "Reset Password"])
    
    with tabs[0]: # List Users
        st.subheader("List All Users")
        if st.button("Refresh User List"):
            try:
                res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
                if res.status_code == 200:
                    st.dataframe(pd.DataFrame(res.json()), use_container_width=True)
                else:
                    st.error(f"Failed to fetch users: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    with tabs[1]: # Add User
        st.subheader("Add a New User")
        with st.form("add_user_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            submitted = st.form_submit_button("Add User")
            if submitted:
                if not new_username or not new_password:
                    st.warning("Please provide both username and password.")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/admin/users", json={"username": new_username, "password": new_password}, auth=auth)
                        if res.status_code == 200:
                            st.success(f"User '{res.json()['username']}' added successfully!")
                        else:
                            st.error(f"Failed to add user: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    with tabs[2]: # Delete User
        st.subheader("Delete a User")
        users_list = get_all_users()
        user_to_delete = st.selectbox("Select user to delete", users_list, key="delete_user_select")
        if st.button("Delete User", type="primary"):
            if not user_to_delete:
                st.warning("Please select a user to delete.")
            else:
                try:
                    res = requests.delete(f"{BASE_URL}/admin/users/{user_to_delete}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"User '{user_to_delete}' deleted successfully!")
                    else:
                        st.error(f"Failed to delete user: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[3]: # Reset Password
        st.subheader("Reset User Password")
        users_list_reset = get_all_users()
        user_to_reset = st.selectbox("Select user to reset password", users_list_reset, key="reset_user_select")
        with st.form("reset_password_form"):
            new_pw = st.text_input("New Password", type="password")
            submitted = st.form_submit_button("Reset Password")
            if submitted:
                if not user_to_reset or not new_pw:
                    st.warning("Please select a user and provide a new password.")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/admin/users/{user_to_reset}/reset_password", json={"password": new_pw}, auth=auth)
                        if res.status_code == 200:
                            st.success(f"Password for '{user_to_reset}' has been reset.")
                        else:
                            st.error(f"Failed to reset password: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- Chat Management ---
elif menu == "Chat Management":
    st.subheader("View User Chat History")
    users_list = get_all_users()
    selected_user = st.selectbox("Select a user", users_list)
    if st.button("View Chat History"):
        if selected_user:
            try:
                res = requests.get(f"{BASE_URL}/admin/chat/history/{selected_user}", auth=auth)
                if res.status_code == 200:
                    history = res.json().get("history", [])
                    if history:
                        st.write(f"Chat History for **{selected_user}**:")
                        for msg in history:
                            st.text(f"- {msg}")
                    else:
                        st.info(f"No chat history found for '{selected_user}'.")
                else:
                    st.error(f"Failed to fetch history: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- Data Management ---
elif menu == "Data Management":
    tabs = st.tabs(["Upload PDFs (Files)", "Upload from Folder", "List All PDFs", "Delete PDFs", "Delete ALL Public PDFs"])

    with tabs[0]: # Upload Files
        st.subheader("Upload PDF Documents")
        with st.form("admin_upload_form"):
            uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True, key="admin_file_uploader")
            is_public = st.radio("Make these PDFs public?", ("Yes", "No"), index=1, key="admin_public_radio")
            submitted = st.form_submit_button("Upload Files")
            if submitted and uploaded_files:
                files_to_send = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                data = {"is_public": 1 if is_public == "Yes" else 0}
                try:
                    res = requests.post(f"{BASE_URL}/admin/pdf/upload", files=files_to_send, data=data, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Successfully uploaded: {', '.join(res.json().get('uploaded', []))}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[1]: # Upload from Folder
        st.subheader("Upload All PDFs from a Folder")
        st.info("Use this option to upload all PDF files from a local folder. In the file dialog, navigate to your folder and select all files (e.g., using Ctrl+A).")
        with st.form("admin_folder_upload_form"):
            folder_files = st.file_uploader("Select all PDF files from a folder", type=["pdf"], accept_multiple_files=True, key="admin_folder_uploader")
            folder_is_public = st.radio("Make these PDFs public?", ("Yes", "No"), index=1, key="admin_folder_public_radio")
            folder_submitted = st.form_submit_button("Upload Folder Contents")
            if folder_submitted and folder_files:
                files_to_send = [("files", (f.name, f.getvalue(), f.type)) for f in folder_files]
                data = {"is_public": 1 if folder_is_public == "Yes" else 0}
                try:
                    res = requests.post(f"{BASE_URL}/admin/pdf/upload", files=files_to_send, data=data, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Successfully uploaded: {', '.join(res.json().get('uploaded', []))}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[2]: # List
        st.subheader("List All Stored PDFs")
        if st.button("Refresh PDF List"):
            try:
                res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
                if res.status_code == 200:
                    st.dataframe(pd.DataFrame(res.json().get("pdfs", [])), use_container_width=True)
                else:
                    st.error(f"Failed to fetch PDFs: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    with tabs[3]: # Delete
        st.subheader("Delete Specific PDFs from Storage")
        pdf_list = get_all_pdfs()
        files_to_delete = st.multiselect("Select PDFs to delete", pdf_list)
        if st.button("Delete Selected PDFs", type="primary"):
            if files_to_delete:
                try:
                    res = requests.post(f"{BASE_URL}/admin/pdf/delete", json={"filenames": files_to_delete}, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Deleted: {res.json().get('deleted')}")
                        if res.json().get('errors'):
                            st.warning(f"Errors: {res.json().get('errors')}")
                    else:
                        st.error(f"Delete failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[4]: # Delete All Public
        st.subheader("Delete All Public PDFs")
        st.warning("This action is irreversible and will delete all PDFs marked as public from storage.")
        if st.button("Delete ALL Public PDFs", type="primary"):
            try:
                res = requests.post(f"{BASE_URL}/admin/pdf/delete_public", auth=auth)
                if res.status_code == 200:
                    st.success(f"Successfully deleted public PDFs: {res.json().get('deleted')}")
                    if res.json().get('errors'):
                        st.warning(f"Errors: {res.json().get('errors')}")
                else:
                    st.error(f"Delete failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- VectorDB Management ---
elif menu == "VectorDB Management":
    tabs = st.tabs([
        "Ingest PDFs", 
        "Remove PDF Data",
        "List Ingested Data", 
        "Clear Chat Memory"
    ])

    with tabs[0]: # Ingest
        st.subheader("Ingest Data into VectorDB")
        
        st.markdown("#### Ingest All Public PDFs")
        if st.button("Ingest All Public"):
            try:
                res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/all", auth=auth)
                if res.status_code == 200:
                    st.success("Successfully started ingestion of all public PDFs.")
                else:
                    st.error(f"Ingestion failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.markdown("---")
        st.markdown("#### Ingest a Specific PDF")
        pdf_list_ingest = get_all_pdfs()
        filename_to_ingest = st.selectbox("Select PDF to ingest", pdf_list_ingest, key="ingest_filename")
        ingest_type = st.radio("Ingest as", ["Public", "Private (for a specific user)"])
        
        user_id_for_ingest = ""
        if ingest_type == "Private (for a specific user)":
            user_list_ingest = get_all_users()
            user_id_for_ingest = st.selectbox("Select User", user_list_ingest, key="ingest_user")

        if st.button("Ingest Selected PDF"):
            if filename_to_ingest:
                try:
                    if ingest_type == "Public":
                        res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/public/{filename_to_ingest}", auth=auth)
                    else:
                        if user_id_for_ingest:
                            res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/private/{filename_to_ingest}?user_id={user_id_for_ingest}", auth=auth)
                        else:
                            st.warning("Please select a user for private ingestion.")
                            st.stop()
                    
                    if res.status_code == 200:
                        st.success(f"Ingestion of '{filename_to_ingest}' started successfully.")
                    else:
                        st.error(f"Ingestion failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    with tabs[1]: # Remove
        st.subheader("Remove Data from VectorDB")
        
        st.markdown("#### Remove by Filename")
        pdf_list_remove = get_all_pdfs()
        filename_to_remove = st.selectbox("Select PDF to remove", pdf_list_remove, key="remove_filename")
        if st.button("Remove PDF Data"):
            try:
                res = requests.delete(f"{BASE_URL}/admin/vectordb/pdf/{filename_to_remove}", auth=auth)
                if res.status_code == 200:
                    st.success(f"Data for '{filename_to_remove}' removed from VectorDB.")
                else:
                    st.error(f"Removal failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.markdown("---")
        st.markdown("#### Remove by User")
        user_list_remove = get_all_users()
        user_to_remove_data = st.selectbox("Select User", user_list_remove, key="remove_user_data")
        if st.button("Remove All Data for User", type="primary"):
            try:
                res = requests.delete(f"{BASE_URL}/admin/vectordb/pdf/user/{user_to_remove_data}", auth=auth)
                if res.status_code == 200:
                    st.success(f"All PDF data for '{user_to_remove_data}' removed from VectorDB.")
                else:
                    st.error(f"Removal failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

    with tabs[2]: # List Ingested
        st.subheader("List All Ingested Data Sources")
        if st.button("Refresh Ingested List"):
            try:
                res = requests.get(f"{BASE_URL}/admin/vectordb/pdf", auth=auth)
                if res.status_code == 200:
                    st.dataframe(pd.DataFrame(res.json().get("sources", [])), use_container_width=True)
                else:
                    st.error(f"Failed to fetch sources: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
                
    with tabs[3]: # Clear Memory
        st.subheader("Clear Chat Memory from VectorDB")
        
        st.markdown("#### Clear a Specific User's Memory")
        user_list_clear = get_all_users()
        user_to_clear = st.selectbox("Select User", user_list_clear, key="clear_user_memory")
        if st.button("Clear User Memory", type="primary"):
            try:
                res = requests.delete(f"{BASE_URL}/admin/vectordb/memory/{user_to_clear}", auth=auth)
                if res.status_code == 200:
                    st.success(f"Chat memory for '{user_to_clear}' has been cleared.")
                else:
                    st.error(f"Clear failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
        
        st.markdown("---")
        st.markdown("#### Clear ALL Users' Memory")
        st.warning("This action is irreversible and will clear the chat history for ALL users.")
        if st.button("Clear ALL Memory", type="primary"):
            try:
                res = requests.delete(f"{BASE_URL}/admin/vectordb/memory", auth=auth)
                if res.status_code == 200:
                    st.success("Successfully cleared all user chat memories.")
                else:
                    st.error(f"Clear failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
