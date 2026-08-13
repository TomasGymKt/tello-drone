import colorsys
from utils.Logger import logger

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    
    FG_BLACK   = "\033[30m"
    FG_RED     = "\033[31m"
    FG_GREEN   = "\033[32m"
    FG_YELLOW  = "\033[33m"
    FG_BLUE    = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN    = "\033[36m"
    FG_WHITE   = "\033[37m"
    
    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"
    
    FG_BRIGHT_BLACK   = "\033[90m"
    FG_BRIGHT_RED     = "\033[91m"
    FG_BRIGHT_GREEN   = "\033[92m"
    FG_BRIGHT_YELLOW  = "\033[93m"
    FG_BRIGHT_BLUE    = "\033[94m"
    FG_BRIGHT_MAGENTA = "\033[95m"
    FG_BRIGHT_CYAN    = "\033[96m"
    FG_BRIGHT_WHITE   = "\033[97m"
    
    BG_BRIGHT_BLACK   = "\033[100m"
    BG_BRIGHT_RED     = "\033[101m"
    BG_BRIGHT_GREEN   = "\033[102m"
    BG_BRIGHT_YELLOW  = "\033[103m"
    BG_BRIGHT_BLUE    = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN    = "\033[106m"
    BG_BRIGHT_WHITE   = "\033[107m"
    
    def FG_8bit(color_8bit: int) -> str:
        "Use the table [here](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit) for reference"
        if color_8bit < 0 or color_8bit > 255:
            logger.warn("Color out of 8 bit range (0-255)")
            return ""
        return f"\033[38;5;{color_8bit}m"
    
    def BG_8bit(color_8bit: int) -> str:
        "Use the table [here](https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit) for reference"
        if color_8bit < 0 or color_8bit > 255:
            logger.warn("Color out of 8 bit range (0-255)")
            return ""
        return f"\033[48;5;{color_8bit}m"
    
    def FG_24bit(r: int, b: int, g: int) -> str:
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
    """returns {percentage}% with color"""
    
    colors = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46]
    index = min(len(colors) - 1, percentage // 10)

    return f"{C.FG_8bit(colors[index])}{percentage}%{C.RESET}"

def colorful_temperature(temp: int) -> str:
    """returns {temp}°C with color"""
    if temp < 82:
        return f"{C.FG_BRIGHT_GREEN}{temp}°C{C.RESET}"
    elif temp < 88:
        return f"{C.FG_BRIGHT_YELLOW}{temp}°C{C.RESET}"
    else:
        return f"{C.FG_BRIGHT_RED}{temp}°C{C.RESET}"

def generate_colors(max_colors):
    """return (b,g,r)"""
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