import streamlit as st
import requests
import pandas as pd
import os

# --- Page Configuration and Access Control ---
st.set_page_config(page_title="User Dashboard", layout="wide")

if not st.session_state.get('logged_in') or st.session_state.get('role') != 'user':
    st.error("You do not have permission to view this page. Please log in as a User.")
    st.stop()

# --- Shared Variables ---
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
auth = st.session_state.get('auth')
username = st.session_state.get('username')

# --- Helper Functions ---
def get_my_pdfs():
    try:
        res = requests.get(f"{BASE_URL}/user/pdf", auth=auth)
        if res.status_code == 200:
            return res.json().get("pdfs", [])
        return []
    except Exception:
        return []

def get_my_ingested_pdfs():
    try:
        res = requests.get(f"{BASE_URL}/user/ingested_pdfs", auth=auth)
        if res.status_code == 200:
            return res.json().get("ingested_pdfs", [])
        return []
    except Exception:
        return []

# --- Main UI ---
st.title(f"👋 Welcome, {username}!")

menu = st.sidebar.radio("User Menu", [
    "Chat",
    "Data Management",
    "VectorDB Management",
])

st.header(menu)

# --- Chat ---
if menu == "Chat":
    st.subheader("Chat with the RAG Model")

    # Display chat messages from history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                payload = {"user_id": username, "message": prompt}
                res = requests.post(f"{BASE_URL}/user/chat", json=payload, auth=auth)
                if res.status_code == 200:
                    full_response = res.json().get("response", "Sorry, I encountered an error.")
                else:
                    full_response = f"Error: {res.text}"
            except Exception as e:
                full_response = f"An error occurred: {e}"
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# --- Data Management ---
elif menu == "Data Management":
    tabs = st.tabs(["Upload PDFs (Files)", "Upload from Folder", "List & Delete My PDFs"])

    with tabs[0]: # Upload Files
        st.subheader("Upload Your PDF Documents")
        with st.form("user_upload_form"):
            uploaded_files = st.file_uploader("Select PDF files", type=["pdf"], accept_multiple_files=True, key="user_file_uploader")
            is_public = st.radio("Make these PDFs public for all users?", ("No", "Yes"), index=0, key="user_public_radio")
            submitted = st.form_submit_button("Upload Files")
            if submitted and uploaded_files:
                files_to_send = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                data = {"is_public": 1 if is_public == "Yes" else 0}
                try:
                    res = requests.post(f"{BASE_URL}/user/pdf/upload", files=files_to_send, data=data, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Successfully uploaded: {', '.join(res.json().get('uploaded', []))}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[1]: # Upload from Folder
        st.subheader("Upload All PDFs from a Folder")
        st.info("Use this option to upload all PDF files from a local folder. In the file dialog, navigate to your folder and select all files (e.g., using Ctrl+A).")
        with st.form("user_folder_upload_form"):
            folder_files = st.file_uploader("Select all PDF files from a folder", type=["pdf"], accept_multiple_files=True, key="user_folder_uploader")
            folder_is_public = st.radio("Make these PDFs public?", ("No", "Yes"), index=0, key="user_folder_public_radio")
            folder_submitted = st.form_submit_button("Upload Folder Contents")
            if folder_submitted and folder_files:
                files_to_send = [("files", (f.name, f.getvalue(), f.type)) for f in folder_files]
                data = {"is_public": 1 if folder_is_public == "Yes" else 0}
                try:
                    res = requests.post(f"{BASE_URL}/user/pdf/upload", files=files_to_send, data=data, auth=auth)
                    if res.status_code == 200:
                        st.success(f"Successfully uploaded: {', '.join(res.json().get('uploaded', []))}")
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[2]: # List & Delete
        st.subheader("Manage Your Stored PDFs")
        my_pdfs = get_my_pdfs()
        if my_pdfs:
            df = pd.DataFrame(my_pdfs)
            st.dataframe(df, use_container_width=True)
            
            st.markdown("---")
            st.markdown("#### Delete PDFs")
            filenames_to_delete = st.multiselect("Select your PDFs to delete from storage", [pdf['filename'] for pdf in my_pdfs])
            if st.button("Delete Selected PDFs", type="primary"):
                if filenames_to_delete:
                    try:
                        res = requests.post(f"{BASE_URL}/user/pdf/delete", json={"filenames": filenames_to_delete}, auth=auth)
                        if res.status_code == 200:
                            st.success(f"Deleted: {res.json().get('deleted')}")
                            if res.json().get('errors'):
                                st.warning(f"Errors: {res.json().get('errors')}")
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {res.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("You have not uploaded any PDFs yet.")

# --- VectorDB Management ---
elif menu == "VectorDB Management":
    tabs = st.tabs(["Ingest My PDFs", "List My Ingested PDFs", "Remove My PDF Data", "Clear My Chat Memory"])

    with tabs[0]: # Ingest
        st.subheader("Ingest Your PDFs into the VectorDB")
        st.info("Ingesting a PDF makes its content available for the chat model to use in its responses.")
        
        st.markdown("#### Ingest All of Your PDFs")
        if st.button("Ingest All My PDFs"):
            try:
                res = requests.post(f"{BASE_URL}/user/vectordb/ingest/all", auth=auth)
                if res.status_code == 200:
                    st.success("Successfully started ingestion for all your PDFs.")
                else:
                    st.error(f"Ingestion failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("#### Ingest a Specific PDF")
        my_pdf_list = [pdf['filename'] for pdf in get_my_pdfs()]
        filename_to_ingest = st.selectbox("Select one of your PDFs to ingest", my_pdf_list)
        if st.button("Ingest Selected PDF"):
            if filename_to_ingest:
                try:
                    res = requests.post(f"{BASE_URL}/user/vectordb/ingest/one/{filename_to_ingest}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Ingestion for '{filename_to_ingest}' started.")
                    else:
                        st.error(f"Ingestion failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[1]: # List Ingested
        st.subheader("List Your Ingested PDFs")
        my_ingested_pdfs = get_my_ingested_pdfs()
        if my_ingested_pdfs:
            st.dataframe(pd.DataFrame(my_ingested_pdfs), use_container_width=True)
        else:
            st.info("You have not ingested any PDFs yet.")

    with tabs[2]: # Remove Data
        st.subheader("Remove Your PDF Data from the VectorDB")
        st.warning("This does not delete the PDF file from storage, only its data from the chat model's knowledge base.")
        
        st.markdown("#### Remove All of Your PDF Data")
        if st.button("Remove All My PDF Data", type="primary"):
            try:
                res = requests.delete(f"{BASE_URL}/user/vectordb/pdf/all", auth=auth)
                if res.status_code == 200:
                    st.success("All your PDF data has been removed from the VectorDB.")
                else:
                    st.error(f"Removal failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
                
        st.markdown("---")
        st.markdown("#### Remove a Specific PDF's Data")
        my_ingested_list = [pdf['filename'] for pdf in get_my_ingested_pdfs()]
        filename_to_remove = st.selectbox("Select PDF data to remove", my_ingested_list)
        if st.button("Remove Selected PDF Data"):
            if filename_to_remove:
                try:
                    res = requests.delete(f"{BASE_URL}/user/vectordb/pdf/one/{filename_to_remove}", auth=auth)
                    if res.status_code == 200:
                        st.success(f"Data for '{filename_to_remove}' removed successfully.")
                        st.rerun()
                    else:
                        st.error(f"Removal failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tabs[3]: # Clear Memory
        st.subheader("Clear Your Chat History")
        st.warning("This will permanently delete your entire chat history from the VectorDB.")
        if st.button("Clear My Chat Memory", type="primary"):
            try:
                res = requests.delete(f"{BASE_URL}/user/vectordb/memory", auth=auth)
                if res.status_code == 200:
                    st.session_state.chat_history = []
                    st.success("Your chat history has been cleared.")
                else:
                    st.error(f"Failed to clear history: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")
