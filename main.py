import os

import chainlit as cl
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

os.environ["NVIDIA_API_KEY"] = "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"
os.environ["CHAINLIT_AUTH_SECRET"] = "Pm3sLU>rs+h$d7yRoCwCERUesF@Jc0TJnkgb=-ljbSeyf9AEcRdmEIR1sdJef9gN"


def bot():
    llm = ChatNVIDIA(model="mixtral_8x7b")
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    medibot_template = """You are a helpful AI medical assistant named MediBot. You will only reply to medical 
    queries. If something is out of context, you will refrain from replying and politely decline to respond to the 
    user.
    Chat History: {chat_history} Input: {input} Answer:"""

    prompt_template = PromptTemplate(
        input_variables=["chat_history", "input"],
        template=medibot_template
    )

    chain = LLMChain(prompt=prompt_template, llm=llm, memory=memory)

    return chain


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


# Chainlit
@cl.on_chat_start
async def start():
    chain = bot()
    msg = cl.Message(content="Starting...")
    await msg.send()
    msg.content = "Hi, I'm MediBot. How can I help you?"
    await msg.update()
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler()
    cb.answer_reached = True
    res = await chain.acall(message.content, callbacks=[cb])
    await cl.Message(res['text']).send()
