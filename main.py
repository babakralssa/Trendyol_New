from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os
import requests
from requests.auth import HTTPBasicAuth
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


class GenerateRequest(BaseModel):
    product_name: str


class TrendyolRequest(BaseModel):
    supplier_id: str
    api_key: str
    api_secret: str


@app.get("/")
def home():
    return {
        "status": "ENTEGRIFY Backend çalışıyor",
        "openai_key": "var" if OPENAI_API_KEY else "yok"
    }


@app.get("/test")
def test():
    return {"message": "Test başarılı"}


@app.post("/products")
def get_products(data: TrendyolRequest):
    try:
        url = f"https://apigw.trendyol.com/integration/product/sellers/{data.supplier_id}/products"

        headers = {
            "User-Agent": f"{data.supplier_id} - SelfIntegration",
            "Accept": "application/json"
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
                "message": "Trendyol API hata döndürdü",
                "status_code": response.status_code,
                "error": response.text[:1000]
            }

        result = response.json()

        products = []

        for p in result.get("content", []):
            images = p.get("images", [])

            clean_images = []
            for img in images:
                clean_images.append({
                    "url": img.get("url")
                })

            products.append({
                "title": p.get("title", "İsimsiz Ürün"),
                "barcode": p.get("barcode", ""),
                "stockCode": p.get("stockCode", ""),
                "productMainId": p.get("productMainId", ""),
                "images": clean_images
            })

        return {
            "success": True,
            "count": len(products),
            "products": products
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Backend ürün çekme hatası",
            "error": str(e),
            "trace": traceback.format_exc()
        }


@app.post("/generate-image")
def generate_image(data: GenerateRequest):
    try:
        if not OPENAI_API_KEY:
            return {
                "success": False,
                "error": "OPENAI_API_KEY Render Environment Variables içinde yok."
            }

        prompt = f"""
        Professional ecommerce product photo for ENTEGRIFY marketplace system.

        Product:
        {data.product_name}

        Create a premium commercial product photo.
        Use realistic lighting, clean composition, high-end ecommerce style.
        No text, no watermark, no fake logo.
        """

        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        return {
            "success": True,
            "image_base64": result.data[0].b64_json
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }
