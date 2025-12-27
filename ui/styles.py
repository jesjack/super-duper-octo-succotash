# Fluent Design Theme (WinUI 3 inspired) - Refined

# Brand Colors - Indigo/Blue Focus
COLOR_PRIMARY = "#4338CA"      # Indigo 700 - Deep, Professional Blue/Purple
COLOR_PRIMARY_HOVER = "#3730A3" # Indigo 800
COLOR_SECONDARY = "#F1F5F9"    # Slate 100 - Light background for secondary actions
COLOR_SECONDARY_HOVER = "#E2E8F0" # Slate 200

# Functional Colors
COLOR_SUCCESS = "#15803D"      # Green 700 - Explicit Success
COLOR_SUCCESS_HOVER = "#166534"
COLOR_DESTRUCTIVE = "#DC2626"  # Red 600 - Explicit Danger
COLOR_DESTRUCTIVE_HOVER = "#B91C1C"
COLOR_DANGER = COLOR_DESTRUCTIVE # Alias for backward compatibility
COLOR_DANGER_HOVER = COLOR_DESTRUCTIVE_HOVER
COLOR_WARNING = "#B45309"      # Amber 700

# UI Colors (Light Mode)
COLOR_BACKGROUND = "#F8FAFC"   # Slate 50 (Very light cool gray)
COLOR_SURFACE = "#FFFFFF"      # Pure White
COLOR_SURFACE_ALT = "#F1F5F9"  # Secondary Surface
COLOR_TEXT = "#0F172A"         # Slate 900 (High contrast)
COLOR_TEXT_LIGHT = "#64748B"   # Slate 500
COLOR_BORDER = "#E2E8F0"       # Slate 200
COLOR_FOCUS = COLOR_PRIMARY    # Focus ring color

# Status Colors
STATUS_OFFLINE = "#EF4444"
STATUS_IDLE = "#94A3B8"
STATUS_CONNECTED = "#10B981"
STATUS_SUSPICIOUS = "#F59E0B"

# Fonts
# Start with Segoe UI Variable if available (Win 11), fallback to Segoe UI
FONT_FAMILY = "Segoe UI Variable Display"
FONT_FAMILY_TEXT = "Segoe UI Variable Text"

# Fluent Typography Hierarchy
FONT_HEADER = (FONT_FAMILY, 20, "bold")      # Panel Titles
FONT_SUBHEADER = (FONT_FAMILY, 16, "bold")   # Section Headers
FONT_BODY = (FONT_FAMILY_TEXT, 13)           # Standard Content
FONT_BODY_BOLD = (FONT_FAMILY_TEXT, 13, "bold")
FONT_BIG_TOTAL = (FONT_FAMILY, 48, "bold")   # Hero Text
FONT_SMALL = (FONT_FAMILY_TEXT, 11)          # Captions

# Dimensions
CORNER_RADIUS = 6           # Slightly tighter for buttons
CORNER_RADIUS_CARD = 10     # Softer for containers
BUTTON_HEIGHT = 42          # Standard button
INPUT_HEIGHT = 40
