from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Godown
from ..utils.response import success, error
from datetime import datetime
from ..middleware.roles import role_required
from sqlalchemy import desc, asc

godown_bp = Blueprint('godown', __name__)

@godown_bp.route('/godown', methods=['POST'])
@jwt_required()
@role_required('godown_owner')
def add_godown():
    identity = get_jwt_identity()
    data = request.json
    # Stricter validation
    required_fields = ['name', 'location', 'capacity', 'pricePerDay']
    for field in required_fields:
        if not data.get(field):
            return error(f"Missing required field: {field}")
    try:
        capacity = int(data.get('capacity'))
        price_per_day = float(data.get('pricePerDay'))
        if capacity <= 0 or price_per_day <= 0:
            return error("Capacity and pricePerDay must be positive numbers")
    except Exception:
        return error("Invalid capacity or pricePerDay format")
    
    new_godown = Godown(
        owner_id=int(identity['user_id']),
        name=data.get('name'),
        location=data.get('location'),
        capacity=capacity,
        available_space=int(data.get('availableSpace', capacity)),
        price_per_sqft=price_per_day  # schema uses price_per_sqft but route uses pricePerDay
    )
    
    try:
        db.session.add(new_godown)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"Error adding godown: {str(e)}", 500)
        
    godown_data = {
        "_id": str(new_godown.id),
        "ownerId": str(new_godown.owner_id),
        "name": new_godown.name,
        "location": new_godown.location,
        "capacity": new_godown.capacity,
        "availableSpace": new_godown.available_space,
        "pricePerDay": new_godown.price_per_sqft,
        "isAvailable": True,
        "createdAt": new_godown.created_at.isoformat() if new_godown.created_at else None
    }
    return success("Godown added", godown_data)

@godown_bp.route('/godown', methods=['GET'])
@jwt_required()
def get_godowns():
    try:
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Filtering
        query = Godown.query
        location = request.args.get('location')
        min_price = request.args.get('minPrice')
        max_price = request.args.get('maxPrice')
        is_available = request.args.get('isAvailable')
        
        if location:
            query = query.filter(Godown.location.ilike(f'%{location}%'))
        if min_price:
            query = query.filter(Godown.price_per_sqft >= float(min_price))
        if max_price:
            query = query.filter(Godown.price_per_sqft <= float(max_price))
        if is_available is not None:
            # We don't have isAvailable directly in Godown model but we can check space
            if is_available.lower() == 'true':
                query = query.filter(Godown.available_space > 0)
            else:
                query = query.filter(Godown.available_space <= 0)
                
        # Sorting
        sort_by = request.args.get('sortBy', 'created_at')
        if sort_by == 'createdAt':
            sort_by = 'created_at'
        elif sort_by == 'pricePerDay':
            sort_by = 'price_per_sqft'
            
        sort_dir = int(request.args.get('sortDir', -1))
        
        order_col = getattr(Godown, sort_by, Godown.created_at)
        if sort_dir == -1:
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))
            
        total = query.count()
        godowns = query.offset(skip).limit(limit).all()
        
        godowns_list = [{
            "_id": str(g.id),
            "ownerId": str(g.owner_id),
            "name": g.name,
            "location": g.location,
            "capacity": g.capacity,
            "availableSpace": g.available_space,
            "pricePerDay": g.price_per_sqft,
            "isAvailable": g.available_space > 0,
            "createdAt": g.created_at.isoformat() if g.created_at else None
        } for g in godowns]
        
        return success("All godowns", {"godowns": godowns_list, "total": total, "page": page, "limit": limit})
    except Exception as e:
        return error(f"Error fetching godowns: {str(e)}", 500)

@godown_bp.route('/godown/owner', methods=['GET'])
@jwt_required()
def get_owner_godowns():
    identity = get_jwt_identity()
    godowns = Godown.query.filter_by(owner_id=int(identity['user_id'])).all()
    godowns_list = [{
        "_id": str(g.id),
        "ownerId": str(g.owner_id),
        "name": g.name,
        "location": g.location,
        "capacity": g.capacity,
        "availableSpace": g.available_space,
        "pricePerDay": g.price_per_sqft,
        "isAvailable": g.available_space > 0,
        "createdAt": g.created_at.isoformat() if g.created_at else None
    } for g in godowns]
    return success("Owner godowns", godowns_list)

@godown_bp.route('/godown/<godown_id>', methods=['PUT'])
@jwt_required()
def update_godown(godown_id):
    identity = get_jwt_identity()
    data = request.json
    try:
        godown = Godown.query.filter_by(id=int(godown_id), owner_id=int(identity['user_id'])).first()
        if not godown:
            return error("Godown not found or unauthorized", 404)
        
        if 'name' in data: godown.name = data['name']
        if 'location' in data: godown.location = data['location']
        if 'capacity' in data: godown.capacity = int(data['capacity'])
        if 'availableSpace' in data: godown.available_space = int(data['availableSpace'])
        if 'pricePerDay' in data: godown.price_per_sqft = float(data['pricePerDay'])
        
        db.session.commit()
        return success("Godown updated")
    except Exception as e:
        db.session.rollback()
        return error(f"Error updating godown: {str(e)}", 500)

@godown_bp.route('/godown/<godown_id>', methods=['DELETE'])
@jwt_required()
def delete_godown(godown_id):
    identity = get_jwt_identity()
    try:
        godown = Godown.query.filter_by(id=int(godown_id), owner_id=int(identity['user_id'])).first()
        if not godown:
            return error("Godown not found or unauthorized", 404)
        db.session.delete(godown)
        db.session.commit()
        return success("Godown deleted")
    except Exception as e:
        db.session.rollback()
        return error(f"Error deleting godown: {str(e)}", 500)
