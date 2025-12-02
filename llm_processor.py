from langchain_huggingface import HuggingFacePipeline
from langsmith import traceable

hf_llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-base",
    task="text2text-generation",
    pipeline_kwargs={
        "max_new_tokens": 256,
        "temperature": 0.1,
    },
)

@traceable
def process_text(text: str, task: str = "summarize") -> str:
    """Process text using LLM."""
    if task == "summarize":
        prompt = f"Please provide a clear and concise summary:\n{text}"
    else:
        prompt = f"Please process and format this information clearly:\n{text}"
    
    result = hf_llm.invoke(prompt)

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    
    return str(result)