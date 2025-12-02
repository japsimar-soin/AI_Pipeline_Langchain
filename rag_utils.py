import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from langchain_qdrant import QdrantVectorStore
from PyPDF2 import PdfReader
from langsmith import traceable
from qdrant_client import QdrantClient
from qdrant_client.http import models

qdrant_client = QdrantClient(":memory:", prefer_grpc=False)
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_DIM = len(embeddings_model.embed_query("dimension probe"))

rag_llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-base",
    task="text2text-generation",
    pipeline_kwargs={
        "max_new_tokens": 256,
        "temperature": 0.1,
    },
)

@traceable
def load_pdf(pdf_path: str):
    """Load and extract text from PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

@traceable
def create_vectorstore_from_pdf(
    pdf_path: str, 
    chunk_size: int = 500, 
    chunk_overlap: int = 50,
    collection_name: str = "pdf_collection"
):
    """Create a Qdrant vector store from a PDF document."""
    text = load_pdf(pdf_path)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)
    
    try:
        qdrant_client.get_collection(collection_name)
    except Exception:
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE,
            ),
        )

    vectordb = QdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embeddings_model
    )

    vectordb.add_texts(chunks)
    return vectordb

@traceable
def query_pdf_rag(vectordb, query: str, k: int = 3):
    """Query the PDF using RAG."""
    
    # Retrieve relevant chunks
    results = vectordb.similarity_search(query, k=k)
    context = "\n".join([r.page_content for r in results])
    
    prompt = f"""Answer the following question using only the provided context. 
    If the answer is not in the context, say "Not enough information."

    Context: {context}

    Question: {query}

    Answer:"""
    
    response = rag_llm.invoke(prompt)
    if isinstance(response, dict) and "generated_text" in response:
        return response["generated_text"]
    return str(response)

