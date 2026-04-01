"""
kb.py — Knowledge Base with ChromaDB vector search
===================================================
Loads .txt / .md files, splits into chunks,
embeds with ChromaDB's default embedder, stores locally.
"""

import os
import glob
import chromadb
from chromadb.utils import embedding_functions

CHUNK_SIZE    = 500   # characters per chunk
CHUNK_OVERLAP = 50    # overlap between chunks


def _chunk_text(text: str, filename: str) -> list[dict]:
    """Split text into overlapping chunks."""
    chunks = []
    start  = 0
    idx    = 0
    while start < len(text):
        end   = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({
                "id":     f"{filename}_{idx}",
                "text":   chunk,
                "source": filename,
            })
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx   += 1
    return chunks


class KnowledgeBase:
    def __init__(self, docs_folder: str = "docs"):
        self.docs_folder = docs_folder
        self.client      = chromadb.PersistentClient(path=".chromadb")
        self.ef          = embedding_functions.DefaultEmbeddingFunction()
        self.collection  = self.client.get_or_create_collection(
            name="kb_docs",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------ #
    #  Indexing                                                            #
    # ------------------------------------------------------------------ #
    def index_docs(self) -> int:
        """Read all docs, chunk them, upsert into ChromaDB."""
        all_chunks = []
        patterns   = [
            f"{self.docs_folder}/**/*.txt",
            f"{self.docs_folder}/**/*.md",
            f"{self.docs_folder}/*.txt",
            f"{self.docs_folder}/*.md",
        ]
        seen_files = set()
        for pattern in patterns:
            for filepath in glob.glob(pattern, recursive=True):
                if filepath in seen_files:
                    continue
                seen_files.add(filepath)
                filename = os.path.relpath(filepath, self.docs_folder)
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                if content:
                    all_chunks.extend(_chunk_text(content, filename))

        if not all_chunks:
            return 0

        # Upsert in batches of 100
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            self.collection.upsert(
                ids        = [c["id"]     for c in batch],
                documents  = [c["text"]   for c in batch],
                metadatas  = [{"source": c["source"]} for c in batch],
            )
        return len(seen_files)

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #
    def search(self, query: str, n_results: int = 5) -> list[dict]:
        """Return top-n relevant chunks for a query."""
        total = self.collection.count()
        if total == 0:
            return []
        results = self.collection.query(
            query_texts = [query],
            n_results   = min(n_results, total),
        )
        chunks = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            chunks.append({"text": doc, "source": meta.get("source", "unknown")})
        return chunks

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #
    def list_docs(self) -> list[str]:
        patterns = [
            f"{self.docs_folder}/**/*.txt",
            f"{self.docs_folder}/**/*.md",
            f"{self.docs_folder}/*.txt",
            f"{self.docs_folder}/*.md",
        ]
        files = set()
        for p in patterns:
            for f in glob.glob(p, recursive=True):
                files.add(os.path.relpath(f, self.docs_folder))
        return sorted(files)

    def total_chunks(self) -> int:
        return self.collection.count()
