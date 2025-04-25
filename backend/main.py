import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from optimizer import optimize_route  # Assuming you have an optimize_route function

# Initialize FastAPI
app = FastAPI()

# Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/optimize")
async def optimize(request: Request):
    try:
        # Receive JSON data
        body = await request.json()
        locations = body.get("locations")

        if not locations or len(locations) < 2:
            return {"error": "At least two locations are required."}

        # Validate and extract coordinates (lat, lng)
        points = [(loc["lat"], loc["lng"]) for loc in locations if "lat" in loc and "lng" in loc]

        if len(points) < 2:
            return {"error": "Invalid location format or missing coordinates."}

        # Call the optimization logic (you need to implement this)
        optimized = optimize_route(points)

        return {"route": optimized}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

@app.post("/save_route")
async def save_route(request: Request):
    try:
        # Receive the optimized route data
        body = await request.json()
        route = body.get("route")

        if not route:
            return {"error": "No route to save."}

        # Save to a JSON-lines file
        with open("saved_routes.jsonl", "a") as f:
            f.write(json.dumps({"route": route}) + "\n")

        return {"status": "saved", "route_length": len(route)}

    except Exception as e:
        return {"error": f"Exception: {str(e)}"}
