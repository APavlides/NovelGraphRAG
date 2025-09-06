import os

from dotenv import load_dotenv

load_dotenv()

from llama_index.core import (SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex, load_index_from_storage)

INDEX_DIR = os.path.join(os.path.dirname(__file__), "..", "data_index")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "novel")

def build_index():
    # Load all .md and .yaml files as documents
    docs = SimpleDirectoryReader(DATA_DIR, recursive=True).load_data()
    # Build a vector index
    index = VectorStoreIndex.from_documents(docs)
    # Persist index to disk
    index.storage_context.persist(INDEX_DIR)
    print("Index built and saved to", INDEX_DIR)


def load_index():
    storage_context = StorageContext.from_defaults(persist_dir=INDEX_DIR)
    return load_index_from_storage(storage_context)


if __name__ == "__main__":
    build_index()
