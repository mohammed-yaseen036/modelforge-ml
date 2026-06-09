import unittest
import numpy as np
from vectaflow.algorithms.elasticity_model import ElasticityModel
from vectaflow.algorithms.pricing_agent import ThompsonPricingAgent
from vectaflow.simulator import MarketplaceSimulator

class TestVectaflowAlgorithms(unittest.TestCase):
    
    def test_elasticity_model_bounds(self):
        """Verify that the custom SGD elasticity model outputs valid probability boundaries."""
        model = ElasticityModel(degree=2, learning_rate=0.1, epochs=10)
        
        # Fit with some mock training data
        prices = [20.0, 20.0, 30.0, 30.0, 40.0, 40.0]
        conversions = [1, 1, 1, 0, 0, 0] # higher price -> lower conversions
        
        model.fit(prices, conversions)
        
        # Check prediction range
        prob = model.predict_probability(35.0)
        self.assertTrue(0.0 <= prob <= 1.0)
        
        # Check elasticity calculation
        el = model.calculate_elasticity(30.0)
        self.assertIsInstance(el, float)
        
    def test_thompson_agent_logic(self):
        """Verify that the Thompson Sampling pricing agent chooses valid arms and updates priors."""
        price_arms = [10.0, 20.0, 30.0]
        agent = ThompsonPricingAgent(price_arms)
        
        # Check selection
        idx, price = agent.select_price()
        self.assertIn(idx, [0, 1, 2])
        self.assertEqual(price, price_arms[idx])
        
        # Check updating priors
        initial_alpha = agent.alphas[idx]
        agent.update(idx, 1) # Successful sale
        self.assertEqual(agent.alphas[idx], initial_alpha + 1)
        self.assertEqual(agent.pulls[idx], 1)
        self.assertEqual(agent.conversions[idx], 1)
        
        # Check Lanczos PDF calculations
        x_pts, y_pts = agent.get_beta_pdf(idx, points=10)
        self.assertEqual(len(x_pts), 10)
        self.assertEqual(len(y_pts), 10)
        self.assertTrue(all(0.0 <= val <= 1.0 for val in x_pts))
        self.assertTrue(all(val >= 0.0 for val in y_pts))
        
    def test_simulator_cycles(self):
        """Verify that the e-commerce marketplace simulator updates inventory, traffic, and prices correctly."""
        sim = MarketplaceSimulator(
            base_traffic=50,
            true_p_mid=30.0,
            true_sensitivity=0.2,
            competitor_price=35.0,
            initial_inventory=1000
        )
        
        # Run 1 day with a mock selector
        # Mock price selection function returns arm 0 (index 0, price 10.0)
        day_stats = sim.step_day(
            price_selection_fn=lambda: (0, 10.0)
        )
        
        self.assertEqual(day_stats["day"], 1)
        self.assertEqual(day_stats["our_price"], 10.0)
        self.assertTrue(day_stats["visits"] <= 55)
        self.assertEqual(sim.inventory, 1000 - day_stats["sales"])
        
        # Run static baselines
        baseline_hist = sim.simulate_static_baseline(20.0, days=5)
        self.assertEqual(len(baseline_hist), 5)
        self.assertTrue(all(d["our_price"] == 20.0 for d in baseline_hist))

if __name__ == '__main__':
    unittest.main()
