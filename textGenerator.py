# from langchain.llms import OpenAI
# from langchain import PromptTemplate, LLMChain
# import random
# # 
# def generate_quiz():
    
#     test_list =['금일', '사흘', '낭송', '사서', '고지식', '설빔']
#     joined_str = ','.join(test_list)
#     # template =""""" 아래의 단어를 문장에 넣어서 한국어 문장을 하나 만들고 같은 의미를 뜻하는 한국어 문장을 하나 더 만들어줘. 
#     # 질문:{question}"""
    
#     template =""""" {question}을 문장에 사용해서 빈칸 추론 문제를 만들거야. 4지 선다형 문제를 아래의 양식을 지켜 만들어줘.
#                     한국의 초등학교 저학년들의 문해력 향상을 위한 퀴즈야.

#                     --------------------------------------------------------
#                     문제1: {question}를 빈칸으로 하는 문장 예제

#                     선택지1:
#                     선택지2:
#                     선택지3:
#                     선택지4:

#                     해설: 해당 선택지 중에서 정답을 알려주고 정답인 이유 및 선택지의 의미 설명
#                     --------------------------------------------------------
#     질문:{question}"""

#     prompt = PromptTemplate.from_template(template)

#     llm = OpenAI()
#     llm_chain = LLMChain(prompt=prompt, llm=llm)
#     result = llm_chain.run(prompt.format(question=random.choice(text)))
#     return result

from dotenv import load_dotenv
load_dotenv()

import openai
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI
from langchain.utilities import SerpAPIWrapper 
from langchain.agents import initialize_agent 
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    temperature: float = 1

SYSTEM_MSG = "You are an expert in making quizzes to improbe the language of elementary school students in Korea."

#########################################################################################################
msg = input('무엇이 하고 싶으신가요?:')

def classify_intent(msg):
    prompt = f"""Your job is to classifiy intent.
    
    Choose one of the following intents:
    - make_quiz
    - word_question with the questioned word
    
    User: {msg}
    Intent:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    user_intent = response.choices[0].message.content.strip()
    return user_intent

user_intent =""

intent = classify_intent(msg)
print('intent:', intent)

if intent !="make_quiz":
    after_with = intent.split("the questioned word")[1].strip()
else:
    after_with = 0

# print('after_with:',after_with)
# print('after_with type:',type(after_with))
####################################################################
if intent == "make_quiz":
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name = "Current Search",
            func = search.run,
            description = "useful for when you need to answer questions about current events or the current state of the world"
        ),
    ]
    
    memory = ConversationBufferMemory(memory_key = "chat_history")
    
    llm = OpenAI(temperature = 0)
    agent_chain = initialize_agent(tools, llm, agent = AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory = memory)
    
    name ="남희주"
    agent_chain.run(input=f"안녕하세요. {name} 어린이. 만나서 반가워요!")
    
    test_list = ['금일', '사흘', '낭송', '사서', '고지식', '설빔']
    joined_str = ','.join(test_list)
    
    ex_quiz = agent_chain.run(input=f"""
                              ({joined_str}) 중에 한 가지를 랜덤하게 선택해줘.
                              """)
    agent_chain.run(input=f"""
                    {ex_quiz}를 사용해서, 상황에 맞는 선택지를 고르는 4지 선다형 문제를 아래의 양식을 지켜 만들어줘.
                    한국의 초등학교 저학년들의 문해력 향상을 위한 퀴즈야.

                    --------------------------------------------------------
                    문제1: {ex_quiz} 중 선택된 단어를 활용한 상황 예제

                    선택지1:
                    선택지2:
                    선택지3:
                    선택지4:

                    해설: 해당 선택지가 정답인 이유 및 선택지의 의미 설명
                    --------------------------------------------------------
                    """)
    
elif intent != "make_quiz":
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name = "Current Search",
            func = search.run,
            description = "useful for when you need to answer questions about current events or the current state of the world"
        ),
    ]
    
    memory = ConversationBufferMemory(memory_key = "chat_history")
    
    llm = OpenAI(tempertature = 0)
    agent_chain = initialize_agent(tools, llm, agent = AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose = True, memory = memory)
    
    agent_chain.run(input = f"""{after_with} 이 무슨 단어인지 예시 문자과 함께 의미를 설명해줘.
                    의미가 다양하다면 각 의미를 모두 설명해줘.
                    """)