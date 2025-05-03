from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

tools = [Tool(name="Search",
              description="Use this tool to search the web for information", func=search.run)]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = initialize_agent(
    tools=tools, 
    llm=llm, 
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True,
    max_iterations=3,
    )


if __name__ == "__main__":
    print("🤖 Agente ReAct activo. Escribe tu pregunta o 'exit' para salir.")
    while True:
        user_input = input("👤 Usuario: ")
        if user_input.lower() == "exit":
            print("👋 Adiós!")
            break
        response = agent.invoke({"input": user_input})
        print("🤖 Agente: ", response["output"])
