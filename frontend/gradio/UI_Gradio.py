import gradio as gr
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
import os
import logging
from typing import List, Tuple, Dict, Any

# --- Basic Logging Configuration ---
# This will print logs to your console, showing the app's activity.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

# --- Configuration ---
BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- API Helper Functions with Corrected Auth Handling and Robust JSON Parsing ---
def get_api_data(endpoint: str, auth_state: Dict[str, Any], key: str) -> list:
    """
    Generic function to fetch list data from an API endpoint with logging.
    This function is now robust and can handle responses that are either a direct
    JSON array (list) or a JSON object (dict) containing the data under a specific key.
    """
    logging.info(f"Attempting to GET data from endpoint: {endpoint}")
    auth_object = auth_state.get('auth') if auth_state else None
    if not auth_object:
        logging.warning(f"API call to {endpoint} failed: No auth object provided in auth_state.")
        return []
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", auth=auth_object, timeout=5)
        if res.status_code == 200:
            response_json = res.json()
            
            # --- FIX: Handle both list and dict responses ---
            if isinstance(response_json, dict):
                # Standard case: data is inside a dictionary with a key.
                data = response_json.get(key, [])
            elif isinstance(response_json, list):
                # Special case (like /admin/users): response is a direct list.
                data = response_json
            else:
                logging.error(f"Unexpected JSON response type from {endpoint}: {type(response_json)}")
                data = []
            # --- END OF FIX ---
            
            logging.info(f"Successfully fetched {len(data)} items from {endpoint}.")
            return data
        else:
            logging.error(f"API call to {endpoint} failed with status {res.status_code}: {res.text}")
            gr.Warning(f"Failed to fetch data from {endpoint}. Status: {res.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Exception during API call to {endpoint}: {e}")
        gr.Error(f"Connection Error: Could not reach the server at {BASE_URL}.")
        return []

def get_all_users(auth_state: Dict[str, Any]) -> List[str]:
    # The key "users" is now effectively ignored by get_api_data for this endpoint, but doesn't harm anything.
    users_data = get_api_data("admin/users", auth_state, "users")
    return [u['username'] for u in users_data]

def get_all_pdfs(auth_state: Dict[str, Any]) -> List[str]:
    pdfs_data = get_api_data("admin/pdf", auth_state, "pdfs")
    return [pdf['filename'] for pdf in pdfs_data]

def get_my_pdfs(auth_state: Dict[str, Any]) -> List[str]:
    pdfs_data = get_api_data("user/pdf", auth_state, "pdfs")
    return [pdf['filename'] for pdf in pdfs_data]

def get_my_ingested_pdfs(auth_state: Dict[str, Any]) -> List[str]:
    pdfs_data = get_api_data("user/ingested_pdfs", auth_state, "ingested_pdfs")
    return [pdf['filename'] for pdf in pdfs_data]

# --- Main Application Logic ---
def login(role: str, username: str, password: str):
    """Handles user/admin login with logging."""
    logging.info(f"Login attempt for user: '{username}', role: {role}")
    if not username or not password:
        gr.Warning("Username and password are required.")
        return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

    auth = HTTPBasicAuth(username, password)
    endpoint = "admin/auth/check" if role == "Admin" else "user/auth/check"
    
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", auth=auth, timeout=5)
        if res.status_code == 200:
            auth_state = {"role": role.lower(), "username": username, "auth": auth}
            gr.Info(f"{role} login successful!")
            logging.info(f"Login successful for user: '{username}'")
            return auth_state, gr.update(visible=False), gr.update(visible=role=="Admin"), gr.update(visible=role=="User")
        else:
            gr.Warning(f"{role} login failed: {res.text}")
            logging.warning(f"Login failed for user: '{username}'. Reason: {res.text}")
            return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)
    except requests.exceptions.RequestException as e:
        gr.Error(f"Connection Error: Is the backend server running at {BASE_URL}?")
        logging.error(f"Login connection error: {e}")
        return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False)

def logout():
    """Logs the user out and resets the UI."""
    logging.info("Logout triggered.")
    gr.Info("You have been logged out.")
    return None, gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), []

