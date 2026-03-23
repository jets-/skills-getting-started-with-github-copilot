"""Tests for the Mergington High School Activities API"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities returns a non-empty dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
    
    def test_activity_structure(self, client):
        """Test that activity objects have required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_initial_participants(self, client):
        """Test that activities contain their initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successfully signing up a new student"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup fails when activity doesn't exist"""
        response = client.post(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_registered(self, client):
        """Test signup fails when student is already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test a student can sign up for multiple activities"""
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=versatile@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming%20Class/signup?email=versatile@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "versatile@mergington.edu" in activities["Chess Club"]["participants"]
        assert "versatile@mergington.edu" in activities["Programming Class"]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_successful_removal(self, client):
        """Test successfully removing a participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_remove_activity_not_found(self, client):
        """Test removal fails when activity doesn't exist"""
        response = client.delete(
            "/activities/NonExistent%20Club/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_remove_student_not_registered(self, client):
        """Test removal fails when student is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/participants/notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_remove_student_from_multiple_activities(self, client):
        """Test removing a student from one activity doesn't affect others"""
        # Add student to two activities
        client.post("/activities/Chess%20Club/signup?email=tempuser@mergington.edu")
        client.post("/activities/Programming%20Class/signup?email=tempuser@mergington.edu")
        
        # Remove from Chess Club
        response = client.delete(
            "/activities/Chess%20Club/participants/tempuser@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify removed from Chess Club but still in Programming Class
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "tempuser@mergington.edu" not in activities["Chess Club"]["participants"]
        assert "tempuser@mergington.edu" in activities["Programming Class"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [301, 302, 303, 307, 308]
        assert "/static/index.html" in response.headers["location"]
