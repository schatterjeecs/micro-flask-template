import uuid


class ElasticHandler:
    def __init__(self, logger, es, data_lst: list):
        self.logger = logger
        self.es = es
        self.data_lst = data_lst

    async def get_data(self, index, ):
        body = {"query": {"match_all": {}}}
        return await self.es.search(
            index=index,
            body=body,
            scroll='2m',
            size=20
        )

    async def create_index_if_not_exists(self, index):
        try:
            await self.es.indices.create(index=index)
            return {"created": True, "error": None}
        except Exception as ex:
            return {"created": False, "error": ex}

    async def delete_index_if_exists(self, index):
        await self.es.indices.delete(index=index, ignore=[400, 404])

    def store_data(self, index, data: str):
        if data in self.data_lst:
            self.logger.warn("Content already present")
            return False
        else:
            self.data_lst.append(data)
            doc = {
                "content": data
            }
            self.es.index(index=index, id=uuid.uuid4(), body=doc)
            self.logger.info("Inserted new content")
            return True
