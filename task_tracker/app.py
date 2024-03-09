from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.responses import Response

from report_builder import ReportBuilder
from tasks_repository import add_user_and_task, mark_task_as_finished, fetch_finished_tasks, ParamError


class CheckInRequest(BaseModel):
    user: str
    task: str


class CheckOutRequest(BaseModel):
    user: str


class ErrorResponse(JSONResponse):
    def __init__(self, error_message: str):
        super().__init__(status_code=400, content={'error': error_message})


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/checkin/')
async def checkin(request: CheckInRequest) -> JSONResponse:
    """ Endpoint for adding a new task. If the user doesn't exist, it creates the user and adds the task atomically
        using a transaction. The task is created with status 'active' and with start time set to utcnow(). """
    if not request.user or not request.task:
        return ErrorResponse("Either user or task is an empty string.")

    try:
        task_id = await add_user_and_task(user_name=request.user, task_name=request.task)
    except ParamError as e:
        return ErrorResponse(str(e))

    return JSONResponse(content={"taskId": task_id})


@app.post('/checkout/')
async def checkout(request: CheckOutRequest) -> JSONResponse:
    """ Endpoint for checking out task. Retrieves the user and the task and updates them if the task is not active.
        The task's end time is set to utcnow(). """
    if not request.user:
        return ErrorResponse("User is an empty string.")

    try:
        await mark_task_as_finished(user_name=request.user)
    except ParamError as e:
        return ErrorResponse(str(e))

    return JSONResponse(content={})


@app.get('/report/')
async def create_report() -> Response:
    """ Endpoint for fetching report of all users and checked out tasks and the time spent on each task.
        side note: in reality it should be paginated. """
    report_builder = ReportBuilder()
    async for row in fetch_finished_tasks():
        report_builder.add(row)

    report = report_builder.get()
    if not report:
        return Response(status_code=204)

    return JSONResponse(content=report)
