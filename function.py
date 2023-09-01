# Key값을 가져오기 위함
from dotenv import load_dotenv, find_dotenv

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
import random

from function import *
load_dotenv(find_dotenv())

def is_korean(word):
    return all(re.match(r'[\uac00-\ud7a3]', char) for char in word)

def generate_issue_words(agent_chain, grade):
    word_10 = agent_chain.run(
        input=f'''This 10 word will be used to make the question for {grade} in South Korea elementary school.
                  You need to make 10 words about Recent Current Events or Affairs in South Korea.
                  It should be a contextually confusing word that has become a social issue in Korea.
                  @@@You must answer in Korean.@@@
                  
                  @@@You must be followed:@@@
                  word1, word2, word3, word4, word5, word6, word7, word8,word9, word10
                  '''
    )
    if all(is_korean(word) for word in word_10):
        return word_10
    else:
        refined_words = agent_chain.run(
            input=f'''10 word be a contextually confusing word that has become a social issue in Korea.
                    10 word should be a word at a level that korean elementary school {grade} can use.
                    @@@You must answer in Korean.@@@
                    
                    @@@You must be followed:@@@
                    word1, word2, word3, word4, word5, word6, word7, word8,word9, word10
                    '''
    )
        return refined_words

def extract_korean_words(refined_words):
    korean_words = re.findall(r'[\uac00-\ud7a3]+', refined_words)
    if len(korean_words) < 5:
        print("생성된 한글 수가 적어 재실행합니다.")
        return False
    return random.sample(korean_words, 5)

def make_issue_prompt(prompt_template,korean_words_5,grade):
    prompt = f'''
    Use {korean_words_5} as the correct answer to the question.
    The number of {korean_words_5} problems should be created.
    Quiz should be a word at a level that south korean elementary school {grade} can use.
    {prompt_template}
    '''
    return prompt

def create_questions(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content.strip()

def convert_to_json(response, template):
    json_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user",
             "content": f'''
                    {response}을 {template}처럼 json 형식으로 깔끔하게 작성해줘.
                    제공해준 Key,Value값의 형태를 항상 유지해야한다.
                    '''
            }
        ],
    )
    return json_response.choices[0].message.content.strip()