from dotenv import load_dotenv
import os
import uuid
import time

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv(".env")
embedding = OpenAIEmbeddings()
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

CHAT_HISTORY_LIMIT = 10

PERSIST_DIR = os.getenv("PERSIST_DIR", ".\\chroma")
CHROMA_MEMORY_DIR = os.path.join(PERSIST_DIR, "chroma_memory")
CHROMA_PDF_DIR = os.path.join(PERSIST_DIR, "chroma_pdf")

######################################
# User message history embedding
######################################

def save_user_message(user_id, message):
    db = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embedding,
        persist_directory=CHROMA_MEMORY_DIR
    )
    # Fetch all existing messages
    all_docs = db.get()
    all_ids = all_docs["ids"]
    all_metadatas = all_docs["metadatas"]
    # Sort by timestamp (if present), else keep as is
    docs_with_time = []
    for idx, meta in enumerate(all_metadatas):
        ts = meta.get("timestamp", 0)
        docs_with_time.append((all_ids[idx], ts))
    docs_with_time.sort(key=lambda x: x[1])  # oldest first
    # If at or above limit, delete oldest so only (limit-1) remain
    if len(docs_with_time) >= CHAT_HISTORY_LIMIT:
        num_to_delete = len(docs_with_time) - (CHAT_HISTORY_LIMIT - 1)
        ids_to_delete = [doc[0] for doc in docs_with_time[:num_to_delete]]
        db.delete(ids=ids_to_delete)
    # Prepare new chunk(s) with timestamp
    now = time.time()
    doc = Document(page_content=message, metadata={"user_id": user_id, "timestamp": now})
    db.add_documents([doc], ids=[str(uuid.uuid4())])

def retrieve_user_memory(user_id, query, k=3):
    db = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embedding,
        persist_directory=CHROMA_MEMORY_DIR
    )
    results = db.similarity_search(query, k=k)
    # Filter out any docs with None or empty page_content
    filtered_results = [doc for doc in results if getattr(doc, "page_content", None)]
    return filtered_results

def get_all_history(user_id):
    db = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embedding,
        persist_directory=CHROMA_MEMORY_DIR
    )
    all_docs = db.get()
    docs = []
    for i, doc in enumerate(all_docs["documents"]):
        meta = all_docs["metadatas"][i]
        ts = meta.get("timestamp", 0)
        docs.append((ts, doc))
    docs.sort(key=lambda x: x[0])  # oldest to newest
    return [doc for ts, doc in docs]

def clear_history_by_user(user_id):
    db = Chroma(
        collection_name=f"user_{user_id}",
        embedding_function=embedding,
        persist_directory=CHROMA_MEMORY_DIR
    )
    db.delete_collection()

def clear_history_all():
    # Remove all user collections in memory dir
    client = Chroma(persist_directory=CHROMA_MEMORY_DIR, embedding_function=None)._client
    for col in client.list_collections():
        db = Chroma(
            collection_name=col.name,
            embedding_function=embedding,
            persist_directory=CHROMA_MEMORY_DIR
        )
        db.delete_collection()

######################################
# PDF embedding
######################################

def insert_new_chunks(chunks):
    db = Chroma(
        persist_directory=CHROMA_PDF_DIR,
        embedding_function=embedding
    )
    # Chunks should be a list of Document objects with metadata
    ids = [str(uuid.uuid4()) for _ in chunks]
    db.add_documents(chunks, ids=ids)
    return True

def get_available_user_ids():
    import re
    client = Chroma(persist_directory=CHROMA_MEMORY_DIR, embedding_function=None)._client
    user_ids = []
    for col in client.list_collections():
        match = re.match(r"user_(.+)", col.name)
        if match:
            user_ids.append(match.group(1))
    return user_ids

def get_pdf_sources():
    db = Chroma(
        persist_directory=CHROMA_PDF_DIR,
        embedding_function=embedding
    )
    all_docs = db.get()
    sources = set()
    for meta in all_docs["metadatas"]:
        if "source" in meta and "user_id" in meta:
            sources.add((meta["source"], meta["user_id"]))
    return [{"source": s, "ingested_by": u} for s, u in sources]

