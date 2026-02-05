from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import razorpay
import qrcode
import json
import os
from datetime import datetime
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import uuid

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Razorpay configuration
RAZORPAY_KEY_ID = "rzp_test_your_key_here"  # Replace with your actual Razorpay key
RAZORPAY_KEY_SECRET = "your_secret_here"  # Replace with your actual Razorpay secret

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# In-memory storage for demo (replace with database in production)
events_db = {}
registrations_db = {}
payments_db = {}

# Default events data
default_events = [
    {
        "id": 1,
        "title": "5 Days Online FDP on Agentic AI",
        "type": "Non-VITian",
        "subType": "(Research Scholar-External)",
        "date": "2026-01-27",
        "mode": "Online",
        "price": 199,
        "downloads": 1,
        "category": "fdp",
        "description": "This 5-day Faculty Development Program on Agentic AI covers advanced topics in artificial intelligence, including autonomous agents, machine learning algorithms, and practical applications. Designed for research scholars, this program includes interactive sessions, case studies, and hands-on projects to enhance your understanding of AI technologies."
    },
    {
        "id": 2,
        "title": "5 Days Online FDP on Agentic AI",
        "type": "Non-VITian",
        "subType": "(Faculty-External)",
        "date": "2026-01-27",
        "mode": "Online",
        "price": 299,
        "downloads": 1,
        "category": "fdp",
        "description": "This 5-day Faculty Development Program on Agentic AI covers advanced topics in artificial intelligence, including autonomous agents, machine learning algorithms, and practical applications. Designed for faculty members, this program includes interactive sessions, case studies, and hands-on projects to enhance your understanding of AI technologies."
    },
    {
        "id": 3,
        "title": "5 Days Online FDP on Agentic AI",
        "type": "Non-VITian",
        "subType": "(UG Student-External)",
        "date": "2026-01-27",
        "mode": "Online",
        "price": 199,
        "downloads": 1,
        "category": "fdp",
        "description": "This 5-day Faculty Development Program on Agentic AI covers advanced topics in artificial intelligence, including autonomous agents, machine learning algorithms, and practical applications. Designed for undergraduate students, this program includes interactive sessions, case studies, and hands-on projects to enhance your understanding of AI technologies."
    },
    {
        "id": 4,
        "title": "5 Days Online FDP on Agentic AI",
        "type": "Non-VITian",
        "subType": "(PG Student-External)",
        "date": "2026-01-27",
        "mode": "Online",
        "price": 199,
        "downloads": 1,
        "category": "fdp",
        "description": "This 5-day Faculty Development Program on Agentic AI covers advanced topics in artificial intelligence, including autonomous agents, machine learning algorithms, and practical applications. Designed for postgraduate students, this program includes interactive sessions, case studies, and hands-on projects to enhance your understanding of AI technologies."
    },
    {
        "id": 5,
        "title": "5 Days Online FDP on Agentic AI",
        "type": "VITian",
        "subType": "(Faculty-Internal)",
        "date": "2026-01-27",
        "mode": "Online",
        "price": 0,
        "downloads": 1,
        "category": "fdp",
        "description": "This 5-day Faculty Development Program on Agentic AI covers advanced topics in artificial intelligence, including autonomous agents, machine learning algorithms, and practical applications. Designed for internal faculty members, this program includes interactive sessions, case studies, and hands-on projects to enhance your understanding of AI technologies."
    },
    {
        "id": 6,
        "title": "5G Hackathon",
        "type": "VITian",
        "subType": "(Student-Internal)",
        "date": "2026-02-10",
        "mode": "Offline",
        "price": 0,
        "downloads": 2,
        "category": "hackathon",
        "description": "Join our exciting 5G Hackathon where students can showcase their innovation in 5G technology. Teams will work on real-world problems, develop prototypes, and compete for prizes. This offline event includes mentorship, workshops, and networking opportunities with industry experts."
    }
]

# Initialize events
for event in default_events:
    events_db[str(event['id'])] = event

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    return jsonify(list(events_db.values()))

@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get specific event"""
    event = events_db.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(event)

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create new event (admin only)"""
    data = request.get_json()

    # Generate new event ID
    event_id = str(max([int(k) for k in events_db.keys()]) + 1)

    event = {
        'id': int(event_id),
        'title': data['title'],
        'type': data['type'],
        'subType': data['subType'],
        'date': data['date'],
        'mode': data['mode'],
        'price': data['price'],
        'downloads': data.get('downloads', 1),
        'category': data['category'],
        'description': data['description']
    }

    events_db[event_id] = event
    return jsonify(event), 201

