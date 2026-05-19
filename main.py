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
