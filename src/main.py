# Zachary Long 6/4/2024
#WOTD Twitter bot V 0.0.5

import tweepy
import drawer
from datetime import datetime, date
from io import BytesIO
import os
from pathlib import Path
import requests
import random
import tempfile
import holidays

PROJECT_ROOT = Path(__file__).resolve().parents[1]
USED_WORDS_PATH = PROJECT_ROOT / "used_words.txt"
reset_used_words = False

def required_secret(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


word_api_key = required_secret("WORD_API_KEY")
api_key = required_secret("TWITTER_API_KEY")
api_secret = required_secret("TWITTER_API_SECRET")
bearer_token = required_secret("TWITTER_BEARER_TOKEN")
access_token = required_secret("TWITTER_ACCESS_TOKEN")
access_token_secret = required_secret("TWITTER_ACCESS_TOKEN_SECRET")

auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
api = tweepy.API(auth)
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)

image_file_ids = {
    "New Year's Day": required_secret("IMAGE_FILE_ID_NEW_YEARS_DAY"),
    "Valentine's Day": required_secret("IMAGE_FILE_ID_VALENTINES_DAY"),
    "Easter": required_secret("IMAGE_FILE_ID_EASTER"),
    "Halloween": required_secret("IMAGE_FILE_ID_HALLOWEEN"),
    "Christmas Day": required_secret("IMAGE_FILE_ID_CHRISTMAS"),
    "Independence Day": required_secret("IMAGE_FILE_ID_INDEPENDENCE_DAY"),
    "Thanksgiving": required_secret("IMAGE_FILE_ID_THANKSGIVING"),
    "Labor Day": required_secret("IMAGE_FILE_ID_LABOR_DAY"),
    "default": required_secret("IMAGE_FILE_ID_BASE")
}

# Choose between Wordnik word of the day and common words library
use_wordnik_word = False  # Set to True to use Wordnik word of the day, False for common words library

# Get the current date
current_datetime = datetime.now()
current_date = current_datetime.strftime("%m/%d")

# Text to include in the tweet
tweet_text = f"{current_date}"

# Get the word of the day

def fetch_word_of_the_day(word_api_key):
    url = f"https://api.wordnik.com/v4/words.json/wordOfTheDay?api_key={word_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("word", None)
    else:
        print("Failed to fetch word of the day.")
        return None

def get_holiday_word():
    today = date.today()
    us_holidays = holidays.US(years=today.year)

    holiday_words = {
        "New Year's Day": ["celebrate", "party", "fireworks", "resolution"],
        "Valentine's Day": ["love", "romance", "heart", "cupid","Please Heather come back I didnt mean what I said"],
        "Easter": ["eggs", "bunny", "chocolate", "spring"],
        "Halloween": ["spooky", "pumpkin", "candy", "ghost"],
        "Christmas Day": ["gift", "merry", "jolly", "tree"],
        "Independence Day": ["freedom", "patriotism", "flag", "fireworks"],
        "Thanksgiving": ["gratitude", "feast", "family", "turkey"],
        "Labor Day": ["work", "rest", "celebration", "parade"]
    }

    for holiday in holiday_words.keys():
        if today in us_holidays and us_holidays[today] == holiday:
            return holiday, random.choice(holiday_words[holiday])
    return None, None

def download_image(file_id, destination):
    url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    try:
        from PIL import Image
        Image.open(BytesIO(response.content)).verify()
    except (OSError, ValueError) as error:
        raise RuntimeError(f"Google Drive file {file_id} not working ") from error
    with open(destination, "wb") as image_file:
        image_file.write(response.content)

# Fetch word of the day from the API
word = None
if use_wordnik_word:
    word = fetch_word_of_the_day(word_api_key)

# Priority to holiday word if available, otherwise use word of the day
holiday, holiday_word = get_holiday_word()

def fetch_random_word():
    global reset_used_words

    words = [line.strip() for line in required_secret("WORD_LIST").splitlines() if line.strip()]
    if not words:
        raise RuntimeError("WORD_LIST must contain at least one word")
    try:
        with open(USED_WORDS_PATH, "r", encoding="utf-8") as used_words_file:
            used_words = {line.strip().casefold() for line in used_words_file if line.strip()}
    except FileNotFoundError:
        used_words = set()

    available_words = [word for word in words if word.casefold() not in used_words]
    if not available_words:
        reset_used_words = True
        available_words = words
    return random.choice(available_words)

def save_used_word(word):
    mode = "w" if reset_used_words else "a"
    with open(USED_WORDS_PATH, mode, encoding="utf-8") as used_words_file:
        used_words_file.write(f"{word}\n")

# Do the word
if holiday_word:
    word=holiday_word
    print("Holiday word drawn:", word)
elif word and use_wordnik_word:
    print("Word of the day drawn from Wordnik:", word)
else:
    word = fetch_random_word()
    print("Random word drawn from WORD_LIST:", word)

tweet_text=tweet_text + " - " + word

# If the day + month + year is cleanly divisible by 10 we can make the joke. Random could be used here but that's less fun. (ex 20 10 2020 = 2050 Good)
if (word[len(word)-2]=='e' or word[len(word)-2]=='o') and word[len(word)-1]=='r' and ((int(current_datetime.strftime("%d")) + int(current_datetime.strftime("%Y")) + int(current_datetime.strftime("%m"))) % 10 == 0):
        tweet_text=tweet_text + " her? I hardly know her!"

print(tweet_text)

with tempfile.TemporaryDirectory() as temporary_directory:
    source_path = os.path.join(temporary_directory, "source_image")
    output_path = os.path.join(temporary_directory, "output.jpg")
    file_id = image_file_ids.get(holiday, image_file_ids["default"])
    download_image(file_id, source_path)
    drawer.draw_text_on_image(word, source_path, output_path=output_path)

    upload = api.media_upload(output_path)
    client.create_tweet(text=tweet_text, media_ids=[upload.media_id_string])

    if not holiday and not (word and use_wordnik_word):
        save_used_word(word)
