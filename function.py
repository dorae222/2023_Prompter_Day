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
import pandas as pd

from function import *
load_dotenv(find_dotenv())

def is_korean(word):
    return all(re.match(r'[\uac00-\ud7a3]', char) for char in word)

def remove_english_and_make_list(korean_with_english):
    word_10_list = [word.strip() for word in korean_with_english.split(',')]
    word_10_list_korean_only = [''.join(re.findall('[가-힣 ]+', word)).strip() for word in word_10_list]
    return word_10_list_korean_only

def generate_issue_words(agent_chain, grade):
    try:
        word_10 = agent_chain.run(
            input=f'''This 10 word will be used to make the question for {grade} grade in South Korea elementary school.
                    You need to make 10 words about Recent Current Events or Affairs in South Korea.
                    It should be a contextually confusing word that has become a social issue in Korea.
                    @@@You must answer in Korean.@@@
                    
                    @@@You must be followed:@@@
                    word1, word2, word3, word4, word5, word6, word7, word8,word9, word10
                    '''
                    )
        print('word_10:',word_10)
        print('type(word_10):',type(word_10))
        word_10=remove_english_and_make_list(word_10)
        if all(is_korean(word) for word in word_10):
            return random.sample(word_10, 5)
        else:
            refined_words = agent_chain.run(
                input=f'''
                @@@You need to make Korean words, not English@@@
                10 word be a contextually confusing word that has become a social issue in Korea.
                10 word should be a word at a level that korean elementary school {grade}nd grade can use.
                @@@You must answer in Korean.@@@
                        
                @@@You must be followed:@@@
                word1, word2, word3, word4, word5, word6, word7, word8,word9, word10
                '''
                )
            refined_words=remove_english_and_make_list(refined_words)
            if all(is_korean(word) for word in refined_words):
                return random.sample(refined_words, 5)
    except:
        return ['금일', '사흘', '낭송', '사서', '고지식']

def extract_korean_words(refined_words):
    korean_words = re.findall(r'[\uac00-\ud7a3]+', refined_words)
    if len(korean_words) < 5:
        print("생성된 한글 수가 적어 재실행합니다.")
        return False
    return random.sample(korean_words, 5)

def make_issue_prompt(prompt_template,korean_words_5,grade):
    print('korean_words_5:',korean_words_5)
    prompt = f'''
    Use {korean_words_5} as the correct answer to the question.
    The number of {korean_words_5} problems should be created.
    Quiz should be a word at a level that south korean elementary school {grade} grade can use.
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

def filter_by_grade_sem(grade, sem):
    df = pd.read_csv('./data/final_data.csv')
    df.drop('Unnamed: 0', axis=1, inplace=True)
    
    grade, sem = int(grade), int(sem)
    textbook_words_df = df[(df['학년'] == grade) & (df['학기'] == sem)]
    
    # 빈도수 또는 다른 측정값으로 정렬
    sorted_df = textbook_words_df.sort_values(by='빈도수', ascending=False)
    
    # 상위 10%에 해당하는 단어만 추출
    top_10_percent_idx = int(0.1 * len(sorted_df))
    top_10_percent_df = sorted_df.iloc[:top_10_percent_idx]
    
    # 상위 10% 중에서 랜덤하게 5개를 선택
    selected_words_df = top_10_percent_df.sample(5)
    
    textbook_words = []
    for index, row in selected_words_df.iterrows():
        word_dict = {
            "낱말": row["낱말"],
            "품사": row["품사"]
        }
        textbook_words.append(word_dict)
    
    return textbook_words

def make_textbook_words_list(grade,sem,textbook_words,prompt_template):
    input = f'''
    I would like to create a context quiz for the {sem} semester of the {grade} grade.
    For the corresponding collection of words ({textbook_words}), create a quiz by considering the part-time and frequency in.
    The following 14 conditions are followed:
    0. ###Make 5 Questions###
    {prompt_template}
    '''
    print('textbook_words:',textbook_words)
    return input