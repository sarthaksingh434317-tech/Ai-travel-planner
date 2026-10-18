"""
Gemini AI Travel Itinerary Service
Integrates with Google Gemini API to generate structured, personalized travel itineraries.
Provides graceful fallbacks and sample mode when the API key is not configured.
"""
import os
import json
import re
import logging
from datetime import datetime, timedelta
import requests
from config import Config

logger = logging.getLogger(__name__)

# Try importing google.genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai SDK not available; will use direct REST API or sample generator.")


def build_prompt(plan_params):
    """
    Construct a structured prompt for Gemini asking for a detailed JSON response.
    """
    destination = plan_params.get("destination", "Goa")
    starting_city = plan_params.get("starting_city", "Mumbai")
    departure_date = plan_params.get("departure_date", "")
    return_date = plan_params.get("return_date", "")
    duration_days = plan_params.get("duration_days", 4)
    travelers = plan_params.get("travelers", 2)
    adults = plan_params.get("adults", 2)
    children = plan_params.get("children", 0)
    budget_inr = plan_params.get("budget_inr", 50000)
    travel_style = plan_params.get("travel_style", "Balanced")
    interests = plan_params.get("interests", ["Beaches", "Culture", "Food"])
    if isinstance(interests, list):
        interests_str = ", ".join(interests)
    else:
        interests_str = str(interests)

    accommodation = plan_params.get("accommodation_pref", "3-Star Hotel / Mid-range Resort")
    transport = plan_params.get("transport_pref", "Flight / Local Cabs")
    dietary = plan_params.get("dietary_pref", "No Restrictions")
    notes = plan_params.get("additional_notes", "None")

    prompt = f"""
You are an expert luxury travel consultant and travel guide architect.
Design an in-depth, realistic, and highly engaging travel itinerary tailored to the traveler's exact preferences.

=== TRAVEL DETAILS ===
- Destination: {destination}
- Origin / Starting City: {starting_city}
- Dates: {departure_date} to {return_date} ({duration_days} Days)
- Travelers: {travelers} total ({adults} Adults, {children} Children)
- Total Estimated Budget: ₹{budget_inr:,} INR (All expenses in Indian Rupees)
- Travel Style: {travel_style}
- Specific Interests: {interests_str}
- Preferred Accommodation: {accommodation}
- Preferred Transportation: {transport}
- Dietary Preferences: {dietary}
- Additional Traveler Notes: {notes}

=== CRITICAL RULES ===
1. Do not invent live flight numbers, hotel availability, or real-time booking status.
2. Clearly formulate all costs as realistic estimates in Indian Rupees (INR).
3. The day-by-day itinerary MUST contain exactly {duration_days} days.
4. Output MUST BE strictly valid JSON with no markdown formatting outside the JSON block.

=== JSON OUTPUT SCHEMA ===
Return a single JSON object with these EXACT keys:
{{
  "title": "A catchy, creative trip title (e.g. 'Sun, Sights & Shacks: The Ultimate Goa Escape')",
  "tagline": "Short evocative tagline",
  "destination": "{destination}",
  "overview": {{
    "summary": "Detailed 2-3 paragraph narrative overview of the trip experience",
    "ideal_pace": "Relaxed | Moderate | Fast-paced",
    "best_season_note": "Brief note on current season / weather expectations",
    "cultural_vibe": "Brief highlight of destination cultural tone"
  }},
  "destination_intro": {{
    "history_and_heritage": "Rich paragraph about history and evolution",
    "geography_and_nature": "Geographical setting and scenic highlights",
    "local_culture_and_etiquette": "Key cultural customs, greeting norms, and dress codes"
  }},
  "days": [
    {{
      "day_number": 1,
      "date": "Date string or Day 1",
      "theme": "Theme of the day (e.g. Arrival & Sunset Shacks)",
      "morning": {{
        "time": "09:00 AM - 12:30 PM",
        "activity": "Activity title",
        "description": "Detailed activity description",
        "estimated_cost_inr": 500,
        "tips": "Practical tip for this activity"
      }},
      "afternoon": {{
        "time": "01:00 PM - 05:00 PM",
        "activity": "Activity title",
        "description": "Detailed activity description with lunch suggestion",
        "estimated_cost_inr": 800,
        "tips": "Practical tip for this activity"
      }},
      "evening": {{
        "time": "05:30 PM - 09:30 PM",
        "activity": "Activity title",
        "description": "Evening and dinner experience",
        "estimated_cost_inr": 1200,
        "tips": "Sunset / nightlife tip"
      }},
      "daily_highlight": "The single best highlight of this day"
    }}
  ],
  "recommended_attractions": [
    {{
      "name": "Attraction name",
      "category": "Historical | Nature | Adventure | Cultural | Scenic",
      "description": "Compelling description",
      "entry_fee_inr": 250,
      "recommended_time_hours": "2-3 hours",
      "best_time_of_day": "Morning / Late Afternoon"
    }}
  ],
  "food_and_dining": {{
    "must_try_dishes": [
      {{ "dish": "Dish name", "description": "Why you must try it and flavor profile" }}
    ],
    "recommended_eateries": [
      {{ "name": "Place name", "cuisine": "Cuisine type", "vibe": "Fine dining / Street / Cafe", "price_range_inr": "₹600 - ₹1,200 for two" }}
    ],
    "dietary_notes": "Specific advice respecting {dietary}"
  }},
  "transportation": {{
    "getting_there": "Best way to reach from {starting_city} (flights, trains, highways)",
    "getting_around": "Local mobility recommendations (cabs, rentals, scooters, metro)",
    "estimated_local_transport_cost_per_day_inr": 1200,
    "pro_travel_tip": "Insider transport hack"
  }},
  "accommodation_areas": [
    {{
      "neighborhood": "Area name",
      "best_for": "Couples / Families / Budget / Nightlife",
      "vibe_description": "Neighborhood ambiance and proximity to landmarks",
      "average_nightly_rate_inr": 4500
    }}
  ],
  "budget_breakdown": {{
    "currency": "INR",
    "accommodation_total_inr": 20000,
    "food_dining_total_inr": 12000,
    "activities_tickets_total_inr": 6000,
    "local_transport_total_inr": 5000,
    "shopping_contingency_total_inr": 7000,
    "total_estimated_budget_inr": {budget_inr},
    "estimated_daily_cost_per_person_inr": 4500,
    "budget_verdict": "Matches the provided budget comfortably with moderate luxury."
  }},
  "packing_checklist": {{
    "clothing": ["Light cottons", "Swimwear", "Evening casuals"],
    "essentials": ["Government ID", "Sunscreen SPF 50+", "Comfortable walking footwear"],
    "electronics": ["Power bank (20,000mAh)", "Universal adapter", "Camera"],
    "health_and_medical": ["First aid kit", "Motion sickness pills", "Oral rehydration salts", "Personal prescription medications"]
  }},
  "safety_and_health": [
    "Safety tip 1 (local emergency numbers, water safety, nighttime precautions)",
    "Safety tip 2 (scam warnings and taxi meter protocols)",
    "Safety tip 3 (medical care / pharmacy availability)"
  ],
  "useful_travel_tips": [
    "Useful tip 1 (SIM card / connectivity / best navigation apps)",
    "Useful tip 2 (Cash vs digital payments / UPI acceptance)",
    "Useful tip 3 (Tipping culture and bargain etiquette)"
  ],
  "bad_weather_alternatives": [
    {{
      "activity": "Alternative rainy/bad-weather activity title",
      "location_or_type": "Indoor museum, artisanal market, cooking workshop",
      "description": "Why it's a great backup plan"
    }}
  ],
  "disclaimer": "All prices, entrance fees, and transit costs are estimates in INR and subject to seasonal fluctuation. Please confirm live bookings, flight fares, and opening hours independently before traveling."
}}
"""
    return prompt.strip()


