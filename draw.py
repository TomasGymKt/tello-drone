import cv2
from utils.models import QR_Code


def draw_cernter_cross(frame, cross_size = 5, color=(0, 0, 255)) -> None:
    """
    Drawes a cross in the middle of the frame
    
    with {cross_size}px to each direction from the center point
    """
    
    frame_height, frame_width = frame.shape[:2]

    screen_center_x = frame_width // 2
    screen_center_y = frame_height // 2

    cv2.line(frame, (screen_center_x - cross_size, screen_center_y), (screen_center_x + cross_size, screen_center_y), color, 2) # Horizontal
    cv2.line(frame, (screen_center_x, screen_center_y - cross_size), (screen_center_x, screen_center_y + cross_size), color, 2) # Veritical


def draw_info(frame, text, x, y, color, opacity=0.5, fontSize=0.6, fontThickness=1):
    frame_height, frame_width = frame.shape[:2]

    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontSize, fontThickness)

    if x < 0:
        x = frame_width + x - text_width

    if y < 0:
        y = frame_height + y

    overlay = frame.copy()

    cv2.rectangle(overlay, (x - 5, y - text_height - 5), (x + text_width + 5, y + 5), (0, 0, 0), -1)
    cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, fontThickness)


def draw_qrcodes(frame, qr_code: QR_Code) -> None:
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
        cv2.line(frame, qr_code.points[i], qr_code.points[(i + 1) % 4], (0, 255, 0), 2)

    # Center

    cv2.circle(frame, qr_code.center_xy, 5, (0, 0, 255), -1)

    # Text
    if qr_code.text:
        cv2.putText(frame, qr_code.text, (qr_code.points.bottom_left.x, qr_code.points.bottom_left.y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No data", (qr_code.points.bottom_left.x, qr_code.points.bottom_left.y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)


    cv2.putText(frame, f"size: {int(qr_code.size)}", (qr_code.points.top_left.x, qr_code.points.top_left.y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"dist: {qr_code.distance_cm:.1f} cm", (qr_code.points.top_left.x, qr_code.points.top_left.y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Čára mezi středem obrazovky a QR
    cv2.line(frame, (screen_center_x, screen_center_y), qr_code.center_xy, (255, 255, 0), 2)



    text = f"dx:{qr_code.error_xy.x} dy:{qr_code.error_xy.y}"

    (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)

    text_x = (screen_center_x + qr_code.center_xy.x) // 2 - text_width // 2
    text_y = (screen_center_y + qr_code.center_xy.y) // 2 + text_height // 2

    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    



