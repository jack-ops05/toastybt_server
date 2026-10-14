import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from handlers import get_data, get_metadata, post_data
from routing.request_bodies import GetDataRequest, PostDataRequest

logger = logging.getLogger("routing")

router = APIRouter()

@router.post("/post_data")
def post_data_route(request: PostDataRequest):
    logger.info(f"Post data request recieved for symbol {request.server_symbol}")
    return post_data.handler(
        request.dataset,
        request.start,
        request.end,
        request.databento_symbol,
        request.db_schema,
        request.server_symbol
    )

@router.get("/get_data")
def get_data_route(request: GetDataRequest):
    logger.info(f"Get data request recieved for symbol {request.symbol}")
    return StreamingResponse(get_data.handler(request.symbol, request.start, request.end), media_type="application/x-ndjson")

@router.get("/get_metadata")
def get_metadata_route():
    logger.info("Get metadata request recieved")
    return get_metadata.handler()