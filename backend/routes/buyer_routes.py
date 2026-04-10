from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from ..extensions import db
from ..models import Order, Crop
from ..utils.response import success, error
from sqlalchemy import desc, asc

buyer_bp = Blueprint('buyer', __name__)

@buyer_bp.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    identity = get_jwt_identity()
    data = request.json
    # Stricter validation
    required_fields = ['cropId', 'quantity']
    for field in required_fields:
        if not data.get(field):
            return error(f"Missing required field: {field}")
    try:
        crop_id = int(data.get('cropId'))
        crop = Crop.query.get(crop_id)
        if not crop:
            return error("Crop not found", 404)
        quantity = int(data.get('quantity', 0))
        if quantity <= 0 or quantity > crop.quantity:
            return error("Invalid quantity")
        total_price = quantity * crop.price
    except Exception:
        return error("Invalid cropId or quantity format")
    
    new_order = Order(
        buyer_id=int(identity['user_id']),
        crop_id=crop.id,
        quantity=quantity,
        total_price=total_price,
        status="pending"
    )
    
    try:
        db.session.add(new_order)
        # Optionally update crop quantity
        crop.quantity -= quantity
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"Error creating order: {str(e)}", 500)
    
    order_data = {
        "_id": str(new_order.id),
        "buyerId": str(new_order.buyer_id),
        "cropId": str(new_order.crop_id),
        "quantity": new_order.quantity,
        "totalPrice": new_order.total_price,
        "status": new_order.status,
        "createdAt": new_order.created_at.isoformat() if new_order.created_at else None
    }
    return success("Order placed", order_data)

@buyer_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    try:
        identity = get_jwt_identity()
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Filtering
        query = Order.query.filter_by(buyer_id=int(identity['user_id']))
        status = request.args.get('status')
        min_total = request.args.get('minTotal')
        max_total = request.args.get('maxTotal')
        
        if status:
            query = query.filter_by(status=status)
        if min_total:
            query = query.filter(Order.total_price >= float(min_total))
        if max_total:
            query = query.filter(Order.total_price <= float(max_total))
            
        # Sorting
        sort_by = request.args.get('sortBy', 'created_at')
        if sort_by == 'createdAt':
            sort_by = 'created_at'
        elif sort_by == 'totalPrice':
            sort_by = 'total_price'
            
        sort_dir = int(request.args.get('sortDir', -1))
        
        order_col = getattr(Order, sort_by, Order.created_at)
        if sort_dir == -1:
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))
            
        total = query.count()
        orders = query.offset(skip).limit(limit).all()
        
        orders_list = [{
            "_id": str(o.id),
            "buyerId": str(o.buyer_id),
            "cropId": str(o.crop_id),
            "quantity": o.quantity,
            "totalPrice": o.total_price,
            "status": o.status,
            "createdAt": o.created_at.isoformat() if o.created_at else None
        } for o in orders]
        
        return success("My orders", {"orders": orders_list, "total": total, "page": page, "limit": limit})
    except Exception as e:
        return error(f"Error fetching orders: {str(e)}", 500)
