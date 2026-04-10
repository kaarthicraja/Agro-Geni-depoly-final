from .price_predictor import PricePredictor
from .spoilage_predictor import SpoilagePredictor

class AIService:
    def __init__(self):
        self.price_predictor = PricePredictor()
        self.spoilage_predictor = SpoilagePredictor()

    def get_price_forecast(self, historical_data):
        """
        Wrapper for price forecasting.
        """
        self.price_predictor.train(historical_data)
        return self.price_predictor.predict()

    def estimate_spoilage(self, crop_type, harvest_date, temp, humidity):
        """
        Wrapper for spoilage estimation.
        """
        return self.spoilage_predictor.predict_remaining_days(crop_type, harvest_date, temp, humidity)

# Singleton Instance
ai_service = AIService()
