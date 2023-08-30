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

import re


SYSTEM_MSG = "You are an expert in making quizzes to improve the language of elementary school students in Korea."

kind_of_data = "시사"
kind_of_game = "문맥추론"
grade = "2nd grade"

def classify_intent(korean_words_5):
    prompt = f"""
    Your job is to evaluate {korean_words_5}is proper to elementary school {grade} in south korea.

    Choose one of the following intents:
    - YES
    - NO

    Intent:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()

memory = ConversationBufferMemory(memory_key="chat_history")
llm=OpenAI(temperature=0.8,model_name="text-davinci-003")

test_list = ['금일', '사흘', '낭송', '사서', '고지식', '설빔']
joined_str = ', '.join(test_list)
##########################################################################################################
def chat():
    if kind_of_data == "시사" and kind_of_game == "문맥추론":
        try:
            search = SerpAPIWrapper()
            tools = [
            Tool(
                name = "Current Search",
                func=search.run,
                description="useful for when you need to answer questions about current events or the current state of the world"
            ),
            Tool(
                name = "News Search",
                func=search.run,
                description="useful for when you need to answer questions about Recent Current Events or News in South Korea, Searching in Searching website Naver"
            ),
            ]
            agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
            agent_chain.run(input=f'''
                                    This 10 word will be used to make the question for {grade} in in Sotuh Korea elementary school.
                                    You need to make 10 words about Recent Current Events or Affairs in South Korea, such as {joined_str}), and find about 10 new words.
                                    It should be a contextually confusing word that has become a social issue in Korea.
                                    '''
            )
            word_10 = agent_chain.run(input=f'''
                                    10 word be a contextually confusing word that has become a social issue in Korea.
                                    10 word should be a word at a level that elementary school {grade} can use.
                                    You must answerd with korean.

                                    You must be return the word in this format:
                                    word1, word2, word3, word4, word5, word6, word7, word8, word9, word10
                                    '''
            )
            # 한글만 추출하기 위한 정규 표현식 사용
            korean_words = re.findall(r'[\uac00-\ud7a3]+', word_10)
            print('korean_words:',korean_words)
            if len(korean_words) < 10:
                print("생성된 한글 수가 적어 재실행합니다.")
                chat()
            korean_words_5=korean_words[:5]
            print("korean_words_5:",korean_words_5)

            property = classify_intent(korean_words_5)

            while property == "YES":
                print("단어 난이도를 판별 중입니다...")
                if property == "YES":
                    pass
                else:
                    print(f"5개의 단어가 한국 초등학교 {grade}에게 너무 어렵습니다.")
                    word_10 = agent_chain.run(input=f'''
                                    10 word be a contextually confusing word that has become a social issue in Korea.
                                    10 word should be a word at a level that elementary school {grade} can use.
                                    You must answerd with korean.

                                    You must be return the word in this format:
                                    word1, word2, word3, word4, word5, word6, word7, word8, word9, word10
                                    '''
                    )

            prompt=f'''
                    If the word to be used is @심심한사과@

                    This is Sample for Question:
                    ------------------------------------------------------------------------------------------------------------------------
                    Question: 아래 문자에서 @사이의 표현의 의미는 무엇일까요?

                    conetent: 내가 좋아하는 유투버가 말실수를 한 것에 대해 @심심한 사과@를 전했고, 당분간 영상을 올리지 않겠다고 말했다.

                    option1: 맛이 없고 싱거운 사과
                    option2: 같은사과
                    option3: 별로 미안하지 않은 사과
                    option4: 싱싱한 사과
                        
                    Explain: 정답은 3입니다. 심심한 사과는 미안한 마음이 크지 않은 상황을 표현합니다. 심심한은 때로는 맛이 없고 싱거운 사과의 의미도 가지기도 합니다.
                    ------------------------------------------------------------------------------------------------------------------------
                    Use the five words of {korean_words_5} to create a question for students in elementary school {grade} in Korea to always have literacy.
                    Word should be a word at a level that elementary school {grade} can use.
                    Refer to the example above and choose one of the {korean_words_5} when creating the problem, and make the five questions according to the form below as shown in the example.

                    You must be answered with korean.

                    Be sure to follow the example form above.
                    The form is in json form and allows the key value to be maintained.
                    '''

            response = openai.ChatCompletion.create(
                                                    model="gpt-4",
                                                    messages=[
                                                        {"role": "user", "content": prompt},
                                                    ],
                                                )
            answer1 = response.choices[0].message.content.strip()
            return print(answer1)
        
        except:
            print('chat()을 재실행합니다.')
            chat()
    ######################################################################################################
    elif kind_of_data == "시사" and kind_of_game != "문맥추론":
        pass
        # return print("b")
    ######################################################################################################
    elif kind_of_data== "교과서" and kind_of_game == "문맥추론":
        pass
        # return print("c")
    ######################################################################################################
    elif kind_of_data == "교과서" and kind_of_game != "문맥추론":
        pass
        # return print("d")
##########################################################################################################
chat()