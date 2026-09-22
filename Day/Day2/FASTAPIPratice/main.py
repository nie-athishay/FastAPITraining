from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()
@app.get("/")
def home():
    return {"page":"home"}

@app.get("/about")
def about():
    return {"page":"about","author":"athishay"}

@app.get("/health")
def health():
    return {"status":"ok"}

#Post request
@app.post("/create")
def create_something():
    return {"message":"created"}

#Path Parameters
@app.get("/student/{usn}")
def get_result(usn):
    return  {"Result": "Distinction","usn":usn}

#Path Parameters with type hint
@app.get("/candidate/{rollno}")
def get_result(rollno: int):
    return  {"Result": "Distinction","rollno":rollno,"type":str(type(rollno))}

#Pydantic Model
class Item(BaseModel):
    name:str
    price:float
    in_stock: bool = True

@app.post("/items")
def create_item(item:Item):
    return {"received": item,"total_price":item.price*1.18}