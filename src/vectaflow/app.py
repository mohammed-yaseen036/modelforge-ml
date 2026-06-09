import logging
import threading
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import numpy as np
from typing import List, Dict, Any

from vectaflow.algorithms.elasticity_model import ElasticityModel
from vectaflow.algorithms.pricing_agent import ThompsonPricingAgent
from vectaflow.simulator import MarketplaceSimulator

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("vectaflow")

app = FastAPI(title="Vectaflow Enterprise Pricing Engine", version="1.0.0")

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL EXCEPTION HANDLER ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception occurred during request %s: %s", request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred while processing the request.",
            "details": str(exc)
        }
    )

# --- GLOBAL STATE MANAGER ---
class GlobalState:
    def __init__(self):
        # Read-write synchronization lock
        self.lock = threading.Lock()
        
        # Default pricing tiers (Arms for Multi-Armed Bandit)
        self.price_arms = [19.99, 24.99, 29.99, 34.99, 39.99, 44.99, 49.99]
        
        # Initialize ML & RL Components with thread safety and stable pricing bounds
        self.agent = ThompsonPricingAgent(self.price_arms)
        self.elasticity_model = ElasticityModel(
            degree=2, 
            learning_rate=0.02, 
            l2_reg=0.001, 
            epochs=150,
            price_min=min(self.price_arms) - 10.0,
            price_max=max(self.price_arms) + 10.0
        )
        
        # Initialize Simulator
        self.simulator = MarketplaceSimulator(
            base_traffic=100,
            true_p_mid=32.0,
            true_sensitivity=0.15,
            competitor_price=35.00,
            initial_inventory=1200
        )
        
        # Tracking manual conversion inputs from customer widget
        self.manual_clicks = 0
        self.manual_purchases = 0
        
        # Stores historical transaction logs for elasticity training: list of (price, conversion)
        self.pricing_history_x = []
        self.pricing_history_y = []
        
        # Cache baseline performance metrics
        self.baseline_low = []
        self.baseline_med = []
        self.baseline_high = []
        self.run_baselines()
        logger.info("Global pricing simulator state initialized successfully.")

    def reset(self, price_arms=None, true_p_mid=32.0, true_sensitivity=0.15, competitor_price=35.0, initial_inventory=1200):
        if price_arms is not None:
            self.price_arms = price_arms
            
        self.agent = ThompsonPricingAgent(self.price_arms)
        self.elasticity_model = ElasticityModel(
            degree=2, 
            learning_rate=0.02, 
            l2_reg=0.001, 
            epochs=150,
            price_min=min(self.price_arms) - 10.0,
            price_max=max(self.price_arms) + 10.0
        )
        self.simulator = MarketplaceSimulator(
            base_traffic=100,
            true_p_mid=true_p_mid,
            true_sensitivity=true_sensitivity,
            competitor_price=competitor_price,
            initial_inventory=initial_inventory
        )
        self.pricing_history_x = []
        self.pricing_history_y = []
        self.manual_clicks = 0
        self.manual_purchases = 0
        self.run_baselines()
        logger.info("Global simulator state successfully reset with config: p_mid=%s, sensitivity=%s, competitor_price=%s, inventory=%s",
                    true_p_mid, true_sensitivity, competitor_price, initial_inventory)

    def run_baselines(self):
        # Cache static price simulations for benchmarking
        self.baseline_low = self.simulator.simulate_static_baseline(self.price_arms[1], days=30)
        self.baseline_med = self.simulator.simulate_static_baseline(self.price_arms[3], days=30)
        self.baseline_high = self.simulator.simulate_static_baseline(self.price_arms[5], days=30)

state = GlobalState()

# --- PYDANTIC SCHEMAS ---
class ConfigUpdate(BaseModel):
    true_p_mid: float
    true_sensitivity: float
    competitor_price: float
    initial_inventory: int

class CustomerAction(BaseModel):
    price_offered: float
    purchased: bool

# --- API ENDPOINTS ---

@app.get("/api/config")
def get_config():
    with state.lock:
        return {
            "price_arms": state.price_arms,
            "true_p_mid": state.simulator.true_p_mid,
            "true_sensitivity": state.simulator.true_sensitivity,
            "competitor_price": state.simulator.competitor_price,
            "inventory": state.simulator.inventory,
            "current_day": state.simulator.current_day
        }

@app.post("/api/reset")
def reset_simulation(config: ConfigUpdate = None):
    with state.lock:
        if config:
            state.reset(
                true_p_mid=config.true_p_mid,
                true_sensitivity=config.true_sensitivity,
                competitor_price=config.competitor_price,
                initial_inventory=config.initial_inventory
            )
        else:
            state.reset()
        return {"status": "success", "message": "Simulation reset successfully."}

