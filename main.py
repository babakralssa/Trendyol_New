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
import requests
from requests.auth import HTTPBasicAuth

class TrendyolRequest(BaseModel):
    supplier_id: str
    api_key: str
    api_secret: str


@app.post("/products")
def get_products(data: TrendyolRequest):
    url = f"https://apigw.trendyol.com/integration/product/sellers/{data.supplier_id}/products"

    headers = {
        "User-Agent": f"{data.supplier_id} - SelfIntegration"
    }

    response = requests.get(
        url,
        headers=headers,
        auth=HTTPBasicAuth(data.api_key, data.api_secret),
        timeout=30
    )

    if response.status_code != 200:
        return {
            "success": False,
            "status_code": response.status_code,
            "error": response.text
        }

    result = response.json()

    products = []

    for p in result.get("content", []):
        products.append({
            "title": p.get("title"),
            "barcode": p.get("barcode"),
            "stockCode": p.get("stockCode"),
            "images": p.get("images", [])
        })

    return {
        "success": True,
        "products": products
    }
