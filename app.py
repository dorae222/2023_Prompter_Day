import openai
import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
from response import *
from introduce import *  # introduce.py에서 (팀,서비스) 소개글을 가져옴

# 환경 변수 로드
load_dotenv()

# 페이지 제목과 헤더 설정
st.set_page_config(page_title="Quiz", page_icon=":robot_face:")

# API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 세션 상태 변수 초기화
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'model_name' not in st.session_state:
    st.session_state['model_name'] = []

# 사이드바 설정
st.sidebar.title("아래의 목차를 선택해주세요.")
# 페이지 선택 라디오 버튼
page_choice = st.sidebar.radio("페이지 선택", ("팀 소개","서비스 소개","챗봇"))
# 사용자 이름 입력
st.session_state['user_name'] = st.sidebar.text_input("이름을 입력해주세요", value=st.session_state['user_name'])
# 대상 선택
target_audience = st.sidebar.radio("해당 되는 곳을 선택하세요", ("초등학교 저학년", "초등학교 고학년", "부모님"))
# 모델 선택
model_name = st.sidebar.radio("모델을 선택하세요", ("GPT-3.5", "GPT-4"))
# 대화 초기화 버튼
clear_button = st.sidebar.button("대화 초기화", key="clear")

# 모델 이름을 OpenAI 모델 ID로 매핑
if model_name == "GPT-3.5":
    model = "gpt-3.5-turbo"
else:
    model = "gpt-4"

# 모든 것 초기화
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]

# 챗봇 페이지
if page_choice == "챗봇":
    st.markdown("<h1 style='text-align: center;'>Quiz - 문해력 서비스 😬</h1>", unsafe_allow_html=True)
    # 선택한 대상 관객을 기반으로 시스템 메시지 업데이트
    if target_audience == "초등학교 저학년":
        st.session_state['messages'] = [{"role": "system", "content": "You are a quiz bot for elementary lower grades."}]
    elif target_audience == "초등학교 고학년":
        st.session_state['messages'] = [{"role": "system", "content": "You are a quiz bot for elementary upper grades."}]
    elif target_audience == "부모님":
        st.session_state['messages'] = [{"role": "system", "content": "You are a quiz bot for parents."}]

    # 메시지 출력
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))

    # 하단에 사용자 입력
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area(f"{st.session_state['user_name']}님", key='input', height=100)
        submit_button = st.form_submit_button(label='보내기')

    # 사용자가 '보내기' 버튼을 눌렀을 때
    if submit_button and user_input:
        output, _, _, _ = generate_response(user_input, model, st.session_state['messages'])
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)

        # 사용자 입력이 항상 하단에 위치하도록 페이지 새로고침
        st.experimental_rerun()

# 팀 소개 페이지
elif page_choice == "팀 소개":
    st.write(team_introduction)

# 서비스 소개 페이지
elif page_choice == "서비스 소개":
    st.write(service_introduction)
