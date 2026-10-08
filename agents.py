from tools import web_search
import logging
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.messages import HumanMessage
from models import model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s|%(levelname)s|%(message)s",
)
#creating subagents
logging.info("initializing subagent1..")
subagent1=create_agent(model=model,tools=[web_search],name="SubAgent1")

logging.info("initializing SubAgent2")
subagent2=create_agent(model=model,tools=[web_search],name="SubAgent2")

@tool
def delegate_to_subagent1(query:str)->str:
    """search the web for given topic by delegating task to subagent 1 to do so"""
    logging.info(f"delegating task to subagent1 {query}")
    response=subagent1.invoke({"messages":[HumanMessage(content=query)]})
    return response["messages"][-1].content


@tool
def delegate_to_subagent2(query:str)->str:
    """search the web for given topic by delegating task to subagent 2 to do so"""
    logging.info(f"delegating task to subagent1 {query}")
    response=subagent2.invoke({"messages":[HumanMessage(content=query)]})
    return response["messages"][-1].content