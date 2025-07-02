from app import app
from waitress import serve
import os
import argparse
import config

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Start the Flask API server.")
  parser.add_argument("--debug", action="store_true", help="Run in debug mode")
  args = parser.parse_args()
  if args.debug:
    print(f">>> Start Flask on port: {config.DEFAULT_PORT} - Development")
    if config.IS_DEV:
      print(f">>> DEV Mode is enable, send mail will print to console")
    app.run(host="0.0.0.0", port=config.DEFAULT_PORT)
  else:
    print(f">>> Start Flask on port: {config.DEFAULT_PORT} - Production")
    serve(app, host="0.0.0.0", port=config.DEFAULT_PORT)