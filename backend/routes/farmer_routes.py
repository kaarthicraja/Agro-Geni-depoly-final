from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db
from ..models import Crop
from ..utils.response import success, error
from sqlalchemy import or_, and_, asc, desc

farmer_bp = Blueprint('farmer', __name__)

@farmer_bp.route('/crops', methods=['POST'])
@jwt_required()
def add_crop():
    identity = get_jwt_identity()
    data = request.json
    # Stricter validation
    required_fields = ['cropName', 'price', 'quantity', 'location']
    for field in required_fields:
        if not data.get(field):
            return error(f"Missing required field: {field}")
    try:
        price = float(data.get('price'))
        quantity = int(data.get('quantity'))
        if price <= 0 or quantity <= 0:
            return error("Price and quantity must be positive numbers")
    except Exception:
        return error("Invalid price or quantity format")
    new_crop = Crop(
        farmer_id=int(identity['user_id']),
        crop_name=data.get('cropName'),
        price=price,
        quantity=quantity,
        location=data.get('location'),
        image=data.get('image')
    )
    try:
        db.session.add(new_crop)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"Error adding crop: {str(e)}", 500)
    
    crop_data = {
        "_id": str(new_crop.id),
        "farmerId": str(new_crop.farmer_id),
        "cropName": new_crop.crop_name,
        "price": new_crop.price,
        "quantity": new_crop.quantity,
        "location": new_crop.location,
        "image": new_crop.image,
        "createdAt": new_crop.created_at.isoformat() if new_crop.created_at else None
    }
    return success("Crop added", crop_data)

@farmer_bp.route('/crops', methods=['GET'])
@jwt_required()
def get_my_crops():
    identity = get_jwt_identity()
    crops = Crop.query.filter_by(farmer_id=int(identity['user_id'])).all()
    crops_list = [{
        "_id": str(c.id),
        "farmerId": str(c.farmer_id),
        "cropName": c.crop_name,
        "price": c.price,
        "quantity": c.quantity,
        "location": c.location,
        "image": c.image,
        "createdAt": c.created_at.isoformat() if c.created_at else None
    } for c in crops]
    return success("My crops", crops_list)

@farmer_bp.route('/crops/<crop_id>', methods=['PUT'])
@jwt_required()
def update_crop(crop_id):
    identity = get_jwt_identity()
    data = request.json
    try:
        crop = Crop.query.filter_by(id=int(crop_id), farmer_id=int(identity['user_id'])).first()
        if not crop:
            return error("Crop not found or unauthorized", 404)
        
        if 'cropName' in data: crop.crop_name = data['cropName']
        if 'price' in data: crop.price = float(data['price'])
        if 'quantity' in data: crop.quantity = int(data['quantity'])
        if 'location' in data: crop.location = data['location']
        if 'image' in data: crop.image = data['image']
        
        db.session.commit()
        return success("Crop updated")
    except Exception as e:
        db.session.rollback()
        return error(f"Error updating crop: {str(e)}", 500)

@farmer_bp.route('/crops/<crop_id>', methods=['DELETE'])
@jwt_required()
def delete_crop(crop_id):
    identity = get_jwt_identity()
    try:
        crop = Crop.query.filter_by(id=int(crop_id), farmer_id=int(identity['user_id'])).first()
        if not crop:
            return error("Crop not found or unauthorized", 404)
        db.session.delete(crop)
        db.session.commit()
        return success("Crop deleted")
    except Exception as e:
        db.session.rollback()
        return error(f"Error deleting crop: {str(e)}", 500)

# Public route for buyers to get all crops with pagination, filtering, sorting
@farmer_bp.route('/crops/all', methods=['GET'])
def get_all_crops():
    try:
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Filtering
        query = Crop.query
        crop_name = request.args.get('cropName')
        location = request.args.get('location')
        min_price = request.args.get('minPrice')
        max_price = request.args.get('maxPrice')
        
        if crop_name:
            query = query.filter(Crop.crop_name.ilike(f'%{crop_name}%'))
        if location:
            query = query.filter(Crop.location.ilike(f'%{location}%'))
        if min_price:
            query = query.filter(Crop.price >= float(min_price))
        if max_price:
            query = query.filter(Crop.price <= float(max_price))
            
        # Sorting
        sort_by = request.args.get('sortBy', 'created_at')
        if sort_by == 'createdAt':
            sort_by = 'created_at'
        elif sort_by == 'cropName':
            sort_by = 'crop_name'
            
        sort_dir = int(request.args.get('sortDir', -1))  # -1: desc, 1: asc
        
        order_col = getattr(Crop, sort_by, Crop.created_at)
        if sort_dir == -1:
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))
            
        total = query.count()
        crops = query.offset(skip).limit(limit).all()
        
        crops_list = [{
            "_id": str(c.id),
            "farmerId": str(c.farmer_id),
            "cropName": c.crop_name,
            "price": c.price,
            "quantity": c.quantity,
            "location": c.location,
            "image": c.image,
            "createdAt": c.created_at.isoformat() if c.created_at else None
        } for c in crops]
        
        return success("All crops", {"crops": crops_list, "total": total, "page": page, "limit": limit})
    except Exception as e:
        return error(f"Error fetching crops: {str(e)}", 500)
