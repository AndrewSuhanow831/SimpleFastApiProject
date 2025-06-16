# main.py
import json
import os.path

from fastapi import FastAPI, Form, UploadFile, File
from starlette.responses import FileResponse, RedirectResponse

from models.models import User, Feedback


id_auto_increment: int = 2

dict_responses: dict =  {1 : "John_Doe", 2 : "Alice_Cooper"}

list_feedback: list[Feedback] = []

unacceptable_words: list = ["редиска", "редиски", "редиске", "редиску", "редиской", "редискою",
                            "бяка", "бяки", "бяке", "бяку", "бякой", "бякою",
                            "козявка", "козявки", "козявке", "козявку", "козявкой", "козявкою"]

feedback_filename = "feedback.json"

error_response: str = "invalid_name"
app = FastAPI()

@app.get("/")
async def root():
    # return {"message": "Hello World"}
    return FileResponse("index.html")

@app.get("/users")
async def get_users(name: str = None, limit: int = 10):
    ret_responses = dict_responses
    if name:
        ret_responses = {key : value for key, value in ret_responses.items() if name == value}

    return dict(list(ret_responses.items())[:limit])

@app.get("/user/{user_id}")
async def get_users_by_id(user_id: int):
    if user_id in dict_responses:
        return {"id" : user_id, "name" : dict_responses[user_id]}
    return error_response

@app.post("/user")
async def add_user(user: User):
    global id_auto_increment
    id_auto_increment += 1
    user_data: str = user.first_name + '_' + user.last_name
    dict_responses[id_auto_increment] = user_data
    return {f"User with name={user_data} was added into responses"}

@app.post("/feedback")
async def add_feedback(feedback: Feedback, is_premium: bool = False):
    try:
        inputs: list[str] = feedback.message.lower().split(' ')
        for val in inputs:
            if await validation_add_feedback(val):
                continue
            raise ValueError("Использование недопустимых слов")

        objects: list[dict] = []
        if os.path.isfile(feedback_filename):
            with open(feedback_filename, encoding="UTF-8") as file:
                try:
                    objects = list(json.load(file))
                except json.JSONDecodeError:
                    print("Ошибка при чтении файла. Файл может быть поврежден или пуст.")
                    objects = []
        with open(feedback_filename, "w", encoding="UTF-8") as file:
            new_obj = {"name" : feedback.name, "message" : feedback.message, "contact" : {"email" : feedback.contact.email}}
            if not feedback.contact.phone is None:
                new_obj["contact"]["phone"] = feedback.contact.phone
            objects.append(new_obj)
            json.dump(objects, file, ensure_ascii=False, indent=2, separators=(',', ': '))

        if is_premium:
            return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён. Ваш отзыв будет рассмотрен в приоритетном порядке."}
        return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}
    except Exception as err:
        return {"message": err}

async def validation_add_feedback(val: str):
    for word in unacceptable_words:
        if len(word) > len(val):
            continue
        len_word = len(word)
        len_val = len(val)
        index_val = 0
        while index_val <= len_val - len_word:
            is_valid: bool = False
            index_word = 0
            for i in range(index_val, index_val + len_word):
                # print(f"{val[i]} ? {word[index_word]}")
                if val[i] != word[index_word]:
                    index_val += 1
                    is_valid = True
                    break
                index_word += 1
            if not is_valid:
                return False
    return True

@app.get("/feedback")
async def get_feedback():
    try:
        if not os.path.isfile(feedback_filename):
            return {"empty page \'feedback\'"}
        with open(feedback_filename, encoding="UTF-8") as file:
            return json.load(file)
    except Exception as err:
        return {"message": err}

@app.options("/")
def options_example():
    return {"message": "Этот запрос проверяет, какие методы доступны"}

@app.head("/")
def head_example():
    return {"message": "Ответ без тела (только заголовки)"}

# @app.patch("/users/{user_id}")
# def patch_user(user_id: int):
#     return {"message": f"Пользователь {user_id} частично обновлён"}

@app.trace("/")
def trace_example():
    return {"message": "TRACE-запрос вернёт сам себя"}

@app.post("/submit")
async def submit_form(username: str = Form(...), password: str = Form(...)):
    return {"username": username, "password_length": len(password)}
    # return RedirectResponse("index_app.html")
    # return FileResponse("index_app.html")

@app.get("/file/download")
async def download_file():
    return FileResponse(path='index.html', filename='page_code.html', media_type='multipart/form-data')

# @app.post("/file/upload-bytes")
# def upload_file_bytes(file_bytes: bytes = File()):
#     return {'file_bytes': str(file_bytes)}

@app.post("/file/upload-file")
def upload_file(file: UploadFile):
    return file