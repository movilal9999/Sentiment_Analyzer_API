from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI()

@app.get('/')
def home():
    return {"message": "Status Ok Nice"}


api_key=os.getenv("Gemini_API_Key")
base_url=os.getenv("BASE_URL")
model = os.getenv("MODEL")

# prompt = "tell me about the 3 top highest demand freelancing with lowest supply skills "
class User_msg(BaseModel):
    prompt:str


client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


@app.post('/call_api')
def call_api(msg:User_msg):
    response = client.chat.completions.create(
        model = model,
        # temprature=0.2,
        messages = [
            {'role': 'system', "content":"you are a system assistant"},
            {'role':'user', "content":msg.prompt}
        ]
    )

    return {"response": response.choices[0].message.content}