"""
TravelGenius AI – Smart Travel Planner
Flask Application Server
"""
import os
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

from config import Config
from database import init_db, save_trip, get_all_trips, get_trip_by_id, delete_trip
from destinations_data import get_all_destinations, get_destination_by_id, filter_destinations
from gemini_service import generate_itinerary

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database schema on startup
with app.app_context():
    init_db()


# -------------------------------------------------------------
# Frontend Page Routes
# -------------------------------------------------------------

@app.route("/")
def index():
    """Landing homepage with hero, popular destinations, how it works, and testimonials."""
    all_destinations = get_all_destinations()
    # Featured 4 popular destinations for homepage preview
    popular_destinations = [d for d in all_destinations if d["id"] in ["goa", "kashmir", "paris", "bali"]]
    return render_template(
        "index.html",
        popular_destinations=popular_destinations,
        has_api_key=bool(Config.GEMINI_API_KEY)
    )


@app.route("/plan")
def plan():
    """Smart AI Trip Planner form and interactive results page."""
    destination_param = request.args.get("destination", "").strip()
    starting_city_param = request.args.get("starting_city", "").strip()
    return render_template(
        "plan.html",
        prefill_destination=destination_param,
        prefill_starting_city=starting_city_param,
        has_api_key=bool(Config.GEMINI_API_KEY)
    )


@app.route("/explore")
def explore():
    """Destination Explorer page showcasing 10 curated destinations with filters."""
    destinations = get_all_destinations()
    return render_template(
        "explore.html",
        destinations=destinations
    )


@app.route("/my-trips")
def my_trips():
    """My Saved Trips page showing user's itineraries from SQLite database."""
    saved_trips = get_all_trips()
    return render_template(
        "my_trips.html",
        trips=saved_trips
    )


@app.route("/about")
def about():
    """About TravelGenius AI, tech stack, ethics, and project architecture."""
    return render_template(
        "about.html",
        has_api_key=bool(Config.GEMINI_API_KEY),
        model_name=Config.GEMINI_MODEL
    )


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

@app.route("/api/generate-itinerary", methods=["POST"])
def api_generate_itinerary():
    """
    Generate an itinerary using Gemini AI or fallback sample mode.
    Validates form data strictly on the backend.
    """
    try:
        data = request.get_json(silent=True) or request.form.to_dict()
        if not data:
            return jsonify({"success": False, "error": "No input payload provided."}), 400

        # Extract and sanitize inputs
        destination = str(data.get("destination", "")).strip()
        starting_city = str(data.get("starting_city", "")).strip()
        departure_date_str = str(data.get("departure_date", "")).strip()
        return_date_str = str(data.get("return_date", "")).strip()

        # Validation: Required text fields
        if not destination:
            return jsonify({"success": False, "error": "Destination city or country is required."}), 400
        if not starting_city:
            return jsonify({"success": False, "error": "Starting city is required."}), 400
        if not departure_date_str:
            return jsonify({"success": False, "error": "Departure date is required."}), 400
        if not return_date_str:
            return jsonify({"success": False, "error": "Return date is required."}), 400

        # Date validation
        try:
            dep_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
            ret_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format. Use YYYY-MM-DD."}), 400

        if ret_date < dep_date:
            return jsonify({"success": False, "error": "Return date cannot be earlier than departure date."}), 400

        duration_days = (ret_date - dep_date).days + 1
        if duration_days <= 0:
            duration_days = 1
        if duration_days > Config.MAX_TRIP_DAYS:
            return jsonify({
                "success": False,
                "error": f"Trips are limited to a maximum of {Config.MAX_TRIP_DAYS} days."
            }), 400

        # Traveler numbers validation
        try:
            adults = int(data.get("adults", 1))
            children = int(data.get("children", 0))
            if adults < 1:
                return jsonify({"success": False, "error": "There must be at least 1 adult traveler."}), 400
            if children < 0:
                return jsonify({"success": False, "error": "Number of children cannot be negative."}), 400
            travelers = adults + children
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid traveler count provided."}), 400

        # Budget validation
        try:
            budget_inr = int(float(str(data.get("budget_inr", 0)).replace(",", "")))
            if budget_inr < 1000:
                return jsonify({"success": False, "error": "Budget must be at least ₹1,000 INR."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Please enter a valid numeric budget in INR."}), 400

        # Preferences
        travel_style = str(data.get("travel_style", "Balanced")).strip()
        accommodation_pref = str(data.get("accommodation_pref", "3-Star Hotel / Mid-range Resort")).strip()
        transport_pref = str(data.get("transport_pref", "Flight / Local Cabs")).strip()
        dietary_pref = str(data.get("dietary_pref", "No Restrictions")).strip()
        additional_notes = str(data.get("additional_notes", "")).strip()

        # Interests list
        interests = data.get("interests", [])
        if isinstance(interests, str):
            try:
                interests = json.loads(interests)
            except Exception:
                interests = [i.strip() for i in interests.split(",") if i.strip()]

        # Prepare parameters
        plan_params = {
            "destination": destination,
            "starting_city": starting_city,
            "departure_date": departure_date_str,
            "return_date": return_date_str,
            "duration_days": duration_days,
            "travelers": travelers,
            "adults": adults,
            "children": children,
            "budget_inr": budget_inr,
            "travel_style": travel_style,
            "interests": interests,
            "accommodation_pref": accommodation_pref,
            "transport_pref": transport_pref,
            "dietary_pref": dietary_pref,
            "additional_notes": additional_notes
        }

        # Check for user-provided API key in header or request payload
        user_key = request.headers.get("X-Gemini-Key") or data.get("gemini_api_key")

        result = generate_itinerary(plan_params, user_api_key=user_key)
        
        # Attach the normalized input parameters to the response for convenience
        result["inputs"] = plan_params

        return jsonify(result), 200

    except Exception as e:
        logger.exception("Error in /api/generate-itinerary: %s", str(e))
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while generating your itinerary. Please try again.",
            "details": str(e)
        }), 500


