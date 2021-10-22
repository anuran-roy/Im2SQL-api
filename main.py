from fastapi import FastAPI, status
from routes import sqlify

app = FastAPI()

app.include_router(sqlify.router)


@app.get('/', status_code=status.HTTP_200_OK)
async def health_response():
    return {
        "status": status.HTTP_200_OK,
        "message": "Hello world!"
    }