def clean_json_response(raw_text):
    """
    Clean markdown code fence wrapper and extract pure JSON string.
    """
    text = raw_text.strip()
    # Remove markdown code fences e.g. ```json ... ``` or ``` ... ```
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    # Sometimes there is explanatory text before or after the JSON
    json_start = text.find("{")
    json_end = text.rfind("}")
    if json_start != -1 and json_end != -1 and json_end > json_start:
        text = text[json_start:json_end+1]
    return text


def call_gemini_api(prompt, api_key=None, model_name=None):
    """
    Execute Gemini API call using google-genai SDK or direct REST API fallback.
    Returns: parsed dictionary response.
    Raises: Exception on failure.
    """
    key = api_key or Config.GEMINI_API_KEY
    if not key:
        raise ValueError("No Gemini API key configured.")

    model = model_name or Config.GEMINI_MODEL or "gemini-2.5-flash"

    # Strategy 1: google-genai SDK if available
    if GENAI_AVAILABLE:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                )
            )
            raw_content = response.text
            cleaned = clean_json_response(raw_content)
            data = json.loads(cleaned)
            return data
        except Exception as e:
            logger.warning("google-genai SDK call failed (%s); trying direct REST API...", str(e))

    # Strategy 2: Direct REST API via requests
    rest_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }
    
    res = requests.post(rest_url, json=payload, timeout=45)
    if not res.ok:
        err_msg = f"Gemini API returned HTTP {res.status_code}: {res.text}"
        raise RuntimeError(err_msg)

    data = res.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini API returned no candidates.")
    
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise RuntimeError("No text parts in Gemini response.")
    
    raw_text = parts[0].get("text", "")
    cleaned = clean_json_response(raw_text)
    return json.loads(cleaned)


