import colorsys
from utils.Logger import logger

class C:
    """ANSI escape-code constants and terminal color constructors."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    
    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"
    
    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"
    
    BG_BRIGHT_BLACK   = "\033[100m"
    BG_BRIGHT_RED     = "\033[101m"
    BG_BRIGHT_GREEN   = "\033[102m"
    BG_BRIGHT_YELLOW  = "\033[103m"
    BG_BRIGHT_BLUE    = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN    = "\033[106m"
    BG_BRIGHT_WHITE   = "\033[107m"
    
    def FG_8bit(color_8bit: int) -> str:
        """Return an ANSI 8-bit foreground color escape sequence.

        Args:
            color_8bit: ANSI palette index from 0 through 255.

        Returns:
            Foreground-color escape sequence, or an empty string when invalid.
        """
        if color_8bit < 0 or color_8bit > 255:
            logger.warn("Color out of 8 bit range (0-255)")
            return ""
        return f"\033[38;5;{color_8bit}m"
    
    def BG_8bit(color_8bit: int) -> str:
        """Return an ANSI 8-bit background color escape sequence.

        Args:
            color_8bit: ANSI palette index from 0 through 255.

        Returns:
            Background-color escape sequence, or an empty string when invalid.
        """
        if color_8bit < 0 or color_8bit > 255:
            logger.warn("Color out of 8 bit range (0-255)")
            return ""
        return f"\033[48;5;{color_8bit}m"
    
    def FG_24bit(r: int, b: int, g: int) -> str:
        """Return an ANSI true-color foreground escape sequence.

        Args:
            r: Red channel from 0 through 255.
            b: Blue channel from 0 through 255.
            g: Green channel from 0 through 255.

        Returns:
            Foreground-color escape sequence, or an empty string when invalid.
        """
        if r < 0 or r > 255:
            logger.warn("RED channel out of 8 bit range (0-255)")
            return ""
        if g < 0 or g > 255:
            logger.warn("GREEN channel out of 8 bit range (0-255)")
            return ""
        if b < 0 or b > 255:
            logger.warn("BLUE channel out of 8 bit range (0-255)")
            return ""
        
        return f"\033[38;2;{r};{g};{b}m"
    
    def BG_24bit(r: int, b: int, g: int) -> str:
        """Return an ANSI true-color background escape sequence.

        Args:
            r: Red channel from 0 through 255.
            b: Blue channel from 0 through 255.
            g: Green channel from 0 through 255.

        Returns:
            Background-color escape sequence, or an empty string when invalid.
        """
        if r < 0 or r > 255:
            logger.warn("RED channel out of 8 bit range (0-255)")
            return ""
        if g < 0 or g > 255:
            logger.warn("GREEN channel out of 8 bit range (0-255)")
            return ""
        if b < 0 or b > 255:
            logger.warn("BLUE channel out of 8 bit range (0-255)")
            return ""
        
        return f"\033[48;2;{r};{g};{b}m"


def colorful_battery(percentage: int) -> str:
    """Format battery percentage with an ANSI severity color.

    Args:
        percentage: Battery charge percentage.

    Returns:
        Colorized percentage string with an ANSI reset sequence.
    """
    
    colors = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46]
    index = min(len(colors) - 1, percentage // 10)

    return f"{C.FG_8bit(colors[index])}{percentage}%{C.RESET}"

def colorful_temperature(temp: int) -> str:
    """Format temperature with an ANSI safety color.

    Args:
        temp: Temperature in degrees Celsius.

    Returns:
        Colorized temperature string with an ANSI reset sequence.
    """
    if temp < 82:
        return f"{C.BRIGHT_GREEN}{temp}°C{C.RESET}"
    elif temp < 88:
        return f"{C.BRIGHT_YELLOW}{temp}°C{C.RESET}"
    else:
        return f"{C.BRIGHT_RED}{temp}°C{C.RESET}"

def generate_colors(max_colors):
    """Generate evenly distributed BGR colors.

    Args:
        max_colors: Number of distinct colors to generate.

    Returns:
        List of BGR color tuples.
    """
    colors = []

    for i in range(max_colors):
        h = i / max_colors
        r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)

        colors.append((
        int(b * 255),
        int(g * 255),
        int(r * 255),
        ))

    return colors
