import unittest
from fastapi.testclient import TestClient
from main import app

class TestLiveGlobalSearch(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_live_search_kayaba_navara(self):
        """Verify /api/parts/live-search finds KAYABA rear shock absorbers for Nissan Navara."""
        res = self.client.post("/api/parts/live-search", data={
            "q": "โช๊คอัพหลัง",
            "car_brand": "NISSAN",
            "car_model": "Navara",
            "car_year": "2012",
            "brand": "KAYABA"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertGreater(data.get("total"), 0)
        results = data.get("results", [])
        
        # Check that returned parts include KAYABA and Navara
        brands = [r.get("brand") for r in results]
        self.assertTrue(any("KAYABA" in b or "KYB" in b for b in brands if b))
        models = [r.get("car_model") for r in results]
        self.assertTrue(any("Navara" in m for m in models if m))

if __name__ == '__main__':
    unittest.main()
