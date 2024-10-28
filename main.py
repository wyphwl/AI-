from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory, ConversationSummaryMemory, \
    ConversationSummaryBufferMemory
import streamlit as st
import pandas as pd
from ultil import get_chat_response

st.title("💗小妲己💗")


def set_api_key():
    api_key = st.text_input("请输入api密钥", type='password')
    sure1 = st.button("确定密钥")
    if sure1 and api_key:
        st.session_state["api_key"] = api_key
        st.info("密钥更新成功😁")
def set_memory(memory):
        if memory == "ConversationBufferWindowMemory":
            st.session_state["memory"] = ConversationBufferWindowMemory(return_messages=True, memory_key='chat_history',
                                                                        k=7)
        elif memory == "ConversationSummaryMemory":
            st.session_state["memory"] = ConversationSummaryMemory(return_messages=True, memory_key='chat_history',
                                                                   llm=st.session_state["model"])
        elif memory == "ConversationSummaryBufferMemory":
            st.session_state["memory"] = ConversationSummaryBufferMemory(llm=st.session_state["model"],
                                                                         max_token_limit=3000, memory_key='chat_history',
                                                                         return_messages=True)
        else:
            st.session_state["memory"] = ConversationBufferMemory(return_messages=True, memory_key='chat_history')
def set_model_param():
    st.session_state["model"]=model
    set_memory(memory)
    st.session_state["temperature"]=temperature



st.markdown("<br><br>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "AI", "content": "你好，我是小妲己，有什么可以帮助主人的呀？"}]


for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()
if  "memory" not in st.session_state:
    st.info("请确定参数")
if prompt:
    if "api_key" not in st.session_state:
        st.info("请先提供密码小妲己才能工作哟")
        st.stop()
    st.session_state["messages"].append({"role": "human", "content": prompt})
    st.chat_message("human").write(prompt)
    with st.spinner("让我想想昂🤔"):
        response = get_chat_response(st.session_state["model"], prompt, st.session_state["memory"],
                                     st.session_state["api_key"],
                                     st.session_state["temperature"])
        message = {'role': 'AI', 'content': response}
        st.session_state["messages"].append(message)
        st.chat_message("ai").write(message['content'])

if "messages_list" not in st.session_state:
    st.session_state["messages_list"] = []
if "conditions" not in st.session_state:
    st.session_state["conditions"] = []
if "chat_number" not in st.session_state:
    st.session_state["chat_number"] = 0


def save_dialog():  # 保存对话
    condition = [st.session_state["model"], st.session_state["temperature"], st.session_state["memory"]]
    st.session_state["conditions"].append(condition)
    st.session_state["messages_list"].append(st.session_state["messages"])
    st.session_state["memory"]=ConversationBufferMemory(return_messages=True, memory_key='chat_history')
    st.session_state["messages"]=st.session_state["messages"] = [{"role": "AI", "content": "你好，我是小妲己，有什么可以帮助主人的呀？"}]
    st.session_state["model"]="gpt-4o"
    st.session_state["temperature"]=1


def load_dialog(a):  # 加载对话
    st.session_state["model"] = st.session_state["conditions"][a][0]
    st.session_state["temperature"] = st.session_state["conditions"][a][1]
    st.session_state["memory"] = st.session_state["conditions"][a][2]
    st.session_state["messages"] = st.session_state["messages_list"][a]


with st.sidebar:
    set_api_key()
    tab1, tab2, tab3 = st.tabs(['model', 'memory', 'temperature'])
    with tab1:
        model = st.selectbox("请选择你想使用的模型",
                             ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-4-32k"],
                             index=0)
    with tab2:
        memory = st.selectbox("请选择你想使用的记忆",
                              ["ConversationBufferMemory", "ConversationBufferWindowMemory",
                               "ConversationSummaryMemory",
                               "ConversationSummaryBufferMemory"], index=0)
    with tab3:
        temperature = st.slider("请选择生成内容的多样性", min_value=0.10, max_value=1.25, value=1.00,
                                step=0.05)
    if st.button("确定参数"):
        set_model_param()
        st.info("更改成功")
    st.divider()
    if st.button("创建新对话"):
        with st.spinner("正在保存🏳"):
            save_dialog()
        st.session_state["chat_number"] += 1
    if (st.session_state["chat_number"]) != 0:
        for a in range(st.session_state["chat_number"] - 1):
            if st.button(f"对话{a + 1}"):
                load_dialog(a)

with st.expander("使用说明"):
    '''
    1.第一次对话需要手动选择参数，之后创建新对话则默认参数（gpt-4o,ConversationBufferMemory,1）,建议在开始一段对话前就将参数设置好，且中途不再改参数，
      否则历史对话会丢失
    
    2.model说明：
    
        gpt-4-32K>gpt-4>gpt-4o>gpt-4o-mini{价格分别每一百万token(大概70万字,包括输入,输出)为60，30，2.5，0.15[单位:美元](官网定价)}
        
    3.记忆说明（也可衡量价格）：
    
        ConversationBufferMemory：将你的历史对话全部传入（算作输入）
        
        ConversationBufferWindowMemory：只将7轮内的对话传入
        
        ConversationSummaryMemory：将历史对话总结再传入（总结会自动调用模型会消耗token）
        
        ConversationSummaryBufferMemory:将历史对话总结且只保留3000token的信息（比较鸡肋）
        
        再说明：无论选择哪种，都有一个上限，这个上限包括输入输出和历史对话，超过则历史对话保存不全或者回答会回不全（被截断）（gpt-4-32k中的32k就表示token上限）
        
    4.AI并不是无所不能，你的要求越明确，它的回答可能越令人满意。
    
      好的提示:
      
        1.把指令放在提示的开头，并且用###或"""来分隔指令和上下文

        2.尽可能对上下文和输出的长度，格式，风格等给出具体，描述性，详细的要求
                
        3.通过一些例子来阐明想要的输出格式
                
        4.先从零样本提示开始，效果不好，则用简单样本(小样本)提示
                
        5.减少空洞和不严谨的描述
                
        6.尽量告知其应该做什么，而不是不应该做什么
    '''
