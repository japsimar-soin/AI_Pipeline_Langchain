import pytest
from llm_processor import process_text

def test_process_text():
    """Test LLM text processing."""
    test_text = "Artificial intelligence is a branch of computer science."
    result = process_text(test_text)
    assert len(result) > 0
    assert isinstance(result, str)

def test_process_text_summarize():
    """Test text summarization."""
    long_text = " ".join(["This is a sentence."] * 10)
    result = process_text(long_text, task="summarize")
    assert len(result) > 0
    assert len(result) < len(long_text)  # Summary should be shorter



