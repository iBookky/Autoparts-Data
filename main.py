import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from scraper import verify_and_process_autoparts

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="VIN Car Parts Discovery API",
    description="API for decoding VIN and searching car parts.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic request model
class SearchRequest(BaseModel):
    oem_code: Optional[str] = Field(None, description="OEM Part Number if known")
    vin: Optional[str] = Field(None, description="VIN code")
    brand: Optional[str] = Field(None, description="Car manufacturer/brand")
    model: Optional[str] = Field(None, description="Car model")
    year: Optional[str] = Field(None, description="Car year")
    product_name: Optional[str] = Field(None, description="Car part/product name to search")

    @field_validator('vin')
    @classmethod
    def validate_vin_flexible(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        v = v.strip().upper()
        return v

@app.get("/api/brands")
async def api_brands():
    try:
        from sheets_helper import SheetsHelper
        sheets = SheetsHelper()
        brands = sheets.get_brands_from_sheet()
        return {"success": True, "brands": brands, "total": len(brands)}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(
            content="<h1>Frontend index.html is missing. Please create it.</h1>", 
            status_code=404
        )
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/search")
async def api_search(req: SearchRequest):
    try:
        result = await verify_and_process_autoparts(
            oem_code=req.oem_code,
            vin=req.vin,
            brand=req.brand,
            model=req.model,
            year=req.year,
            product_name=req.product_name or ""
        )
        if not result.get("success", True):
            return {
                "success": False,
                "error": result.get("error", "เกิดข้อผิดพลาดในการตรวจสอบข้อมูล"),
                "data": result
            }
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