def handle_api_post(endpoint: str, auth_state: Dict[str, Any], json_data: dict = None, files_data: list = None, params: dict = None):
    """Handles POST requests with logging and provides user feedback."""
    logging.info(f"POST request to: {endpoint} with data: {json_data or 'files'}")
    auth_object = auth_state.get('auth') if auth_state else None
    if not auth_object:
        return gr.Error("Authentication is missing. Please log in again.")
    try:
        res = requests.post(f"{BASE_URL}/{endpoint}", auth=auth_object, json=json_data, files=files_data, params=params, timeout=15)
        if res.status_code == 200:
            response_data = res.json()
            gr.Info(f"Success: {response_data.get('detail') or response_data.get('message') or response_data.get('uploaded')}")
            logging.info(f"POST to {endpoint} successful. Response: {response_data}")
            return response_data
        else:
            gr.Warning(f"Failed: {res.text}")
            logging.warning(f"POST to {endpoint} failed. Status: {res.status_code}, Response: {res.text}")
    except Exception as e:
        gr.Error(f"An error occurred: {e}")
        logging.error(f"Exception on POST to {endpoint}: {e}")
    return None

def handle_api_delete(endpoint: str, auth_state: Dict[str, Any]):
    """Handles DELETE requests with logging and provides user feedback."""
    logging.info(f"DELETE request to: {endpoint}")
    auth_object = auth_state.get('auth') if auth_state else None
    if not auth_object:
        return gr.Error("Authentication is missing. Please log in again.")
    try:
        res = requests.delete(f"{BASE_URL}/{endpoint}", auth=auth_object, timeout=10)
        if res.status_code == 200:
            response_data = res.json()
            gr.Info(f"Success: {response_data.get('detail')}")
            logging.info(f"DELETE to {endpoint} successful.")
        else:
            gr.Warning(f"Failed: {res.text}")
            logging.warning(f"DELETE to {endpoint} failed. Status: {res.status_code}, Response: {res.text}")
    except Exception as e:
        gr.Error(f"An error occurred: {e}")
        logging.error(f"Exception on DELETE to {endpoint}: {e}")

# --- Chat Function ---
def user_chat(auth_state: dict, message: str, history: List[Tuple[str, str]]):
    """Handles the user's chat interaction with the backend."""
    if not message:
        return "", history
    logging.info(f"User '{auth_state.get('username')}' sent chat message: '{message}'")
    auth_object = auth_state.get('auth') if auth_state else None
    if not auth_object:
        history.append((message, "Authentication error. Please log out and log back in."))
        return "", history
    try:
        payload = {"user_id": auth_state['username'], "message": message}
        res = requests.post(f"{BASE_URL}/user/chat", json=payload, auth=auth_object)
        bot_response = res.json().get("response", "Sorry, an error occurred.") if res.status_code == 200 else f"Error: {res.text}"
    except Exception as e:
        bot_response = f"An error occurred: {e}"
        logging.error(f"Chat request failed: {e}")
    history.append((message, bot_response))
    return "", history

# --- UI Functions ---
def list_data(endpoint: str, auth_state: dict, key: str):
    """Fetches and displays data in a Gradio Dataframe."""
    logging.info(f"UI request to list data from '{endpoint}'")
    data = get_api_data(endpoint, auth_state, key)
    return pd.DataFrame(data) if data else pd.DataFrame()

def upload_files_action(auth_state: dict, files: list, is_public: str, role: str):
    """Handles the file upload action for both users and admins."""
    if not files:
        gr.Warning("Please select at least one file to upload.")
        return
    logging.info(f"'{role}' is uploading {len(files)} files.")
    files_to_send = [("files", (os.path.basename(f.name), open(f.name, "rb"), "application/pdf")) for f in files]
    data = {"is_public": 1 if is_public == "Yes" else 0}
    handle_api_post(f"{role}/pdf/upload", auth_state, files_data=files_to_send, params=data)

