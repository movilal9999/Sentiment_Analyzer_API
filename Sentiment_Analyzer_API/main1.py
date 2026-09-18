from openai import OpenAI
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Literal
import os
import json


load_dotenv()

app = FastAPI()

@app.get('/')
def home():
    return {"message": "Status Ok Nice"}

### for gemini
# api_key=os.getenv("Gemini_API_Key")
# base_url=os.getenv("BASE_URL")
# model = os.getenv("MODEL")

#### for OpenRouter
api_key=os.getenv("api_key")
base_url=os.getenv("base_url")
model = os.getenv("model")

# prompt = "tell me about the 3 top highest demand freelancing with lowest supply skills "
class UserRequest(BaseModel):
    prompt:str


client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

system_prompt = """
you are a sentiment analysis engine
you do not talk to customers. You do not give advise.

return only valid json.
No mark down.
No extra text.



Rules:

"Sentiment" must be exactly one of: positive | neutral | frustrated
"confidence": must be a float number between "0.0" and "1.0" 
 
"Reason" A short explaination

Example:
Input: "food was great, arrived on time!"
output: {"sentiment": "positive", "confidence": 0.95, "reason": "Customer is happy with food and delibery"}

Now analyze the use message
 
"""

@app.post('/call_api')
def call_api(msg:str):
    response = client.chat.completions.create(
        model = model,
        # temprature=0.2,
        messages = [
            {'role': 'system', "content":system_prompt},
            {'role':'user', "content":msg}
        ]
    )

    # return {"response": response.choices[0].message.content}
    return response

class SentimentResponse(BaseModel):
    sentiment: Literal["frustrated", "neutral", "positive"]
    confidence: float
    reason: str

@app.post('/Analyze')
def Analyze(msg:UserRequest):

    try:
        res = call_api(msg.prompt)
        ai_ans = res.choices[0].message.content

        ai_ans = ai_ans.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        # parse the json into python dict
        try:
            data = json.loads(ai_ans)
        except json.JSONDecodeError:
            print("Ai return invalid json", ai_ans)
            raise HTTPException(
                status_code=502,
                detail="AI return invalid json"
            )

        validated_res = SentimentResponse(**data)
        
        return {
            "status":"success",
            "data": validated_res
        }

    except Exception as e:
        print("Error", e)
        return e


