from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from weather_api import fetch_weather
from rag_utils import create_vectorstore_from_pdf, query_pdf_rag
from llm_processor import process_text
from langsmith import traceable
from dotenv import load_dotenv
import os

load_dotenv()

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

class AgentState(TypedDict):
    question: str
    decision: Literal["weather", "pdf", None]
    raw_data: str
    processed_response: str

PDF_PATH = "pdf_doc.pdf"
pdf_vstore = None

@traceable
def initialize_vectorstore():
    """Initialize vector store if PDF exists."""
    global pdf_vstore
    if os.path.exists(PDF_PATH):
        pdf_vstore = create_vectorstore_from_pdf(PDF_PATH)
    return pdf_vstore

@traceable
def decide_node(state: AgentState) -> AgentState:
    """Decide whether to use weather API or PDF RAG."""
    question = state["question"].lower()
    
    weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"]
    
    if any(keyword in question for keyword in weather_keywords):
        words = state["question"].split()
        city = None
        if "in" in words:
            idx = words.index("in")
            if idx + 1 < len(words):
                city = words[idx + 1].strip(".,!?")
        else:
            city = words[-1].strip(".,!?")
        
        state["decision"] = "weather"
        state["raw_data"] = city or "Bangalore" 
    else:
        state["decision"] = "pdf"
        state["raw_data"] = state["question"]
    
    return state

@traceable
def weather_node(state: AgentState) -> AgentState:
    """Fetch weather data."""
    city = state["raw_data"]
    weather_data = fetch_weather(city)
    state["raw_data"] = weather_data
    return state

@traceable
def pdf_node(state: AgentState) -> AgentState:
    """Query PDF using RAG."""
    if pdf_vstore is None:
        state["raw_data"] = "Error: PDF vector store not initialized. Please ensure pdf_doc.pdf exists."
        return state
    
    question = state["raw_data"]
    answer = query_pdf_rag(pdf_vstore, question)
    state["raw_data"] = answer
    return state

@traceable
def process_node(state: AgentState) -> AgentState:
    """Process the raw data using LLM."""
    raw_data = state["raw_data"]
    processed = process_text(raw_data, task="format")
    state["processed_response"] = processed
    return state

def create_agent_graph():
    """Create and compile the LangGraph agent."""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("decide", decide_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("pdf", pdf_node)
    workflow.add_node("process", process_node)
    
    workflow.add_edge(START, "decide")
    workflow.add_conditional_edges(
        "decide",
        lambda state: state["decision"],
        {
            "weather": "weather",
            "pdf": "pdf"
        }
    )
    workflow.add_edge("weather", "process")
    workflow.add_edge("pdf", "process")
    workflow.add_edge("process", END)
    
    return workflow.compile()

# Initialize graph
agent_graph = None

def get_agent():
    """Get or create the agent graph."""
    global agent_graph, pdf_vstore
    if agent_graph is None:
        pdf_vstore = initialize_vectorstore()
        agent_graph = create_agent_graph()
    return agent_graph

def run_pipeline(question: str) -> str:
    """Run the complete pipeline."""
    agent = get_agent()
    
    initial_state: AgentState = {
        "question": question,
        "decision": None,
        "raw_data": "",
        "processed_response": ""
    }
    
    result = agent.invoke(initial_state)
    return result.get("processed_response", "No response generated.")
