from fastapi import FastAPI
from .routers.whatsapp import router as whatsapp_router
from .routers.messages import router as messages_router

app = FastAPI()

app.include_router(router=whatsapp_router, prefix="/whatsapp")
app.include_router(router=messages_router, prefix="")

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
