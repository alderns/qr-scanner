THEME_COLORS = {
    'primary': '#00a6b6',
    'primary_text': '#ffffff',
    'secondary': '#606060',
    'secondary_light': '#c2c2c2',
    'accent': '#ea4335',
    'success': '#34a853',
    'warning': '#fbbc04',
    'error': '#ea4335',
    'info': '#4285f4',
    'background': '#f0f2f5',
    'surface': '#ffffff',
    'text': '#202124',
    'text_secondary': '#5f6368',
    'border': '#e8eaed',
    'hover': '#f8f9fa',
    'disabled': '#9aa0a6',
    'shadow': '#00000020',
    'primary_hover': '#00c4d6',
    'warning_hover': '#ffd54f',
    'success_hover': '#4caf50',
    'secondary_hover': '#757575',
    'error_hover': '#f44336'
}

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

FONT_FAMILY = 'Segoe UI'
FONT_FAMILY_FALLBACK = ['Arial', 'Helvetica', 'sans-serif']

TITLE_FONT = (FONT_FAMILY, 24, 'bold')
HEADER_FONT = (FONT_FAMILY, 16, 'bold')
SUBTITLE_FONT = (FONT_FAMILY, 14, 'bold')
NORMAL_FONT = (FONT_FAMILY, 10)
SMALL_FONT = (FONT_FAMILY, 9)
TINY_FONT = (FONT_FAMILY, 8)

# Comprehensive spacing system for consistent padding and margins
SPACING = {
    # Tiny spacing for tight layouts
    'xs': 2,
    # Small spacing for compact elements
    'sm': 4,
    # Medium spacing for standard elements
    'md': 8,
    # Large spacing for sections
    'lg': 12,
    # Extra large spacing for major sections
    'xl': 16,
    # Double extra large for page-level spacing
    'xxl': 24,
    # Triple extra large for major page sections
    'xxxl': 32
}



# Component-specific spacing
COMPONENT_SPACING = {
    # Card spacing
    'card_padding': SPACING['xl'],
    'card_margin': SPACING['lg'],
    'card_inner_padding': SPACING['md'],
    
    # Button spacing
    'button_padding_x': SPACING['lg'],
    'button_padding_y': SPACING['md'],
    'button_margin': SPACING['sm'],
    
    # Form spacing
    'form_field_margin': SPACING['md'],
    'form_label_margin': SPACING['sm'],
    'form_section_margin': SPACING['xl'],
    
    # List spacing
    'list_item_padding': SPACING['md'],
    'list_section_margin': SPACING['lg'],
    
    # Tab spacing
    'tab_padding': SPACING['lg'],
    'tab_content_margin': SPACING['xl'],
    
    # Status bar spacing
    'status_padding': SPACING['md'],
    'status_margin': SPACING['sm'],
    
    # Header spacing
    'header_padding': SPACING['xl'],
    'header_margin': SPACING['lg'],
    
    # Content spacing
    'content_padding': SPACING['xl'],
    'content_margin': SPACING['lg'],
    
    # Video frame spacing
    'video_padding': SPACING['lg'],
    'video_margin': SPACING['md'],
    
    # Text area spacing
    'text_padding': SPACING['md'],
    'text_margin': SPACING['sm'],
    
    # Entry field spacing
    'entry_padding': SPACING['md'],
    'entry_margin': SPACING['sm'],
    
    # Treeview spacing
    'tree_padding': SPACING['sm'],
    'tree_margin': SPACING['md']
}

BORDER_RADIUS = 8
SHADOW_OFFSET = 2

BUTTON_STYLES = {
    'primary': {
        'bg': THEME_COLORS['primary'],
        'fg': THEME_COLORS['primary_text'],
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    },
    'secondary': {
        'bg': THEME_COLORS['secondary'],
        'fg': THEME_COLORS['primary_text'],
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    },
    'secondary_light': {
        'bg': THEME_COLORS['secondary_light'],
        'fg': THEME_COLORS['text'],
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    },
    'success': {
        'bg': THEME_COLORS['success'],
        'fg': 'white',
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    },
    'warning': {
        'bg': THEME_COLORS['warning'],
        'fg': 'white',
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    },
    'error': {
        'bg': THEME_COLORS['error'],
        'fg': 'white',
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    },
    'info': {
        'bg': THEME_COLORS['info'],
        'fg': 'white',
        'font': NORMAL_FONT,
        'relief': 'flat',
        'borderwidth': 0,
        'padx': COMPONENT_SPACING['button_padding_x'],
        'pady': COMPONENT_SPACING['button_padding_y'],
        'cursor': 'hand2'
    }
}

STATUS_COLORS = {
    'success': THEME_COLORS['success'],
    'warning': THEME_COLORS['warning'],
    'error': THEME_COLORS['error'],
    'neutral': THEME_COLORS['secondary'],
    'info': THEME_COLORS['primary']
}

ANIMATION_DURATION = 200
HOVER_DELAY = 100
TRANSITION_DURATION = 150 