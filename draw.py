import cv2
from utils.models import AlphaColor, Color, QR_Code

from UI.elements import Container, Line



def draw_cernter_cross(frame, container: Container, cross_size = 5, color: Color | AlphaColor=Color(0, 0, 255)) -> None:
    """
    Drawes a cross in the middle of the frame
    
    with {cross_size}px to each direction from the center point
    """
    
    frame_height, frame_width = frame.shape[:2]

    screen_center_x = frame_width // 2
    screen_center_y = frame_height // 2

    container.add(Line(screen_center_x - cross_size, screen_center_y, screen_center_x + cross_size, screen_center_y, color, 2)) # Horizontal
    container.add(Line(screen_center_x, screen_center_y - cross_size, screen_center_x, screen_center_y + cross_size, color, 2)) # Veritical


# def draw_info(frame, text: str, style: DrawInfoStyle) -> None:
#     frame_height, frame_width = frame.shape[:2]

#     x = style.x
#     y = style.y
#     padding = style.padding

#     (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, style.fontSize, style.fontThickness)

#     if x < 0:
#         x = frame_width + x - text_width - padding.horizontal

#     if y < 0:
#         y = frame_height + y - text_height - padding.vertical

#     overlay = frame.copy()

#     cv2.rectangle(overlay, (x, y), (x + text_width + padding.horizontal, y + text_height + padding.vertical), style.background_color, -1)
#     cv2.addWeighted(overlay, style.background_color.alpha, frame, 1 - style.background_color.alpha, 0, frame)
#     cv2.putText(frame, text, (x + padding.left, y + text_height + padding.top), cv2.FONT_HERSHEY_SIMPLEX, style.fontSize, style.color, style.fontThickness)


def draw_qrcodes(frame, qr_code: QR_Code, opacity: float=1.0) -> None:
    target = frame if opacity >= 1.0 else frame.copy()
    frame_height, frame_width = frame.shape[:2]

    screen_center_x = int(frame_width / 2)
    screen_center_y = int(frame_height / 2)
    
    
    # Contours QR outline
    # result = get_contours(frame)
    # if result:
    #     center_x, center_y = result["center"]

    #     cv2.circle(frame, (center_x, center_y), 10, (0, 0, 255), -1)

    #     for contour in result["finders"]:
    #         cv2.drawContours(frame, [contour], -1, (255, 0, 0), 3)
    


    # QR outline
    for i in range(4):
        cv2.line(target, qr_code.points[i], qr_code.points[(i + 1) % 4], (0, 255, 0), 2)

    # Center

    cv2.circle(target, qr_code.center_xy, 5, (0, 0, 255), -1)

    # Text
    if qr_code.text:
        cv2.putText(target, qr_code.text, (qr_code.points.bottom_left.x, qr_code.points.bottom_left.y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(target, "No data", (qr_code.points.bottom_left.x, qr_code.points.bottom_left.y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)


    cv2.putText(target, f"size: {int(qr_code.size)}", (qr_code.points.top_left.x, qr_code.points.top_left.y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(target, f"dist: {qr_code.distance_cm:.1f} cm", (qr_code.points.top_left.x, qr_code.points.top_left.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Čára mezi středem obrazovky a QR
    cv2.line(target, (screen_center_x, screen_center_y), qr_code.center_xy, (255, 255, 0), 2)



    text = f"dx:{qr_code.error_xy.x} dy:{qr_code.error_xy.y}"

    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)

    text_x = (screen_center_x + qr_code.center_xy.x) // 2 - text_width // 2
    text_y = (screen_center_y + qr_code.center_xy.y) // 2 + text_height // 2

    cv2.putText(target, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    if opacity < 1.0:
        cv2.addWeighted(target, opacity, frame, 1 - opacity, 0, frame)
    



