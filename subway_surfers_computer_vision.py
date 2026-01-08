# -------------------- IMPORTS --------------------
import cv2                          # OpenCV for camera & drawing
import mediapipe as mp              # MediaPipe for pose detection
import time as t                    # Time for FPS & cooldowns
from pynput import keyboard as key  # Keyboard control (Subway Surfers input)
import os

# Reduce MediaPipe console spam
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# -------------------- KEYBOARD CONTROLLER --------------------
# Used to simulate arrow key presses
kb = key.Controller()


# -------------------- GAME STATE --------------------
playing = False     # Game starts only after raising hand


# -------------------- START SCREEN FUNCTION --------------------
def start(frame, h, w, ly, ry):
    """
    Shows the start message on screen
    Also calculates the user's neutral body height
    """

    # Calculate text position to center it
    (text_width, text_height), _ = cv2.getTextSize(
        "To start game raise your right Hand",
        cv2.FONT_HERSHEY_PLAIN, 4, 3
    )
    x = int((w - text_width / 2) // 2)
    y = int((h + text_height) // 2)

    # Neutral height = average of both shoulders
    user_height = int((ly + ry) / 2) + 10

    # Display start message
    cv2.putText(
        frame,
        "To start game raise your right Hand",
        (x, y),
        cv2.FONT_HERSHEY_PLAIN,
        4,
        (0, 0, 0),
        3
    )

    return user_height


# -------------------- FPS CALCULATION --------------------
def fps(ptime=0):
    """
    Calculates FPS using time difference between frames
    """
    ctime = t.time()
    fps = int(1 / (ctime - ptime))
    ptime = ctime
    return fps, ptime


# -------------------- CALIBRATION OVERLAY --------------------
def callibration(frame, user_height, Threshold, w, h):
    """
    Draws:
    - Horizontal band showing jump/roll threshold
    - Center vertical line for lane reference
    """

    overlay = frame.copy()

    # Semi-transparent threshold band
    cv2.rectangle(
        overlay,
        (0, user_height - Threshold),
        (w, user_height + Threshold),
        (0, 0, 0),
        -1
    )

    alpha = 0.3
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Neutral body height line
    cv2.line(frame, (0, user_height), (w, user_height), (255, 255, 255), 2)

    # Center lane divider
    cv2.line(frame, (int(w / 2), 0), (int(w / 2), h), (255, 255, 255), 2)


# -------------------- GAME MECHANICS --------------------
def game_mech(lx, ly, rx, ry, h, w, user_height, Threshold, curr_height):
    """
    Handles:
    - Lane switching (left / center / right)
    - Jump & Roll actions
    - Cooldowns to prevent spam
    """

    global StateL, StateA, last_lane_time, last_action_time
    now = t.time()

    # ----------- LANE DETECTION -----------
    # Based on shoulder positions relative to screen center
    if lx < w / 2 and rx < w / 2:
        target_lane = 0      # Left lane
    elif lx < w / 2 and rx > w / 2:
        target_lane = 1      # Middle lane
    elif lx > w / 2 and rx > w / 2:
        target_lane = 2      # Right lane
    else:
        target_lane = None

    # Convert "Lane X" string to index (0,1,2)
    curr_lane = int(StateL[-1]) - 1

    # Move ONLY one lane per cooldown
    if target_lane is not None and target_lane != curr_lane:
        if now - last_lane_time > LANE_COOLDOWN:

            if target_lane > curr_lane:
                kb.press(key.Key.right)
                kb.release(key.Key.right)
                curr_lane += 1
            else:
                kb.press(key.Key.left)
                kb.release(key.Key.left)
                curr_lane -= 1

            StateL = f"Lane {curr_lane + 1}"
            last_lane_time = now


    # ----------- JUMP / ROLL DETECTION -----------
    NewStateA = "NONE"

    # Jump if body goes above neutral band
    if curr_height < user_height - Threshold:
        NewStateA = "JUMP"

    # Roll if body goes below neutral band
    elif curr_height > user_height + Threshold:
        NewStateA = "ROLL"

    # Trigger action ONLY on state change
    if NewStateA != StateA and now - last_action_time > ACTION_COOLDOWN:

        if NewStateA == "JUMP":
            kb.press(key.Key.up)
            kb.release(key.Key.up)

        elif NewStateA == "ROLL":
            kb.press(key.Key.down)
            kb.release(key.Key.down)

        StateA = NewStateA
        last_action_time = now

    # Reset action state when body returns to neutral
    if abs(curr_height - user_height) < Threshold:
        StateA = "NONE"


# -------------------- CAMERA SETUP --------------------
# CAP_DSHOW fixes most Windows webcam issues
vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)


# -------------------- MEDIAPIPE SETUP --------------------
mppose = mp.solutions.pose
pose = mppose.Pose()
mpdraw = mp.solutions.drawing_utils


# -------------------- INITIAL VALUES --------------------
ptime = 0
Threshold = 55

StateL = "Lane 2"   # Start in middle lane
StateA = None

last_lane_time = 0
last_action_time = 0

LANE_COOLDOWN = 0.18     # Lane switching delay
ACTION_COOLDOWN = 0.05   # Jump/Roll responsiveness


# -------------------- MAIN LOOP --------------------
while True:

    ret, frame = vid.read()
    frame = cv2.flip(frame, 1)  # Mirror image for natural movement

    if not ret:
        print("ERROR!! COULD NOT FETCH FRAME")
        break

    Fps, ptime = fps(ptime)
    key_pressed = cv2.waitKey(1) & 0xFF

    # Convert BGR → RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    if results.pose_landmarks:

        h, w, c = frame.shape
        mpdraw.draw_landmarks(
            frame,
            results.pose_landmarks,
            mppose.POSE_CONNECTIONS
        )

        landmark = results.pose_landmarks.landmark

        # Shoulders are swapped because frame is mirrored
        left_shoulder = landmark[mppose.PoseLandmark.RIGHT_SHOULDER]
        right_shoulder = landmark[mppose.PoseLandmark.LEFT_SHOULDER]
        play = landmark[mppose.PoseLandmark.LEFT_WRIST]

        lx, ly = int(left_shoulder.x * w), int(left_shoulder.y * h)
        rx, ry = int(right_shoulder.x * w), int(right_shoulder.y * h)
        px, py = int(play.x * w), int(play.y * h)

        curr_height = int((ly + ry) / 2)

        # ----------- START GAME LOGIC -----------
        if not playing:
            user_height = start(frame, h, w, ly, ry)

            # Raise hand to start game
            if py < (h / 3):
                kb.press(key.Key.space)
                kb.release(key.Key.space)
                playing = True

        # ----------- GAME RUNNING -----------
        if playing:
            callibration(frame, user_height, Threshold, w, h)
            game_mech(lx, ly, rx, ry, h, w, user_height, Threshold, curr_height)


    # -------------------- UI TEXT --------------------
    cv2.putText(frame, StateL, (10, 60), 1, 2, (0, 255, 0), 2)
    cv2.putText(frame, str(StateA), (10, 100), 1, 2, (255, 0, 0), 2)
    cv2.putText(frame, f"FPS: {Fps}", (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 225), 1)

    # Resizable window
    cv2.namedWindow("Face Cam", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Face Cam", 900, 600)
    cv2.imshow("Face Cam", frame)

    if key_pressed == ord("q"):
        break


# -------------------- CLEANUP --------------------
vid.release()
cv2.destroyAllWindows()
