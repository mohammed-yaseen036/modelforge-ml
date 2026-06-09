import numpy as np
from typing import List, Tuple, Dict, Any

class ThompsonPricingAgent:
    """
    Thompson Sampling Multi-Armed Bandit agent for dynamic pricing.
    Tracks binomial conversion distributions using Beta(alpha, beta) priors.
    """
    def __init__(self, price_arms: List[float] | np.ndarray):
        self.price_arms = np.array(price_arms, dtype=float)
        self.n_arms = len(price_arms)
        self.alphas = np.ones(self.n_arms, dtype=float)
        self.betas = np.ones(self.n_arms, dtype=float)
        
        self.pulls = np.zeros(self.n_arms, dtype=int)
        self.conversions = np.zeros(self.n_arms, dtype=int)

    def select_price(self) -> Tuple[int, float]:
        """
        Selects optimal price tier using Thompson Sampling.
        
        Returns:
            Tuple[int, float]: The index of the selected arm and the price value.
        """
        sampled_rates = np.random.beta(self.alphas, self.betas)
        expected_revenues = self.price_arms * sampled_rates
        selected_arm_idx = int(np.argmax(expected_revenues))
        return selected_arm_idx, float(self.price_arms[selected_arm_idx])

    def update(self, arm_idx: int, conversion: int) -> None:
        """
        Update the Beta distribution parameters based on conversion feedback.
        
        Args:
            arm_idx (int): Index of the pulled arm.
            conversion (int): 1 if a purchase occurred, 0 otherwise.
        """
        self.pulls[arm_idx] += 1
        if conversion == 1:
            self.alphas[arm_idx] += 1
            self.conversions[arm_idx] += 1
        else:
            self.betas[arm_idx] += 1

    def get_arm_stats(self) -> List[Dict[str, Any]]:
        """
        Get summary statistics for each pricing arm.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing metrics for each pricing arm.
        """
        stats = []
        for i in range(self.n_arms):
            alpha = self.alphas[i]
            beta = self.betas[i]
            mean_conversion = alpha / (alpha + beta)
            variance = (alpha * beta) / (((alpha + beta) ** 2) * (alpha + beta + 1))
            expected_revenue = self.price_arms[i] * mean_conversion
            
            stats.append({
                "arm_index": i,
                "price": float(self.price_arms[i]),
                "alpha": float(alpha),
                "beta": float(beta),
                "pulls": int(self.pulls[i]),
                "conversions": int(self.conversions[i]),
                "conversion_rate_mean": float(mean_conversion),
                "conversion_rate_std": float(np.sqrt(variance)),
                "expected_revenue": float(expected_revenue)
            })
        return stats

    @staticmethod
    def _log_gamma(z: float) -> float:
        """
        Compute Log Gamma function using the Lanczos approximation from scratch.
        Provides high-precision log-gamma evaluation for Beta distribution PDF.
        
        Args:
            z (float): Input value, must be positive.
            
        Returns:
            float: Log Gamma value ln(Gamma(z)).
        """
        if z < 0.5:
            return np.log(np.pi) - np.log(np.sin(np.pi * z)) - ThompsonPricingAgent._log_gamma(1.0 - z)
            
        z -= 1.0
        x = 0.99999999999980993
        coef = [
            57.1562356658629235, -59.5979603554754912, 14.1360979747417471,
            -0.491913816097620199, .339946499848118887e-4, .46523628923325806e-4,
            -.9837447530487956e-4, .15808870322495893e-3, -.2102644415749479e-3,
            .21743961855536176e-3, -.16431810653676374e-3, .84418223983852743e-4,
            -.26190838401581408e-4, .36899182659531622e-5
        ]
        for i, c in enumerate(coef):
            x += c / (z + i + 1)
        t = z + 5.24218750000000000
        return 0.5 * np.log(2.0 * np.pi) + (z + 0.5) * np.log(t) - t + np.log(x)

    def get_beta_pdf(self, arm_idx: int, points: int = 50) -> Tuple[List[float], List[float]]:
        """
        Compute PDF values for the Beta distribution of a given arm index.
        
        Args:
            arm_idx (int): The arm index.
            points (int): Number of coordinate points to sample.
            
        Returns:
            Tuple[List[float], List[float]]: X points (conversion rate) and Y points (PDF value).
        """
        alpha = self.alphas[arm_idx]
        beta = self.betas[arm_idx]
        x = np.linspace(0.001, 0.999, points)
        log_beta_const = (self._log_gamma(alpha) + 
                          self._log_gamma(beta) - 
                          self._log_gamma(alpha + beta))
        log_pdf = (alpha - 1.0) * np.log(x) + (beta - 1.0) * np.log(1.0 - x) - log_beta_const
        pdf = np.exp(log_pdf)
        return x.tolist(), pdf.tolist()
