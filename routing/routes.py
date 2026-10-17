from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from handlers import download_data, get_data, get_metadata, sync_data
from routing.request_bodies import DownloadDataRequest, GetDataRequest

router = APIRouter()

@router.post("/download_data")
def download_data_route(request: DownloadDataRequest):
    return download_data.handler(
        request.server_symbol,
        request.dataset,
        request.start,
        request.end,
        request.databento_symbol,
        request.db_schema,
    )

@router.get("/get_data")
def get_data_route(request: GetDataRequest):
    return StreamingResponse(
        get_data.handler(
            request.symbol,
            request.start,
            request.end
        ), media_type="application/x-ndjson")

@router.get("/get_metadata")
def get_metadata_route():
    return get_metadata.handler()

@router.post("/sync_data")
def sync_data_route():
    return sync_data.handler()