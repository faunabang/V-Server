import json
import re
import openai
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.document_loaders import WebBaseLoader,UnstructuredURLLoader
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv;load_dotenv() # openai_key  .env 선언 사용 
import jedol1Fun as jshs
from datetime import datetime, timedelta
from langchain.memory import ChatMessageHistory
import jedol2ChatDbFun as chatDB
import pdfplumber

import numpy as np
import faiss  # Make sure to install faiss-cpu or faiss-gpu
import pickle
import os
from openai import OpenAI

class VectorDB:
    def __init__(self, index_path, page_content_path):
        self.index = faiss.read_index(index_path)
        with open(page_content_path, 'rb') as f:
            self.page_contents = pickle.load(f)

    def similarity_search(self, query, cnt=3):
        query_embedding = create_query_embedding(query) 
        D, I = self.index.search(query_embedding, cnt)  # D는 거리, I는 인덱스
        # 결과를 거리에 따라 정렬합니다.
        results = zip(I.flatten(), D.flatten())  # flatten 결과 리스트
        sorted_results = sorted(results, key=lambda x: x[1])  # 거리에 따라 정렬
        # 정렬된 결과로부터 유사한 문서 추출
        search_results = []
        for idx, distance in sorted_results:
            if idx < len(self.page_contents):  # 유효한 인덱스인지 확인
                search_results.append((self.page_contents[idx], distance))
        return search_results
    
def create_query_embedding(query):
    # OpenAI API를 사용하여 쿼리의 임베딩을 생성합니다.
    client = OpenAI()
    response = client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embedding_vector = response.data[0].embedding  # This is the corrected line
    return np.array(embedding_vector).astype('float32').reshape(1, -1)  # 2D array 형태로 반환합니다.  
   
def vectorDB_create(vectorDB_folder):

    loader = TextLoader("data\jshs-story.txt", encoding='utf-8')
    # loader = WebBaseLoader(web_path="https://jeju-s.jje.hs.kr/jeju-s/0102/history")
    page=loader.load()[0]
    # page.page_content=jshs.html_parsing_text(
    #                 page_content=page.page_content,
    #                 start_str="학교연혁 연혁 기본 리스트 년 도 날 짜 내 용",
    #                 end_str="열람하신 정보에 대해 만족하십니까",
    #                 length=20,
    #                 removeword=[]
    #                 )

    documents=[ Document(
                        page_content=page.page_content,
                        metadata=page.metadata
                        )
               ]
    print(" jshs-story.txt ---- load !~~~~~~~~~")
    # print( page.page_content )
    # print( page.metadata )
    loader = WebBaseLoader(web_path="https://jeju-s.jje.hs.kr/jeju-s")
    page=loader.load()[0]
    page.page_content=jshs.html_parsing_text(
                    page_content=page.page_content,
                    start_str="우[",
                    end_str="Copyright",
                    length=20,
                    removeword=[]
                    )
    documents.append( Document(
                        page_content=page.page_content,
                        metadata=page.metadata
                        )
                    )
  
    # jshs.loader_documents_viewer(documents)
    print(" 학교주소 ---- load !~~~~~~~~~")
    # 식단-----------------------
    today = datetime.now().today()
    date1 = today - timedelta(days=2)
    date2 = today + timedelta(days=5)
    start_date=date1.strftime('%Y-%m-%d')
    end_date=date2.strftime('%Y-%m-%d')
    office_Code="T10"  # 교육청 NEIS 코드
    school_code="9290066" # 학교 Neis 코드   9290066 -> 과학고 학교코드
    url=f"https://api.salvion.kr/neisApi?of={office_Code}&sc={school_code}&ac=date&sd={start_date}&ed={end_date}&code=all"
    loader = WebBaseLoader(web_path=url)
    page=loader.load()[0]
    
    page_content= json.loads(page.page_content)
    page_content= jshs.getMealMenuNeis(page_content=page_content)

    documents.append( Document(
                        page_content=page_content,
                        metadata=page.metadata
                        )
                    )

    print(f" 점심 메뉴 ---- load !~~~~{url}")

    # 학사일정-------------------------------------------
    school_plan=jshs.school_schedule(datetime.now().today().year)
    documents.append( Document(
                            page_content=school_plan,
                            metadata={'source': '홈페이지'}
                        )
                    )
    
    print(f" 학사일정  ---- load !")
    # # 교육과정
    # with pdfplumber.open("data/2023-plan.pdf") as pdf_document:
    #     for page_number, page in enumerate(pdf_document.pages):
    #         text = page.extract_text()

    #         metadata = {
    #             'source': '2023-plan.pdf',
    #             'page': page_number + 1
    #         }
    #         document = Document(page_content=text, metadata=metadata)
    #         documents.append(document)
    # print(f" 2023 교욱과정  ---- load !")
    #  읽은 문서 페이지 나눔 방볍 설정 -----------------------------------
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size =3000, # 이 숫자는 매우 중요
            chunk_overlap =0, # 필요에 따라 사용
            separators=["\n\n","\n",", "], # 결국 페이지dk 분리를 어떻게 하느냐 가 답변의 질을 결정
            length_function=len    
            # 위 내용을 한 페이지를 3000자 이내로 하는데 페이지 나누기는 줄바꿈표시 2개 우선 없음 1개로 3000자를 체크하는 것은 len 함수로 
    )
    
    #  읽은 문서 페이지 나누기 -----------------------------------
    pages = text_splitter.split_documents(documents)
    
    # jshs.splitter_pages_viewer(pages)
    # quit()
    # 신버전
    client = OpenAI()  
    
    
    # 각 페이지에 대한 임베딩을 담을 리스트
    embeddings_list = []
    # 임베딩 생성을 위해 각 페이지에 대해 반복
    for page in pages:
        # print(page.page_content)
        response = client.embeddings.create(
            input=page.page_content,
            model="text-embedding-ada-002"
        )
        
        embedding_vector = response.data[0].embedding  # This is the corrected line
        embeddings_list.append(np.array(embedding_vector).astype('float32').reshape(1, -1))
        

    # FAISS 인덱스 초기화 (전체 임베딩 리스트의 첫 번째 요소를 사용하여 차원을 설정)
    dimension = len(embeddings_list[0][0])  # Get the dimension from the first embedding's length
    index = faiss.IndexFlatL2(dimension)  # Initialize the FAISS index
    # Add the embeddings to the FAISS index
    for embedding in embeddings_list: 
        index.add(embedding)  # Each embedding is already a 2D numpy array
    # faiss.write_index(index, vectorDB_folder)
    if not os.path.exists(vectorDB_folder):
        os.makedirs(vectorDB_folder)

    faiss.write_index(index, f"{vectorDB_folder}/index.faiss")
    page_contents = [page.page_content for page in pages]
    with open(f"{vectorDB_folder}/page.pkl", "wb") as f:
        pickle.dump(page_contents, f)

    print("Page FAISS 인덱스가 성공적으로 저장되었습니다.")

    # 구버전
    # vectorDB = FAISS.from_documents(pages , OpenAIEmbeddings())
    # vectorDB.save_local(vectorDB_folder)
    # OPEN AI 1.1.1 버전
    
    return  vectorDB_folder

