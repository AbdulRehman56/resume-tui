# serve_app.py
from pathlib import Path
from textual_serve.server import Server

# Define the command to run your main TUI application
# Assumes main.py is in the same directory
main_app_script = Path(__file__).parent / "main.py"
command = f"python {main_app_script}"

# Create the server instance, telling it how to run your app
server = Server(command=command, title="Abdul Rehman Resume TUI")

# Start serving the application
# It will typically be available at http://localhost:8000
# Check the terminal output for the exact URL
if __name__ == "__main__":
    print(f"Serving Textual app command: {command}")
    print("Visit the URL provided below in your web browser.")
    server.serve()