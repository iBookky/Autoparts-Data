import os
import json
import httpx
import urllib.parse
import asyncio
from bs4 import BeautifulSoup
from backend.database import insert_temp_part

# Import the existing call_gemini_json from the root scraper
try:
    from scraper import call_gemini_json
except ImportError:
    # Minimal fallback in case of import errors
    async def call_gemini_json(prompt: str) -> dict:
        return {}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "scraper_config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

async def scrape_external_parts(query: str, source_type: str = 'ON_DEMAND', custom_url: str = None, insert_to_db: bool = True, target_brand: str = None, target_product_name: str = None):
    config = load_config()
    headers = config.get("headers", {})
    selectors = config.get("selectors", {})
    
    if custom_url:
        url = custom_url
    else:
        url = config["search_url_template"].format(query=urllib.parse.quote(query))
        
    results = []
    
    if custom_url:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(custom_url, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    items = soup.select(selectors["product_item"])
                    if not items:
                        items = soup.select("tr, li, .item, .product")
                    
                    for item in items:
                        def get_text(sel, default=""):
                            el = item.select_one(sel)
                            return el.text.strip() if el else default

                        brand = get_text(selectors.get("brand", "a"), "GENUINE")
                        if len(brand) > 20: brand = "GENUINE"
                        
                        part_number = get_text(selectors.get("part_number", "code"), query)
                        if len(part_number) > 30: part_number = query
                        
                        oem_number = get_text(selectors.get("oem_number", ""), query)
                        product_name_th = get_text(selectors.get("product_name_th", "h3"), "อะไหล่ตัวเลือกเสริม")
                        
                        part_data = {
                            "brand": brand,
                            "part_number": part_number,
                            "oem_number": oem_number or query,
                            "product_name_th": product_name_th,
                            "product_name_en": get_text(selectors.get("product_name_en", ""), "Car Part Options"),
                            "category": get_text(selectors.get("category", ""), "อะไหล่ทดแทน"),
                            "car_brand": get_text(selectors.get("car_brand", ""), "HONDA"),
                            "car_model": get_text(selectors.get("car_model", ""), "Civic"),
                            "year_start": get_text(selectors.get("year_start", ""), "2012"),
                            "year_end": get_text(selectors.get("year_end", ""), "2020"),
                            "engine": get_text(selectors.get("engine", ""), ""),
                            "fuel": get_text(selectors.get("fuel", ""), ""),
                            "transmission": get_text(selectors.get("transmission", ""), ""),
                            "description": f"ข้อมูลดึงจาก {custom_url}",
                            "cost_unit": get_text(selectors.get("cost_unit", ""), "1200.00"),
                            "notes": "ขูดข้อมูลสดจาก URL แอดมินระบุ",
                            "source_type": source_type,
                            "status": "PENDING_URGENT" if source_type == 'ON_DEMAND' else 'PENDING',
                            "staff_note": ""
                        }
                        results.append(part_data)
        except Exception as e:
            print(f"Scraper request to custom URL {custom_url} failed: {e}")
            
    else:
        from backend.database import get_meta_aftermarket_brands
        try:
            meta_brands = [b["name"] for b in get_meta_aftermarket_brands()]
            brand_list_str = ", ".join(meta_brands)
        except Exception as e:
            meta_brands = ["TRW", "AISIN", "DENSO", "BOSCH", "BREMBO", "SKF", "GSP", "TOKICO", "KYB", "555", "RBI"]
            brand_list_str = ", ".join(meta_brands)

        import asyncio
        from scraper import perform_web_search

        # Build highly-focused search queries to get clean auto parts snippets without generic fallbacks
        queries_to_search = [query]
        if target_brand:
            queries_to_search.append(f"{query} {target_brand}")
        else:
            queries_to_search.append(f"{query} auto parts")
            
        if target_product_name:
            queries_to_search.append(f"{query} {target_product_name}")
        else:
            queries_to_search.append(f"{query} replacement")

        # Perform searches in parallel
        search_results_list = []
        tasks = [perform_web_search(q) for q in queries_to_search]
        try:
            results_text_list = await asyncio.gather(*tasks, return_exceptions=True)
            for idx, text in enumerate(results_text_list):
                if isinstance(text, str) and text.strip():
                    search_results_list.append(f"=== Search results for: {queries_to_search[idx]} ===\n{text}")
        except Exception as e:
            print(f"Error gathering parallel web search: {e}")
            
        search_text = "\n\n".join(search_results_list)
        print(f"Global web search completed. Combined text length: {len(search_text)} chars")
            
        brand_instruction = f"Search ONLY for the specified target aftermarket brand: '{target_brand}'. Ignore other aftermarket brands." if target_brand else f"Search and retrieve equivalent parts from ALL popular aftermarket brands in the system dropdown: {brand_list_str}."

        ai_prompt = f"""
        You are a professional auto parts database compiler and compatibility auditor.
        We performed a global web search for the query "{query}" (Brand: {target_brand if target_brand else 'Any'}, Name: {target_product_name if target_product_name else 'Any'}).
        Here are the search results snippets found online:
        ---
        {search_text}
        ---
        
        Extract ALL real aftermarket equivalent part numbers (such as AISIN, DENSO, BOSCH, TRW, KYB, BREMBO, SKF, GSP, etc.) that match the OEM/SKU query "{query}" STRICTLY from the provided web search results.
        
        CRITICAL COMPATIBILITY & ACCURACY INSTRUCTIONS (100% CORRECTNESS IS REQUIRED):
        1. STRICT GROUNDING: You must ONLY return aftermarket part numbers, SKU codes, and OEM numbers that are EXPLICITLY present in the web search results snippets provided. Do NOT guess, extrapolate, or assume equivalence. Do NOT use your internal training knowledge to generate part numbers that are not documented in the provided text snippets.
        2. AFTERMARKET BRAND FILTER: {brand_instruction}
        3. CROSS-COMPATIBILITY: If the aftermarket part number fits MULTIPLE different car brands, models, or years (cross-compatibility) explicitly documented in the search snippets, return a SEPARATE result item for EACH compatible vehicle specification. List ALL of them exhaustively.
        4. MULTI-BRAND OEM REPLACEMENT: If the query "{query}" is an OEM code, search for and retrieve equivalent parts from all matching brands found in the search text. Return all brands and equivalent numbers found.
        5. SPECIFIC OEM NUMBER PER VEHICLE: For each compatible vehicle option returned, provide the actual real original OEM part number corresponding specifically to that vehicle model/year configuration as documented in the search text.
        6. ZERO HALLUCINATION / 100% CORRECTNESS: The extracted aftermarket part numbers/SKUs and corresponding OEM part numbers must be 100% accurate and correct. Do NOT make up fake part numbers. If no valid, verified aftermarket parts matching the dropdown brands are found in the text, return an empty list: {{ "results": [] }}. It is better to return nothing than to return inaccurate or unverified data.
        
        Return ONLY a valid JSON object matching this schema (do not include any markdown fences or explanation):
        {{
            "results": [
                {{
                    "brand": "Brand Name (e.g. TRW, AISIN)",
                    "part_number": "Actual Alternative Part Number / SKU",
                    "oem_number": "Corresponding OEM Part Number for this specific car brand/model/year combination",
                    "product_name_th": "ชื่อสินค้าภาษาไทย เช่น ผ้าเบรกหน้าเซรามิก",
                    "product_name_en": "Product Name in English",
                    "category": "หมวดหมู่อะไหล่ เช่น ระบบเบรก",
                    "car_brand": "HONDA",
                    "car_model": "Civic",
                    "year_start": "2012",
                    "year_end": "2016",
                    "engine": "R18Z",
                    "fuel": "เบนซิน",
                    "transmission": "อัตโนมัติ",
                    "description": "Short compatibility details from search text",
                    "cost_unit": "1200.00"
                }}
            ]
        }}
        """
        try:
            ai_data = await call_gemini_json(ai_prompt)
            if ai_data and "results" in ai_data:
                for item in ai_data["results"]:
                    part_data = {
                        "brand": item.get("brand", target_brand or "TRW").strip().upper(),
                        "part_number": item.get("part_number", "SKU-ALT-100").strip().upper(),
                        "oem_number": item.get("oem_number", query).strip().upper(),
                        "product_name_th": item.get("product_name_th", target_product_name or "อะไหล่รถยนต์"),
                        "product_name_en": item.get("product_name_en", "Car Part Alt"),
                        "category": item.get("category", target_product_name or "อะไหล่"),
                        "car_brand": item.get("car_brand", "HONDA").strip().upper(),
                        "car_model": item.get("car_model", "Civic FB"),
                        "year_start": str(item.get("year_start", "2012")),
                        "year_end": str(item.get("year_end", "2016")),
                        "engine": item.get("engine", ""),
                        "fuel": item.get("fuel", ""),
                        "transmission": item.get("transmission", ""),
                        "description": item.get("description", "ดึงข้อมูลจากการค้นหาเว็บไซต์ทั่วโลกด้วย AI Search"),
                        "cost_unit": str(item.get("cost_unit", "1200.00")),
                        "notes": "สืบค้นและค้นพบสดจากเครือข่ายบราวเซอร์ระดับโลก",
                        "source_type": source_type,
                        "status": "PENDING_URGENT" if source_type == 'ON_DEMAND' else 'PENDING',
                        "staff_note": ""
                    }
                    results.append(part_data)
        except Exception as ai_err:
            print(f"Gemini fallback lookup failed: {ai_err}")

    # Insert into database temp_parts if requested
    saved_parts = []
    allowed_brands_upper = {b.upper() for b in meta_brands} if 'meta_brands' in locals() else set()
    for idx, part in enumerate(results):
        if insert_to_db:
            try:
                # Strictly filter out brands not in the dropdown list
                part_brand = part.get("brand", "").strip().upper()
                if allowed_brands_upper and part_brand not in allowed_brands_upper:
                    print(f"Skipping brand {part.get('brand')} because it is not in the system dropdown!")
                    continue
                    
                from backend.database import check_exact_duplicate
                if check_exact_duplicate(
                    part.get("brand"), part.get("part_number"), part.get("oem_number"),
                    part.get("car_brand"), part.get("car_model")
                ):
                    print(f"Skipping exact duplicate: {part.get('brand')} - {part.get('part_number')}")
                    continue
                temp_id = insert_temp_part(part)
                part_copy = part.copy()
                part_copy["id"] = temp_id
                saved_parts.append(part_copy)
            except Exception as db_err:
                print(f"Error saving scraped part: {db_err}")
        else:
            part_copy = part.copy()
            part_copy["id"] = idx
            saved_parts.append(part_copy)
            
    return saved_parts

async def run_ai_parts_search(
    brand: str,
    part_number: str,
    oem_number: str,
    car_brand: str,
    car_model: str,
    category: str,
    product_name: str
) -> list:
    """
    Calls Gemini API after verifying via global searches for each aftermarket brand
    to predict/find correct alternative aftermarket cross-references.
    """
    from backend.database import get_meta_aftermarket_brands
    try:
        meta_brands = [b["name"] for b in get_meta_aftermarket_brands()]
        allowed_brands_upper = {b.upper() for b in meta_brands}
        brand_list_str = ", ".join(meta_brands)
    except Exception:
        meta_brands = ["TRW", "AISIN", "DENSO", "BOSCH", "BREMBO", "SKF", "GSP", "TOKICO", "KYB", "555", "RBI"]
        allowed_brands_upper = {b.upper() for b in meta_brands}
        brand_list_str = ", ".join(meta_brands)

    # Perform highly-focused search queries
    import asyncio
    from scraper import perform_web_search
    query_ref = part_number if part_number else oem_number
    
    queries_to_search = [query_ref]
    if brand:
        queries_to_search.append(f"{query_ref} {brand}")
    else:
        queries_to_search.append(f"{query_ref} auto parts")
        
    if product_name:
        queries_to_search.append(f"{query_ref} {product_name}")
    else:
        queries_to_search.append(f"{query_ref} replacement")

    search_results_list = []
    tasks = [perform_web_search(q) for q in queries_to_search]
    try:
        results_text_list = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, text in enumerate(results_text_list):
            if isinstance(text, str) and text.strip():
                search_results_list.append(f"=== Search results for: {queries_to_search[idx]} ===\n{text}")
    except Exception as e:
        print(f"Error gathering parallel web search in AI Search: {e}")
        
    search_text = "\n\n".join(search_results_list)
    print(f"AI Search Google verification completed. Text length: {len(search_text)} chars")

    prompt = f"""
    You are an expert car parts matching and database cross-reference auditor.
    Verify and find alternative aftermarket cross-reference options matching:
    - Current Aftermarket Brand: {brand}
    - Part Number: {part_number}
    - OEM Number: {oem_number}
    - Car Brand: {car_brand}
    - Car Model: {car_model}
    - Product Category: {category}
    - Product Name: {product_name}

    Here are the Google/Bing search results snippets found online matching this part number across different brands:
    ---
    {search_text}
    ---

    CRITICAL COMPATIBILITY & ACCURACY INSTRUCTIONS (100% CORRECTNESS IS REQUIRED):
    1. STRICT GROUNDING: You must ONLY return aftermarket part numbers, SKU codes, and OEM numbers that are EXPLICITLY present in the web search results snippets provided. Do NOT guess, extrapolate, or assume equivalence. Do NOT use your internal training knowledge to generate part numbers that are not documented in the provided text snippets.
    2. AFTERMARKET BRAND FILTER: Search and retrieve equivalent parts from ALL popular aftermarket brands in the system dropdown: {brand_list_str}. Do NOT return any brand not in this list.
    3. CROSS-COMPATIBILITY: If this part fits MULTIPLE other car brands, models, or years (e.g. fits Toyota Corolla and Vios, or Mazda 3, or multiple years/chassis) explicitly documented in the search text, generate a SEPARATE alternative item for EACH compatible vehicle specification. List ALL of them exhaustively.
    4. SPECIFIC OEM NUMBER PER VEHICLE: For each compatibility alternative returned, find and provide the actual real original OEM part number corresponding specifically to that vehicle model/year configuration as documented in the search text.
    5. ACCURACY: The extracted aftermarket part numbers/SKUs and corresponding OEM part numbers must be 100% accurate and correct. Do NOT make up fake part numbers. If no valid equivalents matching dropdown brands are found in the text, return an empty list: {{ "alternatives": [] }}.

    Return ONLY a valid JSON object matching this schema (do not include any markdown fences or explanation):
    {{
        "alternatives": [
            {{
                "brand": "Brand Name",
                "part_number": "Alternative Part Number / SKU",
                "oem_number": "Corresponding OEM Part Number for this specific car brand/model/year combination",
                "product_name_th": "ชื่อสินค้าภาษาไทย เช่น ผ้าเบรกหน้าเซรามิก",
                "product_name_en": "Product Name in English",
                "category": "{category}",
                "car_brand": "TOYOTA",
                "car_model": "Vios",
                "year_start": "2012",
                "year_end": "2016",
                "engine": "R18Z",
                "fuel": "เบนซิน",
                "transmission": "อัตโนมัติ",
                "description": "Short compatibility details",
                "cost_unit": "1450.00"
            }}
        ]
    }}
    """
    
    results = []
    try:
        # Call the helper function
        ai_res = await call_gemini_json(prompt)
        if ai_res and "alternatives" in ai_res:
            for item in ai_res["alternatives"]:
                part_data = {
                    "brand": item.get("brand", "AISIN").strip().upper(),
                    "part_number": item.get("part_number", "SKU-ALT-100").strip().upper(),
                    "oem_number": item.get("oem_number", oem_number).strip().upper(),
                    "product_name_th": item.get("product_name_th", "อะไหล่ทดแทนแบรนด์อื่น"),
                    "product_name_en": item.get("product_name_en", "Car Part Alt"),
                    "category": category or item.get("category", "อะไหล่"),
                    "car_brand": item.get("car_brand", car_brand).strip().upper(),
                    "car_model": item.get("car_model", car_model),
                    "year_start": str(item.get("year_start", "2012")),
                    "year_end": str(item.get("year_end", "2016")),
                    "engine": item.get("engine", ""),
                    "fuel": item.get("fuel", ""),
                    "transmission": item.get("transmission", ""),
                    "description": item.get("description", "AI Suggestion"),
                    "cost_unit": str(item.get("cost_unit", "1300.00")),
                    "notes": "วิเคราะห์หาแบรนด์ทางเลือกใหม่ด้วยระบบ AI Search",
                    "source_type": "ON_DEMAND",
                    "status": "PENDING_URGENT",
                    "staff_note": ""
                }
                
                # Strictly filter out brands not in the dropdown list
                part_brand = part_data.get("brand", "").strip().upper()
                if allowed_brands_upper and part_brand not in allowed_brands_upper:
                    print(f"Skipping brand {part_data.get('brand')} because it is not in the system dropdown!")
                    continue

                # Check for exact duplicate before inserting
                from backend.database import check_exact_duplicate
                if check_exact_duplicate(
                    part_data.get("brand"), part_data.get("part_number"), part_data.get("oem_number"),
                    part_data.get("car_brand"), part_data.get("car_model")
                ):
                    print(f"Skipping exact duplicate in AI Search: {part_data.get('brand')} - {part_data.get('part_number')}")
                    continue

                # Insert into temp_parts
                temp_id = insert_temp_part(part_data)
                part_data["id"] = temp_id
                part_data["source"] = "TEMP"
                results.append(part_data)
    except Exception as e:
        print(f"AI search failed: {e}")
        raise e

    return results
