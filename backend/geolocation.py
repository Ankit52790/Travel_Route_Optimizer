from opencage.geocoder import OpenCageGeocode
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")

if not OPENCAGE_API_KEY:
    raise ValueError("⚠️ OPENCAGE_API_KEY not found in environment variables!")

# Create geocoder object
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

# Define coordinate fetcher
def get_coordinates(place_name):
    results = geocoder.geocode(place_name)
    if results and len(results):
        return results[0]['geometry']['lat'], results[0]['geometry']['lng']
    raise ValueError(f"Could not find coordinates for '{place_name}'")

# 🧪 Test the function
if __name__ == "__main__":
    lat, lon = get_coordinates("Delhi")
    print(f"Coordinates of Delhi: {lat}, {lon}")
