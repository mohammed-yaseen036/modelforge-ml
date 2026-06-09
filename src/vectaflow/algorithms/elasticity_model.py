import numpy as np

class ElasticityModel:
    """
    Polynomial Logistic Regression model trained from scratch with SGD and L2 regularization.
    Estimates the conversion probability P(conversion | price) and calculates price elasticity.
    """
    def __init__(self, degree=2, learning_rate=0.01, l2_reg=0.001, epochs=100, price_min=0.0, price_max=100.0):
        self.degree = degree
        self.learning_rate = learning_rate
        self.l2_reg = l2_reg
        self.epochs = epochs
        self.weights = None
        self.price_min = price_min
        self.price_max = price_max

    def _scale_price(self, price):
        """Scale price to [0, 1] to ensure numerical stability in polynomial features."""
        if self.price_max <= self.price_min:
            return np.zeros_like(price, dtype=float)
        scaled = (price - self.price_min) / (self.price_max - self.price_min)
        return np.clip(scaled, 0.0, 1.0)

    def _polynomial_features(self, scaled_price):
        """Generate polynomial feature vectors: [1, x, x^2, ..., x^degree]."""
        if np.isscalar(scaled_price):
            return np.array([scaled_price ** i for i in range(self.degree + 1)])
        features = np.vstack([scaled_price ** i for i in range(self.degree + 1)]).T
        return features

    def _sigmoid(self, z):
        """Sigmoid function clamped to prevent overflow."""
        z = np.clip(z, -20.0, 20.0)
        return 1.0 / (1.0 + np.exp(-z))

    def fit(self, prices, conversions):
        """
        Fit the model weights using SGD with L2 regularization.
        """
        prices = np.array(prices, dtype=float)
        conversions = np.array(conversions, dtype=float)
        
        if len(prices) == 0:
            return
        
        scaled_prices = self._scale_price(prices)
        X = self._polynomial_features(scaled_prices)
        y = conversions
        
        n_samples, n_features = X.shape
        
        if self.weights is None or len(self.weights) != n_features:
            self.weights = np.zeros(n_features)
            self.weights[0] = 0.0
            if n_features > 1:
                self.weights[1] = -0.5

        for epoch in range(self.epochs):
            indices = np.random.permutation(n_samples)
            for idx in indices:
                x_i = X[idx]
                y_i = y[idx]
                
                z = np.dot(x_i, self.weights)
                y_pred = self._sigmoid(z)
                
                error = y_pred - y_i
                grad = error * x_i
                
                reg_grad = self.l2_reg * self.weights
                reg_grad[0] = 0.0
                
                self.weights -= self.learning_rate * (grad + reg_grad)

    def predict_probability(self, price):
        """Predict conversion probability for a given price."""
        if self.weights is None:
            return 0.5 if np.isscalar(price) else np.full_like(price, 0.5, dtype=float)

        price = np.array(price, dtype=float)
        scaled_price = self._scale_price(price)
        X = self._polynomial_features(scaled_price)
        
        z = np.dot(X, self.weights)
        return self._sigmoid(z)

    def calculate_elasticity(self, price):
        """
        Calculate analytical price elasticity of demand: epsilon = (dP/dx) * (price / P)
        """
        if self.weights is None or self.price_max == self.price_min:
            return 0.0
            
        p_val = self.predict_probability(price)
        p_val = np.clip(p_val, 1e-5, 1.0 - 1e-5)
        
        scaled_price = self._scale_price(price)
        
        dz_dxscaled = 0.0
        for k in range(1, self.degree + 1):
            dz_dxscaled += k * self.weights[k] * (scaled_price ** (k - 1))
            
        dxscaled_dx = 1.0 / (self.price_max - self.price_min)
        
        elasticity = (1.0 - p_val) * dz_dxscaled * dxscaled_dx * price
        return elasticity
