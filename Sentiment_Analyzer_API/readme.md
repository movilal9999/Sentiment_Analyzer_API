# Sentiment Analyzer Chat Bot

A FastAPI-based API that analyzes customer messages and returns **structured sentiment analysis** using an LLM via OpenRouter.

## What It Does

Send any text message -> get back:
**sentiment**: `positive` | `neutral` | `frustrated`
**confidence**: a float between `0.0` and `1.0`
**reason**: a short explanation

## Tech Stack

Web framework => FastAPI 
Data validation => Pydantic 
LLM provider => OpenRouter (OpenAI-compatible) and more like gemini etc.
LLM SDK => OpenAI Python SDK 
Retry logic => Tenacity 
Env management => python-dotenv 


## Setup

### 1. Clone & enter the project

# bash
cd Sentiment_Analyzer_API

# Create a Virtual Environment
python -m venv SAA_env

# Activate the Environment
Window
.\SAA_env\Scripts\Activate

Linux/Mac
source SAA_env/bin/activate

# install dependencies
pip install -r requirements.txt

# Create .env file and you have to setup these 
api_key="your-openrouter-api-key"
base_url="https://openrouter.ai/api/v1/"
model="inclusionai/ling-3.0-flash-fin:free"

> Get a free key at: https://openrouter.ai/keys

uvicorn main2:app --reload

> Request Body (you have to enter your request)
{
  "prompt": "The delivery was super late and the food was cold."
}

> Response
{
  "status": "success",
  "data": {
    "sentiment": "frustrated",
    "confidence": 0.99,
    "reason": "Customer is unhappy with the late delivery and cold food"
  }
}



# main -> first version that respond only string
# main1 -> without tenacity
# main2 -> Apply tenaciity (means if api fails then automatically retry 4 times try again then raise error)