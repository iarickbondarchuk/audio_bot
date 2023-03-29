import os
import requests
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
import pydub
import telebot
import openai

# Set your API keys and tokens
TELEGRAM_API_TOKEN = ''
openai.api_key = ''
GOOGLE_APPLICATION_CREDENTIALS = 'C:/Users/yaroslav/Downloads/web3advertisement-94ba21675884.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_APPLICATION_CREDENTIALS

# Initialize the Telegram bot
bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

# Initialize Google Cloud Speech client
speech_client = speech.SpeechClient()

# Initialize Google Cloud Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

def transcribe_voice(voice):
    audio = speech.RecognitionAudio(content=voice)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
    )

    response = speech_client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript

def get_gpt_response(text):
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user", "content": text}],
        temperature=0.6,
    )
    
    
    return response["choices"][0]["message"]["content"].strip()


def synthesize_speech(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.OGG_OPUS
    )

    response = tts_client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    return response.audio_content


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    voice_file = requests.get(f'https://api.telegram.org/file/bot{TELEGRAM_API_TOKEN}/{file_info.file_path}', stream=True).content

    text = transcribe_voice(voice_file)

    print(text)
    
    gpt_response = get_gpt_response(text)
    
    print(gpt_response)
    
    audio_content = synthesize_speech(gpt_response)
    
    print(audio_content)

    audio_file = f'response_{message.message_id}.ogg'

    bot.send_voice(message.chat.id, audio_content)

if __name__ == '__main__':
    bot.polling(none_stop=True)
