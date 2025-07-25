"""
Theme and styling configuration for the QR Scanner application.
"""

# Modern Theme Colors (Custom Design)
THEME_COLORS = {
    'primary': '#00a6b6',      # Custom Teal
    'primary_text': '#ffffff', # White text on primary
    'secondary': '#606060',    # Dark Gray
    'secondary_light': '#c2c2c2', # Light Gray
    'accent': '#ea4335',       # Red
    'success': '#34a853',      # Green
    'warning': '#fbbc04',      # Yellow
    'error': '#ea4335',        # Red
    'info': '#4285f4',         # Blue
    'background': '#f0f2f5',   # Light Gray
    'surface': '#ffffff',      # White
    'text': '#202124',         # Dark Gray
    'text_secondary': '#5f6368', # Medium Gray
    'border': '#dadce0',       # Light Border
    'hover': '#f8f9fa',        # Hover State
    'disabled': '#9aa0a6',     # Disabled State
    'shadow': '#00000020',     # Shadow Color
    # Enhanced hover colors for different button types
    'primary_hover': '#00c4d6',
    'warning_hover': '#ffd54f',
    'success_hover': '#4caf50',
    'secondary_hover': '#757575',
    'error_hover': '#f44336'
}

# Dark Theme Colors (for future dark mode support)
DARK_THEME_COLORS = {
    'primary': '#8ab4f8',
    'secondary': '#81c995',
    'accent': '#f28b82',
    'success': '#81c995',
    'warning': '#fdd663',
    'error': '#f28b82',
    'info': '#aecbfa',
    'background': '#202124',
    'surface': '#303134',
    'text': '#e8eaed',
    'text_secondary': '#9aa0a6',
    'border': '#5f6368',
    'hover': '#3c4043',
    'disabled': '#5f6368',
    'shadow': '#00000040',
}

# Font Settings
FONT_FAMILY = 'Segoe UI'
FONT_FAMILY_FALLBACK = ['Arial', 'Helvetica', 'sans-serif']

# Font Sizes
TITLE_FONT = (FONT_FAMILY, 24, 'bold')
HEADER_FONT = (FONT_FAMILY, 16, 'bold')
SUBTITLE_FONT = (FONT_FAMILY, 14, 'bold')
NORMAL_FONT = (FONT_FAMILY, 10)
SMALL_FONT = (FONT_FAMILY, 9)
TINY_FONT = (FONT_FAMILY, 8)

# Spacing and Layout
BUTTON_PADDING = 10
SECTION_PADDING = 15
BORDER_RADIUS = 8
SHADOW_OFFSET = 2
MARGIN_SMALL = 5
MARGIN_MEDIUM = 10
MARGIN_LARGE = 20

# Component Styles
BUTTON_STYLES = {
    'primary': {
        'bg': THEME_COLORS['primary'],
        'fg': THEME_COLORS['primary_text'],
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': BUTTON_PADDING,
        'pady': 8,
        'cursor': 'hand2'
    },
    'secondary': {
        'bg': THEME_COLORS['secondary'],
        'fg': THEME_COLORS['primary_text'],
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': BUTTON_PADDING,
        'pady': 8,
        'cursor': 'hand2'
    },
    'secondary_light': {
        'bg': THEME_COLORS['secondary_light'],
        'fg': THEME_COLORS['text'],
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': BUTTON_PADDING,
        'pady': 8,
        'cursor': 'hand2'
    },
    'warning': {
        'bg': THEME_COLORS['warning'],
        'fg': 'white',
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': BUTTON_PADDING,
        'pady': 8,
        'cursor': 'hand2'
    },
    'error': {
        'bg': THEME_COLORS['error'],
        'fg': 'white',
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': BUTTON_PADDING,
        'pady': 8,
        'cursor': 'hand2'
    }
}

# Status Colors
STATUS_COLORS = {
    'success': THEME_COLORS['success'],
    'warning': THEME_COLORS['warning'],
    'error': THEME_COLORS['error'],
    'neutral': THEME_COLORS['secondary'],
    'info': THEME_COLORS['primary']
}

# Animation Settings
ANIMATION_DURATION = 200  # milliseconds
HOVER_DELAY = 100  # milliseconds
TRANSITION_DURATION = 150  # milliseconds 