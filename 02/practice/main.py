from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/items")
async def get_items():
    data = [
        {"id": 1, "name": "apple"},
        {"id": 2, "name": "banana"}
    ]
    return JSONResponse(
        content={
            "message": "Created Succesfully",
            "data": data
        },
        status_code=201
    )