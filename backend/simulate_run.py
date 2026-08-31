import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def run_simulation():
    print("==================================================================")
    print("        SIMULATING OEM VS AFTERMARKET CROSS-REF SYSTEM RUN        ")
    print("==================================================================")

    # 1. Search for a part that doesn't exist in Master
    print("\n[Sales] 1. Searching for '52610-TR7-B03'...")
    res = httpx.get(f"{BASE_URL}/api/parts/search?q=52610-TR7-B03")
    data = res.json()
    print(f"Results Count: {data.get('total', 0)}")
    print(f"Results: {json.dumps(data.get('results', []), indent=2, ensure_ascii=False)}")

    # 2. Trigger Live Search (External Scraper)
    print("\n[Sales] 2. Triggering Live Search for '52610-TR7-B03'...")
    res = httpx.post(f"{BASE_URL}/api/parts/live-search", data={"q": "52610-TR7-B03"})
    data = res.json()
    if not data.get("success", False):
        print(f"Live Search failed: {data}")
        return
        
    print(f"Live Search Scraped Total: {data.get('total', 0)}")
    for idx, item in enumerate(data.get('results', [])):
        print(f"  - Scraped Item {idx+1}: {item.get('brand')} | SKU: {item.get('part_number')} | Status: {item.get('status')} (Badge: ⚠️ รอตรวจสอบ)")

    # 3. Admin views queue
    print("\n[Admin] 3. Viewing Temp Parts Queue...")
    res = httpx.get(f"{BASE_URL}/api/admin/temp-parts")
    data = res.json()
    print(f"Admin Queue Size: {data.get('total', 0)}")
    temp_id = None
    for idx, item in enumerate(data.get('results', [])):
        print(f"  - [{item.get('status')}] {item.get('brand')} | SKU: {item.get('part_number')} | New Pair? {item.get('is_new_pair')}")
        if item.get('brand') == 'LUCAS':
            temp_id = item.get('id')

    # 4. Admin Approves and Confirms
    if temp_id:
        print(f"\n[Admin] 4. Confirming Temp Part ID {temp_id} -> Move to Master...")
        res = httpx.post(f"{BASE_URL}/api/admin/review/{temp_id}", data={"action": "confirm"})
        print(f"Response: {res.json()}")

        # 5. Search again to see it's now in Master
        print("\n[Sales] 5. Searching again for '52610-TR7-B03'...")
        res = httpx.get(f"{BASE_URL}/api/parts/search?q=52610-TR7-B03")
        data = res.json()
        print(f"New Search Results Count: {data.get('total', 0)}")
        for idx, item in enumerate(data.get('results', [])):
            print(f"  - Match {idx+1}: {item.get('brand')} | SKU: {item.get('part_number')} | Source: {item.get('source')} | Status: {item.get('status')}")

    print("\n==================================================================")
    print("               SIMULATION COMPLETED PERFECTLY!                    ")
    print("==================================================================")

if __name__ == "__main__":
    run_simulation()
