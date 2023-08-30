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

SYSTEM_MSG = "You are an expert in making quizzes to improve the language of elementary school students in Korea."

##########################################################################################################
msg = "퀴즈 만들기"

def classify_intent(msg):
    prompt = f"""Your job is to classify intent.

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


user_intent=""

intent = classify_intent(msg)
print('intent:',intent)


if intent != "make_quiz":
    after_with=intent.split("the questioned word")[1].strip()

quesetion_template=f'''--------------------------------------------------------
Question: ~ ___ ~

option1:
option2:
option3:
option4:

해설: 해당 선택지가 정답인 이유 및 선택지의 의미 설명
--------------------------------------------------------'''
##########################################################################################################
if intent == "make_quiz":
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name = "Current Search",
            func=search.run,
            description="useful for when you need to answer questions about current events or the current state of the world"
        ),
    ]

    memory = ConversationBufferMemory(memory_key="chat_history")

    llm=OpenAI(temperature=0)
    agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

    name ="도형준"
    agent_chain.run(input=f"안녕하세요. {name} 어린이. 만나서 반가워요!")

    test_list = ['금일', '사흘', '낭송', '사서', '고지식', '설빔']
    joined_str = ', '.join(test_list)
    ex_quiz=agent_chain.run(input=f'''
                    Search for additional Korean words that people are confused about, such as {joined_str}), and find about 10 new words,
                    Please choose 10 randomly.
                    '''
                    )
    print('ex_quiz:',ex_quiz)
    agent_chain.run(input=f'''
                    I'm going to pick one of the words in {ex_quiz} and touch the problem.
                    The problem contains the content of selecting a word by inferring the context with the word.
                    Word places are presented in the blanks like ~_____~.
                    Fill in the remaining options with words that can be confused with the correct word that can fit in the blank.
                    Make sure to make the problem at the level of elementary school students and low school students.
                    Answer only in Korean
                    Follow the form below to create the problem:

                    {quesetion_template}
                    
                    '''
                    )
############################################################################################################
elif intent != "make_quiz":
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name = "Current Search",
            func=search.run,
            description="useful for when you need to answer questions about current events or the current state of the world"
        ),
    ]

    memory = ConversationBufferMemory(memory_key="chat_history")

    llm=OpenAI(temperature=0)
    agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)

    agent_chain.run(input=f'''{after_with}이 무슨 단어인지 예시 문장과 함께 의미를 설명해줘.
                    의미가 다양하다면 각 의미를 모두 설명해줘.''')