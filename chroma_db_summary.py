import sys
import os
sys.stderr = open(os.devnull, 'w')

from utils import sqlitedb
from utils.vectordb import get_pdf_sources, get_available_user_ids

if __name__ == "__main__":
    print("\n=== ChromaDB/SQLite Summary ===")
    users = sqlitedb.get_all_users()
    all_pdfs = sqlitedb.get_all_pdfs()
    all_ingested = sqlitedb.get_all_ingested_pdfs()
    user_ids = [u['userid'] for u in users]
    print(f"Users: {[u['userid'] for u in users]}")
    print("\n--- Per User ---")
    for user in user_ids:
        user_pdfs = [p for p in all_pdfs if p['uploaded_by'] == user]
        user_ingested = [i for i in all_ingested if i['ingested_by'] == user]
        print(f"\nUser: {user}")
        print(f"  Uploaded PDFs:")
        if user_pdfs:
            for p in user_pdfs:
                print(f"    - {p['filename']}")
        else:
            print("    (none)")
        print(f"  Ingested PDFs:")
        if user_ingested:
            for i in user_ingested:
                print(f"    - {i['filename']}")
        else:
            print("    (none)")
    print("\n--- Admin/Public ---")
    admin_pdfs = [p for p in all_pdfs if p['uploaded_by'] == 'admin']
    public_pdfs = [p for p in all_pdfs if p['is_public'] == 1]
    admin_ingested = [i for i in all_ingested if i['ingested_by'] == 'admin']
    public_ingested = [i for i in all_ingested if i['ingested_by'] == 'public']
    print(f"\nAdmin uploaded PDFs:")
    if admin_pdfs:
        for p in admin_pdfs:
            print(f"  - {p['filename']}")
    else:
        print("  (none)")
    print(f"Public PDFs:")
    if public_pdfs:
        for p in public_pdfs:
            print(f"  - {p['filename']}")
    else:
        print("  (none)")
    print(f"Admin ingested PDFs:")
    if admin_ingested:
        for i in admin_ingested:
            print(f"  - {i['filename']}")
    else:
        print("  (none)")
    print(f"Public ingested PDFs:")
    if public_ingested:
        for i in public_ingested:
            print(f"  - {i['filename']}")
    else:
        print("  (none)")
    print("\n--- ChromaDB PDF Sources ---")
    sources = get_pdf_sources()
    if sources:
        for s in sources:
            print(f"  Source: {s['source']}, Ingested by: {s['ingested_by']}")
    else:
        print("  (none)")
    print("\n--- ChromaDB User Collections ---")
    chroma_users = get_available_user_ids()
    print(f"Chroma user collections: {chroma_users}") 