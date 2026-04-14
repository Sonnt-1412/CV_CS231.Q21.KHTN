import cv2
import mediapipe as mp
import pyautogui
import time

# ===== OPTIMIZE PYAUTOGUI =====
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

# ===== INIT MEDIAPIPE =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,  # faster
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

# ===== SCREEN =====
screen_w, screen_h = pyautogui.size()

# ===== CAMERA =====
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # width
cap.set(4, 480)  # height

# ===== SMOOTH =====
prev_x, prev_y = 0, 0
smoothening = 3

# ===== CLICK CONTROL =====
last_click_time = 0
click_delay = 0.4

# ===== FRAME CONTROL =====
frame_count = 0

while True:
    success, frame = cap.read()
    if not success:
        break

    frame_count += 1

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            # ===== MOVE =====
            x = int(handLms.landmark[8].x * w)
            y = int(handLms.landmark[8].y * h)

            cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)

            screen_x = screen_w * x / w
            screen_y = screen_h * y / h

            # smoothing
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening

            # reduce move frequency
            if frame_count % 2 == 0:
                pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

            # ===== FIST DETECTION =====
            fingers_folded = 0

            if handLms.landmark[8].y > handLms.landmark[6].y:
                fingers_folded += 1
            if handLms.landmark[12].y > handLms.landmark[10].y:
                fingers_folded += 1
            if handLms.landmark[16].y > handLms.landmark[14].y:
                fingers_folded += 1
            if handLms.landmark[20].y > handLms.landmark[18].y:
                fingers_folded += 1¡™¡™

            # ===== CLICK =====
            if fingers_folded >= 3:
                current_time = time.time()
                if current_time - last_click_time > click_delay:
                    pyautogui.click()
                    last_click_time = current_time

                    cv2.putText(frame, "CLICK", (30, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 2)

            # ===== DRAW =====
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Mouse (Optimized)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()