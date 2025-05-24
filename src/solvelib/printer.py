'''Printer utility module.

Provides methods for styled console printing using ANSI escape codes.
Supports colors and styles such as bold and underline.
'''

class Printer:
    '''Utility class for styled console output using ANSI escape codes.'''

    # ANSI color codes
    COLORS = {
        'black': '\033[90m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m'
    }

    # ANSI style codes
    STYLES = {
        'bold': '\033[1m',
        'underline': '\033[4m',
        'reverse': '\033[7m'
    }

    RESET = '\033[0m'

    @classmethod
    def print(cls, msg, color=None, style=None):
        '''Print message with optional color and style.

        Args:
            msg (str): The message to print.
            color (str, optional): The color name ('red', 'green', etc.).
            style (str, optional): The style name ('bold', 'underline', etc.).
        '''
        color_code = cls.COLORS.get(color, '') if color else ''
        style_code = cls.STYLES.get(style, '') if style else ''
        print(f"{style_code}{color_code}{msg}{cls.RESET}")

