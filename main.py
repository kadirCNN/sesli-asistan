from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random
import webbrowser
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import datetime
import requests
from unidecode import unidecode
from bs4 import BeautifulSoup

# Hava durumu API anahtarı
WEATHER_API_KEY = "ac9d660f2abc55c4c76f24bffb8874cf"

# Google API anahtarı
API_KEY = "AIzaSyBMIABUqidamFMhmDZ0JOo9YFV1YaZuemI"

# YouTube API'sini oluştur
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Karşılama mesajları.
greetings = ["Merhaba!", "Selam!", "Nasılsınız?", "Size nasıl yardımcı olabilirim?"]

# Tanınabilir komutlar
recognizable_commands = ["ara", "topla", "çarp", "saat kaç", "tarih", "hava durumu", "şarkı çal"]

# Fonksiyonlar.
def assist(user_input):
    user_input = user_input.lower()
    if "merhaba" in user_input:
        return random.choice(greetings)
    elif "teşekkür" in user_input:
        return "Rica ederim!"
    elif "nasılsın" in user_input:
        return "Ben sadece bir programım, ancak işler yolunda, teşekkür ederim! Siz nasılsınız?"
    elif "yardım" in user_input:
        return "Nasıl yardımcı olabilirim?"
    elif any(command in user_input for command in recognizable_commands):
        return process_command(user_input)
    else:
        return "Üzgünüm, bunu anlayamadım."

#Komutlar
def process_command(user_input):
    if "ara" in user_input:
        search_query = user_input.replace("ara", "").strip()
        search_url = f"https://www.google.com/search?q={search_query}"
        webbrowser.open(search_url)
        return f"'{search_query}' için web araması yapılıyor..."
    elif "topla" in user_input:
        return arithmetic_operation(user_input, "topla")
    elif "çarp" in user_input:
        return arithmetic_operation(user_input, "çarp")
    elif "saat kaç" in user_input:
        return get_time()
    elif "tarih" in user_input:
        return get_date()
    elif "hava durumu" in user_input:
        return get_weather(user_input)
    elif "şarkı çal" in user_input:
        return play_song(user_input)

#Matematik İşlemleri
def arithmetic_operation(user_input, operation):
    numbers = [int(word) for word in user_input.split() if word.isdigit()]
    if len(numbers) != 2:
        return "Lütfen iki sayı girin."
    if operation == "topla":
        return f"{numbers[0]} ile {numbers[1]} toplamı {numbers[0] + numbers[1]}"
    elif operation == "çarp":
        return f"{numbers[0]} ile {numbers[1]} çarpımı {numbers[0] * numbers[1]}"

#Saat Kaç
def get_time():
    now = datetime.datetime.now()
    return f"Saat {now.hour}:{now.minute}"

#Tarih Kaç
def get_date():
    now = datetime.datetime.now()
    return f"Tarih {now.day}.{now.month}.{now.year}"

#Şarkı Çal
def play_song(user_input):
    song_name = user_input.replace("şarkı çal", "").strip()
    search_query = song_name + " official video"
    video_id = search_youtube(search_query)
    if video_id:
        webbrowser.open(f"https://www.youtube.com/watch?v={video_id}")
        return f"'{song_name}' şarkısı çalınıyor..."
    else:
        return f"'{song_name}' için uygun video bulunamadı."

def search_youtube(query):
    try:
        request = youtube.search().list(
            part='snippet',
            maxResults=1,
            q=query
        )
        response = request.execute()
        video_id = response['items'][0]['id']['videoId']
        return video_id
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred: {e.content}')
        return None

#Hava Durumu
def get_weather(user_input):
    speak("Hangi bölgenin hava durumunu öğrenmek istersiniz? ")
    city_voice_input = get_audio().strip()
    city = city_voice_input if city_voice_input else user_input.replace("hava durumu", "").strip()
    #city = unidecode(city)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&lang=tr"
    response = requests.get(url)
    data = response.json()
    if data.get("cod") == 200:
        description = data["weather"][0]["description"]
        temperature = data["main"]["temp"] - 273.15  # Kelvin Çeviriyoruz Celsius
        return f"{city} bölgesinde hava durumu: {description}, sıcaklık: {temperature:.2f} derece"
    else:
        return "Hava durumu bilgisi alınamadı."

#Ses Algılama
def get_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)  # Gürültüyü azalt
        audio = recognizer.listen(source, timeout=10)  # 10 saniyelik zaman aşımı
        try:
            text = recognizer.recognize_google(audio, language="tr-TR")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            return f"Bağlantı hatası: {e}"
        except sr.WaitTimeoutError:
            return ""

#Ses Söyleme
def speak(text):
    tts = gTTS(text=text, lang='tr')
    tts.save("response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()
    os.remove("response.mp3")

#Anahtar
activation_keyword = "hey siri"
activation_flag = False

while True:
    if not activation_flag:
        user_input = get_audio()
        if activation_keyword in user_input.lower():
            speak("Sizi dinliyorum.")
            activation_flag = True
    else:
        while True:
            user_input = get_audio()
            if user_input.strip() == "":
                continue
            print("Kullanıcı: ", user_input)
            if "kes" in user_input.lower():
                speak("Sizi dinlemiyorum.")
                activation_flag = False
                break
            response_text = assist(user_input)
            print("Asistan: ", response_text)
            speak(response_text)
        print("Siri modu sonlandırıldı.")
