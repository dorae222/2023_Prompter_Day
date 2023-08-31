# Key값을 가져오기 위함
from dotenv import load_dotenv
load_dotenv()
# 텍스트 생성 관련 라이브러리 모음
import openai
from langchain.agents import Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain import OpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
# 전처리 관련 라이브러리 모음
import re
import json

# 버튼 클릭시 들어올 조건
kind_of_data = "시사"
kind_of_game = "문맥추론"
grade = "2nd grade"

# 해당 학년에 맞는 난이도 인지 GPT4를 통해 판별
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

# 이전 대화의 기록을 기억해서 차후 생성되는 답변의 질 향상
memory = ConversationBufferMemory(memory_key="chat_history")

# 사용할 LLM모델 선택
# 테스트를 통해 여러 모델을 사용해봤고, text-davinci-003가 가장 나은 성능을 보임
llm=OpenAI(temperature=0.8,model_name="text-davinci-003")

# 현재 이슈가 됐던 어휘 예시
test_list = ['금일', '사흘', '낭송', '사서', '고지식', '설빔']
joined_str = ', '.join(test_list)

# 문맥 추론에 사용할 예시 문제
prompt_template_1 = f"""
If the word to be used is @심심한사과@

This is Sample for Question:
------------------------------------------------------------------------------------------------------------------------
Question: 아래 문자에서 @사이의 표현의 의미는 무엇일까요?

conetent: 내가 좋아하는 유투버가 말실수를 한 것에 대해 @심심한 사과@를 전했고, 당분간 영상을 올리지 않겠다고 말했다.

option: [맛이 없고 싱거운 사과,같은사과,별로 미안하지 않은 사과m싱싱한 사과]
    
Value: 3
description: 정답은 3입니다. 심심한 사과는 미안한 마음이 크지 않은 상황을 표현합니다. 심심한은 때로는 맛이 없고 싱거운 사과의 의미도 가지기도 합니다.
------------------------------------------------------------------------------------------------------------------------
"""
# 답변 고정을 위한 json 형태
prompt_template_2 = f"""
"Question1": {{
    "question": ,
    "content": ,
    "options": ["", "", "", ""],
    "explain": {{
        "value" : ,
        "description" : "
    }}
}},
...
"""

import time
import math
start = time.time()
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
            # 대화 실행
            agent_chain = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
            # 학년에 맞는 시사 단어를 API를 활용하여 10개 생성
            agent_chain.run(input=f'''
                                    This 10 word will be used to make the question for {grade} in in Sotuh Korea elementary school.
                                    You need to make 10 words about Recent Current Events or Affairs in South Korea, such as {joined_str}), and find about 10 new words.
                                    It should be a contextually confusing word that has become a social issue in Korea.
                                    '''
            )
            # 위에서 단어 생성시, 학년대비 난이도가 너무 어려운 케이스들이 존재하여 다시 10개를 정제하는 과정
            word_10 = agent_chain.run(input=f'''
                                    10 word be a contextually confusing word that has become a social issue in Korea.
                                    10 word should be a word at a level that elementary school {grade} can use.
                                    @@@You must answerd with korean.@@@

                                    You must be return the word in this format:
                                    word1, word2, word3, word4, word5, word6, word7, word8, word9, word10
                                    Even if it is related to current events, words that are sensational or too social for elementary school students should not be generated.
                                    '''
            )
            ##########################################################################################################
            # 한글만 추출하기 위한 정규 표현식 사용
            korean_words = re.findall(r'[\uac00-\ud7a3]+', word_10)
            print('korean_words:',korean_words)
            # 생성된 단어 수가 적을 경우, 다시 단어 생성
            if len(korean_words) < 10:
                print("생성된 한글 수가 적어 재실행합니다.")
                False
            # 문제 생성에 사용될 5개 단어 슬라이싱
            korean_words_5=korean_words[:5]
            print("korean_words_5:",korean_words_5)
            ##########################################################################################################
            # 해당 학년에 맞는 단어인지 재점검
            # property = classify_intent(korean_words_5)

            # 단어의 난이도가 맞을 때까지 단어 재생성
            # 단어 난이도를 계속 확인해야 어느 정도 해당 학년에 맞는 수준의 어휘가 생성 됨
            # while property == "YES":
            #     print("단어 난이도를 판별 중입니다...")
            #     if property == "YES":
            #         pass
            #     else:
            #         print(f"5개의 단어가 한국 초등학교 {grade}에게 너무 어렵습니다.")
            #         word_10 = agent_chain.run(input=f'''
            #                         10 word be a contextually confusing word that has become a social issue in Korea.
            #                         10 word should be a word at a level that elementary school {grade} can use.
            #                         If it is too hard words. You can change it properly.
            #                         @@@You must answerd with korean.@@@

            #                         You must be return the word in this format:
            #                         word1, word2, word3, word4, word5, word6, word7, word8, word9, word10
            #                         '''
            #         )
            ##########################################################################################################
            prompt=f'''
                    {prompt_template_1}
                    Use the five words of {korean_words_5} to create a question for students in elementary school {grade} in Korea to always have literacy.
                    Word should be a word at a level that elementary school {grade} can use.
                    Refer to the example above and choose one of the {korean_words_5} when creating the problem, and make the five questions according to the form below as shown in the example.

                    You must be answered with korean.

                    Be sure to follow the example form above.
                    The form is in json form and allows the key value to be maintained.
                    '''

            # 전처리하기에는 케이스가 너무 많아, chatgpt를 사용하여 답변 양식 고정
            response = openai.ChatCompletion.create(
                                                    model="gpt-4",
                                                    messages=[
                                                        {"role": "user", "content": prompt},
                                                    ],
                                                )
            answer1 = response.choices[0].message.content.strip()

            json_response = openai.ChatCompletion.create(
                                                    model="gpt-4",
                                                    messages=[
                                                        {"role": "user",
                                                         "content": f"{answer1}을 {prompt_template_2}처럼 json 형식으로 깔끔하게 작성해줘"},
                                                    ],
                                                )
            json_response = json_response.choices[0].message.content.strip() 

            json_response=re.sub(r'[^\w\s",@{}:\[\]]', '', json_response) # 딕셔너리에서 사용되는 기호 {}와 ,를 제외한 특수기호 제거
            print("json_response:")
            print(json_response)
            print("type:",type(json_response))
            final_json_response = json.loads('{' + json_response + '}') # 위에서 양식에 맞게 답변이 작성되면 json형태로 변환
            print('######################################################################################################')
            print("final_json_response:")
            print(final_json_response)
            print('######################################################################################################')
            print("type:",type(final_json_response))
            return None
            # print('\n----------------------------','final_json_response:',final_json_response,'\n----------------------------','type:',type(final_json_response))
        except:
            print('처음부터 chat()을 재실행합니다.')
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
end = time.time()
print(f"{end - start:.5f} sec")