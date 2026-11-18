"""
nearby_service.py
Real-time Nearby Medical Shops & Hospitals Service for VAIDYARA.
Queries OpenStreetMap / Overpass API using the user's actual GPS coordinates,
classifies facilities (Pharmacies, Government Hospitals, Private Hospitals, Clinics, Emergency 24/7),
calculates exact Haversine distances, and provides formatted address, contact, and directions data.
"""
import math
import json
import urllib.request
import urllib.parse
from datetime import datetime

OVERPASS_MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
]

# In-memory cache for recent coordinate grids: (round(lat, 2), round(lon, 2), radius) -> (timestamp, data)
_PLACES_CACHE = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate geodesic distance in meters between two GPS coordinates using the Haversine formula.
    """
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def format_distance(dist_meters):
    """Format distance into human-readable string (e.g. '350 m' or '1.4 km')."""
    if dist_meters < 1000:
        return f"{int(round(dist_meters))} m"
    else:
        return f"{dist_meters / 1000:.1f} km"

def classify_place(tags):
    """
    Classify an OSM place into one of the required clinical categories:
    - pharmacy: Medical Shop / Pharmacy
    - govt_hospital: Government Hospital
    - private_hospital: Private Hospital
    - multispecialty_hospital: Multispecialty Hospital
    - emergency_hospital: Emergency Hospital (24/7)
    - general_hospital: General Hospital
    - clinic: Clinic & Healthcare Centre
    """
    amenity = tags.get("amenity", "").lower()
    healthcare = tags.get("healthcare", "").lower()
    name = (tags.get("name") or tags.get("name:en") or "").lower()
    operator_type = tags.get("operator:type", "").lower()
    operator = tags.get("operator", "").lower()
    emergency = tags.get("emergency", "").lower()

    # 1. Medical shop / Pharmacy
    if (amenity == "pharmacy" or healthcare == "pharmacy" or
        "pharmacy" in name or "chemist" in name or "medical store" in name or
        "druggist" in name or "medplus" in name or "apollo pharmacy" in name):
        return {
            "category_id": "pharmacy",
            "category_label": "Medical Shop / Pharmacy",
            "type_group": "pharmacy",
            "badge_color": "#10b981", # green
            "icon": "💊"
        }

    # 2. Clinic & Healthcare Centre
    if (amenity in ("clinic", "doctors") or healthcare in ("clinic", "doctor", "centre") or
        "clinic" in name or "dispensary" in name or "health centre" in name or "health center" in name):
        return {
            "category_id": "clinic",
            "category_label": "Clinic & Healthcare Centre",
            "type_group": "clinic",
            "badge_color": "#06b6d4", # cyan
            "icon": "🩺"
        }

    # 3. Hospitals & Emergency Facilities
    if (amenity == "hospital" or healthcare == "hospital" or "hospital" in name):
        if emergency == "yes" or "emergency" in name or "casualty" in name or "trauma" in name:
            return {
                "category_id": "emergency_hospital",
                "category_label": "Emergency Hospital (24/7)",
                "type_group": "hospital",
                "badge_color": "#ef4444", # red
                "icon": "🚨"
            }
        elif (operator_type in ("government", "public") or "govt" in name or
              "district" in name or "civil" in name or "government" in operator or
              "aiims" in name or "primary health centre" in name):
            return {
                "category_id": "govt_hospital",
                "category_label": "Government Hospital",
                "type_group": "hospital",
                "badge_color": "#2563eb", # blue
                "icon": "🏛️"
            }
        elif ("multispecialty" in name or "multi-speciality" in name or "super specialty" in name or "superspeciality" in name):
            return {
                "category_id": "multispecialty_hospital",
                "category_label": "Multispecialty Hospital",
                "type_group": "hospital",
                "badge_color": "#8b5cf6", # purple
                "icon": "🏥"
            }
        elif (operator_type == "private" or "pvt" in name or "apollo" in name or "fortis" in name or "manipal" in name):
            return {
                "category_id": "private_hospital",
                "category_label": "Private Hospital",
                "type_group": "hospital",
                "badge_color": "#f59e0b", # amber
                "icon": "🏥"
            }
        else:
            return {
                "category_id": "general_hospital",
                "category_label": "General Hospital",
                "type_group": "hospital",
                "badge_color": "#dc2626", # dark red
                "icon": "🏥"
            }

    # Generic healthcare fallback
    return {
        "category_id": "general_hospital",
        "category_label": "Healthcare Centre",
        "type_group": "hospital",
        "badge_color": "#0284c7",
        "icon": "⚕️"
    }

def format_address(tags):
    """Assemble a clean, accurate address string from OSM address tags."""
    addr_parts = []
    
    # House number / building
    if tags.get("addr:housenumber"):
        addr_parts.append(tags["addr:housenumber"])
    if tags.get("addr:housename"):
        addr_parts.append(tags["addr:housename"])
        
    # Street / Road
    if tags.get("addr:street"):
        addr_parts.append(tags["addr:street"])
    elif tags.get("addr:road"):
        addr_parts.append(tags["addr:road"])
        
    # Suburb / Locality / Sector
    if tags.get("addr:suburb"):
        addr_parts.append(tags["addr:suburb"])
    elif tags.get("addr:neighbourhood"):
        addr_parts.append(tags["addr:neighbourhood"])
        
    # City / Town
    if tags.get("addr:city"):
        addr_parts.append(tags["addr:city"])
    elif tags.get("addr:town"):
        addr_parts.append(tags["addr:town"])
        
    # Postcode / State
    if tags.get("addr:postcode"):
        addr_parts.append(tags["addr:postcode"])
        
    if addr_parts:
        return ", ".join(addr_parts)
    elif tags.get("addr:full"):
        return tags["addr:full"]
    else:
        # Fallback to local landmark reference
        name = tags.get("name", "")
        return f"Near {name}, Local Medical Zone" if name else "Local Medical Zone"

def query_overpass(lat, lon, radius=3000):
    """
    Build Overpass QL query and fetch nearby pharmacies, hospitals, and clinics.
    Returns raw JSON response or None on error.
    """
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="pharmacy"](around:{radius}, {lat}, {lon});
      way["amenity"="pharmacy"](around:{radius}, {lat}, {lon});
      node["healthcare"="pharmacy"](around:{radius}, {lat}, {lon});
      node["amenity"="hospital"](around:{radius}, {lat}, {lon});
      way["amenity"="hospital"](around:{radius}, {lat}, {lon});
      node["healthcare"="hospital"](around:{radius}, {lat}, {lon});
      node["amenity"="clinic"](around:{radius}, {lat}, {lon});
      way["amenity"="clinic"](around:{radius}, {lat}, {lon});
      node["amenity"="doctors"](around:{radius}, {lat}, {lon});
      node["healthcare"="clinic"](around:{radius}, {lat}, {lon});
    );
    out center body;
    """

    encoded_data = urllib.parse.urlencode({"data": query.strip()}).encode("utf-8")
    
    for mirror_url in OVERPASS_MIRRORS:
        try:
            req = urllib.request.Request(
                mirror_url,
                data=encoded_data,
                headers={"User-Agent": "VAIDYARA-Nearby-Health/2.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and "elements" in data:
                    return data
        except Exception:
            continue
            
    return None

def parse_elements(elements, user_lat, user_lon):
    """
    Parse raw OSM elements into normalized, structured healthcare places.
    """
    places = []
    seen_coords = set()

    for el in elements:
        tags = el.get("tags", {})
        if not tags:
            continue
            
        # Get coordinates: node has 'lat'/'lon', way has 'center'
        lat = el.get("lat") or (el.get("center", {}).get("lat"))
        lon = el.get("lon") or (el.get("center", {}).get("lon"))
        
        if lat is None or lon is None:
            continue
            
        coord_key = (round(lat, 5), round(lon, 5))
        if coord_key in seen_coords:
            continue
        seen_coords.add(coord_key)

        # Name
        name = tags.get("name") or tags.get("name:en")
        if not name:
            amenity = tags.get("amenity", "")
            if amenity == "pharmacy":
                name = "Local Medical & Pharmacy Store"
            elif amenity == "hospital":
                name = "Community Healthcare Hospital"
            elif amenity == "clinic":
                name = "Primary Care Clinic"
            else:
                name = "Healthcare Centre"

        # Classification
        classification = classify_place(tags)
        
        # Distance calculation
        dist_meters = haversine_distance(user_lat, user_lon, lat, lon)
        dist_str = format_distance(dist_meters)

        # Address
        address = format_address(tags)

        # Contact phone
        phone = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile") or ""

        # Opening hours & open status
        opening_hours = tags.get("opening_hours") or ""
        is_open_24_7 = opening_hours == "24/7" or tags.get("emergency") == "yes" or classification["category_id"] == "emergency_hospital"

        # Website
        website = tags.get("website") or tags.get("contact:website") or ""

        # Google Maps navigation URL starting from exact user coordinates to facility
        dest_enc = urllib.parse.quote(name)
        directions_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat:.6f},{user_lon:.6f}&destination={lat:.6f},{lon:.6f}&destination_place_id={dest_enc}"

        places.append({
            "id": el.get("id"),
            "name": name,
            "lat": lat,
            "lon": lon,
            "category_id": classification["category_id"],
            "category_label": classification["category_label"],
            "type_group": classification["type_group"],
            "badge_color": classification["badge_color"],
            "icon": classification["icon"],
            "address": address,
            "distance_meters": dist_meters,
            "distance_str": dist_str,
            "phone": phone,
            "opening_hours": opening_hours or ("24/7 Service" if is_open_24_7 else "Business hours on call"),
            "is_24_7": is_open_24_7,
            "emergency_service": is_open_24_7 or tags.get("emergency") == "yes",
            "website": website,
            "directions_url": directions_url
        })

    # Sort strictly by distance (closest first)
    places.sort(key=lambda p: p["distance_meters"])
    return places

def get_nearby_places(lat, lon, radius=3000, category=None):
    """
    Main entrypoint for fetching nearby healthcare facilities.
    Checks memory cache first, queries Overpass API, and returns structured result.
    """
    try:
        lat = float(lat)
        lon = float(lon)
        radius = int(radius)
    except (ValueError, TypeError):
        return {"success": False, "error": "Invalid GPS coordinates or radius provided.", "places": []}

    cache_key = (round(lat, 2), round(lon, 2), radius)
    now = datetime.now().timestamp()
    
    if cache_key in _PLACES_CACHE:
        cache_time, cached_data = _PLACES_CACHE[cache_key]
        if now - cache_time < CACHE_TTL_SECONDS:
            filtered = filter_places(cached_data, category)
            return {
                "success": True,
                "user_location": {"lat": lat, "lon": lon},
                "radius": radius,
                "total_count": len(filtered),
                "places": filtered,
                "cached": True
            }

    raw_data = query_overpass(lat, lon, radius)
    if not raw_data or not raw_data.get("elements"):
        return {
            "success": True,
            "user_location": {"lat": lat, "lon": lon},
            "radius": radius,
            "total_count": 0,
            "places": [],
            "message": "No healthcare facilities found within the selected radius. Try expanding the search radius."
        }

    parsed = parse_elements(raw_data["elements"], lat, lon)
    _PLACES_CACHE[cache_key] = (now, parsed)
    
    filtered = filter_places(parsed, category)
    return {
        "success": True,
        "user_location": {"lat": lat, "lon": lon},
        "radius": radius,
        "total_count": len(filtered),
        "places": filtered,
        "cached": False
    }

def filter_places(places, category=None):
    """Filter list of places by category_id or type_group."""
    if not category or category == "all":
        return places
    cat_lower = category.lower().strip()
    return [p for p in places if p["category_id"] == cat_lower or p["type_group"] == cat_lower]
