from bs4 import BeautifulSoup
import re

def test_admin_meta_view_dom():
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Admin meta tab button
    tab_btn = soup.find("button", {"id": "tab-admin-meta"})
    assert tab_btn is not None, "Tab button #tab-admin-meta not found"
    assert "switchAdminTab('meta')" in tab_btn.get("onclick", "")
    print("✓ Tab button #tab-admin-meta correctly triggers switchAdminTab('meta')")

    # 2. Admin meta view container
    meta_view = soup.find("div", {"id": "admin-meta-view"})
    assert meta_view is not None, "Container #admin-meta-view not found"
    print("✓ Container #admin-meta-view exists")

    # 3. Verify all 6 cards and essential IDs
    required_ids = [
        # Card 1: Aftermarket Brands
        "meta-aftermarket-count", "meta-add-brand-name", "meta-aftermarket-list",
        # Card 2: Car Brands
        "meta-car-brands-count", "meta-add-car-brand-name", "meta-car-brands-list",
        # Card 3: Categories
        "meta-categories-count", "meta-add-cat-name-th", "meta-add-cat-name-en", "meta-categories-list",
        # Card 4: Car Models
        "meta-model-brand-filter", "meta-add-model-brand", "meta-add-model-name", "meta-car-models-list",
        # Card 5: Production Years
        "meta-years-count", "meta-add-year-val", "meta-years-list",
        # Card 6: AI Models
        "meta-ai-count", "meta-add-ai-name", "meta-add-ai-provider", "meta-ai-list"
    ]

    for req_id in required_ids:
        elem = soup.find(id=req_id)
        assert elem is not None, f"Required element #{req_id} not found in DOM"
        print(f"✓ Element #{req_id} verified")

    # 4. Verify JS functions in script tags
    required_js_funcs = [
        "loadAdminMetaOptions",
        "renderAdminMetaOptions",
        "renderAdminMetaCarModels",
        "filterAdminMetaCarModels",
        "submitAddAftermarketBrand",
        "deleteMetaAftermarketBrand",
        "submitAddCarBrand",
        "deleteMetaCarBrand",
        "submitAddCategory",
        "deleteMetaCategory",
        "submitAddCarModel",
        "deleteMetaCarModel",
        "submitAddCarYear",
        "deleteMetaCarYear",
        "submitAddAIModel",
        "deleteMetaAIModel"
    ]

    for func in required_js_funcs:
        assert f"function {func}" in html_content or f"async function {func}" in html_content, f"JS function {func} missing from index.html"
        print(f"✓ JS function {func} found in script")

    print("\n>>> ALL DOM AND SCRIPT INTEGRITY CHECKS PASSED! <<<")

if __name__ == "__main__":
    test_admin_meta_view_dom()
