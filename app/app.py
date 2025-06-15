# main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в моё приложение FastAPI!"}
    return {"message": "Авторелоад действительно работает"}
    # return FileResponse("../index_app.html")

@app.post("/calculate")
async def calculate(num1 : int, num2 : int):
    return {"message": num1 + num2}
