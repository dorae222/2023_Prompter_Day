# fast api
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Key값을 가져오기 위함
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
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
import pandas as pd
from function import *

import time

# FastAPI
app = FastAPI(debug = True)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# get 요청
@app.get("/game/") # url 예시: /game?grade=3&sem=1&type=sisa&game=context
def main(grade: str, sem: str, game: str, type: str):
    # grade: number; 학년 # sem: number; 학기 # game: 'context' | 'word'; 문맥추론, 어휘 # type: 'text' | 'sisa'; 교과서 데이터, 시사 데이터 
    if type == 'sisa':
        kind_of_data = "시사" 
    elif type == 'text':
        kind_of_data = "교과서" 
    
    if game == 'context':
        kind_of_game = "문맥추론" 
    elif game == 'word':
        kind_of_game = "어휘"
    
    test_list = ['금일', '사흘', '낭송', '사서', '고지식', '설빔']
    joined_str = ', '.join(test_list)

    # 시사& 문맥
    prompt_template_1 = f"""
    0. ###Make 5 Questions###
    1. The other option is to create a new one confusingly with the correct answer.
    2. The options of all problems should not overlap those of other problems.
    3. Description should be within the category that elementary school {grade} grade {sem}semseter students can understand as much as possible.
    4. In the description, as in the example, the reason for the answer and what the answer means should be explained.
    5. Identify the meaning of the word used as the correct answer.
    6. Answer is only one and toatl options are 4.
    7. You shouldn't use a problem with @심심한사과@, you should only refer to it.
    If the answer to be used is @심심한사과@
    ------------------------------------------------------------------------------------------------------------------------
    This is Sample for Context Comprehension Question:

    Question: 아래 문자에서 @사이의 가장 적절한 표현의 의미는 무엇일까요?

    conetent: 내가 좋아하는 유투버가 말실수를 한 것에 대해 @ @를 전했고, 당분간 영상을 올리지 않겠다고 말했다.

    options: [맛이 없고 싱거운 사과,같은사과,별로 미안하지 않은 사과,싱싱한 사과]
        
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

    # 시사 & 어휘
    prompt_template_3= f"""
    0. ###Make 5 Questions###
    1. The other option is to create a new one confusingly with the correct answer.
    2. As shown in the example below, it consists of one correct answer and three other options.
    3. The options of all problems should not overlap those of other problems.
    4. Description should be within the category that elementary school {grade} grade {sem}semseter students can understand as much as possible.
    5. In the description, as in the example, the reason for the answer and what the answer means should be explained.
    6. Identify the meaning of the word used as the correct answer.
    7. Answer is only one and toatl options are 4.
    8. You shouldn't make a problem with @실적@, you should only refer to it.
    If the answer to be used is @실적@
    ------------------------------------------------------------------------------------------------------------------------
    This is Sample for Vocabulary Question:

    Question: 아래 문자에서 @ @사이에 들어올 가장 적절한 표현을 고르세요.

    content: 그 선수는 최근 경기에서 탁월하게 향상된 @ @으로 모두를 놀라게 하였다.

    options: [실적, 자세, 전략, 의욕]

    Value: 1
    description: 정답은 1입니다. "실적"이 정답인 이유는 문장에서 "탁월하게 향상된"이라는 표현을 사용하고 있어, 선수가 경기에서 어떤 명확한 결과나 성과를 보였다는 의미를 강조하고 있습니다. "실적"이라는 단어는 성과나 결과를 구체적으로 나타내므로, 이 문맥에서 가장 적절하다고 볼 수 있습니다.
    ------------------------------------------------------------------------------------------------------------------------
    """
    # 교과서 & 문맥
    prompt_template_4 = f'''
    1. The example below was made in consideration of 낱말 and 품사.
    2. The other option is to create a new one confusingly with the correct answer.
    3. ###Don't use 낱말 as it is, but change it to the context.###
    4. Description should be within the category that elementary school {grade} grade {sem}semseter students can understand as much as possible.
    5. In the description, as in the example, the reason for the answer and what the answer means should be explained.
    6. Identify the meaning of the word used as the correct answer.
    7. Places are not included in the option
    8. Answer is only one and toatl options are 4.
    9. ###If the expression is not correct in Korean when creating a problem, correct it appropriately.###
    10. ###The options between problems must be different.###
    11. Don't use a person's name  and place name.
    12. You shouldn't make a problem with @심심한 사과@, you should only refer to it.
    13. Create content that fits 품사.
    If the answer to be used is @심심한 사과@
    ------------------------------------------------------------------------------------------------------------------------
    This is Sample for Context Comprehension Question:

    Question: 아래 문자에서 @사이의 가장 적절한 표현의 의미는 무엇일까요?

    conetent: 내가 좋아하는 유투버가 말실수를 한 것에 대해 @ @를 전했고, 당분간 영상을 올리지 않겠다고 말했다.

    options: [맛이 없고 싱거운 사과,같은사과,별로 미안하지 않은 사과,싱싱한 사과]
        
    Value: 3
    description: 정답은 3입니다. 심심한 사과는 미안한 마음이 크지 않은 상황을 표현합니다. 심심한은 때로는 맛이 없고 싱거운 사과의 의미도 가지기도 합니다.
    ------------------------------------------------------------------------------------------------------------------------
    '''

    # 교과서 & 어휘
    prompt_template_5 = f'''
    1. The example below was made in consideration of 낱말 and 품사.
    2. The other option is to create a new one confusingly with the correct answer.
    3. ###Don't use 낱말 as it is, but change it to the context.###
    4. Description should be within the category that elementary school {grade} grade {sem}semseter students can understand as much as possible.
    5. In the description, as in the example, the reason for the answer and what the answer means should be explained.
    6. Identify the meaning of the word used as the correct answer.
    7. Places are not included in the option
    8. Answer is only one and toatl options are 4.
    9. ###If the expression is not correct in Korean when creating a problem, correct it appropriately.###
    10. ###The options between problems must be different.###
    11. Don't use a person's name  and place name.
    12. You shouldn't make a problem with @실적@, you should only refer to it.
    13. Create content that fits 품사.
    If the answer to be used is @실적@
    ------------------------------------------------------------------------------------------------------------------------
    This is Sample for Noun Vocabulary Question:

    Question: 아래 문자에서 @ @사이에 들어올 가장 적절한 표현을 고르세요.

    content: 그 선수는 최근 경기에서 탁월하게 향상된 @ @으로 모두를 놀라게 하였다.

    options: [실적, 자세, 전략, 의욕]

    Value: 1
    description: 정답은 1입니다. "실적"이 정답인 이유는 문장에서 "탁월하게 향상된"이라는 표현을 사용하고 있어, 선수가 경기에서 어떤 명확한 결과나 성과를 보였다는 의미를 강조하고 있습니다. "실적"이라는 단어는 성과나 결과를 구체적으로 나타내므로, 이 문맥에서 가장 적절하다고 볼 수 있습니다.
    ------------------------------------------------------------------------------------------------------------------------
    '''

    start = time.time()
    memory = ConversationBufferMemory(memory_key="chat_history")
    llm=OpenAI(temperature=0.8,model_name="text-davinci-003")

    if kind_of_data == "시사" and kind_of_game == "문맥추론":
        try:
            search = SerpAPIWrapper()
            tools = [
            Tool(
                name = "News Search",
                func=search.run,
                description="useful for when you need to answer questions about Recent Current Events or News in South Korea, Searching in Searching website Naver"
            ),
            ]

            agent_chain = initialize_agent(tools, llm, AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
            refined_words_list = generate_issue_words(agent_chain, grade)
            print('refined_words_list:',refined_words_list)
            # korean_words_5 = extract_korean_words(refined_words_list)

            prompt1 = make_issue_prompt(prompt_template_3,refined_words_list,grade)
            question_response = create_questions(prompt1)
            final_json_response = convert_to_json(question_response, prompt_template_2)
            print('----------------------------------------------------------------')
            print('final_json_response:\n',final_json_response)
            return {final_json_response}
        except Exception as e:
            return None

    elif kind_of_data == "시사" and kind_of_game == "어휘":
        try:
            search = SerpAPIWrapper()
            tools = [
            Tool(
                name = "News Search",
                func=search.run,
                description="useful for when you need to answer questions about Recent Current Events or News in South Korea, Searching in Searching website Naver"
            ),
            ]

            agent_chain = initialize_agent(tools, llm, AgentType.CONVERSATIONAL_REACT_DESCRIPTION, verbose=True, memory=memory)
            refined_words_list = generate_issue_words(agent_chain, grade)
            print('refined_words_list:',refined_words_list)
            # korean_words_5 = extract_korean_words(refined_words_list)

            prompt1 = make_issue_prompt(prompt_template_3,refined_words_list,grade)
            question_response = create_questions(prompt1)
            final_json_response = convert_to_json(question_response, prompt_template_2)
            print('----------------------------------------------------------------')
            print('final_json_response:\n',final_json_response)
            return {final_json_response}
        except Exception as e:
            return None
    elif kind_of_data == "교과서" and kind_of_game == "문맥추론":
        try:
            textbook_words = filter_by_grade_sem(grade, sem)
            textbook_words_list = make_textbook_words_list(grade,sem,textbook_words,prompt_template_4)
            question_response = create_questions(textbook_words_list)
            final_json_response = convert_to_json(question_response, prompt_template_2)
            print('----------------------------------------------------------------')
            print('final_json_response:\n',final_json_response)
            return {final_json_response}
        except Exception as e:
            return None
    else:
        try:
            textbook_words = filter_by_grade_sem(grade, sem)
            textbook_words_list = make_textbook_words_list(grade,sem,textbook_words,prompt_template_5)
            question_response = create_questions(textbook_words_list)
            final_json_response = convert_to_json(question_response, prompt_template_2)
            print('----------------------------------------------------------------')
            print('final_json_response:\n',final_json_response)
            return {final_json_response}
        except Exception as e:
            print(f"An error(4) occurred: {e}")
    end = time.time()
    print(f"최종 실행 시간: {end - start:.5f} sec")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host = "0.0.0.0", port = 8000)