@app.post("/api/step")
def step_one_day():
    with state.lock:
        if state.simulator.inventory <= 0:
            logger.info("Simulation step ignored: Inventory is depleted.")
            return {"status": "finished", "message": "Inventory runout, simulation complete."}
            
        # Agent selects price
        arm_idx, price = state.agent.select_price()
        
        # Callback to update the RL pricing agent for every transaction
        def agent_update_callback(a_idx, outcome):
            state.agent.update(a_idx, outcome)
            state.pricing_history_x.append(price)
            state.pricing_history_y.append(outcome)

        # Simulator runs one day
        day_stats = state.simulator.step_day(
            price_selection_fn=lambda: (arm_idx, price),
            update_feedback_fn=agent_update_callback
        )
        
        # Fit elasticity model with historical price vs conversions
        if len(state.pricing_history_x) > 10:
            state.elasticity_model.fit(state.pricing_history_x, state.pricing_history_y)
            
        logger.info("Simulated Day %d: Price offered = %s, sales = %d, revenue = %s", 
                    day_stats["day"], day_stats["our_price"], day_stats["sales"], day_stats["revenue"])
            
        return {
            "status": "success",
            "day_stats": day_stats,
            "agent_stats": state.agent.get_arm_stats()
        }

@app.post("/api/run_all")
def run_all_days():
    with state.lock:
        remaining_days = max(0, 30 - state.simulator.current_day)
        logger.info("Simulating remaining %d business days...", remaining_days)
        history = []
        
        for _ in range(remaining_days):
            if state.simulator.inventory <= 0:
                break
                
            arm_idx, price = state.agent.select_price()
            
            def agent_update_callback(a_idx, outcome):
                state.agent.update(a_idx, outcome)
                state.pricing_history_x.append(price)
                state.pricing_history_y.append(outcome)
                
            day_stats = state.simulator.step_day(
                price_selection_fn=lambda: (arm_idx, price),
                update_feedback_fn=agent_update_callback
            )
            history.append(day_stats)
            
        # Fit elasticity model
        if len(state.pricing_history_x) > 10:
            state.elasticity_model.fit(state.pricing_history_x, state.pricing_history_y)
            
        return {
            "status": "success",
            "history": state.simulator.history,
            "agent_stats": state.agent.get_arm_stats(),
            "baselines": {
                "low": state.baseline_low,
                "med": state.baseline_med,
                "high": state.baseline_high
            }
        }

@app.post("/api/customer_action")
def record_customer_action(action: CustomerAction):
    with state.lock:
        differences = np.abs(state.agent.price_arms - action.price_offered)
        arm_idx = int(np.argmin(differences))
        
        # Update pricing agent
        outcome = 1 if action.purchased else 0
        state.agent.update(arm_idx, outcome)
        
        # Record in transaction history
        state.pricing_history_x.append(action.price_offered)
        state.pricing_history_y.append(outcome)
        
        if action.purchased:
            state.manual_purchases += 1
            state.simulator.inventory = max(0, state.simulator.inventory - 1)
        state.manual_clicks += 1
        
        # Fit elasticity model with manual transaction
        if len(state.pricing_history_x) > 10:
            state.elasticity_model.fit(state.pricing_history_x, state.pricing_history_y)
            
        logger.info("Recorded customer action: price = %s, purchased = %s", action.price_offered, action.purchased)
            
        return {
            "status": "success",
            "agent_stats": state.agent.get_arm_stats(),
            "inventory": state.simulator.inventory
        }

@app.get("/api/analytics")
def get_analytics():
    with state.lock:
        # True demand vs fitted demand
        prices_range = np.linspace(min(state.price_arms) - 5, max(state.price_arms) + 5, 50)
        
        true_demands = []
        fitted_demands = []
        elasticities = []
        
        for p in prices_range:
            true_demands.append(state.simulator.get_true_conversion_rate(p))
            fitted_demands.append(state.elasticity_model.predict_probability(p))
            elasticities.append(state.elasticity_model.calculate_elasticity(p))
            
        # Parse Beta PDFs for arms
        beta_pdfs = []
        for i in range(len(state.price_arms)):
            x_pts, y_pts = state.agent.get_beta_pdf(i, points=40)
            beta_pdfs.append({
                "price": state.price_arms[i],
                "x": x_pts,
                "y": y_pts
            })
            
        # Calculate cumulative revenues
        hist = state.simulator.history
        cum_rev_agent = 0.0
        agent_rev_curve = []
        for day in hist:
            cum_rev_agent += day["revenue"]
            agent_rev_curve.append(cum_rev_agent)
            
        def get_cum_rev_curve(baseline_hist):
            cum = 0.0
            curve = []
            for day in baseline_hist[:len(hist)]:
                cum += day["revenue"]
                curve.append(cum)
            return curve

        return {
            "history": state.simulator.history,
            "true_demand_curve": {"prices": prices_range.tolist(), "rates": true_demands},
            "fitted_demand_curve": {"prices": prices_range.tolist(), "rates": fitted_demands},
            "elasticity_curve": {"prices": prices_range.tolist(), "values": elasticities},
            "beta_pdfs": beta_pdfs,
            "cumulative_revenues": {
                "agent": agent_rev_curve,
                "low_baseline": get_cum_rev_curve(state.baseline_low),
                "med_baseline": get_cum_rev_curve(state.baseline_med),
                "high_baseline": get_cum_rev_curve(state.baseline_high)
            },
            "agent_stats": state.agent.get_arm_stats(),
            "manual_stats": {
                "clicks": state.manual_clicks,
                "purchases": state.manual_purchases
            }
        }

# --- STATIC CONTENT MOUNTING ---
# Ensure all other routes are defined BEFORE mounting StaticFiles, otherwise they will be blocked.
app.mount("/", StaticFiles(directory="src/vectaflow/static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("vectaflow.app:app", host="0.0.0.0", port=8000, reload=True)
