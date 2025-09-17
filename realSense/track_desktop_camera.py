import pyrealsense2 as rs
import numpy as np
import cv2
from collections import deque

# RealSense setting
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

align = rs.align(rs.stream.color)
MIN_AREA = 1000

# Smoothing history
history_bottle = deque(maxlen=10)
history_arm = deque(maxlen=10)

# Valid depth range
MIN_VALID_DEPTH = 0.005
MAX_VALID_DEPTH = 20.0

try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)
        depth_frame = aligned.get_depth_frame()
        color_frame = aligned.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        blurred = cv2.GaussianBlur(color_image, (9, 9), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Define color masks
        mask_bottle = cv2.inRange(hsv, np.array([35, 80, 40]), np.array([85, 255, 255]))
        mask_arm = cv2.inRange(hsv, np.array([85, 100, 40]), np.array([100, 255, 255]))

        kernel = np.ones((5, 5), np.uint8)
        mask_bottle = cv2.morphologyEx(mask_bottle, cv2.MORPH_CLOSE, kernel)
        mask_bottle = cv2.morphologyEx(mask_bottle, cv2.MORPH_OPEN, kernel)
        mask_arm = cv2.morphologyEx(mask_arm, cv2.MORPH_CLOSE, kernel)
        mask_arm = cv2.morphologyEx(mask_arm, cv2.MORPH_OPEN, kernel)

        contours_bottle, _ = cv2.findContours(mask_bottle, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_arm, _ = cv2.findContours(mask_arm, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        valid_bottle = [c for c in contours_bottle if cv2.contourArea(c) > MIN_AREA]
        valid_arm = [c for c in contours_arm if cv2.contourArea(c) > MIN_AREA]

        depth_intrin = depth_frame.profile.as_video_stream_profile().intrinsics

        # track target object
        if valid_bottle:
            largest = max(valid_bottle, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            cx, cy = x + w // 2, y + h // 2
            depth = depth_frame.get_distance(cx, cy)

            if MIN_VALID_DEPTH < depth < MAX_VALID_DEPTH:
                dx, dy, dz = rs.rs2_deproject_pixel_to_point(depth_intrin, [cx, cy], depth)
                history_bottle.append((dx, dy, dz))
                avg = np.mean(history_bottle, axis=0)

                cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = f"Bottle: X:{avg[0]:.2f} Y:{avg[1]:.2f} Z:{avg[2]:.2f} m"
                cv2.putText(color_image, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            cv2.putText(color_image, "No valid target object detected",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # track arm
        if valid_arm:
            largest = max(valid_arm, key=cv2.contourArea)
            x_r, y_r, w_r, h_r = cv2.boundingRect(largest)
            cx_r, cy_r = x_r + w_r // 2, y_r + h_r // 2
            depth_r = depth_frame.get_distance(cx_r, cy_r)

            if MIN_VALID_DEPTH < depth_r < MAX_VALID_DEPTH:
                dx_r, dy_r, dz_r = rs.rs2_deproject_pixel_to_point(depth_intrin, [cx_r, cy_r], depth_r)
                history_arm.append((dx_r, dy_r, dz_r))
                avg_r = np.mean(history_arm, axis=0)

                scale = 3
                w_big = int(w_r * scale)
                h_big = int(h_r * scale)
                x_big = max(cx_r - w_big // 2, 0)
                y_big = max(cy_r - h_big // 2, 0)
                x_end = min(x_big + w_big, color_image.shape[1])
                y_end = min(y_big + h_big, color_image.shape[0])

                cv2.rectangle(color_image, (x_big, y_big), (x_end, y_end), (255, 255, 0), 2)
                text_cyan = f"Arm: X:{avg_r[0]:.2f} Y:{avg_r[1]:.2f} Z:{avg_r[2]:.2f} m"
                cv2.putText(color_image, text_cyan, (x_big, y_big - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        else:
            cv2.putText(color_image, "No valid robot-arm detected",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # show result
        cv2.imshow("Color", color_image)
        cv2.imshow("Bottle Mask (Green)", mask_bottle)
        cv2.imshow("Arm Mask (Cyan)", mask_arm)

        if cv2.waitKey(1) == 27:
            break

except Exception as e:
    print("XXX!:", e)

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
