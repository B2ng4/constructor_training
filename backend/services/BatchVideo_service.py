import cv2
import numpy as np
import tempfile
import os
from skimage.metrics import structural_similarity as compare_ssim
from typing import List
from fastapi import UploadFile, HTTPException


class BatchVideoService:
    def __init__(self):
        self.MIN_STABILITY_TIME = 0.5
        self.WORK_WIDTH = 400
        self.SKIP_FRAMES = 5
        self.SSIM_THRESHOLD = 0.92

    async def extract_slides(self, video_file: UploadFile) -> List[bytes]:
        """Сохраняет во temp и запускает процессинг"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            content = await video_file.read()
            tmp.write(content)
            path = tmp.name

        try:
            return self._process_video(path)
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def _process_video(self, path: str) -> List[bytes]:
        frames = []
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise HTTPException(400, "Bad video file")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        stability_target = int(fps * self.MIN_STABILITY_TIME)

        last_saved_gray = None
        last_hist = None
        prev_gray = None
        stability_count = 0
        idx = 0

        while True:
            if self.SKIP_FRAMES > 1:
                cap.grab()
                idx += 1
                if idx % self.SKIP_FRAMES != 0: continue

            ret, frame = cap.retrieve()
            if not ret: break
            h, w = frame.shape[:2]
            sh = int(h * (self.WORK_WIDTH / w))
            small = cv2.resize(frame, (self.WORK_WIDTH, sh))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (9, 9), 0)
            if last_saved_gray is None:
                self._save(frames, frame)
                last_saved_gray = gray
                last_hist = self._calc_hist(gray)
                prev_gray = gray
                continue

            diff = np.mean(cv2.absdiff(prev_gray, gray))
            if diff < 2.0:
                stability_count += self.SKIP_FRAMES
            else:
                stability_count = 0
                prev_gray = gray
                continue

            if stability_count > stability_target:
                curr_hist = self._calc_hist(gray)
                if cv2.compareHist(last_hist, curr_hist, cv2.HISTCMP_CORREL) > 0.99:
                    stability_count = 0
                    continue

                score, _ = compare_ssim(last_saved_gray, gray, full=True)
                if score < self.SSIM_THRESHOLD and np.mean(gray) > 10:
                    self._save(frames, frame)
                    last_saved_gray = gray
                    last_hist = curr_hist

                stability_count = 0

            prev_gray = gray

        cap.release()
        return frames

    def _save(self, lst, frame):
        ok, buf = cv2.imencode(".png", frame)
        if ok: lst.append(buf.tobytes())

    def _calc_hist(self, img):
        h = cv2.calcHist([img], [0], None, [256], [0, 256])
        return cv2.normalize(h, h).flatten()
