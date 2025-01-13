from geopy.distance import geodesic
from geopy.geocoders import Nominatim

# Function to calculate distance and price
def calculate_price(pickup_location, pickup_floors, dropoff_location, dropoff_floors):
    geolocator = Nominatim(user_agent="mo_van_and_man", timeout=10)
    try:
        pickup_coords = geolocator.geocode(pickup_location)
        dropoff_coords = geolocator.geocode(dropoff_location)
    except Exception as e:
        return None, "Unable to connect to the geocoding service."

    if not pickup_coords or not dropoff_coords:
        return None, "Invalid locations entered."

    distance = geodesic(
        (pickup_coords.latitude, pickup_coords.longitude),
        (dropoff_coords.latitude, dropoff_coords.longitude)
    ).miles

    base_price = distance * 1.5
    floor_price = (pickup_floors + dropoff_floors) * 10
    total_price = base_price + floor_price
    return total_price, None
