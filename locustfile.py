from locust import HttpUser, task, constant_pacing


class GetJson(HttpUser):
    wait_time = constant_pacing(1)

    @task
    def get_json(self):
        self.client.get("/json")


class PostJson(HttpUser):
    wait_time = constant_pacing(1)

    @task
    def post_json(self):
        self.client.post("/1", json={"key1": "value1"})
