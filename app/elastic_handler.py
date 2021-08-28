import asyncio
import uuid
import pandas as pd
import asyncstdlib as asyncach

from flask import json
from deprecated import deprecated

class ElasticHandler:
    def __init__(self, logger, es, data_lst: list):
        self.logger = logger
        self.es = es
        self.data_lst = data_lst

    async def get_data(self, index, page_from=0, page_size=5):
        self.logger.info(f"Searching index: {index}")
        body = {"query": {"match_all": {}}}
        return await self.es.search(
            index=index,
            body=body,
            from_=page_from,
            size=page_size
        )

    async def create_index_if_not_exists(self, index):
        try:
            await self.es.indices.create(index=index)
            return {"created": True, "error": None}
        except Exception as ex:
            return {"created": False, "error": ex}

    async def delete_index_if_exists(self, index):
        await self.es.indices.delete(index=index, ignore=[400, 404])

    @deprecated(version='0.0.1', reason="use load_data")
    async def store_data(self, index, hashtags: list):
        id_list = []

        async def store_each(data: str):
            unique_id = uuid.uuid4()
            if data in self.data_lst:
                self.logger.warn("Content already present")
                return "False"
            else:
                self.data_lst.append(data)
                doc = {
                    "content": data
                }
                await self.es.index(index=index, id=unique_id, body=doc)
                self.logger.info(f"Inserted new content with id: {unique_id}")
                id_list.append(unique_id)
                return unique_id

        co_routine = [store_each(data) for data in hashtags]
        await asyncio.gather(*co_routine)
        return json.dumps(id_list)

    async def load_data(self, index, hashtags: list):

        cache_data_raw = await self.get_unique_hashtags()
        cache_data = cache_data_raw['hashtags']
        self.logger.debug(f"cache_data: {cache_data}")
        id_list = []

        async def store_each(htags):
            if htags in cache_data:
                self.logger.debug(f"{htags} already exists")
                return
            unique_id = uuid.uuid4()
            doc = {
                "content": htags
            }
            id_list.append(unique_id)
            await self.es.index(index=index, id=unique_id, body=doc)

        co_routine = [store_each(htags) for htags in hashtags]
        await asyncio.gather(*co_routine)
        return json.dumps(id_list)

    @asyncach.lru_cache(maxsize=16)
    async def get_unique_hashtags(self):
        body = {
            "size": 0,
            "aggs": {
                "distinct_tags": {
                    "terms": {
                        "field": "content.keyword",
                        "size": 1000
                    }
                }
            }
        }
        resp = await self.es.search(index="digi_hashtags", body=body)
        htags = pd.DataFrame(resp['aggregations']['distinct_tags']['buckets']).get("key").values.tolist()
        return {"hashtags": htags}
