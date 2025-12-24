import os
from typing import TypedDict
from dotenv import load_dotenv

# LangGraph & Google Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LangGraph Imports
from langgraph.graph import StateGraph, START, END

# 1. Load Environment Variables
load_dotenv()

# ---------------------------------------------------------
# STEP 1: DEFINE THE STATE
# ---------------------------------------------------------
# The State is a dictionary that flows through the graph nodes.
class GraphState(TypedDict):
    topic: str
    summary: str

# ---------------------------------------------------------
# STEP 2: DEFINE THE NODES (Functions)
# ---------------------------------------------------------
def call_model(state: GraphState):
    """
    Node logic: Takes the topic from state, calls LLM, and updates the summary.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7 
    )
    
    template = """
    You are a helpful expert assistant. 
    Please write a short, 3-bullet-point summary about the following topic:

    Topic: {topic}

    Ensure the tone is professional and clear.
    """
    
    # We combine the logic here into one node
    chain = PromptTemplate.from_template(template) | llm | StrOutputParser()
    
    response = chain.invoke({"topic": state["topic"]})
    
    # Return the updated state
    return {"summary": response}

# ---------------------------------------------------------
# STEP 3: BUILD THE GRAPH
# ---------------------------------------------------------
workflow = StateGraph(GraphState)

# Add our single node
workflow.add_node("summarizer", call_model)

# Define the flow (Edges)
workflow.add_edge(START, "summarizer")
workflow.add_edge("summarizer", END)

# Compile the graph into an executable app
app = workflow.compile()

# ---------------------------------------------------------
# STEP 4: EXECUTION
# ---------------------------------------------------------


def main():
    print("--- LangGraph Summary Generator ---")
    print("Type 'quit' to exit.")
    
    while True:
        user_input = input("\nEnter a topic: ")
        
        if user_input.lower() in ["quit", "exit"]:
            break
            
        print(f"Generating summary for '{user_input}'...")
        
        try:
            # We pass the initial state to the graph
            # 'app.invoke' runs the graph until it reaches the END node
            initial_state = {"topic": user_input}
            final_output = app.invoke(initial_state)
            
            print("\nResult:")
            print(final_output["summary"])
            print("-" * 30)
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()