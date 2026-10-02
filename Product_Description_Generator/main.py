from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from typing import List
import json
from tenacity import retry, stop_after_attempt, wait_exponential
import os

from dotenv import load_dotenv


load_dotenv()

api_key=os.getenv('api_key')
base_url=os.getenv('base_url')
model=os.getenv('model')

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

app = FastAPI()

@app.get('/')
def health():
    return {"status": "Ok good"}

class About_Product(BaseModel):
    product_name:str
    product_features:str
    target_audience:str


class Response_AI(BaseModel):
    description:str
    bullet_point: List[str]
    seo_keyword: List[str]

system_prompt="""

you are a Product_Description_Generator Chatbot

User request :  
    Product_name
    Product_features
    target_audience

you have to response must be json 
    > "description": Description of product as paragraph
    > "bullet_point":  Quick Highlights
    > "seo_keyword": Phrase or keyword, A real person search on google ( amazone, flipkart etc.) and find it efficiently when loodking for a product 
    
         Example 1: Handmade Jasmine Candle
    product_name: handmade candle, jasmine candle, soy candle
    product_features: eco friendly candle, long burning candle, natural soy candle
    target_audience: gift for wife, home decor gift, candle for women
   
    seo_Keyword:
    [
  "handmade jasmine candle",
  "soy wax candle",
  "eco-friendly candle",
  "long burning candle",
  "jasmine scented candle",
  "home decor gift",
  "gift for wife",
  "aromatherapy candle"
]

Example 2: Wireless Earbuds (buy wireless earbuds online, best earbuds under 2000, budget earbuds)
Keyword Type	Examples
Input:
"product_name":	wireless earbuds, bluetooth earbuds, TWS earbuds
"product_features":	noise cancelling earbuds, waterproof earbuds, 30 hour battery earbuds
"target_audience":	earbuds for gym, earbuds for running, earbuds for work from home
	

seo_keyword:
[
  "wireless earbuds",
  "bluetooth 5.3 earbuds",
  "noise cancelling earbuds",
  "waterproof earbuds",
  "earbuds for gym",
  "30 hour battery earbuds",
  "best earbuds under 2000",
  "TWS earbuds"
]
Output must be in json formate 
Output:
"description": "...",
"bullet_point":["...", "..."],
"seo_keyword":["...", "..."]



"""


# @app.post('/call_ai')
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def call_ai(request:About_Product):

    user_msg=f"""
product_name: {request.product_name}
product_features:{request.product_features}
target_audience: {request.target_audience}

"""

    respone = client.chat.completions.create(
        model=model,
        temperature=0.7,
        messages = [
            {"role":"system", "content":system_prompt},
            {"role":"user", "content":user_msg} # have to fixed here
        ]
    )

    return respone

@app.post('/Analysis')
def Analysis(request: About_Product):

    try:
        ai_res = call_ai(request)  # have to fixed here 

        ai_res = ai_res.choices[0].message.content
        ai_res = ai_res.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()



        try:
            data = json.loads(ai_res)
        except json.JSONDecodeError:
            print("InvalidAPI", ai_res)
            raise HTTPException(status_code=500, detail="Invalid api")

        validate_res = Response_AI(**data)  # unpacked

        return {"status": "success", "data":validate_res}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
