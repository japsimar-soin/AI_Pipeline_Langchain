import pytest
from rag_utils import create_vectorstore_from_pdf, query_pdf_rag
import os

def test_pdf_exists():
    """Test that sample PDF exists."""
    assert os.path.exists("pdf_doc.pdf"), "pdf_doc.pdf not found"

def test_create_vectorstore():
    """Test vector store creation."""
    if not os.path.exists("pdf_doc.pdf"):
        pytest.skip("PDF file not found")
    
    vstore = create_vectorstore_from_pdf("pdf_doc.pdf")
    assert vstore is not None

def test_pdf_query():
    """Test PDF query using RAG."""
    if not os.path.exists("pdf_doc.pdf"):
        pytest.skip("PDF file not found")
    
    vstore = create_vectorstore_from_pdf("pdf_doc.pdf")
    answer = query_pdf_rag(vstore, "What is this document about?")
    assert len(answer) > 0
    assert "Error" not in answer
