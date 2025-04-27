## Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your configuration:
```
DATABASE_URL=postgresql://pos:pos@localhost:5432/vid
CDN_HOST=cdn.example.com
REDIRECT_RATIO=5
```

4. Create the PostgreSQL database:
```bash
createdb video_balancer
```

## Running the Service

Start the service:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Video Balancing
- `GET /?video=http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8`
  - Redirects to either origin server or CDN based on configuration

### Configuration Management
- `GET /config` - Get current configuration
- `PUT /config` - Update configuration
  - Parameters:
    - `cdn_host` (optional): New CDN host
    - `redirect_ratio` (optional): New redirect ratio

## Example Usage

1. Get current configuration:
```bash
curl http://localhost:8000/config
```

2. Update configuration:
```bash
curl -X PUT "http://localhost:8000/config?cdn_host=new-cdn.example.com&redirect_ratio=10"
```

3. Request a video:
```bash
curl -L "http://localhost:8000/?video=http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8"
```

## Performance

The service is designed to handle at least 1000 requests per second on a mid-range laptop with Core i5 7th generation and 16GB RAM. 

### TEST

wrk -t4 -c1000 -d30s "http://localhost:8000/?video=http://s1.origin-cluster/video/1488/xcg2djHckad.m3u8"