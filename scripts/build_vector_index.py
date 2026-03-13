from __future__ import annotations

# For Chroma persistent collections, "building the index" happens automatically.
# This script is kept for parity with the project structure and can be extended to
# run compaction/maintenance routines if needed.

from backend.config import get_settings


def main():
    s = get_settings()
    print(f"Chroma persistence dir: {s.chroma_persist_dir}")
    print(f"Collection: {s.rag_collection}")
    print("Nothing to build; Chroma indexes on upsert/query.")


if __name__ == "__main__":
    main()

