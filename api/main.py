import webbrowser

import uvicorn
from fastapi import FastAPI

from api.router.ask_router  import  router as ask_router
from api.router.prompt_manager_router import router as prompt_manager_router
app = FastAPI(title="LmxAI Ask Service API", docs_url="/api/docs", redoc_url="/api/redoc", )

app.include_router(ask_router)
app.include_router(prompt_manager_router)



if __name__ == "__main__":

    uvicorn.run(app="api.main:app", host="0.0.0.0", port=52015, reload=True, log_level="info")
    webbrowser.open("http://localhost:52015/api/docs")

