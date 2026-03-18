import csv
import os
from statistics import mean

RESULTS_DIR = os.path.expanduser("~/ai4i_assignment/results")

FILES = {
    "Basic": "goal_metrics_basic.csv",
    "House": "goal_metrics_house.csv",
    "Maze": "goal_metrics_maze.csv",
}


def read_csv(path):
    rows = []
    if not os.path.exists(path):
        return rows

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "goal_x": float(row["goal_x"]),
                    "goal_y": float(row["goal_y"]),
                    "exec_time_sec": float(row["exec_time_sec"]),
                    "final_error": float(row["final_error"]),
                    "path_length": float(row["path_length"]),
                    "planned_path_length": float(row["planned_path_length"]),
                    "efficiency_ratio": float(row["efficiency_ratio"]),
                    "recovery_count": float(row["recovery_count"]),
                    "battery_proxy": float(row["battery_proxy"]),
                })
            except Exception:
                continue
    return rows


def summarize(rows):
    if not rows:
        return None

    return {
        "runs": len(rows),
        "avg_time": mean(r["exec_time_sec"] for r in rows),
        "avg_error": mean(r["final_error"] for r in rows),
        "avg_path": mean(r["path_length"] for r in rows),
        "avg_planned": mean(r["planned_path_length"] for r in rows),
        "avg_eff": mean(r["efficiency_ratio"] for r in rows),
        "avg_recovery": mean(r["recovery_count"] for r in rows),
        "avg_battery": mean(r["battery_proxy"] for r in rows),
    }


def main():
    print("\n=== Navigation Performance Comparison ===\n")

    for env_name, filename in FILES.items():
        path = os.path.join(RESULTS_DIR, filename)
        rows = read_csv(path)
        summary = summarize(rows)

        print(f"{env_name} Environment")
        print("-" * 30)

        if summary is None:
            print(f"No valid data found in: {filename}\n")
            continue

        print(f"Runs:                {summary['runs']}")
        print(f"Avg Exec Time (s):   {summary['avg_time']:.2f}")
        print(f"Avg Final Error (m): {summary['avg_error']:.3f}")
        print(f"Avg Path Length (m): {summary['avg_path']:.2f}")
        print(f"Avg Planned Path(m): {summary['avg_planned']:.2f}")
        print(f"Avg Efficiency:      {summary['avg_eff']:.2f}")
        print(f"Avg Recovery Count:  {summary['avg_recovery']:.2f}")
        print(f"Avg Battery Proxy:   {summary['avg_battery']:.2f}")
        print()

    print("Interpretation:")
    print("- More complex environments should usually increase time, path length, and battery use.")
    print("- Final error indicates goal-reaching accuracy.")
    print("- Efficiency may be inflated if planned path is underestimated by /plan timing.\n")


if __name__ == "__main__":
    main()