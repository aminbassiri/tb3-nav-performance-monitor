import csv
import os
from flask import Flask, render_template_string

# Create Flask app
app = Flask(__name__)

# Directory where CSV files are stored
RESULTS_DIR = os.path.expanduser("~/ai4i_assignment/results")

# Environment → CSV mapping
FILES = {
    "Basic": "goal_metrics_basic.csv",
    "House": "goal_metrics_house.csv",
    "Maze": "goal_metrics_maze.csv",
}

# HTML template for dashboard
HTML = """ ... (keep your same HTML unchanged) ... """


def read_rows(path, env_name):
    """
    Reads CSV file and attaches environment label to each row.
    """
    rows = []
    if not os.path.exists(path):
        return rows

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "environment": env_name,
                    "goal_x": row["goal_x"],
                    "goal_y": row["goal_y"],
                    "exec_time_sec": row["exec_time_sec"],
                    "final_error": row["final_error"],
                    "path_length": row["path_length"],
                    "planned_path_length": row["planned_path_length"],
                    "efficiency_ratio": row["efficiency_ratio"],
                    "recovery_count": row["recovery_count"],
                    "battery_proxy": row["battery_proxy"],
                })
            except Exception:
                continue
    return rows


@app.route("/")
def index():
    """
    Main dashboard page.
    Shows latest results per environment + recent runs.
    """
    data = {}
    recent_rows = []

    for env_name, filename in FILES.items():
        path = os.path.join(RESULTS_DIR, filename)
        rows = read_rows(path, env_name)

        latest = rows[-1] if rows else None
        data[env_name] = {"latest": latest}

        # Keep last 3 runs
        recent_rows.extend(rows[-3:])

    return render_template_string(HTML, data=data, recent_rows=recent_rows)


if __name__ == "__main__":
    # Run server accessible from host machine
    app.run(host="0.0.0.0", port=5000, debug=False)
