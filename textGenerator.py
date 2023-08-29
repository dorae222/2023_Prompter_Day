from langchain.llms import OpenAI
from langchain import PromptTemplate, LLMChain
import random
# 
def generate_quiz():
    
    text=['금일', '사흘', '낭송', '사서', '고지식', '설빔']

    template =""""" 아래의 단어를 문장에 넣어서 한국어 문장을 하나 만들고 같은 의미를 뜻하는 한국어 문장을 하나 더 만들어줘. 
    질문:{question}"""

    prompt = PromptTemplate.from_template(template)

    llm = OpenAI()
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    result = llm_chain.run(prompt.format(question=random.choice(text)))
    return result