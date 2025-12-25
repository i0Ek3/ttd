"""
Modern design constants and styling
"""

class ModernStyle:
    """Modern design constants for clean UI"""
    
    # Colors
    COLORS = {
        'primary': '#FF0050',      # TikTok Pink
        'secondary': '#25F4EE',    # TikTok Cyan
        'success': '#34C759',      # Green
        'warning': '#FF9500',      # Orange
        'error': '#FF3B30',        # Red
        'background': '#FFFFFF',   # White
        'surface': '#F2F2F7',      # Light Gray
        'text_primary': '#000000', # Black
        'text_secondary': '#8E8E93', # Gray
        'border': '#C6C6C8'        # Light Border
    }
    
    # Typography
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'heading': ('Segoe UI', 18, 'bold'),
        'body': ('Segoe UI', 14, 'normal'),
        'caption': ('Segoe UI', 12, 'normal'),
        'button': ('Segoe UI', 14, 'normal')
    }
    
    # Spacing
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32
    }
    
    # Border radius
    RADIUS = {
        'small': 6,
        'medium': 10,
        'large': 16,
        'button': 8
    }
    
    # Shadows
    SHADOWS = {
        'light': '0 1px 3px rgba(0,0,0,0.1)',
        'medium': '0 4px 6px rgba(0,0,0,0.1)',
        'heavy': '0 10px 25px rgba(0,0,0,0.15)'
    }

    TEXTBOX_STYLE = {
        'fg_color': 'transparent',
        'border_width': 2,
        'border_color': "#979DA2",
        'corner_radius': 8
    }
    
    @classmethod
    def get_button_style(cls, variant='primary'):
        """Get button styling based on variant"""
        styles = {
            'primary': {
                'fg_color': cls.COLORS['primary'],
                'hover_color': '#E6004A',
                'text_color': 'white',
                'corner_radius': cls.RADIUS['button']
            },
            'secondary': {
                'fg_color': cls.COLORS['secondary'],
                'hover_color': '#1DD1C1',
                'text_color': 'white',
                'corner_radius': cls.RADIUS['button']
            },
            'outline': {
                'fg_color': 'transparent',
                'border_width': 1,
                'border_color': cls.COLORS['border'],
                'text_color': cls.COLORS['text_primary'],
                'corner_radius': cls.RADIUS['button']
            }
        }
        return styles.get(variant, styles['primary'])