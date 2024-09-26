from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

#Main route
@app.get("/transcript/{video_id}")
async def get_transcript(video_id: str):
    max_retries = 5
    logger.info(f"Attempting to fetch transcript for video ID: {video_id}")
    
    for attempt in range(max_retries + 1):
        try:
            logger.info(f"Attempt {attempt + 1} of {max_retries + 1}")
            
            proxy_user = os.environ.get("PROXY_USER")
            proxy_password = os.environ.get("PROXY_PASSWORD")
            proxies = {
                "http": f"http://{proxy_user}:{proxy_password}@p.webshare.io:80",
                "https": f"http://{proxy_user}:{proxy_password}@p.webshare.io:80",
            }
            logger.debug(f"Using proxies: {proxies}")
            
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id, proxies=proxies)
            frst_lang = list(transcripts._generated_transcripts)[0]
            logger.info(f"Fetching transcript in language: {frst_lang}")
            
            transcript = transcripts._generated_transcripts[frst_lang].fetch()
            
            transcript_dict = {}
            for item in transcript:
                timestamp = f"{int(item['start']) // 60}:{item['start'] % 60:.0f}"
                transcript_dict[timestamp] = item['text']
            
            logger.info(f"Successfully fetched and processed transcript for video ID: {video_id}")
            return transcript_dict
        
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries:
                logger.error(f"All {max_retries + 1} attempts failed for video ID: {video_id}")
                raise HTTPException(status_code=404, detail=f"Failed to fetch transcript after {max_retries + 1} attempts: {str(e)}")
    
    # This line should never be reached, but added for completeness
    logger.error(f"Unexpected error occurred for video ID: {video_id}")
    raise HTTPException(status_code=404, detail="Unexpected error occurred")