def generate_sample_itinerary(plan_params):
    """
    Generates a realistic, highly customized sample itinerary when Gemini API key
    is not set or the API is unavailable.
    Explicitly marks `is_sample: true` so the UI clearly alerts the user.
    """
    dest_name = plan_params.get("destination", "Goa").strip()
    starting_city = plan_params.get("starting_city", "Mumbai").strip()
    duration_days = int(plan_params.get("duration_days", 4))
    travelers = int(plan_params.get("travelers", 2))
    budget_inr = int(plan_params.get("budget_inr", 50000))
    travel_style = plan_params.get("travel_style", "Balanced")
    dietary = plan_params.get("dietary_pref", "No Restrictions")
    interests = plan_params.get("interests", ["Beaches", "Food", "Culture"])

    # Determine per person daily cost estimate
    per_person_daily = max(2000, round(budget_inr / max(1, duration_days * travelers)))
    
    # Calculate sensible budget breakdown percentages
    stay_budget = round(budget_inr * 0.40)
    food_budget = round(budget_inr * 0.25)
    activities_budget = round(budget_inr * 0.15)
    transport_budget = round(budget_inr * 0.12)
    contingency_budget = budget_inr - (stay_budget + food_budget + activities_budget + transport_budget)

    # Destination-specific flavor data
    dest_lower = dest_name.lower()
    
    if "manali" in dest_lower:
        dest_tagline = "Snowy Himalayan Valleys, Roaring Rivers & Alpine Serenity"
        day_activities = [
            ("Arrival & Old Manali Stroll", "Hadimba Temple in cedar woods", "Old Manali riverside cafes & trout tasting", "Mall Road shopping for woolens & apple cider"),
            ("Solang Valley Thrills", "Solang Valley adventure & paragliding", "Zorbing and mountain ATV trails", "Vashisht hot sulfur springs & village walk"),
            ("Atal Tunnel & Sissu Expedition", "Scenic drive through Atal Tunnel to Lahaul", "Sissu waterfall exploration & snow vistas", "Campfire & Himachali Siddu tasting"),
            ("Naggar Castle & River Rafting", "Naggar Castle art gallery & Beas views", "White water rafting in Beas River", "Riverside twilight cafe chill in Old Manali"),
            ("Jogini Waterfalls & Trek", "Morning hike to Jogini Falls from Vashisht", "Picnic lunch overlooking Kullu Valley", "Old town souvenir shopping & cafe desserts"),
            ("Rohtang Snow Excursion", "Early morning climb to Rohtang Pass (subject to permit)", "Snow sledging and panoramic glacier vistas", "Cozy dinner at Johnson's Cafe"),
            ("Farewell to Himachal", "Quiet morning walk along cedar sanctuary", "Final souvenir collection & pine honey purchase", "Departure transfers from Kullu/Manali")
        ]
        must_try = [
            {"dish": "Himachali Siddu", "description": "Steamed wheat bread stuffed with spiced lentils and poppy seeds, drenched in pure desi ghee."},
            {"dish": "Kullu Trout Fish", "description": "Pan-fried fresh Himalayan river trout seasoned with lemon butter and mountain herbs."},
            {"dish": "Chana Madra", "description": "Traditional slow-cooked yogurt and chickpea curry infused with cardamom and cloves."}
        ]
        attractions = [
            {"name": "Solang Valley", "category": "Adventure", "description": "Premier hub for paragliding, zorbing, and quad-biking.", "entry_fee_inr": 500, "recommended_time_hours": "4 hours", "best_time_of_day": "Morning"},
            {"name": "Hadimba Devi Temple", "category": "Historical", "description": "Four-tiered wooden pagoda temple set inside Dhungri pine forest.", "entry_fee_inr": 50, "recommended_time_hours": "1.5 hours", "best_time_of_day": "Morning"},
            {"name": "Atal Tunnel & Sissu", "category": "Scenic", "description": "Engineering marvel leading to the stark, dramatic mountains of Lahaul.", "entry_fee_inr": 0, "recommended_time_hours": "5 hours", "best_time_of_day": "Midday"}
        ]
        neighborhoods = [
            {"neighborhood": "Old Manali", "best_for": "Backpackers, Couples, Cafe Enthusiasts", "vibe_description": "Bohemian cobblestone lanes lined with live music cafes and pine views.", "average_nightly_rate_inr": 3500},
            {"neighborhood": "Aleo & Prini", "best_for": "Luxury & Families", "vibe_description": "Tranquil apple orchard resorts away from traffic hustle.", "average_nightly_rate_inr": 6500}
        ]
    elif "jaipur" in dest_lower:
        dest_tagline = "Royal Forts, Terracotta Pink Palaces & Timeless Heritage"
        day_activities = [
            ("Welcome to the Royal Capital", "Hawa Mahal photo stop and City Palace tour", "Jantar Mantar astronomical observatory", "Nahargarh Fort panoramic sunset & heritage dinner"),
            ("Citadels of Amber & Jaigarh", "Elephant/Jeep ascent to majestic Amer Fort", "Sheesh Mahal (Hall of Mirrors) exploration", "Sound & light show at Amber courtyard"),
            ("Artisans & Bazaars", "Albert Hall Museum & Ram Niwas Garden", "Johari & Bapu Bazaar shopping for gems & textiles", "Chokhi Dhani ethnic village cultural fiesta"),
            ("Secret Stepwells & Mansions", "Panna Meena Ka Kund stepwell photography", "Jal Mahal lake viewpoint & local lassi", "Rooftop dinner overlooking illuminated Hawa Mahal"),
            ("Royal Cenotaphs & Heritage Walk", "Gaitore Ki Chhatriyan marble cenotaphs", "Block printing workshop in Sanganer", "Laxmi Misthan Bhandar Rajasthani Thali feast")
        ]
        must_try = [
            {"dish": "Dal Baati Churma", "description": "Iconic Rajasthani trio of baked wheat dough balls, rich mixed dal, and sweet churma with ghee."},
            {"dish": "Laal Maas", "description": "Fiery mutton curry simmered with spicy Mathania red chilies and royal Rajasthani spices."},
            {"dish": "Ghevar & Pyaaz Kachori", "description": "Crisp honeycomb sweet disc drenched in syrup, paired with spicy onion kachori."}
        ]
        attractions = [
            {"name": "Amer Fort & Palace", "category": "Historical", "description": "Massive hilltop fortress with intricate mirror palaces and Maota Lake views.", "entry_fee_inr": 200, "recommended_time_hours": "3.5 hours", "best_time_of_day": "Early Morning"},
            {"name": "Hawa Mahal (Palace of Winds)", "category": "Historical", "description": "Iconic 953-window honeycomb pink facade designed for royal ladies to view street festivals.", "entry_fee_inr": 100, "recommended_time_hours": "1 hour", "best_time_of_day": "Sunrise / Early Morning"},
            {"name": "Nahargarh Fort", "category": "Scenic", "description": "High ridge fort offering unmatched sunset panoramas over Jaipur city.", "entry_fee_inr": 150, "recommended_time_hours": "2.5 hours", "best_time_of_day": "Late Afternoon"}
        ]
        neighborhoods = [
            {"neighborhood": "C-Scheme & Civil Lines", "best_for": "Upscale dining, Luxury boutique stays", "vibe_description": "Green tree-lined avenues with premier cafes and designer boutiques.", "average_nightly_rate_inr": 5500},
            {"neighborhood": "Old Walled City (Pink City)", "best_for": "Heritage enthusiasts & Walkers", "vibe_description": "Historic Havelis converted into heritage hotels within walking distance of forts.", "average_nightly_rate_inr": 3800}
        ]
    elif "paris" in dest_lower:
        dest_tagline = "Artistic Splendor, Haute Gastronomy & Seine River Romance"
        day_activities = [
            ("Arrival & Iconic Landmarks", "Stroll along Champ de Mars & Eiffel Tower ascent", "Trocadéro photo vantage & Seine river picnic", "Evening Seine River Champagne Cruise"),
            ("World Art & Louvre Treasures", "Morning tour of Louvre Museum (Mona Lisa & Venus)", "Tuileries Garden walk and Angelina hot chocolate", "Stroll through Place Vendôme & Palais Garnier"),
            ("Bohemian Montmartre & Latin Quarter", "Sacré-Cœur Basilica summit & artists' square", "Lunch at rustic Montmartre bistro", "Shakespeare and Company bookstore & Notre-Dame perimeter"),
            ("Royal Versailles Day Trip", "Morning RER train to Palace of Versailles", "Hall of Mirrors & Grand Trianon gardens", "Return to Saint-Germain-des-Prés for sidewalk cafe dinner"),
            ("Fashion, Marais & Rooftops", "Trendy Le Marais boutiques & Place des Vosges", "Centre Pompidou contemporary art", "Rooftop cocktails at Galeries Lafayette terrace")
        ]
        must_try = [
            {"dish": "Fresh Butter Croissants & Baguettes", "description": "Crisp flaky artisan pastry from local boulangeries."},
            {"dish": "Boeuf Bourguignon", "description": "Slow-braised beef stew cooked in Burgundy red wine with mushrooms and carrots."},
            {"dish": "Artisan Macarons", "description": "Delicate almond meringue confections from Maison Ladurée or Pierre Hermé."}
        ]
        attractions = [
            {"name": "Eiffel Tower", "category": "Historical", "description": "The world's most romantic wrought-iron symbol offering panoramic Paris views.", "entry_fee_inr": 2500, "recommended_time_hours": "2.5 hours", "best_time_of_day": "Sunset"},
            {"name": "The Louvre Museum", "category": "Cultural", "description": "World's grandest art museum housing 35,000 treasures inside a historic palace.", "entry_fee_inr": 2000, "recommended_time_hours": "4 hours", "best_time_of_day": "Morning"},
            {"name": "Sainte-Chapelle", "category": "Historical", "description": "Gothic jewel box featuring 13th-century stained glass windows soaring 15 meters high.", "entry_fee_inr": 1200, "recommended_time_hours": "1.5 hours", "best_time_of_day": "Morning"}
        ]
        neighborhoods = [
            {"neighborhood": "Saint-Germain-des-Prés (6th Arr.)", "best_for": "Romance & Art lovers", "vibe_description": "Quintessential Parisian cafes, art galleries, and historic streets.", "average_nightly_rate_inr": 18000},
            {"neighborhood": "Le Marais (3rd/4th Arr.)", "best_for": "Trendsetters, Boutique shopping, Foodies", "vibe_description": "Medieval alleys, courtyard cafes, and vibrant nightlife.", "average_nightly_rate_inr": 15000}
        ]
    else:
        # Default high-fidelity beach/destination template (e.g. Goa, Bali, Kerala, or any customized place)
        dest_tagline = f"Enchanting Getaway to {dest_name}: Sun, Culture & Local Flavors"
        day_activities = [
            ("Arrival & Coastal Orientation", f"Check in to your hotel and unwind after transit from {starting_city}", f"Explore scenic coastal walkways and iconic neighborhood landmarks", f"Sunset dinner at a beachfront / terrace restaurant with local delicacies"),
            ("Heritage, Culture & Local Sights", "Guided morning tour of key historical sanctuaries and monuments", "Lunch featuring fresh regional cuisine and artisan cafe tasting", "Bustling local evening market, handicraft shopping, and live folk music"),
            ("Adventure & Scenic Exploration", "Exciting outdoor expedition or panoramic nature trail excursion", "Scenic lunch overlooking verdant valleys or sparkling waters", "Golden hour photo walk followed by a starlit dinner"),
            ("Hidden Gems & Slow Travel", "Visit off-the-beaten-path fishing villages, spice plantations or sacred temples", "Leisurely afternoon spa / wellness / pool relaxation", "Farewell celebratory dinner with traditional music and signature desserts"),
            ("Day Excursion & Nature Retreat", "Excursion to nearby waterfalls, islands or national park boundaries", "Picnic lunch in pristine nature surroundings", "Return for a relaxed sunset lounge evening"),
            ("Arts, Markets & Cooking Class", "Interactive regional culinary masterclass with a local chef", "Tasting session and artisan gallery exploration", "Evening river / coastal dinner cruise"),
            ("Cherished Memories & Departure", "Sunrise walk and peaceful coffee overlooking panoramic views", "Final souvenir collection and local sweets packaging", f"Transfer back toward {starting_city}")
        ]
        must_try = [
            {"dish": f"Signature {dest_name} Special Curry", "description": "Fragrant regional spices slow-simmered with coconut milk and garden herbs."},
            {"dish": "Local Street Food Delights", "description": "Crisp savory pastries and freshly made sweet delicacies from street bazaars."},
            {"dish": "Fresh Harvest Seafood / Organic Platter", "description": "Catch of the day grilled with lemon, garlic butter, and local red paste."}
        ]
        attractions = [
            {"name": f"Historic Fort & Coastal Viewpoint", "category": "Historical", "description": "Ancient lookout perched high on a headland offering sweeping ocean views.", "entry_fee_inr": 150, "recommended_time_hours": "2 hours", "best_time_of_day": "Late Afternoon"},
            {"name": f"Sacred Cathedral & Heritage Quarter", "category": "Cultural", "description": "Centuries-old architecture adorned with intricate woodwork and gilded altars.", "entry_fee_inr": 100, "recommended_time_hours": "2 hours", "best_time_of_day": "Morning"},
            {"name": f"Emerald Spice & Nature Reserve", "category": "Nature", "description": "Guided walking tour through cardamom, vanilla, and pepper plantations.", "entry_fee_inr": 400, "recommended_time_hours": "3 hours", "best_time_of_day": "Midday"}
        ]
        neighborhoods = [
            {"neighborhood": "Coastal Promenade / Beachfront", "best_for": "Beach lovers, Nightlife, Couples", "vibe_description": "Steps away from the sands, shacks, and vibrant sunset venues.", "average_nightly_rate_inr": 4500},
            {"neighborhood": "Heritage District / Old Quarter", "best_for": "Culture seekers, History buffs, Quiet stays", "vibe_description": "Charming colonial architecture, boutique cafes, and tree-lined walkways.", "average_nightly_rate_inr": 5200}
        ]

    # Generate day schedule based on requested duration
    days_list = []
    base_date = datetime.now() + timedelta(days=14)
    if plan_params.get("departure_date"):
        try:
            base_date = datetime.strptime(plan_params.get("departure_date"), "%Y-%m-%d")
        except Exception:
            pass

    for i in range(duration_days):
        day_date = (base_date + timedelta(days=i)).strftime("%A, %b %d")
        activity_tuple = day_activities[i % len(day_activities)]
        days_list.append({
            "day_number": i + 1,
            "date": day_date,
            "theme": activity_tuple[0],
            "morning": {
                "time": "09:00 AM - 12:30 PM",
                "activity": activity_tuple[1],
                "description": f"Kickstart the day with a nourishing breakfast followed by a visit to {activity_tuple[1]}.",
                "estimated_cost_inr": round(per_person_daily * 0.25),
                "tips": "Carry your water bottle and comfortable walking shoes."
            },
            "afternoon": {
                "time": "01:00 PM - 04:30 PM",
                "activity": activity_tuple[2],
                "description": f"Enjoy a relaxed regional lunch, followed by {activity_tuple[2]}.",
                "estimated_cost_inr": round(per_person_daily * 0.35),
                "tips": "Book entry passes or table reservations slightly ahead of peak hours."
            },
            "evening": {
                "time": "05:00 PM - 09:30 PM",
                "activity": activity_tuple[3],
                "description": f"Witness the golden hour magic and wrap up your day with {activity_tuple[3]}.",
                "estimated_cost_inr": round(per_person_daily * 0.40),
                "tips": "Ideal time for sunset photos and evening relaxation."
            },
            "daily_highlight": f"Unforgettable memories at {activity_tuple[1]} and sunset dining."
        })

    sample_itinerary = {
        "title": f"The Ultimate {travel_style} Journey to {dest_name}",
        "tagline": dest_tagline,
        "destination": dest_name,
        "is_sample": True,
        "sample_notice": "SAMPLE ITINERARY MODE: This detailed plan was curated using TravelGenius AI's high-fidelity travel template engine because the Gemini API key is not configured or reachable. Configure GEMINI_API_KEY to enable live AI generation.",
        "overview": {
            "summary": f"Welcome to your tailored {duration_days}-day itinerary to {dest_name}, starting from {starting_city}. Specially curated for {travelers} traveler(s) with an approximate budget of ₹{budget_inr:,} INR. Whether you are seeking relaxing sceneries, authentic culinary adventures, or unforgettable cultural memories, this itinerary balances iconic landmarks with handpicked local gems.",
            "ideal_pace": "Balanced & Immersive",
            "best_season_note": "Great time for clear skies, pleasant daytime strolls, and mild evenings.",
            "cultural_vibe": f"Warm, welcoming, and deeply rooted in local traditions and hospitality."
        },
        "destination_intro": {
            "history_and_heritage": f"{dest_name} boasts a rich history where centuries of cultural trade, ancient dynasties, and geographic significance have woven a vibrant tapestry evident in its forts, sanctuaries, and architecture.",
            "geography_and_nature": f"Surrounded by striking landscapes, the region offers captivating natural contrasts, from lush greenery to iconic vantage points perfect for photography.",
            "local_culture_and_etiquette": f"Locals are courteous and helpful. Modest clothing is appreciated at sacred and religious sites, and a polite greeting opens doors everywhere."
        },
        "days": days_list,
        "recommended_attractions": attractions,
        "food_and_dining": {
            "must_try_dishes": must_try,
            "recommended_eateries": [
                {"name": f"The Garden Bistro & Cafe", "cuisine": "Local & Continental Fusion", "vibe": "Cozy heritage setting with live acoustic music", "price_range_inr": "₹800 - ₹1,400 for two"},
                {"name": f"Heritage Spice Court", "cuisine": "Authentic Regional Cuisine", "vibe": "Traditional thali dining with family-friendly warmth", "price_range_inr": "₹600 - ₹1,100 for two"},
                {"name": f"Skyline Sunset Lounge", "cuisine": "Tapas & Refreshments", "vibe": "Panoramic open-air terrace with sunset views", "price_range_inr": "₹1,200 - ₹2,000 for two"}
            ],
            "dietary_notes": f"Dietary preference '{dietary}' is well accommodated across most reputable cafes and restaurants. Always inform the server beforehand."
        },
        "transportation": {
            "getting_there": f"Direct flights or convenient express trains link {starting_city} to the nearest airport/railway junction for {dest_name}.",
            "getting_around": "App-based cabs, prepaid airport taxis, and local auto-rickshaws or self-drive rentals are readily available.",
            "estimated_local_transport_cost_per_day_inr": max(600, round(transport_budget / max(1, duration_days))),
            "pro_travel_tip": "Download offline Google Maps of the region before traveling for seamless navigation during low-connectivity patches."
        },
        "accommodation_areas": neighborhoods,
        "budget_breakdown": {
            "currency": "INR",
            "accommodation_total_inr": stay_budget,
            "food_dining_total_inr": food_budget,
            "activities_tickets_total_inr": activities_budget,
            "local_transport_total_inr": transport_budget,
            "shopping_contingency_total_inr": contingency_budget,
            "total_estimated_budget_inr": budget_inr,
            "estimated_daily_cost_per_person_inr": per_person_daily,
            "budget_verdict": f"The budget of ₹{budget_inr:,} INR provides a comfortable {travel_style.lower()} experience for {travelers} traveler(s)."
        },
        "packing_checklist": {
            "clothing": [
                "Light breathable cotton shirts / t-shirts",
                "Comfortable walking trousers / linen pants",
                "Light windbreaker or evening shawl",
                "Swimwear / quick-dry beachwear (if coastal)"
            ],
            "essentials": [
                "Government Photo ID & soft copies saved on phone",
                "Broad-spectrum sunscreen (SPF 50+) and sunglasses",
                "Sturdy, broken-in walking shoes and flip-flops",
                "Reusable water bottle with filter"
            ],
            "electronics": [
                "Smartphone with offline maps installed",
                "20,000 mAh fast-charging power bank",
                "Universal travel plug / multi-port charging hub",
                "Camera with extra memory card"
            ],
            "health_and_medical": [
                "Personal prescription medications with prescriptions",
                "Motion sickness pills & antacids",
                "Insect repellent spray / cream",
                "Basic first-aid kit with bandages and antiseptic wipes"
            ]
        },
        "safety_and_health": [
            "Drink bottled or filtered water from verified dispensers.",
            "Always negotiate or ensure the meter is running before boarding unmetered taxis/autos.",
            "Keep emergency contact numbers and hotel address card in your wallet and phone.",
            "Be cautious when engaging in watersports or adventure sports; verify certified instructors."
        ],
        "useful_travel_tips": [
            "UPI payments (Google Pay, PhonePe, Paytm) are accepted almost everywhere in India; carry ₹2,000 in small cash notes for rural stalls.",
            "Early morning visits to popular monuments beat both the heat and large tour crowds.",
            "Respect local photography guidelines, especially inside temples, tribal hamlets, and government buildings."
        ],
        "bad_weather_alternatives": [
            {
                "activity": "Regional Heritage Museum & Art Gallery Tour",
                "location_or_type": "Indoor Cultural Center",
                "description": "Discover indigenous artifacts, royal memorabilia, and contemporary folk art inside air-conditioned halls."
            },
            {
                "activity": "Traditional Cooking & Spice Blending Masterclass",
                "location_or_type": "Local Culinary Studio / Homestay",
                "description": "Learn to grind signature spices and cook a three-course traditional feast with an expert local chef."
            },
            {
                "activity": "Artisan Silk & Handicraft Emporium Exploration",
                "location_or_type": "Covered Indoor Bazaar",
                "description": "Watch master weavers and potters at work, and pick up authentic certified souvenirs without getting wet."
            }
        ],
        "disclaimer": "All prices, entrance tickets, and transit fares are realistic estimates in Indian Rupees (INR) and subject to seasonal changes. Please verify current timings and live flight/hotel fares before booking."
    }

    return sample_itinerary