def ai_response( vectorDB_folder="", query="", token=""):

    client = OpenAI()
    chat_history=chatDB.query_history(token) # 기존 대화 내용
    # print("chat_history=",chat_history)
    answer="" 
    new_chat=""
          
    index_path = os.path.join(vectorDB_folder, "index.faiss")
    page_content_path = os.path.join(vectorDB_folder, "page.pkl")

    vectorDB = VectorDB(index_path, page_content_path)

    docs = vectorDB.similarity_search(query, cnt=6)
    prompt=[]
    
    for page, distance in docs:    
        prompt.append({"role": "system", "content": f"{ page }"})      
        # print( "{}\n".format(distance),"="*100, page.replace('\n', ''))
        
    prompt.append({"role": "system", "content": f"""
                        오늘 일자는 {jshs.today_date()} 이다.
                        오늘 요일는 {jshs.today_week_name()} 이다.
                        이번 달은 {jshs.today_month()} 이다.
                        올해는 {jshs.today_year()} 이다.
                        제공되는 정보는 모두 제돌이가 학습해서 알고 있는 지식이다.
                        제주과학고등학교 안내 도움이 이다.
                        정보가 없는 질문에는 정보가 없다고 답변해야한다.
                        질문에 간결하게 답한다.
                        """})
        
    prompt.append({"role": "user", "content": "우리학교 이름은" } )    
    prompt.append({"role": "assistant", "content": "제주과학고입니다." } )    

    prompt.append({"role": "user", "content": "넌 누구야?" } )    
    prompt.append({"role": "assistant", "content": "제주과학고 1학년 학생입니다. 이름은 '제돌이', 나이는 16세 입니다." } )    
    
    prompt.append({"role": "user", "content": "너의 이름은 ?" } )    
    prompt.append({"role": "assistant", "content": "나의 이름은 제돌이입니다."} )    

    prompt=chat_history + prompt 
        
    prompt.append({"role": "user", "content": query } )    
    
    response  = client.chat.completions.create(
                        model="gpt-4-1106-preview",
                        messages=prompt
                        ) 
    #print("response.choices[0].message=",response)
    answer= response.choices[0].message.content
    no_answer=False
    checkMsg=["죄송합니다","확인하십시요","OpenAI","불가능합니다","미안합니다."]
    for a in checkMsg: 
            if a in answer:
                no_answer=True
            break
    
    new_chat=[{"role": "user", "content": query },{"role": "assistant", "content":answer}]  

    answer_no_update = any( chat["content"] == answer  for chat in chat_history)
    checkMsg=["죄송합니다","확인하십시요","OpenAI","불가능합니다","미안합니다.","않았습니다"]
    for a in checkMsg: 
        if a in answer:
           answer_no_update=True
           break
    # if not answer_no_update:
    #         response = openai.ChatCompletion.create( model="gpt-4-vision-preview", messages= prompt,max_tokens=2000)
    #         answer=response.choices[0].message.content
                
    # 새로운 대화 내용을 업데이트
    if not answer_no_update:
        chatDB.update_history(token, new_chat, max_token=3000, ai_mode=ai_mode)
    return answer    

if __name__ == "__main__":
      today = str( datetime.now().date().today())
      print( f"vectorDB-faiss-jshs-{today}")

      vectorDB_folder = f"vectorDB-faiss-jshs-{today}"
      vectorDB_create(vectorDB_folder)


      while True:  # 무한 반복 설정
        query = input("질문? ")  # 사용자로부터 질문 받기
        if query == "":  # 종료 조건 검사
            print("프로그램을 종료합니다.")
            break  # 종료 조건이 만족되면 while 루프 탈출

        answer = ai_response(
            vectorDB_folder=vectorDB_folder,
            query=query,
            token="dhxzZUwGDzdhGrBTMSMs2",  # 예시 토큰 값입니다. 실제 토큰으로 교체하세요.
        )


        print(f"AI 응답: {answer}")
      