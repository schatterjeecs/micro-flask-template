import os
import asyncio

from aioflask import Flask
from elasticsearch import AsyncElasticsearch
import toml

app = Flask(__name__)
app.config.from_file('../../config.toml', toml.load)
logger = app.logger
logger.info(f"Started app with name: {app.name}")

# fix required for running Flask with async on Windows
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

es_client = AsyncElasticsearch([
    {'host': 'localhost'},
    {'host': 'es01',
     'port': 9200
     },
])
from continum.contents import routes
from continum.generic import routes
