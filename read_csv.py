import argparse
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Read a CSV file and save it as a new CSV file."
    )
    parser.add_argument("input_csv", help="Path to the input CSV file")
    parser.add_argument(
        "output_csv",
        nargs="?",
        default="output.csv",
        help="Path to the output CSV file (default: output.csv)",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv, header=None)
    df.to_csv(args.output_csv, index=False, header=False)
    print(f"Saved {len(df)} rows to {args.output_csv}")


if __name__ == "__main__":
    main()