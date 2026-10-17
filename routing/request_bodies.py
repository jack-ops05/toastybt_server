from pydantic import BaseModel


class DownloadDataRequest(BaseModel):
    server_symbol: str
    dataset: str
    start: str
    end: str
    databento_symbol: str
    db_schema: str

class GetDataRequest(BaseModel):
    symbol: str
    start: str
    end: str