# Other Imports
import os
from dotenv import load_dotenv
from utils import errhandler, syshandler

# Loading Environment Variables
load_dotenv()

try:
    # App Factory Package
    from website import create_app

    # Accessor Instance
    app = create_app(FLASK_MODE=os.getenv("FLASK_MODE"))

    # Entry Point
    if __name__ == "__main__":
        app.run()

# Handling Exceptions
except Exception as e:
    errhandler(e, log="main", path="server")

# Handling Successful Server Startups
else:
    syshandler("Application Server Operated Successfully. Shutting Down Now", log="main", path="server")