# --- Gradio UI Definition ---
with gr.Blocks(title="RAG Chatbot Portal") as demo:
    auth_state = gr.State()

    gr.Markdown("# RAG Chatbot Portal")

    # --- Login View ---
    with gr.Row(visible=True) as login_view:
        with gr.Column(scale=1):
            gr.Markdown("## Login")
            login_role = gr.Radio(["User", "Admin"], label="Select Role", value="User")
            login_username = gr.Textbox(label="Username", placeholder="Enter your username")
            login_password = gr.Textbox(label="Password", type="password", placeholder="Enter your password")
            login_btn = gr.Button("Login", variant="primary")

    # --- Admin View ---
    with gr.Column(visible=False) as admin_view:
        with gr.Row():
            gr.Markdown("# 👑 Admin Dashboard")
            logout_btn_admin = gr.Button("Logout")
        with gr.Tabs() as admin_tabs:
            with gr.Tab("User Management"):
                with gr.Tabs():
                    with gr.Tab("List Users"):
                        admin_users_df = gr.Dataframe(interactive=False)
                        admin_list_users_btn = gr.Button("Refresh User List")
                    with gr.Tab("Add User"):
                        with gr.Row():
                            admin_add_user_username = gr.Textbox(label="New Username")
                            admin_add_user_password = gr.Textbox(label="New Password", type="password")
                        admin_add_user_btn = gr.Button("Add User", variant="primary")
                    with gr.Tab("Delete User"):
                        admin_delete_user_select = gr.Dropdown(label="Select user to delete")
                        admin_delete_user_btn = gr.Button("Delete User", variant="stop")
                    with gr.Tab("Reset Password"):
                        admin_reset_pw_select = gr.Dropdown(label="Select user to reset password")
                        admin_reset_pw_new_pw = gr.Textbox(label="New Password", type="password")
                        admin_reset_pw_btn = gr.Button("Reset Password", variant="primary")
            with gr.Tab("Chat Management"):
                admin_chat_user_select = gr.Dropdown(label="Select user to view chat history")
                admin_view_chat_btn = gr.Button("View Chat History")
                admin_chat_history_display = gr.Textbox(label="Chat History", lines=10, interactive=False)
            with gr.Tab("Data Management"):
                with gr.Tabs():
                    with gr.Tab("Upload PDFs"):
                        admin_upload_files = gr.File(label="Select PDF files", file_count="multiple", file_types=[".pdf"])
                        admin_upload_is_public = gr.Radio(["No", "Yes"], label="Make these PDFs public?", value="No")
                        admin_upload_btn = gr.Button("Upload PDF(s)", variant="primary")
                    with gr.Tab("List & Delete PDFs"):
                        admin_pdfs_df = gr.Dataframe(interactive=False)
                        admin_list_pdfs_btn = gr.Button("Refresh PDF List")
                        admin_delete_files_select = gr.Dropdown(label="Select PDFs to delete", multiselect=True)
                        admin_delete_files_btn = gr.Button("Delete Selected PDFs", variant="stop")
                    with gr.Tab("Delete All Public PDFs"):
                        gr.Markdown("⚠️ **Warning:** This will delete all PDFs marked as public.")
                        admin_delete_public_btn = gr.Button("Delete ALL Public PDFs", variant="stop")
            with gr.Tab("VectorDB Management"):
                with gr.Tabs():
                    with gr.Tab("Ingest"):
                        gr.Markdown("### Ingest All Public PDFs")
                        admin_ingest_all_public_btn = gr.Button("Ingest All Public")
                        gr.Markdown("### Ingest Specific PDF")
                        admin_ingest_pdf_select = gr.Dropdown(label="Select PDF to ingest")
                        admin_ingest_type = gr.Radio(["Public", "Private"], label="Ingest as", value="Public")
                        admin_ingest_user_select = gr.Dropdown(label="Select User for Private Ingest", visible=False)
                        admin_ingest_specific_btn = gr.Button("Ingest Selected PDF")
                    with gr.Tab("Remove"):
                        gr.Markdown("### Remove by Filename")
                        admin_remove_pdf_select = gr.Dropdown(label="Select PDF data to remove")
                        admin_remove_pdf_btn = gr.Button("Remove PDF Data")
                        gr.Markdown("### Remove by User")
                        admin_remove_user_data_select = gr.Dropdown(label="Select user to remove all their data")
                        admin_remove_user_data_btn = gr.Button("Remove All Data for User", variant="stop")
                    with gr.Tab("List Ingested"):
                        admin_ingested_df = gr.Dataframe(interactive=False)
                        admin_list_ingested_btn = gr.Button("Refresh Ingested List")
                    with gr.Tab("Clear Memory"):
                        gr.Markdown("### Clear Specific User's Memory")
                        admin_clear_user_mem_select = gr.Dropdown(label="Select user")
                        admin_clear_user_mem_btn = gr.Button("Clear User Memory", variant="stop")
                        gr.Markdown("### Clear ALL Memory")
                        admin_clear_all_mem_btn = gr.Button("Clear ALL Users' Memory", variant="stop")

    # --- User View ---
    with gr.Column(visible=False) as user_view:
        with gr.Row():
            gr.Markdown(f"# 👋 User Dashboard")
            logout_btn_user = gr.Button("Logout")
        with gr.Tabs() as user_tabs:
            with gr.Tab("Chat"):
                user_chatbot = gr.Chatbot(label="RAG Chatbot", height=500)
                user_msg_box = gr.Textbox(label="Your Message", placeholder="Type a message and press Enter...", show_label=False)
                user_clear_chat_btn = gr.Button("Clear Chat")
            with gr.Tab("Data Management"):
                with gr.Tabs():
                    with gr.Tab("Upload PDFs"):
                        user_upload_files = gr.File(label="Select PDF files", file_count="multiple", file_types=[".pdf"])
                        user_upload_is_public = gr.Radio(["No", "Yes"], label="Make these PDFs public?", value="No")
                        user_upload_btn = gr.Button("Upload", variant="primary")
                    with gr.Tab("List & Delete My PDFs"):
                        user_pdfs_df = gr.Dataframe(interactive=False)
                        user_list_pdfs_btn = gr.Button("Refresh My PDF List")
                        user_delete_storage_select = gr.Dropdown(label="Select PDFs to delete", multiselect=True)
                        user_delete_storage_btn = gr.Button("Delete from Storage", variant="stop")
            with gr.Tab("VectorDB Management"):
                with gr.Tabs():
                    with gr.Tab("Ingest My PDFs"):
                        gr.Markdown("### Ingest All My PDFs")
                        user_ingest_all_btn = gr.Button("Ingest All My PDFs")
                        gr.Markdown("### Ingest a Specific PDF")
                        user_ingest_select = gr.Dropdown(label="Select one of your PDFs to ingest")
                        user_ingest_one_btn = gr.Button("Ingest Selected PDF")
                    with gr.Tab("List My Ingested PDFs"):
                        user_ingested_df = gr.Dataframe(interactive=False)
                        user_list_ingested_btn = gr.Button("Refresh Ingested List")
                    with gr.Tab("Remove PDF Data"):
                        gr.Markdown("### Remove All My PDF Data")
                        user_remove_all_data_btn = gr.Button("Remove All My Data", variant="stop")
                        gr.Markdown("### Remove Specific PDF Data")
                        user_remove_one_data_select = gr.Dropdown(label="Select PDF data to remove")
                        user_remove_one_data_btn = gr.Button("Remove Selected Data")
                    with gr.Tab("Clear My Chat Memory"):
                        gr.Markdown("⚠️ **Warning:** This will delete your entire chat history.")
                        user_clear_memory_btn = gr.Button("Clear My Chat Memory", variant="stop")

    # --- Event Handlers ---
    # Login/Logout
    login_btn.click(login, [login_role, login_username, login_password], [auth_state, login_view, admin_view, user_view])
    logout_btn_admin.click(logout, None, [auth_state, login_view, admin_view, user_view, user_chatbot])
    logout_btn_user.click(logout, None, [auth_state, login_view, admin_view, user_view, user_chatbot])

    # Dynamic Dropdown Updates
    def update_admin_dd(auth_st):
        logging.info("Updating admin dropdowns.")
        users = get_all_users(auth_st)
        pdfs = get_all_pdfs(auth_st)
        return gr.update(choices=users), gr.update(choices=users), gr.update(choices=users), gr.update(choices=pdfs), gr.update(choices=pdfs), gr.update(choices=users), gr.update(choices=pdfs), gr.update(choices=users), gr.update(choices=users)
    def update_user_dd(auth_st):
        logging.info("Updating user dropdowns.")
        pdfs = get_my_pdfs(auth_st)
        ingested_pdfs = get_my_ingested_pdfs(auth_st)
        return gr.update(choices=pdfs), gr.update(choices=pdfs), gr.update(choices=ingested_pdfs)
    
    admin_tabs.select(update_admin_dd, auth_state, [admin_delete_user_select, admin_reset_pw_select, admin_chat_user_select, admin_delete_files_select, admin_ingest_pdf_select, admin_ingest_user_select, admin_remove_pdf_select, admin_remove_user_data_select, admin_clear_user_mem_select])
    user_tabs.select(update_user_dd, auth_state, [user_delete_storage_select, user_ingest_select, user_remove_one_data_select])
    admin_ingest_type.change(lambda x: gr.update(visible=x=="Private"), admin_ingest_type, admin_ingest_user_select)

    # Admin Actions
    admin_list_users_btn.click(lambda auth: list_data("admin/users", auth, "users"), auth_state, admin_users_df)
    admin_add_user_btn.click(lambda auth, u, p: handle_api_post("admin/users", auth, json_data={"username":u, "password":p}), [auth_state, admin_add_user_username, admin_add_user_password], None).then(lambda auth: list_data("admin/users", auth, "users"), auth_state, admin_users_df)
    admin_delete_user_btn.click(lambda auth, u: handle_api_delete(f"admin/users/{u}", auth), [auth_state, admin_delete_user_select], None).then(lambda auth: list_data("admin/users", auth, "users"), auth_state, admin_users_df)
    admin_reset_pw_btn.click(lambda auth, u, p: handle_api_post(f"admin/users/{u}/reset_password", auth, json_data={"password":p}), [auth_state, admin_reset_pw_select, admin_reset_pw_new_pw], None)
    admin_view_chat_btn.click(lambda auth, u: "\n".join(get_api_data(f"admin/chat/history/{u}", auth, "history")), [auth_state, admin_chat_user_select], admin_chat_history_display)
    admin_upload_btn.click(lambda auth, f, p: upload_files_action(auth, f, p, "admin"), [auth_state, admin_upload_files, admin_upload_is_public], None).then(lambda auth: list_data("admin/pdf", auth, "pdfs"), auth_state, admin_pdfs_df)
    admin_list_pdfs_btn.click(lambda auth: list_data("admin/pdf", auth, "pdfs"), auth_state, admin_pdfs_df)
    admin_delete_files_btn.click(lambda auth, f: handle_api_post("admin/pdf/delete", auth, json_data={"filenames": f}), [auth_state, admin_delete_files_select], None).then(lambda auth: list_data("admin/pdf", auth, "pdfs"), auth_state, admin_pdfs_df)
    admin_delete_public_btn.click(lambda auth: handle_api_post("admin/pdf/delete_public", auth), auth_state, None).then(lambda auth: list_data("admin/pdf", auth, "pdfs"), auth_state, admin_pdfs_df)
    admin_ingest_all_public_btn.click(lambda auth: handle_api_post("admin/vectordb/ingest/all", auth), auth_state, None)
    admin_ingest_specific_btn.click(lambda auth, f, t, u: handle_api_post(f"admin/vectordb/ingest/{'private' if t=='Private' else 'public'}/{f}", auth, params={"user_id": u} if t=='Private' else None), [auth_state, admin_ingest_pdf_select, admin_ingest_type, admin_ingest_user_select], None)
    admin_remove_pdf_btn.click(lambda auth, f: handle_api_delete(f"admin/vectordb/pdf/{f}", auth), [auth_state, admin_remove_pdf_select], None)
    admin_remove_user_data_btn.click(lambda auth, u: handle_api_delete(f"admin/vectordb/pdf/user/{u}", auth), [auth_state, admin_remove_user_data_select], None)
    admin_list_ingested_btn.click(lambda auth: list_data("admin/vectordb/pdf", auth, "sources"), auth_state, admin_ingested_df)
    admin_clear_user_mem_btn.click(lambda auth, u: handle_api_delete(f"admin/vectordb/memory/{u}", auth), [auth_state, admin_clear_user_mem_select], None)
    admin_clear_all_mem_btn.click(lambda auth: handle_api_delete("admin/vectordb/memory", auth), auth_state, None)
    
    # User Actions
    user_msg_box.submit(user_chat, [auth_state, user_msg_box, user_chatbot], [user_msg_box, user_chatbot])
    user_clear_chat_btn.click(lambda: ([], None), None, [user_chatbot, user_msg_box], queue=False)
    user_upload_btn.click(lambda auth, f, p: upload_files_action(auth, f, p, "user"), [auth_state, user_upload_files, user_upload_is_public], None).then(lambda auth: list_data("user/pdf", auth, "pdfs"), auth_state, user_pdfs_df)
    user_list_pdfs_btn.click(lambda auth: list_data("user/pdf", auth, "pdfs"), auth_state, user_pdfs_df)
    user_delete_storage_btn.click(lambda auth, f: handle_api_post("user/pdf/delete", auth, json_data={"filenames": f}), [auth_state, user_delete_storage_select], None).then(lambda auth: list_data("user/pdf", auth, "pdfs"), auth_state, user_pdfs_df)
    user_ingest_all_btn.click(lambda auth: handle_api_post("user/vectordb/ingest/all", auth), auth_state, None)
    user_ingest_one_btn.click(lambda auth, f: handle_api_post(f"user/vectordb/ingest/one/{f}", auth), [auth_state, user_ingest_select], None)
    user_list_ingested_btn.click(lambda auth: list_data("user/ingested_pdfs", auth, "ingested_pdfs"), auth_state, user_ingested_df)
    user_remove_all_data_btn.click(lambda auth: handle_api_delete("user/vectordb/pdf/all", auth), auth_state, None)
    user_remove_one_data_btn.click(lambda auth, f: handle_api_delete(f"user/vectordb/pdf/one/{f}", auth), [auth_state, user_remove_one_data_select], None)
    user_clear_memory_btn.click(lambda auth: handle_api_delete("user/vectordb/memory", auth), auth_state, None).then(lambda: [], None, user_chatbot)

if __name__ == "__main__":
    demo.launch()