def retrieve_pdf_for_user(user_id, query, k=3):
    db = Chroma(
        persist_directory=CHROMA_PDF_DIR,
        embedding_function=embedding
    )
    all_docs = db.get()

    # Filter docs by user_id or is_public
    filtered_docs = []
    for i, meta in enumerate(all_docs["metadatas"]):
        # print(meta.get("user_id"), meta.get("is_public"))
        if meta.get("user_id") == user_id or meta.get("is_public") == 1:
            doc_text = all_docs["documents"][i]
            filtered_docs.append(Document(page_content=doc_text, metadata=meta))
    if not filtered_docs:
        return []

    # Create a temporary Chroma collection for filtered docs
    temp_db = Chroma.from_documents(filtered_docs, embedding=embedding)
    results = temp_db.similarity_search(query, k=k)
    return results

def clear_pdf_by_source(source_name):
    """
    Delete all vector chunks for a given PDF source that belong to the specified user.
    Only deletes chunks where both source (or filename) and user_id match.
    For public PDFs, only deletes the user's own ingested copy.
    """
    db = Chroma(
        persist_directory=CHROMA_PDF_DIR,
        embedding_function=embedding
    )
    all_docs = db.get()
    ids_to_delete = []
    for i, meta in enumerate(all_docs["metadatas"]):
        if (
            (meta.get("source") == source_name or meta.get("filename") == source_name)
            # and meta.get("user_id") == user_id
        ):
            ids_to_delete.append(all_docs["ids"][i])
    if ids_to_delete:
        db.delete(ids=ids_to_delete)

def clear_pdf_by_source_userid(source_name, user_id):
    """
    Delete all vector chunks for a given PDF source that belong to the specified user.
    Only deletes chunks where both source (or filename) and user_id match.
    For public PDFs, only deletes the user's own ingested copy.
    """
    db = Chroma(
        persist_directory=CHROMA_PDF_DIR,
        embedding_function=embedding
    )
    all_docs = db.get()
    ids_to_delete = []
    for i, meta in enumerate(all_docs["metadatas"]):
        if (
            (meta.get("source") == source_name or meta.get("filename") == source_name)
            and meta.get("user_id") == user_id
        ):
            ids_to_delete.append(all_docs["ids"][i])
    if ids_to_delete:
        db.delete(ids=ids_to_delete)


def clear_pdf_by_user(user_id):
    """
    Delete all vector chunks for all PDFs ingested by the specified user.
    Does not delete public PDFs ingested by other users.
    """
    db = Chroma(
        persist_directory=CHROMA_PDF_DIR,
        embedding_function=embedding
    )
    all_docs = db.get()
    ids_to_delete = []
    for i, meta in enumerate(all_docs["metadatas"]):
        if meta.get("user_id") == user_id:
            ids_to_delete.append(all_docs["ids"][i])
    if ids_to_delete:
        db.delete(ids=ids_to_delete)

def clear_all_pdf():
    client = Chroma(persist_directory=CHROMA_PDF_DIR, embedding_function=None)._client
    for col in client.list_collections():
        db = Chroma(
            collection_name=col.name,
            embedding_function=embedding,
            persist_directory=CHROMA_PDF_DIR
        )
        db.delete_collection()

if __name__ == "__main__":
    print("=== Vectordb Test ===")
    # Test user message history
    test_user = "testuser"
    print(f"Saving messages for user: {test_user}")
    save_user_message(test_user, "Hello, this is the first message.")
    save_user_message(test_user, "This is a follow-up message.")
    save_user_message(test_user, "Another message about AI.")
    print("All history:", get_all_history(test_user))
    print("Memory search for 'AI':", retrieve_user_memory(test_user, "AI", k=2))
    print("Clearing user history...")
    clear_history_by_user(test_user)
    print("All history after clear:", get_all_history(test_user))

    # Test PDF embedding
    from langchain_core.documents import Document
    print("\nInserting PDF chunks...")
    chunks = [
        Document(page_content="This is a PDF chunk about machine learning.", metadata={"user_id": test_user, "filename": "ml.pdf", "source": "ml.pdf", "is_public": 0}),
        Document(page_content="This is a public PDF chunk about AI.", metadata={"user_id": "otheruser", "filename": "ai.pdf", "source": "ai.pdf", "is_public": 1}),
    ]
    insert_new_chunks(chunks)
    print("PDF sources:", get_pdf_sources())
    print("Retrieve PDF for user (should get both public and own):", retrieve_pdf_for_user(test_user, "AI", k=2))
    print("Clearing PDF by source 'ml.pdf'...")
    clear_pdf_by_source("ml.pdf", test_user)
    print("Retrieve PDF for user after clear by source:", retrieve_pdf_for_user(test_user, "machine", k=2))
    print("Clearing all PDF data...")
    clear_all_pdf()
    print("Retrieve PDF for user after clear all:", retrieve_pdf_for_user(test_user, "AI", k=2))