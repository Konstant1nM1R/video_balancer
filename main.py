from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlparse, urljoin
import random
from typing import Optional

from database import get_db, BalancerConfig, get_cached_config
from config import settings

app = FastAPI(title="Video Traffic Balancer")

@app.get("/")
@app.head("/")
async def balance_video(
    video: str = Query(..., description="URL of the video file"),
):
    if not video:
        raise HTTPException(status_code=400, detail="Video URL is required")

    try:
        parsed_url = urlparse(video)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid video URL")

        # Extract server name (s1, s2, etc.) and path
        server_name = parsed_url.netloc.split('.')[0]
        video_path = parsed_url.path

        # Get configuration from cache
        config = get_cached_config()
        
        # Determine if request should go to origin server
        should_go_to_origin = random.randint(1, config.redirect_ratio) == 1

        if should_go_to_origin:
            # Redirect to origin server
            return RedirectResponse(url=video, status_code=301)
        else:
            # Redirect to CDN
            cdn_url = f"http://{config.cdn_host}/{server_name}{video_path}"
            return RedirectResponse(url=cdn_url, status_code=301)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config")
async def get_config():
    config = get_cached_config()
    return {
        "cdn_host": config.cdn_host,
        "redirect_ratio": config.redirect_ratio
    }

@app.put("/config")
@app.post("/config")
async def update_config(
    cdn_host: Optional[str] = None,
    redirect_ratio: Optional[int] = None,
    db: Session = Depends(get_db)
):
    config = db.query(BalancerConfig).first()
    if not config:
        config = BalancerConfig(
            cdn_host=settings.CDN_HOST,
            redirect_ratio=settings.REDIRECT_RATIO
        )
        db.add(config)
    
    if cdn_host is not None:
        config.cdn_host = cdn_host
    if redirect_ratio is not None:
        if redirect_ratio < 1:
            raise HTTPException(status_code=400, detail="Redirect ratio must be at least 1")
        config.redirect_ratio = redirect_ratio
    
    db.commit()
    db.refresh(config)
    
    # Invalidate cache
    from database import _config_cache, _config_cache_time
    _config_cache = None
    _config_cache_time = 0
    
    return {
        "cdn_host": config.cdn_host,
        "redirect_ratio": config.redirect_ratio
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)