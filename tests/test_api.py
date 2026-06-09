import unittest
from fastapi.testclient import TestClient
from vectaflow.app import app

class TestVectaflowAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Reset simulator state to defaults before running each test
        self.client.post("/api/reset")

    def test_get_config(self):
        response = self.client.get("/api/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("price_arms", data)
        self.assertIn("true_p_mid", data)
        self.assertIn("inventory", data)
        self.assertEqual(data["current_day"], 0)

    def test_reset_simulation_with_custom_config(self):
        config = {
            "true_p_mid": 45.0,
            "true_sensitivity": 0.25,
            "competitor_price": 40.0,
            "initial_inventory": 500
        }
        response = self.client.post("/api/reset", json=config)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "success")

        # Verify config settings were adjusted in the engine
        cfg_resp = self.client.get("/api/config")
        cfg_data = cfg_resp.json()
        self.assertEqual(cfg_data["true_p_mid"], 45.0)
        self.assertEqual(cfg_data["true_sensitivity"], 0.25)
        self.assertEqual(cfg_data["competitor_price"], 40.0)
        self.assertEqual(cfg_data["inventory"], 500)

    def test_step_simulation(self):
        response = self.client.post("/api/step")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("day_stats", data)
        self.assertIn("agent_stats", data)
        self.assertEqual(data["day_stats"]["day"], 1)

        # Confirm day counter increased in state
        cfg_resp = self.client.get("/api/config")
        self.assertEqual(cfg_resp.json()["current_day"], 1)

    def test_run_all_simulation(self):
        response = self.client.post("/api/run_all")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("history", data)
        self.assertIn("agent_stats", data)
        self.assertIn("baselines", data)

    def test_customer_action(self):
        action = {
            "price_offered": 24.99,
            "purchased": True
        }
        # Fetch initial stock levels
        cfg_data = self.client.get("/api/config").json()
        orig_inv = cfg_data["inventory"]

        response = self.client.post("/api/customer_action", json=action)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["inventory"], orig_inv - 1)

    def test_get_analytics(self):
        # Run 12 days to exceed elasticity fit history requirements (>10 samples)
        for _ in range(12):
            self.client.post("/api/step")

        response = self.client.get("/api/analytics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("true_demand_curve", data)
        self.assertIn("fitted_demand_curve", data)
        self.assertIn("elasticity_curve", data)
        self.assertIn("history", data)
        self.assertIn("cumulative_revenues", data)
        self.assertGreater(len(data["history"]), 10)

    def test_root_index_html(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("content-type", ""))
        self.assertIn("Vectaflow.AI", response.text)

if __name__ == "__main__":
    unittest.main()
