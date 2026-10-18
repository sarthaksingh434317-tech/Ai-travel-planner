"""
Curated destination catalog for TravelGenius AI
Provides rich data, photography, budget estimates, and filters for 10 top destinations.
"""

DESTINATIONS = [
    {
        "id": "goa",
        "name": "Goa",
        "country": "India",
        "region": "Domestic",
        "tagline": "Sun, Sand, Spice & Coastal Charm",
        "description": "India's beach paradise offers sun-kissed Arabian Sea beaches, Portuguese colonial architecture, vibrant night markets, water sports, and world-class seafood shacks.",
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&w=800&q=80",
        "best_time": "November to February",
        "budget_category": "Budget",
        "budget_range_inr": "₹15,000 – ₹40,000 / person",
        "travel_styles": ["Beaches", "Nightlife", "Budget", "Romantic"],
        "popular_attractions": ["Baga & Anjuna Beaches", "Fort Aguada", "Dudhsagar Falls", "Basilica of Bom Jesus", "Chapora Fort"],
        "ideal_duration": "4 - 5 Days",
        "highlights": [
            "Sunset cruises on Mandovi River",
            "Beach shack dining and Goan fish curry",
            "Water sports at Calangute",
            "Heritage walk in Fontainhas Latin Quarter"
        ]
    },
    {
        "id": "manali",
        "name": "Manali",
        "country": "India",
        "region": "Domestic",
        "tagline": "Snowy Peaks, Pine Forests & Alpine Thrills",
        "description": "Nestled in the breathtaking Himalayas of Himachal Pradesh, Manali is a wonderland of snowy vistas, roaring Beas river, apple orchards, and adventurous mountain passes.",
        "image_url": "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=800&q=80",
        "best_time": "October to June (Snow in Dec-Feb)",
        "budget_category": "Budget",
        "budget_range_inr": "₹18,000 – ₹45,000 / person",
        "travel_styles": ["Mountains", "Adventure", "Romantic", "Nature"],
        "popular_attractions": ["Solang Valley", "Rohtang Pass", "Hadimba Temple", "Old Manali Cafes", "Jogini Waterfall"],
        "ideal_duration": "4 - 6 Days",
        "highlights": [
            "Paragliding & Zorbing in Solang",
            "Old Manali live acoustic cafes",
            "Hot water sulfur springs at Vashisht",
            "Scenic drive through Atal Tunnel"
        ]
    },
    {
        "id": "jaipur",
        "name": "Jaipur",
        "country": "India",
        "region": "Domestic",
        "tagline": "The Pink City of Royal Palaces & Timeless Forts",
        "description": "Rajasthan's historic capital mesmerizes travelers with grand hilltop citadels, intricate terracotta pink facades, royal museum artifacts, and buzzing bazaars overflowing with handicrafts.",
        "image_url": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=800&q=80",
        "best_time": "October to March",
        "budget_category": "Budget",
        "budget_range_inr": "₹12,000 – ₹35,000 / person",
        "travel_styles": ["Culture", "History", "Shopping", "Family"],
        "popular_attractions": ["Hawa Mahal", "Amer Fort", "City Palace", "Jantar Mantar", "Nahargarh Fort Sunset"],
        "ideal_duration": "3 - 4 Days",
        "highlights": [
            "Elephant / Jeep ride up Amer Fort",
            "Authentic Dal Baati Churma dining",
            "Shopping for blue pottery & block prints at Johari Bazaar",
            "Sunset panoramas overlooking Jaipur from Nahargarh"
        ]
    },
    {
        "id": "kerala",
        "name": "Kerala",
        "country": "India",
        "region": "Domestic",
        "tagline": "God's Own Country: Backwaters, Tea Hills & Ayurveda",
        "description": "Immerse yourself in lush emerald tea plantations in Munnar, serene traditional houseboats gliding along Alleppey's backwaters, and rejuvenating Ayurvedic wellness sanctuaries.",
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=800&q=80",
        "best_time": "September to March",
        "budget_category": "Mid-Range",
        "budget_range_inr": "₹25,000 – ₹60,000 / person",
        "travel_styles": ["Nature", "Romantic", "Family", "Culture"],
        "popular_attractions": ["Alleppey Houseboat Backwaters", "Munnar Tea Gardens", "Periyar Wildlife Sanctuary", "Fort Kochi", "Varkala Cliff Beach"],
        "ideal_duration": "5 - 7 Days",
        "highlights": [
            "Overnight traditional Kettuvallam houseboat stay",
            "Fresh tea tasting in misty Munnar hills",
            "Kathakali dance performance in Fort Kochi",
            "Ayurvedic herbal massage & rejuvenation"
        ]
    },
    {
        "id": "kashmir",
        "name": "Kashmir",
        "country": "India",
        "region": "Domestic",
        "tagline": "Paradise on Earth: Pristine Valleys & Shikara Rides",
        "description": "Framed by snow-capped Pir Panjal peaks, Kashmir enchants with tranquil Dal Lake houseboats, colorful blooming tulip gardens, world-famous Gulmarg ski slopes, and Lidder river pines in Pahalgam.",
        "image_url": "https://images.unsplash.com/photo-1595815771614-ade9d652a65d?auto=format&fit=crop&w=800&q=80",
        "best_time": "March to August (Spring/Summer), Dec to Feb (Snow)",
        "budget_category": "Mid-Range",
        "budget_range_inr": "₹30,000 – ₹70,000 / person",
        "travel_styles": ["Mountains", "Romantic", "Nature", "Photography"],
        "popular_attractions": ["Dal Lake Shikara", "Gulmarg Gondola", "Betaab Valley Pahalgam", "Mughal Gardens Srinagar", "Sonamarg Glaciers"],
        "ideal_duration": "5 - 7 Days",
        "highlights": [
            "Sunset Shikara ride on Dal Lake with floating flower market",
            "Riding Phase 2 Gondola up to Apharwat Peak (13,780 ft)",
            "Sampling authentic Kashmiri Wazwan & Kahwa tea",
            "Pony trek across Baisaran 'Mini Switzerland' in Pahalgam"
        ]
    },
    {
        "id": "bali",
        "name": "Bali",
        "country": "Indonesia",
        "region": "International",
        "tagline": "Island of the Gods: Volcanic Vistas, Temples & Surf",
        "description": "A magical island offering cascading green rice terraces, sacred Hindu water temples, dramatic sea cliffs in Uluwatu, vibrant cafes in Seminyak, and serene yoga retreats in Ubud.",
        "image_url": "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80",
        "best_time": "April to October",
        "budget_category": "Mid-Range",
        "budget_range_inr": "₹55,000 – ₹1,10,000 / person",
        "travel_styles": ["Beaches", "Culture", "Romantic", "Adventure"],
        "popular_attractions": ["Ubud Monkey Forest & Rice Terraces", "Tanah Lot Temple", "Uluwatu Sunset & Kecak Dance", "Nusa Penida Kelingking Beach", "Mount Batur Sunrise Trek"],
        "ideal_duration": "6 - 8 Days",
        "highlights": [
            "Sunrise hike up Mount Batur volcano with breakfast",
            "Floating breakfast in private jungle villa",
            "Day speedboat excursion to Nusa Penida",
            "Traditional Balinese massage & spa treatment"
        ]
    },
    {
        "id": "dubai",
        "name": "Dubai",
        "country": "United Arab Emirates",
        "region": "International",
        "tagline": "Futuristic Skylines, Desert Safaris & Ultra Luxury",
        "description": "Where boundless architectural ambition meets Arabian desert mystique. Marvel at the world's tallest tower, ski indoors, shop in monumental mega-malls, and glide over golden sand dunes.",
        "image_url": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=800&q=80",
        "best_time": "November to March",
        "budget_category": "Luxury",
        "budget_range_inr": "₹70,000 – ₹1,60,000 / person",
        "travel_styles": ["Luxury", "Shopping", "Family", "Adventure"],
        "popular_attractions": ["Burj Khalifa 148th Floor", "Dubai Mall & Fountain Show", "Desert Safari with BBQ Dinner", "Museum of the Future", "Palm Jumeirah & Atlantis"],
        "ideal_duration": "4 - 6 Days",
        "highlights": [
            "4x4 dune bashing and starlit Bedouin desert camp",
            "Observatory view from Burj Khalifa At The Top",
            "Yacht cruise around Dubai Marina",
            "Exploring Old Dubai gold & spice souks via Abra boat"
        ]
    },
    {
        "id": "paris",
        "name": "Paris",
        "country": "France",
        "region": "International",
        "tagline": "The City of Light: Haute Couture, Art & Culinary Elegance",
        "description": "Walk along the Seine, gaze up at the glittering Eiffel Tower, immerse yourself in world masterpieces at the Louvre, and savor buttery croissants at quaint Montmartre sidewalk bistros.",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80",
        "best_time": "April to June & September to November",
        "budget_category": "Luxury",
        "budget_range_inr": "₹1,20,000 – ₹2,50,000 / person",
        "travel_styles": ["Romantic", "Culture", "History", "Food"],
        "popular_attractions": ["Eiffel Tower & Champ de Mars", "Louvre Museum", "Notre-Dame & Sainte-Chapelle", "Montmartre & Sacré-Cœur", "Palace of Versailles"],
        "ideal_duration": "5 - 7 Days",
        "highlights": [
            "Seine river champagne dinner cruise",
            "Admiring Mona Lisa and Venus de Milo in the Louvre",
            "Pastry tasting: Macarons at Ladurée & artisan eclairs",
            "Sunset from the steps of Basilique du Sacré-Cœur"
        ]
    },
    {
        "id": "tokyo",
        "name": "Tokyo",
        "country": "Japan",
        "region": "International",
        "tagline": "Neon Metropolises, Ancient Shrines & Culinary Perfection",
        "description": "A mind-bending fusion of hyper-modern neon skyscrapers, robotic pop culture, Michelin-starred ramen bars, and tranquil centuries-old Shinto shrines tucked inside quiet bamboo groves.",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "best_time": "March to May (Cherry Blossoms) & Oct to Nov (Autumn)",
        "budget_category": "Luxury",
        "budget_range_inr": "₹1,40,000 – ₹2,80,000 / person",
        "travel_styles": ["Culture", "Food", "Shopping", "Photography"],
        "popular_attractions": ["Shibuya Crossing", "Senso-ji Temple in Asakusa", "teamLab Planets Digital Art", "Shinjuku Gyoen National Garden", "Meiji Shrine & Harajuku"],
        "ideal_duration": "6 - 8 Days",
        "highlights": [
            "Crossing the iconic Shibuya pedestrian scramble",
            "Tasting Tsukiji outer market fresh sushi & wagyu skewers",
            "Immersive digital art projections at teamLab Planets",
            "Day trip on Shinkansen bullet train to Mount Fuji"
        ]
    },
    {
        "id": "switzerland",
        "name": "Switzerland",
        "country": "Switzerland",
        "region": "International",
        "tagline": "Fairytale Alps, Glacial Lakes & Scenic Trains",
        "description": "Pristine turquoise Alpine lakes, dramatic snow-capped peaks of the Matterhorn and Jungfrau, storybook chalets, world-famous chocolate ateliers, and the world's most scenic panoramic railways.",
        "image_url": "https://images.unsplash.com/photo-1530122037265-a5f1f91d3b99?auto=format&fit=crop&w=800&q=80",
        "best_time": "June to September (Hiking) or Dec to March (Skiing)",
        "budget_category": "Luxury",
        "budget_range_inr": "₹1,80,000 – ₹3,50,000 / person",
        "travel_styles": ["Mountains", "Luxury", "Nature", "Romantic"],
        "popular_attractions": ["Jungfraujoch (Top of Europe)", "Zermatt & Matterhorn", "Lake Lucerne & Mount Pilatus", "Interlaken Adventure Hub", "Bern Historic Old Town"],
        "ideal_duration": "6 - 8 Days",
        "highlights": [
            "Cogwheel railway climb to Jungfraujoch ice palace",
            "Lake Lucerne panoramic steam boat cruise",
            "Authentic Swiss cheese fondue & chocolate tasting",
            "Hiking through Lauterbrunnen valley of 72 waterfalls"
        ]
    }
]

