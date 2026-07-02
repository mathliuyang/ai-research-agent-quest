from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "experiment_log.csv"
RESULTS = ROOT / "results"


def load_rows(path):
    with path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        row["mesh_size"] = int(row["mesh_size"])
        row["loss"] = float(row["loss"])
        row["time_s"] = float(row["time_s"])
    return rows


def main():
    rows = load_rows(DATA_PATH)
    RESULTS.mkdir(exist_ok=True)

    by_method = {}
    for row in rows:
        by_method.setdefault(row["method"], []).append(row)

    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["method", "best_loss", "avg_time_s", "runs"])
        for method, items in sorted(by_method.items()):
            best_loss = min(item["loss"] for item in items)
            avg_time = sum(item["time_s"] for item in items) / len(items)
            writer.writerow([method, f"{best_loss:.4f}", f"{avg_time:.2f}", len(items)])

    best = min(rows, key=lambda item: item["loss"])
    (RESULTS / "trend.txt").write_text(
        f"Best method: {best['method']} at mesh_size={best['mesh_size']}, loss={best['loss']:.4f}\n",
        encoding="utf-8",
    )
    print(f"OK read {len(rows)} rows")
    print("OK wrote results/summary.csv")
    print("OK wrote results/trend.txt")


if __name__ == "__main__":
    main()
