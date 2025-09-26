#!/usr/bin/env python3
"""
Focused test for the fixed video upload and connection endpoints
"""

import requests
import json
import base64

BACKEND_URL = "https://7db3be5f-d3ab-4a1f-a8b3-d65e998bdfe2.preview.emergentagent.com/api"

def create_sample_video_data():
    """Create sample base64 encoded video data"""
    sample_data = "SAMPLE_VIDEO_DATA_FOR_TESTING_PURPOSES"
    return base64.b64encode(sample_data.encode()).decode()

def test_fixed_endpoints():
    print("🧪 Testing Fixed Endpoints After Form Parameter Fix")
    print("=" * 60)
    
    # Get existing users
    response = requests.get(f"{BACKEND_URL}/users")
    if response.status_code != 200:
        print("❌ Cannot get users for testing")
        return
    
    users = response.json()
    if len(users) < 2:
        print("❌ Need at least 2 users for testing")
        return
    
    user1, user2 = users[0], users[1]
    print(f"✅ Using users: {user1['name']} and {user2['name']}")
    
    # Test 1: Video Upload with Form Data (FIXED)
    print("\n🎥 Testing Video Upload with Form Data...")
    video_form_data = {
        'user_id': user1['id'],
        'title': 'Test Dance Performance - Fixed Endpoint',
        'description': 'Testing the fixed video upload endpoint with form data',
        'category': 'solo',
        'video_data': create_sample_video_data()
    }
    
    response = requests.post(f"{BACKEND_URL}/videos", data=video_form_data)
    if response.status_code == 200:
        video = response.json()
        print(f"✅ Video Upload: SUCCESS")
        print(f"   Video ID: {video['id']}")
        print(f"   AI Tags: {video.get('ai_generated_tags', [])}")
        print(f"   Skill Rating: {video.get('ai_skill_rating', 'N/A')}")
        
        # Verify AI features are working (even if with fallback values)
        if video.get('ai_generated_tags') and video.get('ai_skill_rating'):
            print("✅ AI Analysis: Working (tags and rating generated)")
        else:
            print("⚠️ AI Analysis: Partial (using fallback values)")
    else:
        print(f"❌ Video Upload: FAILED - Status {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 2: Connection Request with Form Data (FIXED)
    print("\n🤝 Testing Connection Request with Form Data...")
    connection_form_data = {
        'from_user_id': user1['id'],
        'to_user_id': user2['id'],
        'message': 'Testing the fixed connection endpoint with form data'
    }
    
    response = requests.post(f"{BACKEND_URL}/connections", data=connection_form_data)
    if response.status_code == 200:
        connection = response.json()
        print(f"✅ Connection Request: SUCCESS")
        print(f"   Connection ID: {connection['id']}")
        print(f"   From: {user1['name']} → To: {user2['name']}")
        print(f"   Status: {connection['status']}")
        print(f"   Message: {connection.get('message', 'N/A')}")
        
        # Test connection response
        print("\n📝 Testing Connection Response...")
        response_data = {'status': 'accepted'}
        response = requests.post(f"{BACKEND_URL}/connections/{connection['id']}/respond", 
                               data=response_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Connection Response: SUCCESS - {result.get('message', '')}")
        else:
            print(f"❌ Connection Response: FAILED - Status {response.status_code}")
    else:
        print(f"❌ Connection Request: FAILED - Status {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test 3: Verify other endpoints still work
    print("\n🔍 Testing Other Core Endpoints...")
    
    # Test get videos
    response = requests.get(f"{BACKEND_URL}/videos")
    if response.status_code == 200:
        videos = response.json()
        print(f"✅ Get Videos: SUCCESS - {len(videos)} videos retrieved")
    else:
        print(f"❌ Get Videos: FAILED - Status {response.status_code}")
    
    # Test AI recommendations
    response = requests.get(f"{BACKEND_URL}/recommendations/{user1['id']}")
    if response.status_code == 200:
        recommendations = response.json()
        video_count = len(recommendations.get('recommended_videos', []))
        print(f"✅ AI Recommendations: SUCCESS - {video_count} recommendations")
    else:
        print(f"❌ AI Recommendations: FAILED - Status {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🏁 Focused Test Complete")

if __name__ == "__main__":
    test_fixed_endpoints()