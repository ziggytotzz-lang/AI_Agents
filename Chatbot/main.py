from fastapi import FastAPI  # FastAPI framework for creating the web application
from pydantic import BaseModel  # BaseModel for structured data data models
from typing import List  # List type hint for type annotations
from langchain_community.tools.tavily_search import TavilySearchResults  # TavilySearchResults tool for handling search results from Tavily
import os  # os module for environment variable handling
from langgraph.prebuilt import create_react_agent  # Function to create a ReAct agent
from langchain_openai import ChatOpenAI    # ChatGroq class for interacting with LLMs
from dotenv import load_dotenv
load_dotenv()

# Retrieve and set API keys for external tools and services
api_key = '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'  # Groq API key
os.environ["TAVILY_API_KEY"] = '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'  # Set Tavily API key

# Predefined list of supported model names
MODEL_NAMES = [
    "gpt-4o-mini",
    "gpt-4o"
]

# Initialize the TavilySearchResults tool with a specified maximum number of results.
tool_tavily = TavilySearchResults(max_results=2)  # Allows retrieving up to 2 results

# Combine the TavilySearchResults and ExecPython tools into a list.
tools = [tool_tavily, ]

# FastAPI application setup with a title
app = FastAPI(title='LangGraph AI Agent')

class Message(BaseModel):
    role: str
    content: str

class RequestState(BaseModel):
    model_name: str  # Name of the model to use for processing the request
    system_prompt: str  # System prompt for initializing the model
    messages: List[Message]   # List of messages in the chat

@app.post("/chat")
def chat_endpoint(request: RequestState):
    """
    API endpoint to interact with the chatbot using LangGraph and tools.
    Dynamically selects the model specified in the request.
    """
    if request.model_name not in MODEL_NAMES:
        # Return an error response if the model name is invalid
        return {"error": "Invalid model name. Please select a valid model."}

    # Initialize the LLM with the selected model
    llm = ChatOpenAI(model=request.model_name,temperature=0)

    # Create a ReAct agent using the selected LLM and tools
    agent = create_react_agent(llm, tools=tools)

    # Create the initial state for processing
    state = {
        "messages": [
            {"role": "system", "content": request.system_prompt},
            *[msg.dict() for msg in request.messages]
        ]
    }

    # Process the state using the agent
    result = agent.invoke(state)  # Invoke the agent (can be async or sync based on implementation)

    # Return the result as the response
    return result

# Run the application if executed as the main script
if __name__ == '__main__':
    import uvicorn  # Import Uvicorn server for running the FastAPI app
    uvicorn.run(app, host='127.0.0.1', port=8000)  # Start the app on localhost with port 8000