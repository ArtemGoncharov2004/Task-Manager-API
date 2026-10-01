from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.projects import router as projects_router
from app.api.tags import router as tags_router
from app.api.tasks import router as tasks_router
from app.core.exceptions import ConflictError, NotFoundError

app = FastAPI(title="Task Manager API")


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.detail})


@app.exception_handler(ConflictError)
def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


app.include_router(tasks_router)
app.include_router(projects_router)
app.include_router(tags_router)


@app.get("/health")
def health():
    return {"status": "ok"}
