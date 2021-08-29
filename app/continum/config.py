import os


class Config:
    def __init__(self):
        self.es_host = os.environ['es_host']
        self.es_port = os.environ['es_port']
