import cv2
import numpy as np
import tempfile
import os
from skimage.metrics import structural_similarity as compare_ssim
from typing import List
from fastapi import UploadFile, HTTPException


class BatchVideoService:
    def __init__(self):
        self.STABILITY_DURATION = 0.5
        self.ACTIVITY_THRESHOLD = 1500
        self.SSIM_THRESHOLD = 0.985
        self.MIN_AREA = 500
        self.MIN_TOTAL_AREA = 1000

    async def extract_slides(self, video_file: UploadFile) -> List[bytes]:
        """API-версия (для FastAPI)"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await video_file.read())
            video_path = tmp.name

        try:
            return self._process_screencast(video_path)
        finally:
            if os.path.exists(video_path):
                os.unlink(video_path)

    def test_local(self, video_path: str, output_dir: str = "debug_output"):
        os.makedirs(output_dir, exist_ok=True)

        frames_bytes = self._process_screencast(video_path)
        for i, frame_data in enumerate(frames_bytes):
            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
            cv2.imwrite(f"{output_dir}/frame_{i:03d}.png", frame)
        return frames_bytes

    def _process_screencast(self, path: str) -> List[bytes]:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30

        frames_to_wait = int(fps * self.STABILITY_DURATION)
        stability_counter = 0

        last_saved_frame = None
        prev_gray = None

        saved_frames_bytes = []
        frame_idx = 0

        while True:
            cap.grab()
            ret, frame = cap.read()
            if not ret: break
            frame_idx += 2

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            if last_saved_frame is None:
                self._save(saved_frames_bytes, frame)
                last_saved_frame = gray
                prev_gray = gray
                continue

            diff = cv2.absdiff(prev_gray, gray)
            _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
            motion_score = np.sum(thresh) / 255

            if motion_score < self.ACTIVITY_THRESHOLD:
                stability_counter += 2
            else:
                stability_counter = 0
            if stability_counter > frames_to_wait:
                (score, diff_map) = compare_ssim(last_saved_frame, gray, full=True)

                if score < self.SSIM_THRESHOLD:
                    diff_map = (diff_map * 255).astype("uint8")
                    thresh_diff = cv2.threshold(diff_map, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                    cnts = cv2.findContours(thresh_diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

                    significant_change = False
                    total_area = 0
                    for c in cnts:
                        area = cv2.contourArea(c)
                        total_area += area
                        if area > self.MIN_AREA:
                            significant_change = True

                    if significant_change and total_area > self.MIN_TOTAL_AREA:
                        self._save(saved_frames_bytes, frame)

                        last_saved_frame = gray
                        stability_counter = 0
                    else:
                        print(f"Frame {frame_idx}: Шум (Area: {total_area:.0f})")
                else:
                    print(f"⏸Frame {frame_idx}: Стабильно (SSIM: {score:.3f})")
            prev_gray = gray
        cap.release()
        return saved_frames_bytes

    def _save(self, lst, frame):
        ok, buf = cv2.imencode(".png", frame)
        if ok: lst.append(buf.tobytes())
