import os
import asyncio
from background import keep_alive
from aiogram import Bot, Dispatcher, executor, types
from aiogram import md
import aiogram.utils.exceptions as aioExc
import aiogram.utils.markdown as fmt
import openai
import re
import sumy
import nltk
nltk.download('punkt')
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

openAiKey = os.environ['openAiKey']
telegramKey = os.environ['telegramKey']

openai.api_key = openAiKey
messages = []
left = 0
right = 4
# Объект бота
bot = Bot(token=telegramKey)
# Диспетчер для бота
dp = Dispatcher(bot)

def clean_data(data):
  text = re.sub(r"\[[0-9]*\]"," ",data)
  text = text.lower()
  text = re.sub(r'\s+'," ",text)
  text = re.sub(r","," ",text)
  return text

# Сокращение текста с помощью обработчика естесственного языка, составление резюме (краткого содержания)
def reductText():
    global messages
    for i in range(left, right):
        raw_data = messages[i]["content"]
        cleaned_article_content = clean_data(raw_data)
        # For Strings
        parser = PlaintextParser.from_string(cleaned_article_content,Tokenizer("russian"))
        
        summarizer = LexRankSummarizer()
        #Summarize the document with 2 sentences
        summary = summarizer(parser.document, 2)
        text = ""
        for sentense in summary:
            text += str(sentense)
        messages[i]["content"] = text
    
def deleteLastFive():
    global messages
    messages=messages[5:]

    
@dp.message_handler()
async def get_text_messages(message: types.Message):
    try:
        messages.append({"role": "user", "content": message.text})
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages,temperature=0.5)
        answer = completion.choices[0].message.content
        if completion.usage.total_tokens == 4097:
            print("salam")
            raise openai.error.InvalidRequestError("Number of tokens equals 4097 (response is cropped)", param = None)
    except openai.error.InvalidRequestError as e:
        print(f"Error occurred: {e}")
        print(f"Param of error: {e.param}")
        reductText()
        global left
        global right
        left += 5
        right += 5
        if left >= 10:
            deleteLastFive()
            left -= 5
            right -= 5
        await get_text_messages(message)
    except openai.error.RateLimitError as e:
        print(f"Error occurred: {e}")
        await message.reply("⚠️ OpenAi API сильно загружено, повторите запрос позже")
    except openai.error.APIError as e:
        print(f"Error occurred: {e}")
        await message.reply("⚠️ Ошибка на стороне OpenAi API, повторите запрос позже")
    except aioExc.PollError as e:
        print(f"Error occurred: {e}")
        await asyncio.sleep(5)
        await get_text_messages(message)
    except aioExc.TelegramAPIError as e:
        print(f"Error occurred: {e}")
    else:
        await message.reply(answer)
        messages.append({"role": "assistant", "content": answer})
        print(messages)
        print(completion.usage.total_tokens)
    

keep_alive()
executor.start_polling(dp, skip_updates=True)