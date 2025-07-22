import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Chatbot Admin/User Portal", layout="wide")

if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'password' not in st.session_state:
    st.session_state['password'] = ''
if 'auth' not in st.session_state:
    st.session_state['auth'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

st.title("RAG Chatbot Portal")

# Role selection and login
if not st.session_state['logged_in']:
    st.sidebar.header("Login")
    role = st.sidebar.radio("Select role", ["User", "Admin"])
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        auth = HTTPBasicAuth(username, password)
        if role == "Admin":
            res = requests.get(f"{BASE_URL}/admin/auth/check", auth=auth)
            if res.status_code == 200:
                st.session_state['role'] = 'admin'
                st.session_state['username'] = username
                st.session_state['password'] = password
                st.session_state['auth'] = auth
                st.session_state['logged_in'] = True
                st.success("Admin login successful!")
                st.experimental_rerun()
            else:
                st.error("Admin login failed: Incorrect credentials.")
        else:
            res = requests.get(f"{BASE_URL}/user/auth/check", auth=auth)
            if res.status_code == 200:
                st.session_state['role'] = 'user'
                st.session_state['username'] = username
                st.session_state['password'] = password
                st.session_state['auth'] = auth
                st.session_state['logged_in'] = True
                st.success("User login successful!")
                st.experimental_rerun()
            else:
                st.error("User login failed: Incorrect credentials.")
    st.stop()

# Sidebar menu
role = st.session_state['role']
username = st.session_state['username']
auth = st.session_state['auth']

st.sidebar.header(f"{role.capitalize()} Menu")
if st.sidebar.button("Logout"):
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.session_state['username'] = ''
    st.session_state['password'] = ''
    st.session_state['auth'] = None
    st.experimental_rerun()

if role == 'admin':
    menu = st.sidebar.radio("Select section", [
        "User Management",
        "Chat Management",
        "Data Management",
        "VectorDB Management"
    ])
    st.header(f"Admin: {menu}")

    if menu == "User Management":
        st.subheader("User Management")
        tab1, tab2, tab3, tab4 = st.tabs(["List Users", "Add User", "Delete User", "Reset Password"])
        with tab1:
            st.write("### List Users")
            try:
                res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
                if res.status_code == 200:
                    users = res.json()
                    st.table(users)
                else:
                    st.error(f"Failed to fetch users: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
        with tab2:
            st.write("### Add User")
            new_username = st.text_input("New Username", key="add_user_username")
            new_password = st.text_input("New Password", type="password", key="add_user_password")
            if st.button("Add User"):
                if not new_username or not new_password:
                    st.warning("Please enter both username and password.")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/admin/users", json={"username": new_username, "password": new_password}, auth=auth)
                        if res.status_code == 200:
                            st.success(f"User added: {res.json()}")
                        else:
                            st.error(f"Add user failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab3:
            st.write("### Delete User")
            try:
                res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
                if res.status_code == 200:
                    users = res.json()
                    usernames = [u['username'] for u in users]
                else:
                    usernames = []
            except Exception:
                usernames = []
            del_username = st.selectbox("Select user to delete", usernames, key="delete_user_select")
            if st.button("Delete User"):
                if not del_username:
                    st.warning("Please select a user to delete.")
                else:
                    try:
                        res = requests.delete(f"{BASE_URL}/admin/users/{del_username}", auth=auth)
                        if res.status_code == 200:
                            st.success(f"User deleted: {res.json()}")
                        else:
                            st.error(f"Delete user failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab4:
            st.write("### Reset User Password")
            try:
                res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
                if res.status_code == 200:
                    users = res.json()
                    usernames = [u['username'] for u in users]
                else:
                    usernames = []
            except Exception:
                usernames = []
            reset_username = st.selectbox("Select user to reset password", usernames, key="reset_user_select")
            new_pw = st.text_input("New Password", type="password", key="reset_user_pw")
            if st.button("Reset Password"):
                if not reset_username or not new_pw:
                    st.warning("Please select a user and enter a new password.")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/admin/users/{reset_username}/reset_password", json={"password": new_pw}, auth=auth)
                        if res.status_code == 200:
                            st.success(f"Password reset: {res.json()}")
                        else:
                            st.error(f"Reset password failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    elif menu == "Chat Management":
        st.subheader("Chat Management")
        # Fetch users for selection
        try:
            res = requests.get(f"{BASE_URL}/admin/users", auth=auth)
            if res.status_code == 200:
                users = res.json()
                usernames = [u['username'] for u in users]
            else:
                usernames = []
                st.error(f"Failed to fetch users: {res.text}")
        except Exception as e:
            usernames = []
            st.error(f"Error: {e}")
        if usernames:
            selected_user = st.selectbox("Select user to view chat history", usernames)
            if st.button("View Chat History"):
                try:
                    res = requests.get(f"{BASE_URL}/admin/chat/history/{selected_user}", auth=auth)
                    if res.status_code == 200:
                        history = res.json().get("history", [])
                        if history:
                            for i, msg in enumerate(history, 1):
                                st.markdown(f"**{i}.** {msg}")
                        else:
                            st.info("No chat history found for this user.")
                    else:
                        st.error(f"Failed to fetch chat history: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No users available.")
    elif menu == "Data Management":
        st.subheader("Data Management")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Upload PDFs", "Upload All from Folder", "List PDFs", "Delete PDFs", "Delete All Public PDFs"])
        with tab1:
            st.write("### Upload PDF(s)")
            uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True, key="admin_upload_files")
            is_public = st.radio("Is public?", ["No", "Yes"], key="admin_upload_is_public")
            if st.button("Upload PDF(s)"):
                if not uploaded_files:
                    st.warning("Please select at least one PDF file.")
                else:
                    files = []
                    for f in uploaded_files:
                        files.append(("files", (f.name, f, "application/pdf")))
                    data = {"is_public": "1" if is_public == "Yes" else "0"}
                    try:
                        res = requests.post(f"{BASE_URL}/admin/pdf/upload", files=files, data=data, auth=auth)
                        if res.status_code == 200:
                            st.success(f"Upload successful: {res.json()}")
                        else:
                            st.error(f"Upload failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab2:
            st.write("### Upload All PDFs from Folder")
            folder = st.text_input("Enter folder path (server-side)", key="admin_folder_path")
            is_public2 = st.radio("Is public?", ["No", "Yes"], key="admin_folder_is_public")
            if st.button("Upload All from Folder"):
                import os
                if not folder or not os.path.isdir(folder):
                    st.warning("Please enter a valid folder path on the server.")
                else:
                    files = []
                    for fname in os.listdir(folder):
                        if fname.lower().endswith(".pdf"):
                            files.append(("files", (fname, open(os.path.join(folder, fname), "rb"), "application/pdf")))
                    data = {"is_public": "1" if is_public2 == "Yes" else "0"}
                    try:
                        res = requests.post(f"{BASE_URL}/admin/pdf/upload", files=files, data=data, auth=auth)
                        if res.status_code == 200:
                            st.success(f"Upload successful: {res.json()}")
                        else:
                            st.error(f"Upload failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab3:
            st.write("### List All PDFs")
            try:
                res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
                if res.status_code == 200:
                    pdfs = res.json().get("pdfs", [])
                    st.table(pdfs)
                else:
                    st.error(f"Failed to fetch PDFs: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
        with tab4:
            st.write("### Delete PDFs")
            try:
                res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
                if res.status_code == 200:
                    pdfs = res.json().get("pdfs", [])
                    filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
                else:
                    filenames = []
            except Exception:
                filenames = []
            del_files = st.multiselect("Select PDFs to delete", filenames, key="admin_delete_files")
            if st.button("Delete Selected PDFs"):
                if not del_files:
                    st.warning("Please select at least one PDF to delete.")
                else:
                    try:
                        res = requests.post(f"{BASE_URL}/admin/pdf/delete", json={"filenames": del_files}, auth=auth)
                        if res.status_code == 200:
                            st.success(f"Deleted: {res.json()}")
                        else:
                            st.error(f"Delete failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        with tab5:
            st.write("### Delete All Public PDFs")
            if st.button("Delete All Public PDFs"):
                try:
                    res = requests.post(f"{BASE_URL}/admin/pdf/delete_public", auth=auth)
                    if res.status_code == 200:
                        st.success(f"All public PDFs deleted: {res.json()}")
                    else:
                        st.error(f"Delete failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    elif menu == "VectorDB Management":
        st.subheader("VectorDB Management")
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "Ingest All Public PDFs", "Ingest PDF (public/private)", "Remove PDF Data by Filename", "Remove PDF Data by User", "List Available PDF Data", "Clear All Users' Memory", "Clear User Memory by User ID"])
        with tab1:
            st.write("### Ingest All Public PDFs")
            if st.button("Ingest All Public PDFs"):
                try:
                    res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/all", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Ingestion successful: {res.json()}")
                    else:
                        st.error(f"Ingestion failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        with tab2:
            st.write("### Ingest PDF (public/private)")
            try:
                res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
                if res.status_code == 200:
                    pdfs = res.json().get("pdfs", [])
                    filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
                else:
                    filenames = []
            except Exception:
                filenames = []
            filename = st.selectbox("Select PDF to ingest", filenames, key="admin_vectordb_ingest_filename")
            ingest_type = st.radio("Ingest as", ["Public", "Specific user"], key="admin_vectordb_ingest_type")
            user_id = ""
            if ingest_type == "Specific user":
                user_id = st.text_input("User ID", key="admin_vectordb_ingest_userid")
            if st.button("Ingest Selected PDF"):
                try:
                    if ingest_type == "Public":
                        res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/public/{filename}", auth=auth)
                    else:
                        res = requests.post(f"{BASE_URL}/admin/vectordb/ingest/private/{filename}?user_id={user_id}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Ingestion successful: {res.json()}")
                    else:
                        st.error(f"Ingestion failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        with tab3:
            st.write("### Remove PDF Data by Filename")
            try:
                res = requests.get(f"{BASE_URL}/admin/pdf", auth=auth)
                if res.status_code == 200:
                    pdfs = res.json().get("pdfs", [])
                    filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
                else:
                    filenames = []
            except Exception:
                filenames = []
            filename = st.selectbox("Select PDF to remove from VectorDB", filenames, key="admin_vectordb_remove_filename")
            if st.button("Remove PDF Data"):
                try:
                    res = requests.delete(f"{BASE_URL}/admin/vectordb/pdf/{filename}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Removed: {res.json()}")
                    else:
                        st.error(f"Remove failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        with tab4:
            st.write("### Remove PDF Data by User")
            user_id = st.text_input("User ID to remove all PDF data", key="admin_vectordb_remove_userid")
            if st.button("Remove All PDF Data for User"):
                try:
                    res = requests.delete(f"{BASE_URL}/admin/vectordb/pdf/user/{user_id}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Removed: {res.json()}")
                    else:
                        st.error(f"Remove failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        with tab5:
            st.write("### List Available PDF Data")
            if st.button("List Available PDF Data"):
                try:
                    res = requests.get(f"{BASE_URL}/admin/vectordb/pdf", auth=auth)
                    if res.status_code == 200:
                        sources = res.json().get("sources", [])
                        st.table(sources)
                    else:
                        st.error(f"Failed to fetch sources: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        with tab6:
            st.write("### Clear All Users' Memory")
            if st.button("Clear All Users' Memory"):
                try:
                    res = requests.delete(f"{BASE_URL}/admin/vectordb/memory", auth=auth)
                    if res.status_code == 200:
                        st.success(f"All users' memory cleared: {res.json()}")
                    else:
                        st.error(f"Clear failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        with tab7:
            st.write("### Clear User Memory by User ID")
            user_id = st.text_input("User ID to clear memory", key="admin_vectordb_clear_userid")
            if st.button("Clear User Memory"):
                try:
                    res = requests.delete(f"{BASE_URL}/admin/vectordb/memory/{user_id}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"User memory cleared: {res.json()}")
                    else:
                        st.error(f"Clear failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("Feature UI coming soon...")
else:
    menu = st.sidebar.radio("Select section", [
        "Upload PDFs",
        "Upload All PDFs from Folder",
        "List My PDFs",
        "Ingest a PDF",
        "Ingest All My PDFs",
        "List My Ingested PDFs",
        "Delete a PDF from Storage",
        "Delete All My PDFs from Storage",
        "Remove a PDF from VectorDB",
        "Remove All My PDFs from VectorDB"
    ])
    st.header(f"User: {menu}")

    if menu == "Upload PDFs":
        st.subheader("Upload PDF(s)")
        uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True)
        is_public = st.radio("Is public?", ["No", "Yes"])
        if st.button("Upload"):
            if not uploaded_files:
                st.warning("Please select at least one PDF file.")
            else:
                files = []
                for f in uploaded_files:
                    files.append(("files", (f.name, f, "application/pdf")))
                data = {"is_public": "1" if is_public == "Yes" else "0"}
                try:
                    res = requests.post(f"{BASE_URL}/user/pdf/upload", files=files, data=data, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Upload successful: {res.json()}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    elif menu == "Upload All PDFs from Folder":
        st.subheader("Upload All PDFs from Folder (Multi-file Upload)")
        st.markdown("Drag and drop all PDF files from your folder below. All selected files will be uploaded at once.")
        uploaded_files = st.file_uploader("Select multiple PDF files", type=["pdf"], accept_multiple_files=True, key="user_upload_folder_files")
        is_public = st.radio("Is public?", ["No", "Yes"], key="user_upload_folder_is_public")
        if st.button("Upload All PDFs"):
            if not uploaded_files:
                st.warning("Please select at least one PDF file.")
            else:
                files = []
                for f in uploaded_files:
                    files.append(("files", (f.name, f, "application/pdf")))
                data = {"is_public": "1" if is_public == "Yes" else "0"}
                try:
                    res = requests.post(f"{BASE_URL}/user/pdf/upload", files=files, data=data, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Upload successful: {res.json()}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    elif menu == "List My PDFs":
        st.subheader("My Uploaded PDFs")
        try:
            res = requests.get(f"{BASE_URL}/user/pdf", auth=auth)
            if res.status_code == 200:
                pdfs = res.json().get("pdfs", [])
                if pdfs:
                    st.table(pdfs)
                else:
                    st.info("No PDFs uploaded yet.")
            else:
                st.error(f"Failed to fetch PDFs: {res.text}")
        except Exception as e:
            st.error(f"Error: {e}")
    elif menu == "Ingest a PDF":
        st.subheader("Ingest a PDF")
        # Fetch user's PDFs for selection
        try:
            res = requests.get(f"{BASE_URL}/user/pdf", auth=auth)
            if res.status_code == 200:
                pdfs = res.json().get("pdfs", [])
                filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
            else:
                filenames = []
                st.error(f"Failed to fetch PDFs: {res.text}")
        except Exception as e:
            filenames = []
            st.error(f"Error: {e}")
        if filenames:
            selected_file = st.selectbox("Select a PDF to ingest", filenames)
            if st.button("Ingest Selected PDF"):
                try:
                    res = requests.post(f"{BASE_URL}/user/vectordb/ingest/one/{selected_file}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Ingestion successful: {res.json()}")
                    else:
                        st.error(f"Ingestion failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No PDFs available to ingest.")
    elif menu == "Ingest All My PDFs":
        st.subheader("Ingest All My PDFs")
        if st.button("Ingest All"):
            try:
                res = requests.post(f"{BASE_URL}/user/vectordb/ingest/all", auth=auth)
                if res.status_code == 200:
                    st.success(f"All PDFs ingested: {res.json()}")
                else:
                    st.error(f"Ingestion failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    elif menu == "List My Ingested PDFs":
        st.subheader("My Ingested PDFs")
        try:
            res = requests.get(f"{BASE_URL}/user/ingested_pdfs", auth=auth)
            if res.status_code == 200:
                ingested = res.json().get("ingested_pdfs", [])
                if ingested:
                    st.table(ingested)
                else:
                    st.info("No PDFs ingested yet.")
            else:
                st.error(f"Failed to fetch ingested PDFs: {res.text}")
        except Exception as e:
            st.error(f"Error: {e}")
    elif menu == "Delete a PDF from Storage":
        st.subheader("Delete a PDF from Storage")
        # Fetch user's PDFs for selection
        try:
            res = requests.get(f"{BASE_URL}/user/pdf", auth=auth)
            if res.status_code == 200:
                pdfs = res.json().get("pdfs", [])
                filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
            else:
                filenames = []
                st.error(f"Failed to fetch PDFs: {res.text}")
        except Exception as e:
            filenames = []
            st.error(f"Error: {e}")
        if filenames:
            selected_file = st.selectbox("Select a PDF to delete from storage", filenames)
            if st.button("Delete Selected PDF from Storage"):
                try:
                    res = requests.post(f"{BASE_URL}/user/pdf/delete", json={"filenames": [selected_file]}, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Deleted: {res.json()}")
                    else:
                        st.error(f"Delete failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No PDFs available to delete.")
    elif menu == "Delete All My PDFs from Storage":
        st.subheader("Delete All My PDFs from Storage")
        try:
            res = requests.get(f"{BASE_URL}/user/pdf", auth=auth)
            if res.status_code == 200:
                pdfs = res.json().get("pdfs", [])
                filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
            else:
                filenames = []
                st.error(f"Failed to fetch PDFs: {res.text}")
        except Exception as e:
            filenames = []
            st.error(f"Error: {e}")
        if filenames:
            if st.button("Delete All PDFs from Storage"):
                try:
                    res = requests.post(f"{BASE_URL}/user/pdf/delete", json={"filenames": filenames}, auth=auth)
                    if res.status_code == 200:
                        st.success(f"All PDFs deleted: {res.json()}")
                    else:
                        st.error(f"Delete failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No PDFs available to delete.")
    elif menu == "Remove a PDF from VectorDB":
        st.subheader("Remove a PDF from VectorDB")
        # Fetch user's PDFs for selection
        try:
            res = requests.get(f"{BASE_URL}/user/pdf", auth=auth)
            if res.status_code == 200:
                pdfs = res.json().get("pdfs", [])
                filenames = [pdf["filename"] for pdf in pdfs] if pdfs else []
            else:
                filenames = []
                st.error(f"Failed to fetch PDFs: {res.text}")
        except Exception as e:
            filenames = []
            st.error(f"Error: {e}")
        if filenames:
            selected_file = st.selectbox("Select a PDF to remove from VectorDB", filenames)
            if st.button("Remove Selected PDF from VectorDB"):
                try:
                    res = requests.delete(f"{BASE_URL}/user/vectordb/pdf/one/{selected_file}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Removed from VectorDB: {res.json()}")
                    else:
                        st.error(f"Remove failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("No PDFs available to remove.")
    elif menu == "Remove All My PDFs from VectorDB":
        st.subheader("Remove All My PDFs from VectorDB")
        if st.button("Remove All from VectorDB"):
            try:
                res = requests.delete(f"{BASE_URL}/user/vectordb/pdf/all", auth=auth)
                if res.status_code == 200:
                    st.success(f"All PDFs removed from VectorDB: {res.json()}")
                else:
                    st.error(f"Remove failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Feature UI coming soon...") 