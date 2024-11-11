from dash import Dash, dcc, callback, Input, Output, no_update
import plotly.express as px
import pandas as pd
from tavily import TavilyClient
from langgraph.checkpoint.memory import MemorySaver  # an in-memory checkpointer
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
import os

current_dir_path = os.getcwd()
# relative path of the sibling directory that contains the .env file
sibling_dir_path = os.path.join(current_dir_path, "..", "agents_company_financials")
dotenv_path = find_dotenv(sibling_dir_path)
load_dotenv(dotenv_path)   # change to use Groq
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@tool
def search_web(query: str):
    """Uses the tavily web search tool to answer the user's question."""
    print(f"performing web search for: {query}")
    return tavily_client.search(query)


model = ChatOpenAI(model="gpt-4o")
tools = [search_web]
system_message = """You are an experienced web researcher that is an expert in arms trade and defense companies.
When a user asks you about the main defense companies that make armamnet in a particular country, you will give them 3 to 5 
companies with a one sentence description of that company."""

memory = MemorySaver()
langgraph_agent_executor = create_react_agent(
    model, tools, state_modifier=system_message, checkpointer=memory
)

config = {"configurable": {"thread_id": "test-thread"}}


df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/refs/heads/master/AI/Arms-Trade/country%20trade%20register.csv")

app = Dash()
app.layout = [
    dcc.RadioItems(["Supplier", "Recipient"], value="Supplier", id="radio-btn"),
    dcc.RangeSlider(
        min=df["Delivery year"].min(),
        max=df["Delivery year"].max(),
        step=1,
        value=[df["Delivery year"].min(), df["Delivery year"].max() - 13],
        id="years",
        marks={
            2000: "2000",
            2002: "02",
            2004: "04",
            2006: "06",
            2008: "08",
            2010: "2010",
            2012: "12",
            2014: "14",
            2016: "16",
            2018: "18",
            2020: "20",
            2022: "22",
            2023: "2023",
        },
    ),
    dcc.Graph(id="my-graph"),
    dcc.Markdown(id='search-area')
]


@callback(
    Output("my-graph", "figure"),
    Input("radio-btn", "value"),
    Input("years", "value"),
)
def update_graph(selected_value, selected_years):
    # print(selected_years)
    # [2000,2023]
    if selected_years[0] == selected_years[1]:
        dff = df[df["Delivery year"] == selected_years[0]]
    else:
        dff = df[
            df["Delivery year"].isin(range(selected_years[0], selected_years[1] + 1))
        ]
        # print(dff['Delivery year'].unique())
    if selected_value == "Supplier":
        fig = px.treemap(
            dff,
            path=[px.Constant("all"), selected_value, "Recipient", "Armament category"],
            values="Numbers delivered",
            title=f"Suppliers of Armaments from {selected_years[0]} to {selected_years[1]}",
            height=650,
        )
    else:
        fig = px.treemap(
            dff,
            path=[px.Constant("all"), selected_value, "Supplier", "Armament category"],
            values="Numbers delivered",
            title=f"Recipients of Armaments from {selected_years[0]} to {selected_years[1]}",
            height=650,
        )

    fig.update_layout(margin=dict(l=10, r=10, t=30, b=30))
    return fig


@callback(
    Output('search-area', 'children'),
    Input("my-graph", "clickData"),
    prevent_initial_call=True
)
def country_info(clicked):
    print(f"Label is: {clicked['points'][0]['label']}")
    print(f"Value is: {clicked['points'][0]['value']}")
    print(f"Parent is: {clicked['points'][0]['parent']}")

    label_tree = clicked['points'][0]['label']
    parent_tree = clicked['points'][0]['parent']

    if parent_tree == 'all': # then we know that a supplier country was clicked which is saved under the label_tree
        response = langgraph_agent_executor.invoke(
            {
                "messages": [
                    ("user", f"What are the main defense companies that make armamnet in the {label_tree}?")
                ]
            },
            config,
        )["messages"][-1].content

        print(response)

        return response
    else:
        return no_update



if __name__ == "__main__":
    app.run_server(debug=False)