from fastapi import FastAPI
from app.api import character

app = FastAPI()

app.include_router(character.router, prefix="/characters", tags=["Characters"])
