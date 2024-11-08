from langchain.agents import AgentType, initialize_agent
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_openai import ChatOpenAI

import os
from dotenv import find_dotenv, load_dotenv
# activate api keys
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)
tools = [YahooFinanceNewsTool()]
agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

agent_chain.invoke(
	"What is the stock market's sentiment toward Lockheed Martin Corporation (LMT) after the 2024 U.S. presidential election?")

agent_chain.invoke(
    "Given the result of the 2024 U.S. presidential election, what is the earnings outlook in the 1st quarter of 2025 of RTX Corporation, formerly Raytheon Technologies Corporation?")