def generate_itinerary(plan_params, user_api_key=None):
    """
    Main entry point for generating itineraries.
    Attempts Gemini API first if a key is provided (either via parameter, headers, or env).
    Falls back gracefully to high-quality sample itinerary if key is absent or API fails.
    Returns: dict with itinerary data and status metadata.
    """
    key = (user_api_key or "").strip() or Config.GEMINI_API_KEY
    
    if key:
        prompt = build_prompt(plan_params)
        try:
            logger.info("Calling Gemini API with model %s...", Config.GEMINI_MODEL)
            data = call_gemini_api(prompt, api_key=key, model_name=Config.GEMINI_MODEL)
            data["is_sample"] = False
            data["generated_by"] = "Google Gemini AI"
            return {
                "success": True,
                "is_sample": False,
                "data": data,
                "message": "Itinerary successfully generated with Gemini AI!"
            }
        except Exception as e:
            logger.error("Gemini API error: %s. Falling back to sample mode.", str(e))
            sample = generate_sample_itinerary(plan_params)
            sample["api_error"] = str(e)
            return {
                "success": True,
                "is_sample": True,
                "data": sample,
                "message": f"Notice: Gemini API unavailable ({str(e)}). Providing a high-fidelity sample itinerary.",
                "error_detail": str(e)
            }
    else:
        logger.info("No Gemini API key supplied. Serving sample itinerary.")
        sample = generate_sample_itinerary(plan_params)
        return {
            "success": True,
            "is_sample": True,
            "data": sample,
            "message": "Running in Demo Mode: Sample itinerary generated. Configure GEMINI_API_KEY to unlock live AI generation."
        }
