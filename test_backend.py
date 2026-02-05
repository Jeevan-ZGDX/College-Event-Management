#!/usr/bin/env python3
"""
Test script for VIT Event Management Portal Backend
"""

import requests
import json
import time

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:5000"

    print("🧪 Testing VIT Event Management Portal Backend...")
    print("=" * 50)

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)

    try:
        # Test events endpoint
        print("📋 Testing /api/events endpoint...")
        response = requests.get(f"{base_url}/api/events")
        if response.status_code == 200:
            events = response.json()
            print(f"✅ Events endpoint working! Found {len(events)} events")
            if events:
                print(f"📄 First event: {events[0]['title']}")
        else:
            print(f"❌ Events endpoint failed: {response.status_code}")

        # Test QR generation endpoint
        print("\n📱 Testing /api/generate-qr endpoint...")
        qr_data = {
            "upi_id": "test@upi",
            "payee_name": "Test User",
            "amount": 100,
            "currency": "INR",
            "transaction_note": "Test Payment"
        }
        response = requests.post(f"{base_url}/api/generate-qr", json=qr_data)
        if response.status_code == 200:
            qr_result = response.json()
            print("✅ QR generation working!")
            print(f"📊 QR code generated (length: {len(qr_result.get('qr_code', ''))})")
        else:
            print(f"❌ QR generation failed: {response.status_code} - {response.text}")

        # Test payment order creation
        print("\n💳 Testing /api/create-payment-order endpoint...")
        order_data = {
            "amount": 100,
            "event_name": "Test Event"
        }
        response = requests.post(f"{base_url}/api/create-payment-order", json=order_data)
        if response.status_code == 200:
            order_result = response.json()
            print("✅ Payment order creation working!")
            print(f"🆔 Order ID: {order_result.get('order_id', 'N/A')}")
        else:
            print(f"❌ Payment order creation failed: {response.status_code} - {response.text}")

        print("\n🎉 Backend testing completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running?")
        print("💡 Make sure to run: python run.py")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_backend()