from pydantic import BaseModel


class PostDataRequest(BaseModel):
    dataset: str
    start: str
    end: str
    databento_symbol: str
    db_schema: str
    server_symbol: str

class GetDataRequest(BaseModel):
    symbol: str
    start: str
    end: str