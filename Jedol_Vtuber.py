import asyncio
import time
import keyboard
import threading
import pygame
from openai import OpenAI
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv;load_dotenv()  # openai_key .env 선언 사용
import json
import re
import pyvts
from datetime import datetime
import os
import sys
from emoji import demojize
import Jedol_Answer as ans
from dotenv import load_dotenv;load_dotenv() # openai_key  .env 선언 사용
import utils.movement as move
import pytchat
from chat_GPT_tts import *
from utils import subtitle as sub


def setup():
    global feeling, total_characters, chat, chat_now, chat_prev, is_Speaking, owner_name, myvts, api_key

    # to help the CLI write unicode characters to the terminal
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

    api_key = os.getenv('OPENAI_API_KEY')

    total_characters = 0
    chat = ""
    chat_now = ""
    chat_prev = ""
    owner_name = "nabang"
    is_Speaking = False

    # # Connect with Vtube studio api
    # myvts = pyvts.vts()
    # asyncio.run(move.connect_auth(myvts))
    # feeling = ""


# function to get the user's input text
def type_text():
    # result = owner_name + " said " + input("Type your question: ")
    result = input("Type your question: ")
    
    with open("texts/chat.txt", "w", encoding="utf-8") as outfile:
        try:
            words = result.split()
            lines = [words[i:i+10] for i in range(0, len(words), 10)]
            for line in lines:
                outfile.write(" ".join(line) + "\n")
        except:
            print("Error writing to chat.txt")


def get_chat():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = str( datetime.now().date().today())
    print( f"vectorDB-faiss-jshs-{today}")

    vectorDB_folder = f"vectorDB-faiss-jshs-{today}"
    ans.vectorDB_create(vectorDB_folder)
    chat_prev = ""

    while True:
        try:
            file_path = "texts/chat.txt"
            if not os.path.exists(file_path):
                print("##############    no file    ################")
                time.sleep(1)
                continue

            with open(file_path, 'r', encoding="utf-8") as f:
                chat_now = f.read()

            if chat_now.strip() == "":
                time.sleep(1)  # 파일이 비어있으면 잠시 대기
                continue

            if chat_now != chat_prev:    

                print(f"chat_prev: {chat_prev}, chat_now: {chat_now}")

                answer = ans.ai_response(
                    vectorDB_folder=vectorDB_folder,
                    query=chat_now,
                    token="dhxzZUwGDzdhGrBTMSMs2",  # 예시 토큰 값입니다. 실제 토큰으로 교체하세요.
                )

                print(f"answer: {answer}")

                chat_prev = chat_now
                new_chat=[{"date": current_time },{"role": "user", "content": chat_now },{"role": "assistant", "content":answer}]
                # 이걸 chatDb에 저장하는 코드 추가

                while is_Speaking==True:
                    time.sleep(1)

                sub.generate_subtitle(chat_now,answer)
                # answer과 chat_now를 각각 texts/answer.txt, texts/selected_chat.txt에 저장하는 코드 추가

                chatGPT_tts(answer)

        except Exception as e:
            chat_now = f"Error reading file: {e}" 

def mp3_play(mp3_file, remove=True):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy(): 
            pygame.time.Clock().tick(10)
    
    finally:  
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        if remove:
            os.remove(mp3_file)

def chatGPT_tts(answer):
    global is_Speaking

    is_Speaking = True

    client = OpenAI()

    print("Speaking Start")

    Path("templates/chat_audio").mkdir(parents=True, exist_ok=True)
    response = client.audio.speech.create(
            model="tts-1",
            voice="fable",
            input=answer)
    response.stream_to_file("templates/chat_audio/answer.mp3")

    mp3_play("templates/chat_audio/answer.mp3", True)
    
    # # Clear the text files after the assistant has finished speaking
    # time.sleep(1)
    # with open ("answer.txt", "w") as f:
    #     f.truncate(0)
    # with open ("chat.txt", "w") as f:
    #     f.truncate(0)
    
    is_Speaking = False
    print("Speaking Finished")


if __name__ == "__main__":
    try:
        setup()
        
        get_chat()

        # # Threading is used to capture livechat and answer the chat at the same time
        # t = threading.Thread(target=get_chat)
        # t.start()

        # print("Press and Hold Right Shift to record audio or Press Left Shift to type text")
        # while True:
        #     if keyboard.is_pressed('LEFT_SHIFT'):
        #         type_text()
            
    except KeyboardInterrupt:
        # t.join()
        print("Stopped")
