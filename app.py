
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)

DIRECTIONS = ["North", "East", "South", "West"]

NORMAL_CYCLE = [
    {"North": "GREEN", "South": "GREEN",
     "East": "RED", "West": "RED"},
    {"North": "YELLOW", "South": "YELLOW",
     "East": "RED", "West": "RED"},
    {"North": "RED", "South": "RED",
     "East": "GREEN", "West": "GREEN"},
    {"North": "RED", "South": "RED",
     "East": "YELLOW", "West": "YELLOW"}
]

state = {
    "mode": "normal",
    "emergency_vehicle": None,
    "priority_direction": None,
    "alert": "System online. Normal traffic active.",
    "last_event": "System started",
    "updated_at": datetime.now().strftime("%H:%M:%S"),
    "signals": NORMAL_CYCLE[0].copy(),
    "cycle_index": 0
}


def update_time():
    state["updated_at"] = datetime.now().strftime("%H:%M:%S")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/state", methods=["GET"])
def get_state():
    return jsonify(state)


@app.route("/api/emergency", methods=["POST"])
def emergency():
    data = request.get_json(silent=True) or {}

    vehicle = data.get("vehicle", "Ambulance")
    direction = data.get("direction", "North")

    if vehicle not in ["Ambulance", "Fire Engine", "Police"]:
        return jsonify({"error": "Invalid vehicle"}), 400

    if direction not in DIRECTIONS:
        return jsonify({"error": "Invalid direction"}), 400

    state["mode"] = "emergency"
    state["emergency_vehicle"] = vehicle
    state["priority_direction"] = direction

    # Simulation: give green to the selected approach.
    # All conflicting approaches are set to red.
    state["signals"] = {
        road: "GREEN" if road == direction else "RED"
        for road in DIRECTIONS
    }

    state["alert"] = (
        f"{vehicle} detected from {direction}. "
        "Emergency priority activated."
    )
    state["last_event"] = f"{vehicle}: {direction}"
    update_time()

    return jsonify(state)


@app.route("/api/reset", methods=["POST"])
def reset():
    state["mode"] = "normal"
    state["emergency_vehicle"] = None
    state["priority_direction"] = None
    state["cycle_index"] = 0
    state["signals"] = NORMAL_CYCLE[0].copy()
    state["alert"] = "Normal traffic mode restored."
    state["last_event"] = "System reset"
    update_time()

    return jsonify(state)


@app.route("/api/next-phase", methods=["POST"])
def next_phase():
    if state["mode"] == "emergency":
        return jsonify({
            "error": "Reset emergency mode first."
        }), 409

    state["cycle_index"] = (
        state["cycle_index"] + 1
    ) % len(NORMAL_CYCLE)

    state["signals"] = NORMAL_CYCLE[
        state["cycle_index"]
    ].copy()

    state["alert"] = "Normal traffic phase updated."
    state["last_event"] = "Phase advanced"
    update_time()

    return jsonify(state)


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
