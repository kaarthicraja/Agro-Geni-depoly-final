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
    """
    crop = request.args.get('crop', 'wheat').lower()
    
    # Mock forecast response
    return jsonify({
        "crop": crop,
        "forecast": [
            {"date": "2026-04-12", "price": 25.5},
            {"date": "2026-04-13", "price": 26.1},
            {"date": "2026-04-14", "price": 25.8},
            {"date": "2026-04-15", "price": 27.2}
        ],
        "trend": "stable"
    }), 200
