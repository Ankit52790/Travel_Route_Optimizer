import sys
import os
import json
import csv
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from optimizer import optimize_route

# Allow local module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure the save folder exists
SAVE_FOLDER = "./saved_routes"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.post("/optimize")
async def optimize(request: Request):
    try:
        body = await request.json()
        locations = body.get("locations")

        if not locations or len(locations) < 2:
            return {"error": "At least two locations are required."}

        points = [(loc["lat"], loc["lng"]) for loc in locations if "lat" in loc and "lng" in loc]
        if len(points) < 2:
            return {"error": "Invalid location format or missing coordinates."}

        optimized = optimize_route(points)
        return {"route": optimized}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

@app.post("/save_route")
def save_route(data: dict):
    route = data.get("route")
    route_name = data.get("route_name", "Untitled Route")

    if not route or not isinstance(route, list):
        raise HTTPException(status_code=400, detail="Invalid route data.")

    with open("saved_routes.jsonl", "a") as f:
        entry = {"name": route_name, "route": route}
        f.write(json.dumps(entry) + "\n")

    return {"status": "saved", "name": route_name}

@app.get("/get_routes")
def get_routes():
    routes = []
    try:
        with open("saved_routes.jsonl", "r") as f:
            for line in f:
                routes.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    return {"routes": routes}



        # Unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        json_filename = f"route_{timestamp}.json"
        csv_filename = f"route_{timestamp}.csv"

        # Save as JSON
        with open(os.path.join(SAVE_FOLDER, json_filename), "w") as jf:
            json.dump(route, jf)

        # Save as CSV
        with open(os.path.join(SAVE_FOLDER, csv_filename), "w", newline="") as cf:
            writer = csv.writer(cf)
            writer.writerow(["Latitude", "Longitude"])
            for lat, lng in route:
                writer.writerow([lat, lng])

        return {
            "status": "saved",
            "json_file": json_filename,
            "csv_file": csv_filename,
            "route_length": len(route)
        }

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}
