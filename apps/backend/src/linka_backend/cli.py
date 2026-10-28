"""Local development server entry point."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Run the Linka development API server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    from .main import app

    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
