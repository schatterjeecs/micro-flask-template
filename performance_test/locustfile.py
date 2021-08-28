from locust import HttpUser, task


class FlaskAppUser(HttpUser):
    @task
    def flask_app(self):
        self.client.get("/v1/healthcheck")
        self.client.get("/v1/content/search/digi_hashtags/2/3")