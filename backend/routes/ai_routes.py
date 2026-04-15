from flask import Blueprint, request, jsonify

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

    if not crop_type or not harvest_date:
        return jsonify({"error": "crop_type and harvest_date are required"}), 400

    # Mock AI response (AI service requires pandas which is not installed in production)
    return jsonify({
        "crop_type": crop_type,
        "spoilage_risk": 0.35,
        "recommendation": "Store in cool, dry place"
    }), 200

@ai_bp.route('/price-forecast', methods=['GET'])
def price_forecast():
    """
    Endpoint to get future price trends.
    Returns data in the format expected by frontend: array of {ds, yhat, yhat_lower, yhat_upper}
    """
    crop = request.args.get('crop', 'wheat').lower()
    
    # Mock forecast response in Prophet format
    return jsonify([
        {"ds": "2026-04-12", "yhat": 2550, "yhat_lower": 2400, "yhat_upper": 2700},
        {"ds": "2026-04-13", "yhat": 2610, "yhat_lower": 2460, "yhat_upper": 2760},
        {"ds": "2026-04-14", "yhat": 2580, "yhat_lower": 2430, "yhat_upper": 2730},
        {"ds": "2026-04-15", "yhat": 2720, "yhat_lower": 2570, "yhat_upper": 2870},
        {"ds": "2026-04-16", "yhat": 2750, "yhat_lower": 2600, "yhat_upper": 2900},
        {"ds": "2026-04-17", "yhat": 2810, "yhat_lower": 2660, "yhat_upper": 2960},
        {"ds": "2026-04-18", "yhat": 2890, "yhat_lower": 2740, "yhat_upper": 3040},
        {"ds": "2026-04-19", "yhat": 2920, "yhat_lower": 2770, "yhat_upper": 3070},
        {"ds": "2026-04-20", "yhat": 2850, "yhat_lower": 2700, "yhat_upper": 3000}
    ]), 200
