from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Tibiantis Character Tracker API"}