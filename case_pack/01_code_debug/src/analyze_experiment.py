from pathlib import Path
import csv


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "experiment_log.csv"
RESULTS = ROOT / "results"


def load_rows(path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    rows = load_rows(DATA_PATH)

    # Intentional demo bug:
    # 1. results directory is not created.
    # 2. loss/time_s are strings, so min and average can be wrong or fail later.
    by_method = {}
    for row in rows:
        method = row["method"]
        by_method.setdefault(method, []).append(row)

    with (RESULTS / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["method", "best_loss", "avg_time_s", "runs"])
        for method, items in by_method.items():
            best_loss = min(item["loss"] for item in items)
            avg_time = sum(item["time_s"] for item in items) / len(items)
            writer.writerow([method, best_loss, avg_time, len(items)])

    best = min(rows, key=lambda item: item["loss"])
    (RESULTS / "trend.txt").write_text(
        f"Best method: {best['method']} at mesh_size={best['mesh_size']}, loss={best['loss']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
