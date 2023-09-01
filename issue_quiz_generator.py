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

from function import *

import time

def main():
    count = 0
    kind_of_data = "시사"
    # kind_of_data = "교과서"
    kind_of_game = "어휘"
    # kind_of_game = "문맥추론"
    grade = "2nd grade"

    test_list = ['금일', '사흘', '낭송', '사서', '고지식', '설빔']
    joined_str = ', '.join(test_list)

    # 문맥 퀴즈용 템플릿
    prompt_template_1 = f"""
    If the answer to be used is @심심한사과@
    The other option is to create a new one confusingly with the correct answer.
    The options of all problems should not overlap those of other problems.
    Description should be within the category that elementary school {grade} students can understand as much as possible.
    In the description, as in the example, the reason for the answer and what the answer means should be explained.
    Answer is only one.
    ------------------------------------------------------------------------------------------------------------------------
    This is Sample for Context Comprehension Question:

    Question: 아래 문자에서 @사이의 표현의 의미는 무엇일까요?

    conetent: 내가 좋아하는 유투버가 말실수를 한 것에 대해 @심심한 사과@를 전했고, 당분간 영상을 올리지 않겠다고 말했다.

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

    # 어휘 퀴즈용 템플릿
    prompt_template_3= f"""
    If the answer to be used is @실적@
    The other option is to create a new one confusingly with the correct answer.
    As shown in the example below, it consists of one correct answer and three other options.
    The options of all problems should not overlap those of other problems.
    Description should be within the category that elementary school {grade} students can understand as much as possible.
    In the description, as in the example, the reason for the answer and what the answer means should be explained.
    Answer is only one.
    ------------------------------------------------------------------------------------------------------------------------
    This is Sample for Vocabulary Question:

    Question: 아래 문자에서 @ @사이에 들어올 표현을 고르세요.

    content: 그 선수는 최근 경기에서 탁월하게 향상된 @ @으로 모두를 놀라게 하였다.

    options: [실적, 자세, 전략, 의욕]

    Value: 1
    description: 정답은 1입니다. "실적"이 정답인 이유는 문장에서 "탁월하게 향상된"이라는 표현을 사용하고 있어, 선수가 경기에서 어떤 명확한 결과나 성과를 보였다는 의미를 강조하고 있습니다. "실적"이라는 단어는 성과나 결과를 구체적으로 나타내므로, 이 문맥에서 가장 적절하다고 볼 수 있습니다.
    ------------------------------------------------------------------------------------------------------------------------
    """

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
            korean_words_5 = extract_korean_words(refined_words_list)
            

            prompt1 = make_issue_prompt(prompt_template_1,korean_words_5,grade)
            question_response = create_questions(prompt1)
            final_json_response = convert_to_json(question_response, prompt_template_2)
            print('----------------------------------------------------------------')
            print('<final_json_response>\n',final_json_response)

            count += 1

        except Exception as e:
            print(f"An error occurred: {e}")
            count += 1

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
            korean_words_5 = extract_korean_words(refined_words_list)

            prompt1 = make_issue_prompt(prompt_template_3,korean_words_5,grade)
            question_response = create_questions(prompt1)
            final_json_response = convert_to_json(question_response, prompt_template_2)
            print('----------------------------------------------------------------')
            print('final_json_response:\n',final_json_response)
            count += 1

        except Exception as e:
            print(f"An error occurred: {e}")
            count += 1
    end = time.time()
    print(f"최종 실행 시간: {end - start:.5f} sec")
    print(f"최종 실행 횟수:{count}")

if __name__ == "__main__":
    main()