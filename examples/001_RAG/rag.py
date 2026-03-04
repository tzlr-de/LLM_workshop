#!/usr/bin/env python

"""
= Installation =
1. Download and Install Ollama: https://ollama.com/download
2. Pull required llm models:
    ollama pull xxx
3. Install Anaconda or Miniconda: https://docs.anaconda.com/miniconda/install/
4. Create a new environment:
    conda create -n rag-demo python=3.12
    conda activate rag-demo
5. Install the required packages:
    pip install llama-index llama-index-llms-ollama llama-index-embeddings-ollama structlog
"""
import structlog
from configparser import ConfigParser
from pathlib import Path

from llama_index import core
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from tabulate import tabulate

logger = structlog.get_logger()
Settings = core.Settings

def read_configs(config_path):
    parser = ConfigParser()
    parser.read(config_path)
    configs = {}
    for section in parser.sections():
        configs[section] = {}
        for key, value in parser.items(section):
            try:
                configs[section][key] = eval(value)
            except Exception:
                configs[section][key] = value
    return configs

def setup_llm(*, model, temperature=0.75, topk=40, **ollama_params):
    global logger, Settings

    logger.info("Setting up LLM...")
    Settings.llm = Ollama(
        model=model,
        temperature=temperature,
        additional_kwargs=dict(
            topk=topk,
        ),
        **ollama_params
    )
    logger.info(f"LLM is ready: {Settings.llm.model}")

def setup_embed_model(model: str, **ollama_params):
    global logger, Settings
    logger.info("Setting up Embedding...")
    Settings.embed_model = OllamaEmbedding(model_name=model, **ollama_params)
    logger.info(f"Embedding is ready: {Settings.embed_model.model_name}")

def setup_index(document_path: str,
                chunk_size: int = 1024,
                chunk_overlap: int = 20,
                *, persist: bool = False) -> core.VectorStoreIndex:
    persist_path = None if not persist else Path(document_path) / f"local_store_{chunk_size}x{chunk_overlap}"
    logger.info(f"Setting up Vector Store Index using {chunk_size=}, {chunk_overlap=}...")

    Settings.chunk_size = chunk_size
    Settings.chunk_overlap = chunk_overlap

    if persist and Path(persist_path).exists():
        logger.info(f"Loading existing index from {persist_path}...")
        context = core.StorageContext.from_defaults(persist_dir=persist_path)
        index_store = core.load_index_from_storage(context)

    else:
        logger.info(f"Creating new index for documents in {document_path}...")
        reader = core.SimpleDirectoryReader(document_path)
        documents = reader.load_data(num_workers=4)
        index_store = core.VectorStoreIndex.from_documents(
            documents,
            show_progress=True,
        )
        if persist:
            logger.info(f"Storing index to {persist_path}...")
            index_store.storage_context.persist(persist_dir=persist_path)
        else:
            logger.info("Index persistence is disabled.")


    return index_store

def setup_query_engine(index: core.VectorStoreIndex, top_k: int = 4, response_mode: str = "compact") -> RetrieverQueryEngine:
    logger.info("Setting up Query Engine...")
    return index.as_query_engine(
        similarity_top_k=top_k,
        response_mode=response_mode,
    )

def start_chat(query_engine: RetrieverQueryEngine, query: str = None):

        logger.info("RAGDemo is ready!")
        last_query = ""
        single_run = False
        while True:
            print("=" * 50)

            # Get user input or use the provided query
            if query is not None:
                print(f"Running single query: {query}")
                single_run = True
            else:
                query = input("Enter query: ")
                if not query:
                    query = last_query
                last_query = query

                if not query or query.lower() in ["exit", "quit", "q"]:
                    logger.info("Exiting...")
                    break

            # Run the query
            response = query_engine.query(query)

            # Display the response and source nodes
            print("=" * 50)
            print("= Response =")
            print(response.response)

            rows = []
            for i, node_w_score in enumerate(response.source_nodes, 1):
                node = node_w_score.node
                fname = node.metadata.get("file_name", "None")
                rows.append((i, fname, node.start_char_idx, node.end_char_idx, f"{node_w_score.score:.4f}"))

            print("= Used files =")
            print(tabulate(rows, headers=["#", "File Name", "Start", "End", "Score"], tablefmt="fancy_grid"))

            if single_run:
                break
            query = None


def main(args):
    configs = read_configs(args.configs)
    ollama_params = configs.get("ollama")
    assert ollama_params is not None, "No 'ollama' section found in the config file."

    llm_params = configs.get("llm")
    assert llm_params is not None, "No 'llm' section found in the config file."
    setup_llm(**llm_params, **ollama_params)

    embed_params = configs.get("embedding")
    assert embed_params is not None, "No 'embedding' section found in the config file."
    setup_embed_model(**embed_params, **ollama_params)

    index = setup_index(args.document_path,
                        chunk_size=args.chunk_size,
                        chunk_overlap=args.chunk_overlap,
                        persist=True)

    query_engine_params = configs.get("query_engine")
    assert query_engine_params is not None, "No 'query_engine' section found in the config file."

    query_engine = setup_query_engine(index, **query_engine_params)


    start_chat(query_engine, query=args.query)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--document_path", "-docs", default="data/documents", help="Path to the document directory")
    parser.add_argument("--configs", "-conf", default="configs.conf", help="Path to the config file")
    parser.add_argument("--query", "-q", default=None, help="Optional query to run once and exit")
    parser.add_argument("--chunk_size", "-cs", type=int, default=256, help="Chunk size for text splitting")
    parser.add_argument("--chunk_overlap", "-co", type=int, default=10, help="Chunk overlap for text splitting")

    main(parser.parse_args())



"""
Testing queries:
- Ich würde gerne Bafög beantragen. Welche Unterlagen brauche ich dafür und wer ist die Ansprechperson für Bafög. Mein Nachname ist Lorsch
- was muss ich beachten, wenn ich einen Brunnen bohren will und welche Unterlagen muss ich dafür einreichen?
- Ich will eine Garage bauen. Bei wem muss ich die Baugenehmigung einreichen und wie lautet die telefonnummer
"""
