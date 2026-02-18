from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    host = "http://localhost:8002/"  # Указываем адрес API
    wait_time = between(1, 3)  # Пауза между запросами

    @task
    def get_trainings(self):
        self.client.get("/tags/")
