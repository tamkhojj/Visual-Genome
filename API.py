from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import os
from mangum import Mangum

dir = os.path.dirname(__file__)

app = FastAPI()
handler = Mangum(app)


@app.get('/')
async def root():
    return {"Hello": "World"}


@app.get("/{data}", response_class=StreamingResponse)
async def get_data(data):
    path = os.path.join(dir, 'Dataset/{filename}.json/{filename}.json'.format(filename=data))

    if os.path.exists(path):
        file = open(path, "rb")
        return StreamingResponse(file, media_type="application/json")
    return JSONResponse({"Error": "File Not Found"})
