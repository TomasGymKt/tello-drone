import cv2
from utils.models import QR_Code
from utils.color import generate_colors
from settings import ScanMethod
from .base import Scanner as BaseScanner
from utils.DebugFrames import debug_frames

number = 0
count = 0
off = 16

def get_contours(frame) -> QR_Code | None:
    global number, count
    if count >= 20:
        count = 0
        number = (number + 1) % 35
    count +=1
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canvas = frame.copy()
    
    # gray = cv2.GaussianBlur(gray, (3, 3), 0)

    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        number + off
    )
    

    binary = cv2.bitwise_not(binary)

    debug_frames.set("Binary Frame", binary)
    
    # canny = cv2.Canny(gray, 125, 175)
    # cv2.imshow("Canny edge", canny)
    
    # canny_binary = cv2.Canny(binary, 125, 175)
    # cv2.imshow("Binary Canny edge", canny_binary)
    
    
    contours, hierarchy = cv2.findContours(
        binary,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if hierarchy is None:
        return None
        
    hierarchy = hierarchy[0]
    
    
    colors = generate_colors(len(contours))
    for i, contour in enumerate(contours):
        cv2.drawContours(canvas, contours, i, colors[i], 2)
    
    # contours_we_care_about = []
    
    # for i, contour in enumerate(contours):
    #     area = cv2.contourArea(contour)
        
    #     if area < 0:
    #         continue
        
    #     # if hierarchy[i][3] < 0: 
    #     #     continue
        
    #     right_contour = find_contour_right_of(
    #         contour,
    #         contours,
    #         max_dx=10,
    #         max_dy=4
    #         )
    #     if right_contour is None:
    #         continue
        
    #     contours_we_care_about.append(contour)
    
    # cv2.drawContours(canvas, contours_we_care_about, -1, (255, 0, 0), 4)

    
    
    cv2.putText(canvas, f"{number+off}", (7, 35), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    debug_frames.set("Contours Canvas", canvas)
    return None


class Scanner(BaseScanner):
    method = ScanMethod.CONTOURS

    def scan(self, frame) -> QR_Code | None:
        return get_contours(frame)

