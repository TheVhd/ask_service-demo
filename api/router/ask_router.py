import asyncio
import logging
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status, Depends
from api.models.query_model import QueryRequest, QueryResponse
from api.services.ask_service import AskService
from api.utils.auth import get_current_user
from sse_starlette.sse import EventSourceResponse
from api.services.ask_stream_service import AskStreamService

router = APIRouter(tags=["Ask Service"])

@router.post(path="/llm/ask",
             response_model=QueryResponse,
             summary="Ask Service with LLM model",
             description="Ask Service with LLM model", )
async def handle_query(query: QueryRequest, user_data: dict = Depends(get_current_user)):
    """
    Query Router:
    - Handle the query request.
    - Execute the query service.
    """


    try:
        ask_service = AskService()
        results, errors = await ask_service.execute_ask_query_service(query=query,user_data = user_data)

        if errors:
            logging.error(f"Errors occurred: {errors}")
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(errors))

        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(results))
    except ValidationError as e:
        logging.error(f"Validation error: {e.errors()}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"details": e.errors()})
    except Exception as e:
        logging.exception(f"Unexpected error: {str(e)}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})

@router.post("/llm/ask/stream")
async def stream_llm_response(query: QueryRequest, user_data: dict = Depends(get_current_user), request=None):
    service = AskStreamService()
    async def event_generator():
        async for chunk_json in service.stream_openai_response(query.question, query.sessionID, user_data.get("user_id")):
            if request and await request.is_disconnected():
                break
            yield {"data": chunk_json}
    return EventSourceResponse(event_generator())
