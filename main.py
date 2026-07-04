import argparse
from scheduler import start_scheduler, run_pipeline


def main():
    """CLI entrypoint for one-off runs or long-running weekly scheduler mode."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["run", "schedule"], default="run")
    args = parser.parse_args()

    if args.mode == "run":
        run_pipeline()

    elif args.mode == "schedule":
        start_scheduler()


if __name__ == "__main__":
    main()