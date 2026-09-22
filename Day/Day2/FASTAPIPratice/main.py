from fastapi import FastAPI
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