#!/usr/bin/env python3
"""
VIT Event Management Portal - Backend Server Runner
Run this script to start the Flask backend server for the VIT Event Management Portal.
"""

import os
import sys
from backend import app

if __name__ == '__main__':
    print("🚀 Starting VIT Event Management Portal Backend Server...")
    print("📍 Server will be available at: http://localhost:5000")
    print("🔧 API endpoints:")
    print("   - GET  /api/events - Get all events")
    print("   - POST /api/create-payment-order - Create Razorpay payment order")
    print("   - POST /api/generate-qr - Generate UPI QR code")
    print("   - POST /api/verify-payment - Verify payment status")
    print("   - GET  /api/users - Get all users")
    print("   - POST /api/login - User login")
    print("   - POST /api/register - User registration")
    print("")

    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )