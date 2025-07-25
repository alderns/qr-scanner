"""
Accessibility configuration for the QR Scanner application.
"""

# Keyboard Navigation Settings
KEYBOARD_NAVIGATION = {
    'enable_tab_navigation': True,
    'enable_arrow_keys': True,
    'enable_enter_space': True,
    'focus_highlight': True,
    'focus_timeout': 2000,  # milliseconds
}

# Screen Reader Support
SCREEN_READER = {
    'enable_aria_labels': True,
    'enable_descriptions': True,
    'announce_changes': True,
    'announce_timeout': 1000,  # milliseconds
}

# Visual Accessibility
VISUAL_ACCESSIBILITY = {
    'high_contrast_mode': False,
    'large_font_mode': False,
    'color_blind_friendly': True,
    'reduce_motion': False,
    'focus_indicators': True,
}

# Audio Accessibility
AUDIO_ACCESSIBILITY = {
    'enable_sound_feedback': True,
    'enable_voice_announcements': False,
    'sound_volume': 0.5,
    'scan_success_sound': True,
    'scan_error_sound': True,
}

# Input Accessibility
INPUT_ACCESSIBILITY = {
    'enable_voice_input': False,
    'enable_gesture_input': False,
    'enable_eye_tracking': False,
    'input_timeout': 5000,  # milliseconds
}

# Performance Accessibility
PERFORMANCE_ACCESSIBILITY = {
    'reduce_animations': False,
    'simplified_ui': False,
    'auto_save_interval': 30000,  # milliseconds
    'cache_size_limit': 1000,  # items
}

# Keyboard Shortcuts
KEYBOARD_SHORTCUTS = {
    'start_camera': '<Control-s>',
    'stop_camera': '<Control-s>',
    'copy_last_scan': '<Control-c>',
    'clear_history': '<Control-h>',
    'export_history': '<Control-e>',
    'show_help': '<F1>',
    'show_settings': '<F2>',
    'toggle_fullscreen': '<F11>',
    'quit_application': '<Control-q>',
}

# Tooltip Settings
TOOLTIP_SETTINGS = {
    'enable_tooltips': True,
    'tooltip_delay': 500,  # milliseconds
    'tooltip_duration': 3000,  # milliseconds
    'tooltip_position': 'auto',  # auto, above, below, left, right
    'tooltip_style': 'modern',  # modern, classic, minimal
}

# Status Announcements
STATUS_ANNOUNCEMENTS = {
    'announce_scan_success': True,
    'announce_scan_error': True,
    'announce_connection_status': True,
    'announce_loading_complete': True,
    'announce_error_messages': True,
}

# Color Contrast Ratios (WCAG 2.1 AA compliant)
COLOR_CONTRAST = {
    'normal_text': 4.5,  # minimum contrast ratio
    'large_text': 3.0,   # minimum contrast ratio for large text
    'ui_components': 3.0, # minimum contrast ratio for UI components
}

# Focus Management
FOCUS_MANAGEMENT = {
    'restore_focus': True,
    'focus_ring_visible': True,
    'focus_ring_color': '#00a6b6',
    'focus_ring_width': 2,
    'focus_ring_style': 'solid',
}

# Error Handling
ERROR_HANDLING = {
    'show_error_dialogs': True,
    'log_errors': True,
    'announce_errors': True,
    'error_recovery': True,
    'graceful_degradation': True,
}

# Default Accessibility Profile
DEFAULT_ACCESSIBILITY_PROFILE = {
    'name': 'Standard',
    'description': 'Standard accessibility settings for most users',
    'settings': {
        'keyboard_navigation': KEYBOARD_NAVIGATION,
        'screen_reader': SCREEN_READER,
        'visual_accessibility': VISUAL_ACCESSIBILITY,
        'audio_accessibility': AUDIO_ACCESSIBILITY,
        'input_accessibility': INPUT_ACCESSIBILITY,
        'performance_accessibility': PERFORMANCE_ACCESSIBILITY,
        'tooltip_settings': TOOLTIP_SETTINGS,
        'status_announcements': STATUS_ANNOUNCEMENTS,
        'focus_management': FOCUS_MANAGEMENT,
        'error_handling': ERROR_HANDLING,
    }
}

# High Contrast Profile
HIGH_CONTRAST_PROFILE = {
    'name': 'High Contrast',
    'description': 'High contrast settings for users with visual impairments',
    'settings': {
        'keyboard_navigation': KEYBOARD_NAVIGATION,
        'screen_reader': SCREEN_READER,
        'visual_accessibility': {
            **VISUAL_ACCESSIBILITY,
            'high_contrast_mode': True,
            'large_font_mode': True,
        },
        'audio_accessibility': AUDIO_ACCESSIBILITY,
        'input_accessibility': INPUT_ACCESSIBILITY,
        'performance_accessibility': PERFORMANCE_ACCESSIBILITY,
        'tooltip_settings': TOOLTIP_SETTINGS,
        'status_announcements': STATUS_ANNOUNCEMENTS,
        'focus_management': FOCUS_MANAGEMENT,
        'error_handling': ERROR_HANDLING,
    }
}

# Performance Profile
PERFORMANCE_PROFILE = {
    'name': 'Performance',
    'description': 'Optimized settings for users with performance concerns',
    'settings': {
        'keyboard_navigation': KEYBOARD_NAVIGATION,
        'screen_reader': SCREEN_READER,
        'visual_accessibility': VISUAL_ACCESSIBILITY,
        'audio_accessibility': AUDIO_ACCESSIBILITY,
        'input_accessibility': INPUT_ACCESSIBILITY,
        'performance_accessibility': {
            **PERFORMANCE_ACCESSIBILITY,
            'reduce_animations': True,
            'simplified_ui': True,
        },
        'tooltip_settings': TOOLTIP_SETTINGS,
        'status_announcements': STATUS_ANNOUNCEMENTS,
        'focus_management': FOCUS_MANAGEMENT,
        'error_handling': ERROR_HANDLING,
    }
}

# Available Accessibility Profiles
ACCESSIBILITY_PROFILES = {
    'standard': DEFAULT_ACCESSIBILITY_PROFILE,
    'high_contrast': HIGH_CONTRAST_PROFILE,
    'performance': PERFORMANCE_PROFILE,
} 