@app.route('/api/events/<event_id>', methods=['PUT'])
def update_event(event_id):
    """Update event (admin only)"""
    if event_id not in events_db:
        return jsonify({'error': 'Event not found'}), 404

    data = request.get_json()
    events_db[event_id].update(data)
    return jsonify(events_db[event_id])

@app.route('/api/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete event (admin only)"""
    if event_id not in events_db:
        return jsonify({'error': 'Event not found'}), 404

    deleted_event = events_db.pop(event_id)
    return jsonify(deleted_event)

@app.route('/api/payment/create-order', methods=['POST'])
def create_payment_order():
    """Create Razorpay payment order"""
    try:
        data = request.get_json()
        amount = data['amount']  # Amount in paisa (multiply by 100 for rupees)
        currency = data.get('currency', 'INR')
        event_id = data.get('event_id')
        user_details = data.get('user_details', {})

        # Create Razorpay order
        order_data = {
            'amount': amount * 100,  # Convert to paisa
            'currency': currency,
            'payment_capture': 1  # Auto capture
        }

        order = razorpay_client.order.create(order_data)

        # Store order details
        order_id = order['id']
        payments_db[order_id] = {
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'event_id': event_id,
            'user_details': user_details,
            'status': 'created',
            'created_at': datetime.now().isoformat()
        }

        return jsonify({
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'key': RAZORPAY_KEY_ID
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment"""
    try:
        data = request.get_json()
        razorpay_order_id = data['razorpay_order_id']
        razorpay_payment_id = data['razorpay_payment_id']
        razorpay_signature = data['razorpay_signature']

        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update payment status
            if razorpay_order_id in payments_db:
                payments_db[razorpay_order_id]['status'] = 'paid'
                payments_db[razorpay_order_id]['payment_id'] = razorpay_payment_id
                payments_db[razorpay_order_id]['paid_at'] = datetime.now().isoformat()

            return jsonify({'status': 'success', 'message': 'Payment verified successfully'})

        except razorpay.errors.SignatureVerificationError:
            return jsonify({'status': 'failed', 'message': 'Payment verification failed'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/qr/generate', methods=['POST'])
def generate_qr():
    """Generate QR code for payment"""
    try:
        data = request.get_json()
        amount = data['amount']
        event_id = data.get('event_id')
        event_title = data.get('event_title', 'VIT Event')
        upi_id = data.get('upi_id', 'events@vit.edu')

        # Create UPI payment string
        upi_string = f"upi://pay?pa={upi_id}&pn=VIT%20Events&am={amount}&cu=INR&tn={event_title}"

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_string)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 for response
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            'qr_code': f'data:image/png;base64,{img_base64}',
            'upi_string': upi_string,
            'amount': amount,
            'event_title': event_title
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/qr/generate-custom', methods=['POST'])
def generate_custom_qr():
    """Generate custom QR code with branding"""
    try:
        data = request.get_json()
        text = data['text']
        size = data.get('size', 300)
        logo_url = data.get('logo_url')

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)

        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Resize QR code
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Add logo if provided (simplified version)
        if logo_url:
            try:
                # In a real implementation, you'd download and add the logo
                # For now, we'll just return the QR code
                pass
            except:
                pass

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        return jsonify({
            'qr_code': f'data:image/png;base64,{img_base64}',
            'text': text
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registration', methods=['POST'])
def create_registration():
    """Create event registration"""
    try:
        data = request.get_json()

        registration_id = str(uuid.uuid4())
        registration = {
            'id': registration_id,
            'event_id': data['event_id'],
            'user_details': data['user_details'],
            'participants': data['participants'],
            'payment_status': data.get('payment_status', 'pending'),
            'registration_date': datetime.now().isoformat(),
            'status': 'confirmed'
        }

        registrations_db[registration_id] = registration

        return jsonify({
            'registration_id': registration_id,
            'status': 'success',
            'message': 'Registration created successfully'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/registrations/<event_id>', methods=['GET'])
def get_event_registrations(event_id):
    """Get registrations for an event (admin only)"""
    event_registrations = [
        reg for reg in registrations_db.values()
        if str(reg['event_id']) == event_id
    ]
    return jsonify(event_registrations)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting VIT Event Management Backend Server...")
    print("📍 Server will run on http://localhost:5000")
    print("🔧 API Endpoints:")
    print("   GET  /api/events - Get all events")
    print("   POST /api/events - Create event")
    print("   POST /api/payment/create-order - Create payment order")
    print("   POST /api/payment/verify - Verify payment")
    print("   POST /api/qr/generate - Generate QR code")
    print("   POST /api/registration - Create registration")
    app.run(debug=True, host='0.0.0.0', port=5000)