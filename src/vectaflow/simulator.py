import numpy as np

class MarketplaceSimulator:
    """
    Simulates an e-commerce marketplace with consumer conversions,
    competitor pricing dynamics, inventory constraints, and multiple pricing policies.
    """
    def __init__(self, 
                 base_traffic=100, 
                 true_p_mid=30.0, 
                 true_sensitivity=0.15, 
                 competitor_price=32.0, 
                 initial_inventory=1000):
        
        self.base_traffic = base_traffic
        self.true_p_mid = true_p_mid
        self.true_sensitivity = true_sensitivity
        self.initial_competitor_price = competitor_price
        self.initial_inventory = initial_inventory
        self.reset()

    def reset(self):
        """Reset the simulator state."""
        self.current_day = 0
        self.competitor_price = self.initial_competitor_price
        self.inventory = self.initial_inventory
        self.history = []

    def get_true_conversion_rate(self, price, competitor_price=None):
        """Compute the true conversion probability given our price and competitor price."""
        if competitor_price is None:
            competitor_price = self.competitor_price
            
        z = self.true_sensitivity * (self.true_p_mid - price)
        base_conversion = 1.0 / (1.0 + np.exp(-z))
        
        if price > competitor_price:
            undercut_ratio = (price - competitor_price) / competitor_price
            penalty = np.exp(-2.0 * undercut_ratio)
            conversion = base_conversion * penalty
        else:
            cheaper_ratio = (competitor_price - price) / price
            boost = 1.0 + 0.15 * (1.0 - np.exp(-3.0 * cheaper_ratio))
            conversion = base_conversion * boost
            
        return float(np.clip(conversion, 0.0, 1.0))

    def update_competitor_price(self, our_prev_price):
        """Competitor adjusts their price based on our previous price with some random behavior."""
        if our_prev_price is None:
            our_prev_price = self.initial_competitor_price
            
        min_floor = self.true_p_mid * 0.6
        
        if np.random.rand() < 0.15:
            target_price = max(min_floor, our_prev_price * 0.8)
        else:
            variation = np.random.uniform(-0.05, 0.05)
            target_price = max(min_floor, our_prev_price * (1.0 + variation))
            
        self.competitor_price = 0.7 * self.competitor_price + 0.3 * target_price
        self.competitor_price = float(np.round(self.competitor_price, 2))

    def step_day(self, price_selection_fn, update_feedback_fn=None):
        """
        Simulate one business day.
        """
        self.current_day += 1
        
        if self.inventory <= 0:
            day_stats = {
                "day": self.current_day,
                "our_price": 0.0,
                "competitor_price": self.competitor_price,
                "visits": 0,
                "sales": 0,
                "revenue": 0.0,
                "inventory": 0,
                "conversion_rate": 0.0
            }
            self.history.append(day_stats)
            return day_stats

        our_prev_price = self.history[-1]["our_price"] if len(self.history) > 0 else None
        if our_prev_price is not None and our_prev_price > 0:
            self.update_competitor_price(our_prev_price)

        arm_idx, price = price_selection_fn()
        
        daily_traffic = int(np.round(self.base_traffic * np.random.uniform(0.9, 1.1)))
        visits = min(daily_traffic, self.inventory)
        
        conversion_prob = self.get_true_conversion_rate(price)
        conversions = np.random.binomial(n=1, p=conversion_prob, size=visits)
        sales = int(np.sum(conversions))
        revenue = float(np.round(sales * price, 2))
        
        self.inventory -= sales
        self.inventory = max(0, self.inventory)
        
        if update_feedback_fn is not None and visits > 0:
            for outcome in conversions:
                update_feedback_fn(arm_idx, int(outcome))

        day_stats = {
            "day": self.current_day,
            "our_price": float(price),
            "competitor_price": self.competitor_price,
            "visits": visits,
            "sales": sales,
            "revenue": revenue,
            "inventory": self.inventory,
            "conversion_rate": float(sales / visits) if visits > 0 else 0.0
        }
        self.history.append(day_stats)
        return day_stats

    def simulate_static_baseline(self, static_price, days=30):
        """Simulate a baseline history where price is kept constant to compare performance."""
        saved_competitor_price = self.competitor_price
        saved_inventory = self.inventory
        
        self.competitor_price = self.initial_competitor_price
        self.inventory = self.initial_inventory
        
        baseline_history = []
        
        for d in range(1, days + 1):
            if self.inventory <= 0:
                baseline_history.append({
                    "day": d,
                    "our_price": 0.0,
                    "revenue": 0.0,
                    "sales": 0,
                    "inventory": 0
                })
                continue
                
            our_prev_price = baseline_history[-1]["our_price"] if len(baseline_history) > 0 else None
            if our_prev_price is not None and our_prev_price > 0:
                self.update_competitor_price(our_prev_price)
                
            daily_traffic = int(np.round(self.base_traffic * np.random.uniform(0.9, 1.1)))
            visits = min(daily_traffic, self.inventory)
            
            conversion_prob = self.get_true_conversion_rate(static_price)
            conversions = np.random.binomial(n=1, p=conversion_prob, size=visits)
            sales = int(np.sum(conversions))
            revenue = float(np.round(sales * static_price, 2))
            
            self.inventory -= sales
            self.inventory = max(0, self.inventory)
            
            baseline_history.append({
                "day": d,
                "our_price": float(static_price),
                "revenue": revenue,
                "sales": sales,
                "inventory": self.inventory
            })
            
        self.competitor_price = saved_competitor_price
        self.inventory = saved_inventory
        
        return baseline_history
