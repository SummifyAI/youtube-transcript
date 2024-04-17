from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
import os

app = FastAPI()

#Main route
@app.get("/transcript/{video_id}")
async def get_transcript(video_id: str):
    try:
        proxy_user = os.environ.get("PROXY_USER")
        proxy_password = os.environ.get("PROXY_PASSWORD")
        proxies = {
            "http": f"http://{proxy_user}:{proxy_password}@p.webshare.io:80",
             "https": f"http://{proxy_user}:{proxy_password}@p.webshare.io:80",
        }
        #transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies)
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
        frst_lang = list(transcripts._generated_transcripts)[0]
        transcript = transcripts._generated_transcripts[frst_lang].fetch()
        
        transcript_dict = {}
        for item in transcript:
            timestamp = f"{int(item['start']) // 60}:{item['start'] % 60:.0f}"
            transcript_dict[timestamp] = item['text']
        return transcript_dict
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
