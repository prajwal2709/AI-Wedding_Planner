from models import model
from langchain.messages import HumanMessage
import logging
from langchain.agents import create_agent
from agents import delegate_to_subagent1,delegate_to_subagent2
from prompts import WEDDING_PLANNER_AGENT_PROMPT,USER_PROMPT_FOR_MAIN_AGENT


# configuration for logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logging.info("Asking user about their requirments")
user_requirments=input("please enter your requirments and preference for your wedding:")

# updating the system prompt with the user's requirements
updated_system_prompt=WEDDING_PLANNER_AGENT_PROMPT.format(requirements=user_requirments)

#creating main agent
logging.info("initializing main wedding planner agent")
main_wedding_planner_agent=create_agent(model=model,tools=[delegate_to_subagent2,delegate_to_subagent1],name="main_wedding_planner_agent",system_prompt=updated_system_prompt)

#invoking main_wedding_planner_agent
main_wedding_planner_agent_response=main_wedding_planner_agent.invoke({"messages":[HumanMessage(content=USER_PROMPT_FOR_MAIN_AGENT)]})

# printing the response from the main agent
print("\nMain Wedding Planner Agent's Response:")
print(main_wedding_planner_agent_response["messages"][-1].content)