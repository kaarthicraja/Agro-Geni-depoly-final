from flask import Blueprint, request, jsonify
from ..ai.ai_service import ai_service
import pandas as pd

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/predict-spoilage', methods=['POST'])
def predict_spoilage():
    """
    Endpoint for farmers to call when booking a slot.
    Input: { "crop_type": "Tomato", "harvest_date": "2026-03-20", "temp": 28, "humidity": 70 }
    """
    data = request.json
    crop_type = data.get('crop_type')
    harvest_date = data.get('harvest_date')
    temp = data.get('temp', 25)
    humidity = data.get('humidity', 60)

    if not crop_type or not harvest_date:
        return jsonify({"error": "crop_type and harvest_date are required"}), 400

    result = ai_service.estimate_spoilage(crop_type, harvest_date, temp, humidity)
    return jsonify(result), 200

@ai_bp.route('/price-forecast', methods=['GET'])
def price_forecast():
    """
    Endpoint to get future price trends.
    For Phase 1, we demonstrate using a static or randomly generated historical set.
    """
    import random
    crop = request.args.get('crop', 'wheat').lower()
    
    # In practice, you'd fetch this from your 'prices' collection in MongoDB.
    # We generate varying dummy data based on the crop to show a dynamic chart
    base_price = 10
    volatility = 0.1
    
    if crop == 'rice':
        base_price = 40
        volatility = 0.2
    elif crop == 'tomato':
        base_price = 25
        volatility = 1.5
    elif crop == 'corn':
        base_price = 15
        volatility = 0.3
    elif crop == 'cotton':
        base_price = 60
        volatility = 0.5
    elif crop == 'sugarcane':
        base_price = 5
        volatility = 0.05
    elif crop == 'vegetables':
        base_price = 30
        volatility = 1.0

    random.seed(len(crop) + ord(crop[0])) # consistent random seed per crop
    
    dummy_data = {
        "ds": pd.date_range(start="2026-01-01", periods=100, freq='D'),
        "y": [base_price + i * volatility + random.uniform(-volatility*5, volatility*5) for i in range(100)]
    }
    df = pd.DataFrame(dummy_data)
    
    forecast = ai_service.get_price_forecast(df)
    return jsonify(forecast.to_dict(orient='records')), 200
