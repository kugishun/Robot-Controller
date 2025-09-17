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
        kernel = np.ones((5, 5), np.uint8)
        mask_bottle = cv2.morphologyEx(mask_bottle, cv2.MORPH_CLOSE, kernel)
        mask_bottle = cv2.morphologyEx(mask_bottle, cv2.MORPH_OPEN, kernel)

        contours_bottle, _ = cv2.findContours(mask_bottle, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        valid_bottle = [c for c in contours_bottle if cv2.contourArea(c) > MIN_AREA]

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

        # show result
        cv2.imshow("Color", color_image)
        cv2.imshow("Bottle Mask (Green)", mask_bottle)

        if cv2.waitKey(1) == 27:
            break

except Exception as e:
    print("XXX!:", e)

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