@app.route("/api/save-trip", methods=["POST"])
def api_save_trip():
    """Save an itinerary to SQLite database."""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "No JSON payload provided."}), 400

        destination = data.get("destination", "").strip()
        if not destination:
            return jsonify({"success": False, "error": "Trip must have a valid destination."}), 400

        trip_id = save_trip(data)
        logger.info("Trip %s saved successfully to SQLite.", trip_id)
        return jsonify({
            "success": True,
            "trip_id": trip_id,
            "message": "Trip itinerary saved to My Trips successfully!"
        }), 201

    except Exception as e:
        logger.exception("Error saving trip: %s", str(e))
        return jsonify({
            "success": False,
            "error": "Failed to save trip to database.",
            "details": str(e)
        }), 500


@app.route("/api/trips", methods=["GET"])
def api_get_trips():
    """Fetch all saved trips."""
    try:
        trips = get_all_trips()
        return jsonify({"success": True, "trips": trips}), 200
    except Exception as e:
        logger.exception("Error fetching trips: %s", str(e))
        return jsonify({"success": False, "error": "Failed to retrieve trips."}), 500


@app.route("/api/trips/<trip_id>", methods=["GET"])
def api_get_trip_detail(trip_id):
    """Fetch full details of a saved trip by ID."""
    try:
        trip = get_trip_by_id(trip_id)
        if not trip:
            return jsonify({"success": False, "error": "Trip not found."}), 404
        return jsonify({"success": True, "trip": trip}), 200
    except Exception as e:
        logger.exception("Error fetching trip %s: %s", trip_id, str(e))
        return jsonify({"success": False, "error": "Failed to retrieve trip details."}), 500


@app.route("/api/trips/<trip_id>", methods=["DELETE"])
@app.route("/api/trips/<trip_id>/delete", methods=["POST", "DELETE"])
def api_delete_trip(trip_id):
    """Delete a saved trip."""
    try:
        success = delete_trip(trip_id)
        if not success:
            return jsonify({"success": False, "error": "Trip not found or already deleted."}), 404
        return jsonify({"success": True, "message": "Trip successfully deleted."}), 200
    except Exception as e:
        logger.exception("Error deleting trip %s: %s", trip_id, str(e))
        return jsonify({"success": False, "error": "Failed to delete trip."}), 500


@app.route("/api/destinations", methods=["GET"])
def api_get_destinations():
    """Retrieve filtered destination catalog."""
    region = request.args.get("region")
    budget = request.args.get("budget")
    travel_style = request.args.get("travel_style")
    q = request.args.get("q")
    destinations = filter_destinations(region=region, budget=budget, travel_style=travel_style, search_query=q)
    return jsonify({"success": True, "count": len(destinations), "destinations": destinations})


@app.route("/api/destinations/<dest_id>", methods=["GET"])
def api_get_destination_detail(dest_id):
    """Retrieve a single destination's detail."""
    dest = get_destination_by_id(dest_id)
    if not dest:
        return jsonify({"success": False, "error": "Destination not found."}), 404
    return jsonify({"success": True, "destination": dest})


@app.route("/api/calculate-budget", methods=["POST"])
def api_calculate_budget():
    """
    Interactive Travel Budget Estimator tool.
    Estimates typical budget breakdown for given travelers, duration, and comfort tier.
    """
    try:
        data = request.get_json(silent=True) or {}
        days = max(1, int(data.get("days", 4)))
        travelers = max(1, int(data.get("travelers", 2)))
        tier = data.get("tier", "mid").lower()  # budget, mid, luxury
        is_international = bool(data.get("is_international", False))

        # Base per person daily cost estimates (INR)
        if tier == "budget":
            daily_base = 3500 if is_international else 1800
        elif tier == "luxury":
            daily_base = 18000 if is_international else 8500
        else:  # mid
            daily_base = 8000 if is_international else 3800

        total_est = daily_base * days * travelers
        
        breakdown = {
            "accommodation": round(total_est * 0.40),
            "food_dining": round(total_est * 0.25),
            "sightseeing_activities": round(total_est * 0.15),
            "local_transport": round(total_est * 0.12),
            "contingency_shopping": round(total_est * 0.08),
            "total_estimated_inr": total_est,
            "per_person_inr": round(total_est / travelers),
            "per_day_per_person_inr": daily_base
        }
        return jsonify({"success": True, "estimate": breakdown}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/health")
def api_health():
    """Health check endpoint for Render/deployment uptime monitors."""
    return jsonify({
        "status": "healthy",
        "service": "TravelGenius AI",
        "has_gemini_key": bool(Config.GEMINI_API_KEY),
        "model": Config.GEMINI_MODEL,
        "database": "sqlite_ready",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


# -------------------------------------------------------------
# Error Handlers
# -------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Endpoint not found", "code": 404}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error", "code": 500}), 500
    return render_template("500.html"), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = Config.DEBUG
    logger.info("Starting TravelGenius AI on port %d (debug=%s)", port, debug)
    app.run(host="0.0.0.0", port=port, debug=debug)
