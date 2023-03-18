import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import datetime
import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections.abc import MutableMapping

#class MyDict(MutableMapping):
# Implementação da classe

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]
col = db[MONGODB_COLLECTION_NAME]

# Telegram API Configuration
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("job_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
def get_jobs_by_location(location):
    url = f"http://api.indeed.com/ads/apisearch?publisher={os.getenv('PUBLISHER_ID')}&q=python&l={location}&sort=&radius=&st=&jt=&start=&limit=50&fromage=&filter=&latlong=1&co=br&chnl=&userip=1.2.3.4&useragent=Mozilla/%2F4.0%28Firefox%29&v=2"
    response = requests.get(url)
    data = json.loads(response.text)
    return data["results"]
def send_job_list(chat_id, job_list):
    for job in job_list:
        if col.find_one({"jobkey": job["jobkey"]}) is None:
            col.insert_one(job)
            message_text = f"""
*{job['jobtitle']}*
_{job['company']}_
{job['formattedLocation']}

{job['snippet']}

*{job['url']}*
"""
            message_text = re.sub("<.*?>", "", message_text)
            sentiment_score = SentimentIntensityAnalyzer().polarity_scores(message_text)["compound"]
            sentiment_label = "Ruim" if sentiment_score < -0.1 else "Ótima" if sentiment_score > 0.1 else "Boa"
            message_text += f"\nClassificação de sentimento: {sentiment_label}"
            bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")
@bot.on_message(filters.command("start"))
def start(bot, update):
    chat_id = update.chat.id
    message_text = "Olá, eu sou um bot que envia vagas de emprego para programadores Python no Brasil. Para começar, por favor, envie sua localização."
    bot.send_message(chat_id=chat_id, text=message_text)

@bot.on_message(filters.location)
def location_received(bot, update):
    chat_id = update.chat.id
    latitude = update.location.latitude
    longitude = update.location.longitude

    geocode_url = f"https://geocode.xyz/{latitude},{longitude}?geoit=json"
    geocode_response = requests.get(geocode_url)
    geocode_data = json.loads(geocode_response.text)

    city = geocode_data["city"]
    state = geocode_data["state"]
    location = f"{city}, {state}"
    job_list = get_jobs_by_location(location)
    send_job_list(chat_id, job_list)

bot.run()
    # Iniciar o loop do bot
app.run()
    
if __name__ == "__main__":
    main()
