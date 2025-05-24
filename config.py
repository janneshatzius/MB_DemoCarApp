from pathlib import Path
import os



# ------------- Base Directories -----------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" 
ASSETS_DIR = BASE_DIR / "assets"

# ------------- Database -------------------------------

DB_PATH = Path(
    os.getenv(
       "APP_DB_PATH",
       r"\\"
    )
)

# ------------- In-app image assets --------------------

ICON_HOME = ASSETS_DIR / "home-icon.png"
ICON_BACKPAGE = ASSETS_DIR / "back-arrow.png"
ICON_MERCEDES = ASSETS_DIR / "Mercedes-Benz-Logo.png"
APP_ICON_ICO = ASSETS_DIR / "App-Logo.ico"

# ------------ UI defaults -----------------------------

WINDOW_TITLE = "Mercedes Vans Testfahrzeuge"
DEFAULT_WIDTH = "1024"
DEFAULT_HEIGHT = "768"

# ------------ Recommendation source codes -------------

AUTO_SOURCE = 1
MANUAL_SOURCE = 2
