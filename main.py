from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenerateRequest(BaseModel):
    product_name: str

@app.get("/")
def home():
    return {"status": "Backend çalışıyor"}

@app.get("/test")
def test():
    return {"message": "Test başarılı"}

@app.post("/generate-image")
def generate_image(data: GenerateRequest):
    prompt = f"""
    Professional ecommerce product photo for Trendyol:
    {data.product_name}

    Premium studio lighting,
    realistic commercial photography,
    clean background,
    product focused,
    no text,
    no watermark.
    """

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    return {
        "image_base64": result.data[0].b64_json
    }
