from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Booking, Godown
from ..utils.response import success, error
from datetime import datetime
from sqlalchemy import desc, asc
from dateutil.parser import parse as parse_date

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/bookings', methods=['POST'])
@jwt_required()
def book_godown():
    identity = get_jwt_identity()
    data = request.json
    # Stricter validation
    required_fields = ['godownId', 'startDate', 'endDate']
    for field in required_fields:
        if not data.get(field):
            return error(f"Missing required field: {field}")
    try:
        godown_id = int(data.get('godownId'))
        godown = Godown.query.get(godown_id)
        if not godown:
            return error("Godown not found", 404)
    except Exception:
        return error("Invalid godownId format")
        
    try:
        start_date = parse_date(data.get('startDate'))
        end_date = parse_date(data.get('endDate'))
    except Exception:
        return error("Invalid date format")
        
    space_booked = int(data.get('space_booked', 100)) # Default or from payload
        
    new_booking = Booking(
        farmer_id=int(identity['user_id']),
        godown_id=godown_id,
        start_date=start_date,
        end_date=end_date,
        space_booked=space_booked,
        status="pending"
    )
    
    try:
        db.session.add(new_booking)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return error(f"Error creating booking: {str(e)}", 500)
        
    booking_data = {
        "_id": str(new_booking.id),
        "farmerId": str(new_booking.farmer_id),
        "godownId": str(new_booking.godown_id),
        "startDate": new_booking.start_date.isoformat(),
        "endDate": new_booking.end_date.isoformat(),
        "status": new_booking.status,
        "createdAt": new_booking.created_at.isoformat() if new_booking.created_at else None
    }
    return success("Booking created", booking_data)

@booking_bp.route('/bookings/farmer', methods=['GET'])
@jwt_required()
def get_farmer_bookings():
    try:
        identity = get_jwt_identity()
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Filtering
        query = Booking.query.filter_by(farmer_id=int(identity['user_id']))
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
            
        # Sorting
        sort_by = request.args.get('sortBy', 'created_at')
        if sort_by == 'createdAt':
            sort_by = 'created_at'
            
        sort_dir = int(request.args.get('sortDir', -1))
        
        order_col = getattr(Booking, sort_by, Booking.created_at)
        if sort_dir == -1:
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))
            
        total = query.count()
        bookings = query.offset(skip).limit(limit).all()
        
        bookings_list = [{
            "_id": str(b.id),
            "farmerId": str(b.farmer_id),
            "godownId": str(b.godown_id),
            "startDate": b.start_date.isoformat(),
            "endDate": b.end_date.isoformat(),
            "status": b.status,
            "createdAt": b.created_at.isoformat() if b.created_at else None
        } for b in bookings]
        
        return success("Farmer bookings", {"bookings": bookings_list, "total": total, "page": page, "limit": limit})
    except Exception as e:
        return error(f"Error fetching bookings: {str(e)}", 500)

@booking_bp.route('/bookings/owner', methods=['GET'])
@jwt_required()
def get_owner_bookings():
    try:
        identity = get_jwt_identity()
        # Find godowns owned by this owner
        godowns = Godown.query.filter_by(owner_id=int(identity['user_id'])).all()
        godown_ids = [g.id for g in godowns]
        
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit
        
        # Filtering
        query = Booking.query.filter(Booking.godown_id.in_(godown_ids))
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
            
        # Sorting
        sort_by = request.args.get('sortBy', 'created_at')
        if sort_by == 'createdAt':
            sort_by = 'created_at'
            
        sort_dir = int(request.args.get('sortDir', -1))
        
        order_col = getattr(Booking, sort_by, Booking.created_at)
        if sort_dir == -1:
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))
            
        total = query.count()
        bookings = query.offset(skip).limit(limit).all()
        
        bookings_list = [{
            "_id": str(b.id),
            "farmerId": str(b.farmer_id),
            "godownId": str(b.godown_id),
            "startDate": b.start_date.isoformat(),
            "endDate": b.end_date.isoformat(),
            "status": b.status,
            "createdAt": b.created_at.isoformat() if b.created_at else None
        } for b in bookings]
        
        return success("Owner bookings", {"bookings": bookings_list, "total": total, "page": page, "limit": limit})
    except Exception as e:
        return error(f"Error fetching bookings: {str(e)}", 500)

@booking_bp.route('/bookings/<booking_id>', methods=['PUT'])
@jwt_required()
def update_booking(booking_id):
    identity = get_jwt_identity()
    data = request.json
    try:
        # Only owner of godown can approve/reject
        booking = Booking.query.get(int(booking_id))
        if not booking:
            return error("Booking not found", 404)
            
        godown = Godown.query.get(booking.godown_id)
        if not godown or godown.owner_id != int(identity['user_id']):
            return error("Unauthorized", 403)
            
        if 'status' in data: booking.status = data['status']
        if 'startDate' in data: booking.start_date = parse_date(data['startDate'])
        if 'endDate' in data: booking.end_date = parse_date(data['endDate'])
        
        db.session.commit()
        return success("Booking updated")
    except Exception as e:
        db.session.rollback()
        return error(f"Error updating booking: {str(e)}", 500)
