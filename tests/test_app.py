"""
Unit and Integration Tests for TravelGenius AI
"""
import unittest
import json
import os
import tempfile
from datetime import datetime, timedelta

# Set testing environment before importing app
os.environ["FLASK_ENV"] = "testing"
from app import app
from database import init_db, get_db_connection
from config import Config


class TravelGeniusTestCase(unittest.TestCase):
    def setUp(self):
        # Configure app for testing
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        
        # Use a temporary SQLite database for test isolation
        self.db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.db_fd)
        Config.DATABASE_PATH = self.temp_db_path
        init_db()

        self.client = app.test_client()

    def tearDown(self):
        import gc
        gc.collect()
        try:
            if os.path.exists(self.temp_db_path):
                os.unlink(self.temp_db_path)
        except OSError:
            pass

    def test_health_check(self):
        """Test health check endpoint."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "TravelGenius AI")

    def test_home_page(self):
        """Test homepage rendering."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("TravelGenius AI", html)
        self.assertIn("Your Dream Trip", html)
        self.assertIn("Popular Destinations", html)
        self.assertIn("How TravelGenius AI Works", html)

    def test_plan_page(self):
        """Test trip planner page rendering."""
        res = self.client.get("/plan")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Smart AI Trip Planner", html)
        self.assertIn("Starting City", html)
        self.assertIn("Destination City", html)

    def test_plan_page_with_prefill(self):
        """Test trip planner prefill parameters."""
        res = self.client.get("/plan?destination=Goa&starting_city=Mumbai")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn('value="Goa"', html)
        self.assertIn('value="Mumbai"', html)

    def test_explore_page(self):
        """Test destination explorer page with all 10 destinations."""
        res = self.client.get("/explore")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Explore Curated Destinations", html)
        for dest in ["Goa", "Manali", "Jaipur", "Kerala", "Kashmir", "Bali", "Dubai", "Paris", "Tokyo", "Switzerland"]:
            self.assertIn(dest, html)

    def test_my_trips_page_empty(self):
        """Test my trips page renders empty state."""
        res = self.client.get("/my-trips")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("My Saved Trips", html)
        self.assertIn("No Saved Trips Yet", html)

    def test_about_page(self):
        """Test about page renders."""
        res = self.client.get("/about")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("About TravelGenius AI", html)
        self.assertIn("Technology Stack", html)

    def test_destinations_api_and_filters(self):
        """Test /api/destinations endpoint with filters."""
        # All destinations
        res = self.client.get("/api/destinations")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["count"], 10)

        # Filter domestic
        res_dom = self.client.get("/api/destinations?region=Domestic")
        data_dom = res_dom.get_json()
        self.assertEqual(data_dom["count"], 5)  # Goa, Manali, Jaipur, Kerala, Kashmir

        # Filter international
        res_intl = self.client.get("/api/destinations?region=International")
        data_intl = res_intl.get_json()
        self.assertEqual(data_intl["count"], 5)  # Bali, Dubai, Paris, Tokyo, Switzerland

        # Single destination lookup
        res_single = self.client.get("/api/destinations/goa")
        self.assertEqual(res_single.status_code, 200)
        self.assertEqual(res_single.get_json()["destination"]["name"], "Goa")

    def test_api_generate_itinerary_validation_errors(self):
        """Test validation rules in /api/generate-itinerary."""
        # Missing destination
        res = self.client.post("/api/generate-itinerary", json={
            "starting_city": "Mumbai",
            "departure_date": "2026-05-01",
            "return_date": "2026-05-05"
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Destination city or country is required", res.get_json()["error"])

        # Return date earlier than departure date
        res = self.client.post("/api/generate-itinerary", json={
            "destination": "Goa",
            "starting_city": "Mumbai",
            "departure_date": "2026-05-10",
            "return_date": "2026-05-05",
            "budget_inr": 30000
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Return date cannot be earlier", res.get_json()["error"])

        # Invalid budget
        res = self.client.post("/api/generate-itinerary", json={
            "destination": "Goa",
            "starting_city": "Mumbai",
            "departure_date": "2026-05-01",
            "return_date": "2026-05-05",
            "budget_inr": 200
        })
        self.assertEqual(res.status_code, 400)
        self.assertIn("Budget must be at least ₹1,000", res.get_json()["error"])

    def test_api_generate_itinerary_sample_mode(self):
        """Test itinerary generation in sample mode (without API key)."""
        dep_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        ret_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        payload = {
            "destination": "Goa",
            "starting_city": "Mumbai",
            "departure_date": dep_date,
            "return_date": ret_date,
            "adults": 2,
            "children": 0,
            "budget_inr": 45000,
            "travel_style": "Beaches",
            "interests": ["Beaches", "Food", "Nightlife"],
            "accommodation_pref": "3-Star Hotel",
            "transport_pref": "Flight / Local Cabs",
            "dietary_pref": "Non-Vegetarian",
            "additional_notes": "First time visiting"
        }

        res = self.client.post("/api/generate-itinerary", json=payload)
        self.assertEqual(res.status_code, 200)
        res_data = res.get_json()
        self.assertTrue(res_data["success"])
        self.assertTrue(res_data["is_sample"])

        data = res_data["data"]
        self.assertIn("title", data)
        self.assertIn("overview", data)
        self.assertIn("destination_intro", data)
        self.assertIn("days", data)
        self.assertEqual(len(data["days"]), 5)  # 10 to 14 inclusive is 5 days
        self.assertIn("recommended_attractions", data)
        self.assertIn("food_and_dining", data)
        self.assertIn("transportation", data)
        self.assertIn("accommodation_areas", data)
        self.assertIn("budget_breakdown", data)
        self.assertIn("packing_checklist", data)
        self.assertIn("safety_and_health", data)
        self.assertIn("useful_travel_tips", data)
        self.assertIn("bad_weather_alternatives", data)

    def test_save_and_retrieve_trip_crud(self):
        """Test saving, retrieving, and deleting trips in SQLite."""
        trip_payload = {
            "title": "Weekend in Jaipur",
            "destination": "Jaipur",
            "starting_city": "Delhi",
            "departure_date": "2026-11-01",
            "return_date": "2026-11-04",
            "duration_days": 4,
            "travelers": 2,
            "adults": 2,
            "children": 0,
            "budget_inr": 35000,
            "travel_style": "Culture",
            "interests": ["History", "Culture"],
            "itinerary": {
                "title": "Weekend in Jaipur",
                "days": [{"day_number": 1, "theme": "Forts"}]
            },
            "is_sample": True
        }

        # 1. Save trip
        save_res = self.client.post("/api/save-trip", json=trip_payload)
        self.assertEqual(save_res.status_code, 201)
        save_data = save_res.get_json()
        self.assertTrue(save_data["success"])
        trip_id = save_data["trip_id"]
        self.assertIsNotNone(trip_id)

        # 2. Get all trips
        list_res = self.client.get("/api/trips")
        self.assertEqual(list_res.status_code, 200)
        trips = list_res.get_json()["trips"]
        self.assertEqual(len(trips), 1)
        self.assertEqual(trips[0]["destination"], "Jaipur")

        # 3. Get single trip details
        detail_res = self.client.get(f"/api/trips/{trip_id}")
        self.assertEqual(detail_res.status_code, 200)
        detail_data = detail_res.get_json()["trip"]
        self.assertEqual(detail_data["title"], "Weekend in Jaipur")
        self.assertIn("itinerary", detail_data)

        # 4. Delete trip
        del_res = self.client.delete(f"/api/trips/{trip_id}")
        self.assertEqual(del_res.status_code, 200)

        # 5. Verify trip is gone
        del_check = self.client.get(f"/api/trips/{trip_id}")
        self.assertEqual(del_check.status_code, 404)

    def test_api_calculate_budget(self):
        """Test /api/calculate-budget endpoint."""
        res = self.client.post("/api/calculate-budget", json={
            "days": 5,
            "travelers": 2,
            "tier": "mid",
            "is_international": False
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("total_estimated_inr", data["estimate"])
        self.assertIn("accommodation", data["estimate"])
        self.assertIn("food_dining", data["estimate"])


if __name__ == "__main__":
    unittest.main()
