from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json

from tenacity import retry, stop_after_attempt, wait_exponential


load_dotenv()
app = FastAPI()

@app.get('/')
def health():
    return {"status": "ok"}


api_key=os.getenv("api_key")
base_url=os.getenv("base_url")
model=os.getenv("model")

# prompt = input("Enter the your request")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

class UserRequest(BaseModel):
    rough_Email:str




system_prompt="""
you are a Email Rewriter Tool

you get a rought or formal email  
generate these three field 

Email consist three fields:
"formal": "..."
"casual": "..."
"concise": "..."

Output formate must be json
Example:
rough email
{"hey you did't pay yet, pay fast,"}

Response:
{
"formal":"Dear [client!], I wanted to follow up on the outstanding invoice",
"casual":"Hey! just checking in on that invoice when you get a chance",
"concise":"Following up on invoice #123 - due 15 days ago"
}

Example 2:
rough email
{"hey you did't pay yet, pay fast,"}


Response:

{
"formal":"Dear [client!] i hope this message find you well. I am writing to kindly follow up on the outstanding invoice that is now past due. let me know when we expect payment",
"casual":"Hey! just wanted to check in on that voice when you get a meoment. Let me know if you need anything from my side",
"concise":"Following up on the outstanding invoice - now overdue. Please advise on payment timeline"
}

"""
# @app.post('/call_ai')
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def call_ai(user_msg: UserRequest):

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.7,

           messages = [
            {"role":"system", "content":system_prompt},
            {"role":"user", "content":user_msg.rough_Email}
        ])

        # return {"response": response.choices[0].message.content}
        return response


    except Exception as e:
        print("Error", e)
        return {"message":str(e)}



class AI_Response(BaseModel):
    formal: str
    casual: str
    concise: str


@app.post('/analyse')
def analyse(msg:UserRequest):

    try:
        ai_res = call_ai(msg)

        

        ai_res = ai_res.choices[0].message.content
   

        ai_res = ai_res.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

        try:
                data = json.loads(ai_res)

        except json.JSONDecodeError:
                print("Invalid json", ai_res)
                raise HTTPException(status_code=502, detail="AI returned invalid JSON")

        result = AI_Response(**data)

        return {
             "status": "success",
             "data":result
                }
                

    except Exception as e:
        print("can't be reach to api")                
        return {"Error": str(e)}

            
       


    


