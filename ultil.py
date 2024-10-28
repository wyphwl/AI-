from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain import hub
from langchain.agents import create_structured_chat_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.agents.agent_toolkits import create_python_agent
from toolbox import TextLengthTool
from langchain.tools import Tool

def get_chat_response(model, inputting, memory, api_key, temperature):
    prompt = hub.pull("hwchase17/structured-chat-agent")
    client = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://api.gptsapi.net/v1",
        temperature=temperature,
    )
    python_agent_executor = create_python_agent(llm=client,tool=PythonREPLTool())
    tools = [
        Tool(
            name="Python代码工具",
            description=""""当你需要借助Python解释器，使用这个工具。
            用自然语言把要求给这个工具，他会生成Python代码并返回代码执行的结果。
            """,
            func=python_agent_executor.invoke),
        TextLengthTool()
    ]
    agent = create_structured_chat_agent(
        llm=client,
        tools=tools,
        prompt=prompt,
    )
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        handle_parsing_errors=True
    )
    # chain = ConversationChain(llm=client,memory=memory)
    response = agent_executor.invoke({"input": inputting})
    return response["output"]
