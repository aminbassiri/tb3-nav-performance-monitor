import csv
import os
from flask import Flask, render_template_string

app = Flask(__name__)

RESULTS_DIR = os.path.expanduser("~/ai4i_assignment/results")

FILES = {
    "Basic": "goal_metrics_basic.csv",
    "House": "goal_metrics_house.csv",
    "Maze": "goal_metrics_maze.csv",
}

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Navigation Performance Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; background: #f7f7f7; }
        h1, h2 { color: #222; }
        .card { background: white; padding: 16px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        table { border-collapse: collapse; width: 100%; background: white; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: center; }
        th { background: #efefef; }
        .muted { color: #666; }
    </style>
</head>
<body>
    <h1>Navigation Performance Dashboard</h1>
    <p class="muted">Auto-refresh every 5 seconds</p>

    {% for env_name, env_data in data.items() %}
    <div class="card">
        <h2>{{ env_name }} Environment</h2>

        {% if env_data["latest"] %}
            <p><strong>Latest Goal:</strong> ({{ env_data["latest"]["goal_x"] }}, {{ env_data["latest"]["goal_y"] }})</p>
            <p><strong>Execution Time:</strong> {{ env_data["latest"]["exec_time_sec"] }} s</p>
            <p><strong>Final Error:</strong> {{ env_data["latest"]["final_error"] }} m</p>
            <p><strong>Path Length:</strong> {{ env_data["latest"]["path_length"] }} m</p>
            <p><strong>Planned Path:</strong> {{ env_data["latest"]["planned_path_length"] }} m</p>
            <p><strong>Efficiency:</strong> {{ env_data["latest"]["efficiency_ratio"] }}</p>
            <p><strong>Recovery Count:</strong> {{ env_data["latest"]["recovery_count"] }}</p>
            <p><strong>Battery Proxy:</strong> {{ env_data["latest"]["battery_proxy"] }}</p>
        {% else %}
            <p>No data yet.</p>
        {% endif %}
    </div>
    {% endfor %}

    <div class="card">
        <h2>Recent Runs</h2>
        <table>
            <tr>
                <th>Environment</th>
                <th>Goal X</th>
                <th>Goal Y</th>
                <th>Exec Time</th>
                <th>Error</th>
                <th>Path</th>
                <th>Planned</th>
                <th>Efficiency</th>
                <th>Recovery</th>
                <th>Battery</th>
            </tr>
            {% for row in recent_rows %}
            <tr>
                <td>{{ row["environment"] }}</td>
                <td>{{ row["goal_x"] }}</td>
                <td>{{ row["goal_y"] }}</td>
                <td>{{ row["exec_time_sec"] }}</td>
                <td>{{ row["final_error"] }}</td>
                <td>{{ row["path_length"] }}</td>
                <td>{{ row["planned_path_length"] }}</td>
                <td>{{ row["efficiency_ratio"] }}</td>
                <td>{{ row["recovery_count"] }}</td>
                <td>{{ row["battery_proxy"] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""


def read_rows(path, env_name):
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
    data = {}
    recent_rows = []

    for env_name, filename in FILES.items():
        path = os.path.join(RESULTS_DIR, filename)
        rows = read_rows(path, env_name)
        latest = rows[-1] if rows else None
        data[env_name] = {"latest": latest}
        recent_rows.extend(rows[-3:])

    return render_template_string(HTML, data=data, recent_rows=recent_rows)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)