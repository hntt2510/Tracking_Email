from app import app
from waitress import serve
import os
import argparse

PORT = int(os.getenv("DEFAULT_PORT", 5000))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Start the Flask API server.")
  parser.add_argument("--debug", action="store_true", help="Run in debug mode")
  args = parser.parse_args()
  if args.debug:
    print(f">>> Start Flask on port: {PORT} - Development")
    app.run(host="0.0.0.0", port=PORT)
  else:
    print(f">>> Start Flask on port: {PORT} - Production")
    serve(app, host="0.0.0.0", port=PORT)