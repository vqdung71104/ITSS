import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import user_routes, project_routes, group_routes, task_routes, report_routes, evaluation_routes
from database import init_db
from config import env

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    await init_db()
    yield 
    print("Shutting down gracefully...")

class FastAPIApp:
    def __init__(self):
        self.app = FastAPI(lifespan=lifespan)
        self.configure_cors()
        self.include_routers()

    def configure_cors(self):
        origins = ["http://localhost:4200"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def include_routers(self):
        self.app.include_router(user_routes.router)
        self.app.include_router(project_routes.router)
        self.app.include_router(group_routes.router)
        self.app.include_router(task_routes.router)
        self.app.include_router(report_routes.router)
        self.app.include_router(evaluation_routes.router)

app_instance = FastAPIApp().app

if __name__ == "__main__":  
    uvicorn.run("main:app_instance", host=env.HOST, port=env.PORT, reload=True)