def get_all_destinations():
    """Return all 10 curated destinations."""
    return DESTINATIONS

def get_destination_by_id(dest_id):
    """Retrieve destination details by unique ID."""
    dest_id_lower = (dest_id or "").strip().lower()
    for dest in DESTINATIONS:
        if dest["id"] == dest_id_lower or dest["name"].lower() == dest_id_lower:
            return dest
    return None

def filter_destinations(region=None, budget=None, travel_style=None, search_query=None):
    """
    Filter destinations by region (Domestic/International),
    budget tier (Budget/Mid-Range/Luxury), travel style, or text search.
    """
    results = DESTINATIONS
    
    if region and region.lower() != "all":
        results = [d for d in results if d["region"].lower() == region.lower()]
        
    if budget and budget.lower() != "all":
        results = [d for d in results if d["budget_category"].lower() == budget.lower()]
        
    if travel_style and travel_style.lower() != "all":
        style_clean = travel_style.lower()
        results = [d for d in results if any(style_clean in s.lower() for s in d["travel_styles"])]
        
    if search_query:
        q = search_query.strip().lower()
        results = [
            d for d in results
            if q in d["name"].lower()
            or q in d["country"].lower()
            or q in d["tagline"].lower()
            or q in d["description"].lower()
            or any(q in a.lower() for a in d["popular_attractions"])
        ]
        
    return results
