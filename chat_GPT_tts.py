import asyncio
import time
import keyboard
import threading
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


def chatGPT_tts(answer):
    global is_Speaking

    is_Speaking = True

    client = OpenAI()

    print("Speaking Start")

    Path("templates/chat_audio").mkdir(parents=True, exist_ok=True)
    response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=answer)
    response.stream_to_file("templates/chat_audio/answer.mp3")

    
    # # Clear the text files after the assistant has finished speaking
    # time.sleep(1)
    # with open ("answer.txt", "w") as f:
    #     f.truncate(0)
    # with open ("chat.txt", "w") as f:
    #     f.truncate(0)
    
    is_Speaking = False
    print("Speaking Finished")

    return is_Speaking