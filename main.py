from pytube import YouTube
import json
import logging
import requests
from io import BytesIO
#import asyncio
import os
from dotenv import load_dotenv   #for python-dotenv method
load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEEPGRAM_API_KEY = os.environ.get('DEEPGRAM_API_KEY')
TEXT_API_KEY = os.environ.get('TEXT_API_KEY')
NLP_API_KEY = os.environ.get('NLP_API_KEY')
IS_DEV = True if os.getenv("IS_DEV", 'True').lower() in ('true', '1', 't') else False

def get_transcript(audio):
    # for using the sdk
    #source = {'buffer': audio.getvalue(), 'mimetype': 'audio/mp3'}

    headers = {
        'Authorization': f'Token {DEEPGRAM_API_KEY}',
        # if using the sdk, set this to application/json
        'content-type': 'audio/mp3'
    }

    url = 'https://api.deepgram.com/v1/listen?punctuate=true&utterances=false'
    response = requests.post(url, headers=headers, data=audio.getvalue())
    #response = await dg_client.transcription.prerecorded(source, {'punctuate': True, 'utterances': False})

    if response.ok:
        response = response.json()
        return response['results']['channels'][0]['alternatives'][0]['transcript']
    else:
        logger.error(f"ERROR: {response.status_code} {response.text}")
        print(f"ERROR: {response.status_code} {response.text}")
        exit()

def get_youtube_audio(url):
    # url input from user
    yt = YouTube(url)
    
    # extract only audio
    video = yt.streams.filter(only_audio=True).first()

    title = yt.title
    thumbnail = yt.thumbnail_url
    audio = BytesIO()

    video.stream_to_buffer(buffer=audio)

    # validating the buffer works
    #with open('foo.mp3', "wb") as f:
    #    f.write(archive.getvalue())

    return [title, thumbnail, audio]

def get_summary_api(text):
    headers = {
        "Content-Type": "application/json",
        "apikey": TEXT_API_KEY
    }

    body = {
        "text": text
    }

    url = "https://app.thetextapi.com/text/summarize"

    response = requests.post(url, headers=headers, json=body)
    summary = json.loads(response.text)["summary"]
    
    return summary

def get_summary_nlpcloud(text):
    url = "https://api.nlpcloud.io/v1/bart-large-cnn/summarization"

    headers = {
        "Authorization": f"Token {NLP_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "text": text
    }

    response = requests.post(url, headers=headers, json=body)
    summary = response.json()["summary_text"]
    
    return summary

def lambda_handler(event, context):
    logger.info("running the entry lambda!")
    logger.info(f"event repr is:\n{event}\n\context repr is:{context}")
    print(f"event repr is:\n{event}\n\context repr is:{context}")

    # maybe need json.loads...
    video_url = event['video_url']

    # get the summary
    [title, thumbnail, summary] = main(video_url)

    # return it
    return {
        "video_title": title, 
        "video_thumbnail": thumbnail, 
        "summary": summary
    }

def main(video_url):
    [title, thumbnail, audio] = get_youtube_audio(video_url)
    raw_transcript = get_transcript(audio)

    if IS_DEV:
        summary = get_summary_nlpcloud(raw_transcript)
        # summary = raw_transcript[:300] + "..."
    else:
        summary = get_summary_api(raw_transcript)

    return title, thumbnail, summary

if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=ecuQdkBx1ic"
    print(
        lambda_handler({ 'video_url': video_url }, 'foo')
    )
    #asyncio.run(main(video_url))
