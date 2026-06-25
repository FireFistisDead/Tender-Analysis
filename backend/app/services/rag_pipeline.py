"""
RAG Pipeline for Tender Sustainability Analysis.
Handles document chunking, embedding, storage in ChromaDB, and retrieval.
"""

import json
import re
import logging
from pathlib import Path
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

from app.config import (
    CHUNK_SIZE, CHUNK_OVERLAP, CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL, TOP_K_RESULTS, COLLECTION_NAME,
    SDG_COLLECTION_NAME, KNOWLEDGE_DIR
)

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG pipeline: chunk → embed → store → retrieve.
    """

    def __init__(self):
        logger.info("Initializing RAG Pipeline...")
        self._embeddings = None
        self._sdg_store = None
        self._tender_stores = {}
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    @property
    def embeddings(self):
        if self._embeddings is None:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            self._embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
        return self._embeddings

    def initialize_sdg_knowledge(self):
        """Load SDG knowledge base into ChromaDB."""
        sdg_dir = str(CHROMA_PERSIST_DIR / "sdg_knowledge")
        if Path(sdg_dir).exists() and any(Path(sdg_dir).iterdir()):
            self._sdg_store = Chroma(
                collection_name=SDG_COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=sdg_dir
            )
            return

        documents = []
        for fname, key in [("sdg11_targets.json", "sdg11"), ("sdg12_targets.json", "sdg12")]:
            fpath = KNOWLEDGE_DIR / fname
            if not fpath.exists():
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for t in data["targets"]:
                txt = (
                    f"SDG {data['sdg']} - {data['name']}\n"
                    f"Target {t['id']}: {t['name']}\n"
                    f"Description: {t['description']}\n"
                    f"Procurement Criteria:\n" +
                    "\n".join(f"  - {c}" for c in t["procurement_criteria"])
                )
                documents.append(Document(
                    page_content=txt,
                    metadata={"source": key, "target_id": t["id"],
                              "target_name": t["name"], "type": "sdg_target"}
                ))

        std_path = KNOWLEDGE_DIR / "green_procurement_standards.json"
        if std_path.exists():
            with open(std_path, "r", encoding="utf-8") as f:
                stds = json.load(f)
            for s in stds["standards"]:
                txt = (
                    f"Standard: {s['name']}\n{s['description']}\n"
                    f"Relevance: {s['relevance']}\nRequirements:\n" +
                    "\n".join(f"  - {r}" for r in s["requirements"])
                )
                documents.append(Document(
                    page_content=txt,
                    metadata={"source": "standards", "standard_id": s["id"],
                              "type": "standard"}
                ))

        if documents:
            self._sdg_store = Chroma.from_documents(
                documents=documents, embedding=self.embeddings,
                collection_name=SDG_COLLECTION_NAME, persist_directory=sdg_dir
            )
            logger.info(f"SDG knowledge base: {len(documents)} docs indexed")

    def index_tender(self, upload_id: str, text: str, filename: str) -> int:
        """Chunk and index tender text into ChromaDB."""
        chunks = self._text_splitter.create_documents(
            texts=[text],
            metadatas=[{"upload_id": upload_id, "filename": filename}]
        )
        for chunk in chunks:
            pages = re.findall(r'\[PAGE (\d+)\]', chunk.page_content)
            chunk.metadata["page"] = int(pages[0]) if pages else 0

        persist_dir = str(CHROMA_PERSIST_DIR / f"tender_{upload_id}")
        store = Chroma.from_documents(
            documents=chunks, embedding=self.embeddings,
            collection_name=f"{COLLECTION_NAME}_{upload_id}",
            persist_directory=persist_dir
        )
        self._tender_stores[upload_id] = store
        logger.info(f"Indexed {len(chunks)} chunks for {upload_id}")
        return len(chunks)

    def retrieve_tender_context(self, upload_id: str, queries: List[str],
                                top_k: int = None) -> List[Document]:
        """Retrieve relevant chunks from a tender."""
        store = self._get_tender_store(upload_id)
        if not store:
            return []
        if top_k is None:
            top_k = TOP_K_RESULTS

        all_docs, seen = [], set()
        for q in queries:
            try:
                for doc in store.similarity_search(q, k=top_k):
                    h = hash(doc.page_content[:200])
                    if h not in seen:
                        seen.add(h)
                        all_docs.append(doc)
            except Exception as e:
                logger.error(f"Retrieval error: {e}")
        return all_docs

    def retrieve_sdg_context(self, queries: List[str], top_k: int = 3) -> List[Document]:
        """Retrieve SDG knowledge base entries."""
        if self._sdg_store is None:
            self.initialize_sdg_knowledge()
        if not self._sdg_store:
            return []

        all_docs, seen = [], set()
        for q in queries:
            try:
                for doc in self._sdg_store.similarity_search(q, k=top_k):
                    h = hash(doc.page_content[:200])
                    if h not in seen:
                        seen.add(h)
                        all_docs.append(doc)
            except Exception as e:
                logger.error(f"SDG retrieval error: {e}")
        return all_docs

    def chat_with_tender(self, upload_id: str, question: str) -> List[Document]:
        """Retrieve context for a user question."""
        store = self._get_tender_store(upload_id)
        if not store:
            return []
        try:
            return store.similarity_search(question, k=TOP_K_RESULTS)
        except Exception as e:
            logger.error(f"Chat retrieval error: {e}")
            return []

    def _get_tender_store(self, upload_id: str) -> Optional[Chroma]:
        if upload_id in self._tender_stores:
            return self._tender_stores[upload_id]
        d = str(CHROMA_PERSIST_DIR / f"tender_{upload_id}")
        if Path(d).exists():
            store = Chroma(
                collection_name=f"{COLLECTION_NAME}_{upload_id}",
                embedding_function=self.embeddings,
                persist_directory=d
            )
            self._tender_stores[upload_id] = store
            return store
        return None
