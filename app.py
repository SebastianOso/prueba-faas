import uvicorn
from fastapi import FastAPI
from routes import pokemon

app = FastAPI()

@app.get("/")
def home():
    return ("hello world")

if __name__ == "__min__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

app.include_router(pokemon.router)