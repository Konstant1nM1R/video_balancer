from locust import HttpUser, task, between

class VideoBalancerUser(HttpUser):
    wait_time = between(1, 3)  

    @task
    def balance_video(self):
        video_url = "http://example.com/video.mp4"
        
        self.client.get("/", params={"video": video_url})
