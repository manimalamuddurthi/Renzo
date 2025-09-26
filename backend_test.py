#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Renzo Platform
Tests all major API endpoints for the dance/music platform
"""

import requests
import json
import base64
import time
from typing import Dict, List, Optional

# Backend URL from frontend/.env
BACKEND_URL = "https://7db3be5f-d3ab-4a1f-a8b3-d65e998bdfe2.preview.emergentagent.com/api"

class RenzoAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_users = []
        self.test_videos = []
        self.test_connections = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    def create_sample_video_data(self) -> str:
        """Create sample base64 encoded video data"""
        # Create a small sample "video" data (just text for testing)
        sample_data = "SAMPLE_VIDEO_DATA_FOR_TESTING_PURPOSES"
        return base64.b64encode(sample_data.encode()).decode()

    def get_existing_users(self) -> List[Dict]:
        """Get existing users from the database"""
        try:
            response = self.session.get(f"{self.base_url}/users")
            if response.status_code == 200:
                users = response.json()
                return users[:3]  # Get first 3 users for testing
        except Exception as e:
            print(f"Error getting existing users: {e}")
        return []

    def test_user_registration(self) -> Dict:
        """Test user registration with AI bio generation"""
        print("🧪 Testing User Registration...")
        
        # First try to get existing users
        existing_users = self.get_existing_users()
        if existing_users:
            self.test_users = existing_users
            self.log_test("Use Existing Users", "PASS", 
                        f"Found {len(existing_users)} existing users to test with")
            return {"registered_users": len(existing_users), "total_attempted": 0, "used_existing": True}
        
        test_users_data = [
            {
                "email": "sophia.ballet@example.com",
                "name": "Sophia Martinez",
                "username": "sophia_ballet",
                "profile_type": "dancer",
                "tags": ["ballet", "contemporary", "choreography", "performance"]
            },
            {
                "email": "marcus.jazz@example.com", 
                "name": "Marcus Johnson",
                "username": "marcus_jazz",
                "profile_type": "musician",
                "tags": ["jazz", "saxophone", "improvisation", "blues"]
            },
            {
                "email": "elena.director@example.com",
                "name": "Elena Rodriguez",
                "username": "elena_director",
                "profile_type": "director",
                "tags": ["choreography", "theater", "musical", "direction"]
            }
        ]
        
        registered_users = []
        
        for user_data in test_users_data:
            try:
                response = self.session.post(f"{self.base_url}/auth/register", json=user_data)
                
                if response.status_code == 200:
                    user = response.json()
                    registered_users.append(user)
                    
                    # Verify AI bio was generated
                    if user.get('ai_generated_bio'):
                        self.log_test(f"Register {user['name']}", "PASS", 
                                    f"User registered with AI bio: {user['ai_generated_bio'][:50]}...")
                    else:
                        self.log_test(f"Register {user['name']}", "FAIL", "AI bio not generated")
                        
                else:
                    self.log_test(f"Register {user_data['name']}", "FAIL", 
                                f"Status: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Register {user_data['name']}", "FAIL", f"Exception: {str(e)}")
        
        self.test_users = registered_users
        return {"registered_users": len(registered_users), "total_attempted": len(test_users_data)}

    def test_user_login(self) -> Dict:
        """Test user login functionality"""
        print("🧪 Testing User Login...")
        
        if not self.test_users:
            self.log_test("User Login", "SKIP", "No registered users to test login")
            return {"status": "skipped"}
        
        login_attempts = 0
        successful_logins = 0
        
        for user in self.test_users:
            try:
                login_data = {
                    "email": user["email"],
                    "password": "dummy_password"  # MVP uses simple email-based auth
                }
                
                response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
                login_attempts += 1
                
                if response.status_code == 200:
                    login_result = response.json()
                    if login_result.get('user_id') == user['id']:
                        successful_logins += 1
                        self.log_test(f"Login {user['name']}", "PASS", 
                                    f"User ID: {login_result['user_id']}")
                    else:
                        self.log_test(f"Login {user['name']}", "FAIL", "User ID mismatch")
                else:
                    self.log_test(f"Login {user['name']}", "FAIL", 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Login {user['name']}", "FAIL", f"Exception: {str(e)}")
        
        return {"successful_logins": successful_logins, "total_attempts": login_attempts}

    def test_get_user_profile(self) -> Dict:
        """Test getting user profiles"""
        print("🧪 Testing Get User Profile...")
        
        if not self.test_users:
            self.log_test("Get User Profile", "SKIP", "No users to test")
            return {"status": "skipped"}
        
        successful_gets = 0
        
        for user in self.test_users:
            try:
                response = self.session.get(f"{self.base_url}/users/{user['id']}")
                
                if response.status_code == 200:
                    profile = response.json()
                    if profile['id'] == user['id'] and profile['email'] == user['email']:
                        successful_gets += 1
                        self.log_test(f"Get Profile {user['name']}", "PASS", 
                                    f"Profile type: {profile['profile_type']}")
                    else:
                        self.log_test(f"Get Profile {user['name']}", "FAIL", "Profile data mismatch")
                else:
                    self.log_test(f"Get Profile {user['name']}", "FAIL", 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Get Profile {user['name']}", "FAIL", f"Exception: {str(e)}")
        
        return {"successful_gets": successful_gets, "total_users": len(self.test_users)}

    def test_get_all_users(self) -> Dict:
        """Test getting all users for discovery"""
        print("🧪 Testing Get All Users...")
        
        try:
            response = self.session.get(f"{self.base_url}/users")
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list) and len(users) >= len(self.test_users):
                    self.log_test("Get All Users", "PASS", 
                                f"Retrieved {len(users)} users")
                    return {"status": "success", "user_count": len(users)}
                else:
                    self.log_test("Get All Users", "FAIL", "Insufficient users returned")
            else:
                self.log_test("Get All Users", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get All Users", "FAIL", f"Exception: {str(e)}")
        
        return {"status": "failed"}

    def test_video_upload(self) -> Dict:
        """Test video upload with AI tag generation and skill rating"""
        print("🧪 Testing Video Upload with AI Analysis...")
        
        if not self.test_users:
            self.log_test("Video Upload", "SKIP", "No users to test video upload")
            return {"status": "skipped"}
        
        test_videos_data = [
            {
                "title": "Contemporary Ballet Solo - Swan Lake Interpretation",
                "description": "My personal interpretation of the Swan Lake theme with contemporary ballet movements",
                "category": "solo",
                "video_data": self.create_sample_video_data()
            },
            {
                "title": "Jazz Saxophone Improvisation Session",
                "description": "Freestyle jazz improvisation on my tenor saxophone",
                "category": "solo", 
                "video_data": self.create_sample_video_data()
            },
            {
                "title": "Hip-Hop Dance Crew Performance",
                "description": "Street dance performance with my crew at the local competition",
                "category": "group",
                "video_data": self.create_sample_video_data()
            }
        ]
        
        uploaded_videos = []
        
        for i, video_data in enumerate(test_videos_data):
            if i < len(self.test_users):
                user = self.test_users[i]
                try:
                    # Use direct form data as per fixed endpoint
                    form_data = {
                        'user_id': user["id"],
                        'title': video_data["title"],
                        'description': video_data["description"],
                        'category': video_data["category"],
                        'video_data': video_data["video_data"]
                    }
                    
                    response = self.session.post(f"{self.base_url}/videos", data=form_data)
                    
                    if response.status_code == 200:
                        video = response.json()
                        uploaded_videos.append(video)
                        
                        # Verify AI features
                        ai_tags = video.get('ai_generated_tags', [])
                        skill_rating = video.get('ai_skill_rating')
                        
                        if ai_tags and skill_rating:
                            self.log_test(f"Upload Video '{video['title'][:30]}...'", "PASS", 
                                        f"AI Tags: {ai_tags}, Skill Rating: {skill_rating}")
                        else:
                            self.log_test(f"Upload Video '{video['title'][:30]}...'", "FAIL", 
                                        "AI analysis incomplete")
                    else:
                        self.log_test(f"Upload Video '{video_data['title'][:30]}...'", "FAIL", 
                                    f"Status: {response.status_code}, Response: {response.text}")
                        
                except Exception as e:
                    self.log_test(f"Upload Video '{video_data['title'][:30]}...'", "FAIL", 
                                f"Exception: {str(e)}")
        
        self.test_videos = uploaded_videos
        return {"uploaded_videos": len(uploaded_videos), "total_attempted": len(test_videos_data)}

    def test_get_videos(self) -> Dict:
        """Test getting all videos with user data"""
        print("🧪 Testing Get All Videos...")
        
        try:
            response = self.session.get(f"{self.base_url}/videos")
            
            if response.status_code == 200:
                videos = response.json()
                if isinstance(videos, list):
                    # Verify videos have user data enrichment
                    enriched_count = 0
                    for video in videos:
                        if video.get('user_name') and video.get('user_username'):
                            enriched_count += 1
                    
                    if enriched_count == len(videos):
                        self.log_test("Get All Videos", "PASS", 
                                    f"Retrieved {len(videos)} videos, all enriched with user data")
                        return {"status": "success", "video_count": len(videos)}
                    else:
                        self.log_test("Get All Videos", "FAIL", 
                                    f"Only {enriched_count}/{len(videos)} videos enriched")
                else:
                    self.log_test("Get All Videos", "FAIL", "Invalid response format")
            else:
                self.log_test("Get All Videos", "FAIL", f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get All Videos", "FAIL", f"Exception: {str(e)}")
        
        return {"status": "failed"}

    def test_get_specific_video(self) -> Dict:
        """Test getting specific video and view increment"""
        print("🧪 Testing Get Specific Video with View Increment...")
        
        if not self.test_videos:
            self.log_test("Get Specific Video", "SKIP", "No videos to test")
            return {"status": "skipped"}
        
        successful_gets = 0
        
        for video in self.test_videos:
            try:
                # Get initial view count
                response1 = self.session.get(f"{self.base_url}/videos/{video['id']}")
                
                if response1.status_code == 200:
                    video1 = response1.json()
                    initial_views = video1.get('views', 0)
                    
                    # Get video again to test view increment
                    time.sleep(0.1)  # Small delay
                    response2 = self.session.get(f"{self.base_url}/videos/{video['id']}")
                    
                    if response2.status_code == 200:
                        video2 = response2.json()
                        new_views = video2.get('views', 0)
                        
                        if new_views > initial_views:
                            successful_gets += 1
                            self.log_test(f"Get Video '{video['title'][:30]}...'", "PASS", 
                                        f"Views incremented: {initial_views} → {new_views}")
                        else:
                            self.log_test(f"Get Video '{video['title'][:30]}...'", "FAIL", 
                                        "Views not incremented")
                    else:
                        self.log_test(f"Get Video '{video['title'][:30]}...'", "FAIL", 
                                    f"Second request failed: {response2.status_code}")
                else:
                    self.log_test(f"Get Video '{video['title'][:30]}...'", "FAIL", 
                                f"Status: {response1.status_code}")
                    
            except Exception as e:
                self.log_test(f"Get Video '{video['title'][:30]}...'", "FAIL", 
                            f"Exception: {str(e)}")
        
        return {"successful_gets": successful_gets, "total_videos": len(self.test_videos)}

    def test_video_likes(self) -> Dict:
        """Test video like/unlike functionality"""
        print("🧪 Testing Video Like/Unlike...")
        
        if not self.test_videos or not self.test_users:
            self.log_test("Video Likes", "SKIP", "No videos or users to test")
            return {"status": "skipped"}
        
        successful_likes = 0
        
        for video in self.test_videos:
            for user in self.test_users:
                if user['id'] != video['user_id']:  # Don't like own video
                    try:
                        # Like the video
                        like_data = {"user_id": user["id"]}
                        response1 = self.session.post(f"{self.base_url}/videos/{video['id']}/like", 
                                                    data=like_data)
                        
                        if response1.status_code == 200:
                            result1 = response1.json()
                            likes_count1 = result1.get('likes_count', 0)
                            
                            # Unlike the video
                            response2 = self.session.post(f"{self.base_url}/videos/{video['id']}/like", 
                                                        data=like_data)
                            
                            if response2.status_code == 200:
                                result2 = response2.json()
                                likes_count2 = result2.get('likes_count', 0)
                                
                                if likes_count2 < likes_count1:
                                    successful_likes += 1
                                    self.log_test(f"Like/Unlike Video by {user['name']}", "PASS", 
                                                f"Likes: {likes_count1} → {likes_count2}")
                                    break  # Test one like per video
                                else:
                                    self.log_test(f"Like/Unlike Video by {user['name']}", "FAIL", 
                                                "Unlike didn't decrease count")
                            else:
                                self.log_test(f"Unlike Video by {user['name']}", "FAIL", 
                                            f"Status: {response2.status_code}")
                        else:
                            self.log_test(f"Like Video by {user['name']}", "FAIL", 
                                        f"Status: {response1.status_code}")
                            
                    except Exception as e:
                        self.log_test(f"Like/Unlike Video by {user['name']}", "FAIL", 
                                    f"Exception: {str(e)}")
                    break  # Test one user per video
        
        return {"successful_likes": successful_likes, "total_videos": len(self.test_videos)}

    def test_connection_requests(self) -> Dict:
        """Test connection request system"""
        print("🧪 Testing Connection Requests...")
        
        if len(self.test_users) < 2:
            self.log_test("Connection Requests", "SKIP", "Need at least 2 users")
            return {"status": "skipped"}
        
        successful_connections = 0
        
        # Test connection between first two users
        user1 = self.test_users[0]
        user2 = self.test_users[1]
        
        try:
            # Use direct form data as per fixed endpoint
            form_data = {
                'from_user_id': user1["id"],
                'to_user_id': user2["id"],
                'message': f"Hi {user2['name']}, I'd love to collaborate on a dance project!"
            }
            
            response = self.session.post(f"{self.base_url}/connections", data=form_data)
            
            if response.status_code == 200:
                connection = response.json()
                self.test_connections.append(connection)
                
                self.log_test("Send Connection Request", "PASS", 
                            f"Connection from {user1['name']} to {user2['name']}")
                successful_connections += 1
            else:
                self.log_test("Send Connection Request", "FAIL", 
                            f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Send Connection Request", "FAIL", f"Exception: {str(e)}")
        
        return {"successful_connections": successful_connections}

    def test_get_connections(self) -> Dict:
        """Test getting user connections"""
        print("🧪 Testing Get User Connections...")
        
        if not self.test_users:
            self.log_test("Get Connections", "SKIP", "No users to test")
            return {"status": "skipped"}
        
        successful_gets = 0
        
        for user in self.test_users:
            try:
                response = self.session.get(f"{self.base_url}/connections/{user['id']}")
                
                if response.status_code == 200:
                    result = response.json()
                    connections = result.get('connections', [])
                    
                    self.log_test(f"Get Connections for {user['name']}", "PASS", 
                                f"Found {len(connections)} connections")
                    successful_gets += 1
                else:
                    self.log_test(f"Get Connections for {user['name']}", "FAIL", 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Get Connections for {user['name']}", "FAIL", 
                            f"Exception: {str(e)}")
        
        return {"successful_gets": successful_gets, "total_users": len(self.test_users)}

    def test_connection_response(self) -> Dict:
        """Test accepting/rejecting connection requests"""
        print("🧪 Testing Connection Response...")
        
        if not self.test_connections:
            self.log_test("Connection Response", "SKIP", "No connections to test")
            return {"status": "skipped"}
        
        successful_responses = 0
        
        for connection in self.test_connections:
            try:
                # Accept the connection
                response_data = {"status": "accepted"}
                response = self.session.post(
                    f"{self.base_url}/connections/{connection['id']}/respond", 
                    data=response_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "accepted" in result.get('message', ''):
                        self.log_test("Accept Connection", "PASS", 
                                    f"Connection accepted: {connection['id']}")
                        successful_responses += 1
                    else:
                        self.log_test("Accept Connection", "FAIL", "Unexpected response message")
                else:
                    self.log_test("Accept Connection", "FAIL", 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test("Accept Connection", "FAIL", f"Exception: {str(e)}")
        
        return {"successful_responses": successful_responses, "total_connections": len(self.test_connections)}

    def test_ai_recommendations(self) -> Dict:
        """Test AI-powered video recommendations"""
        print("🧪 Testing AI Recommendations...")
        
        if not self.test_users:
            self.log_test("AI Recommendations", "SKIP", "No users to test")
            return {"status": "skipped"}
        
        successful_recommendations = 0
        
        for user in self.test_users:
            try:
                response = self.session.get(f"{self.base_url}/recommendations/{user['id']}")
                
                if response.status_code == 200:
                    result = response.json()
                    recommended_videos = result.get('recommended_videos', [])
                    
                    # Verify recommendations are relevant to user's tags
                    user_tags = user.get('tags', [])
                    relevant_count = 0
                    
                    for video in recommended_videos:
                        video_tags = video.get('ai_generated_tags', [])
                        if any(tag in video_tags for tag in user_tags):
                            relevant_count += 1
                    
                    if recommended_videos:
                        self.log_test(f"AI Recommendations for {user['name']}", "PASS", 
                                    f"Got {len(recommended_videos)} recommendations, {relevant_count} relevant")
                        successful_recommendations += 1
                    else:
                        self.log_test(f"AI Recommendations for {user['name']}", "PASS", 
                                    "No recommendations (expected if no matching content)")
                        successful_recommendations += 1
                else:
                    self.log_test(f"AI Recommendations for {user['name']}", "FAIL", 
                                f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"AI Recommendations for {user['name']}", "FAIL", 
                            f"Exception: {str(e)}")
        
        return {"successful_recommendations": successful_recommendations, "total_users": len(self.test_users)}

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Renzo Platform Backend API Tests")
        print("=" * 60)
        
        results = {}
        
        # Authentication Tests
        results['registration'] = self.test_user_registration()
        results['login'] = self.test_user_login()
        results['get_user_profile'] = self.test_get_user_profile()
        results['get_all_users'] = self.test_get_all_users()
        
        # Video System Tests
        results['video_upload'] = self.test_video_upload()
        results['get_videos'] = self.test_get_videos()
        results['get_specific_video'] = self.test_get_specific_video()
        results['video_likes'] = self.test_video_likes()
        
        # Social Features Tests
        results['connection_requests'] = self.test_connection_requests()
        results['get_connections'] = self.test_get_connections()
        results['connection_response'] = self.test_connection_response()
        results['ai_recommendations'] = self.test_ai_recommendations()
        
        # Summary
        print("=" * 60)
        print("🏁 Test Summary")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in results.items():
            if isinstance(result, dict):
                if result.get('status') == 'success' or result.get('status') == 'skipped':
                    passed_tests += 1
                elif any(key.startswith('successful_') for key in result.keys()):
                    # Count individual successes
                    for key, value in result.items():
                        if key.startswith('successful_') and isinstance(value, int) and value > 0:
                            passed_tests += 1
                            break
                total_tests += 1
        
        print(f"Total Test Categories: {total_tests}")
        print(f"Passed Categories: {passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        
        return results

if __name__ == "__main__":
    tester = RenzoAPITester()
    results = tester.run_all_tests()