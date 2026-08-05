"""Log-to-Video Engine: Converts Chicago TDD execution logs & OCEL event streams into MP4 videos."""

import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any

# Constants
# Log data keys
LOG_RECEIPT_KEY = "receipt"
LOG_STATUS_KEY = "status"
LOG_QUALITY_KEY = "quality"
LOG_OCEL_EVENT_KEY = "OCEL_Event"
LOG_OCEL_EID_KEY = "ocel:eid"
LOG_DISPATCH_KEY = "dispatch"
LOG_DISPATCH_APM_KEY = "APM"

# Default values
DEFAULT_RECEIPT = "N/A"
DEFAULT_STATUS = "EXECUTED"
DEFAULT_OCEL_EID = "evt-000"
DEFAULT_APM = 100000

# Video dimensions and format
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
VIDEO_COLOR_MODE = "RGB"
VIDEO_BACKGROUND_COLOR = (17, 17, 27)

# Frame text templates
FRAME_TEXT_EXECUTION_LOOP = "CHICAGO TDD EXECUTION LOOP: {status}"
FRAME_TEXT_PHASE_1 = "Phase 1 (Chinese Strategy): PDDL+/POWL Hyper-Graph Synthesized"
FRAME_TEXT_PHASE_2 = "Phase 2 (Japanese Genba Quality): OCEL Event {ocel_eid} PASSED"
FRAME_TEXT_PHASE_3 = "Phase 3 (Korean Dispatch): Executed at {dispatch_apm:,} APM"
FRAME_TEXT_RECEIPT = "BLAKE3 Causal Receipt: {receipt[:32]}..."

# Frame text positions
HEADER_X = 40
HEADER_Y = 40
HEADER_LINE_Y = 70
HEADER_LINE_END_X = 1240
HEADER_LINE_WIDTH = 2
STEP_LABEL_Y = 180
STEP_TEXT_Y = 220
FOOTER_Y = 620

# Text colors
HEADER_TEXT_COLOR = (137, 180, 250)
STEP_LABEL_COLOR = (249, 226, 175)
STEP_TEXT_COLOR = (205, 214, 244)
FOOTER_TEXT_COLOR = (166, 227, 161)

# Header text
HEADER_TEXT = "CHICAGO TDD AUTONOMIC LOG STREAM"
STEP_LABEL_TEMPLATE = "Step {idx} of {total}:"
FOOTER_TEXT_TEMPLATE = "BLAKE3 RECEIPT: {receipt}"

# File paths and patterns
TEMP_DIR_PREFIX = "chicago_video_"
FRAME_FILENAME_PATTERN = "frame_{idx:03d}.png"
FRAME_GLOB_PATTERN = "frame_%03d.png"

# FFmpeg configuration
FFMPEG_CMD = "ffmpeg"
FFMPEG_ARG_Y = "-y"
FFMPEG_ARG_FRAMERATE = "-framerate"
FFMPEG_ARG_INPUT = "-i"
FFMPEG_ARG_VIDEO_CODEC = "-c:v"
FFMPEG_CODEC_H264 = "libx264"
FFMPEG_ARG_PIX_FORMAT = "-pix_fmt"
FFMPEG_PIX_FORMAT_YUV420P = "yuv420p"
FFMPEG_SUCCESS_CODE = 0

# Error messages
FFMPEG_ERROR_TEMPLATE = "FFmpeg video concatenation failed: {stderr}"


def convert_log_to_video(
    log_data: Dict[str, Any],
    output_path: Path,
    fps: int = 1,
    duration_per_step: float = 2.0
) -> Path:
    """Transform Chicago TDD log dictionary into an MP4 video visualization using PIL and ffmpeg."""
    from PIL import Image, ImageDraw, ImageFont

    output_path.parent.mkdir(parents=True, exist_ok=True)

    receipt = str(log_data.get(LOG_RECEIPT_KEY, DEFAULT_RECEIPT))
    status = str(log_data.get(LOG_STATUS_KEY, DEFAULT_STATUS))
    ocel_eid = str(log_data.get(LOG_QUALITY_KEY, {}).get(LOG_OCEL_EVENT_KEY, {}).get(LOG_OCEL_EID_KEY, DEFAULT_OCEL_EID))
    dispatch_apm = log_data.get(LOG_DISPATCH_KEY, {}).get(LOG_DISPATCH_APM_KEY, DEFAULT_APM)

    frame_texts = [
        FRAME_TEXT_EXECUTION_LOOP.format(status=status),
        FRAME_TEXT_PHASE_1,
        FRAME_TEXT_PHASE_2.format(ocel_eid=ocel_eid),
        FRAME_TEXT_PHASE_3.format(dispatch_apm=dispatch_apm),
        FRAME_TEXT_RECEIPT.format(receipt=receipt)
    ]

    temp_dir = Path(tempfile.mkdtemp(prefix=TEMP_DIR_PREFIX))
    try:
        width = VIDEO_WIDTH
        height = VIDEO_HEIGHT
        font = ImageFont.load_default()

        for idx, text in enumerate(frame_texts):
            img_path = temp_dir / FRAME_FILENAME_PATTERN.format(idx=idx)

            img = Image.new(VIDEO_COLOR_MODE, (width, height), color=VIDEO_BACKGROUND_COLOR)
            draw = ImageDraw.Draw(img)

            # Header
            draw.text((HEADER_X, HEADER_Y), HEADER_TEXT, fill=HEADER_TEXT_COLOR, font=font)
            draw.line([(HEADER_X, HEADER_LINE_Y), (HEADER_LINE_END_X, HEADER_LINE_Y)], fill=HEADER_TEXT_COLOR, width=HEADER_LINE_WIDTH)

            # Frame narrative step
            step_label = STEP_LABEL_TEMPLATE.format(idx=idx + 1, total=len(frame_texts))
            draw.text((HEADER_X, STEP_LABEL_Y), step_label, fill=STEP_LABEL_COLOR, font=font)
            draw.text((HEADER_X, STEP_TEXT_Y), text, fill=STEP_TEXT_COLOR, font=font)

            # BLAKE3 hash footer
            footer_text = FOOTER_TEXT_TEMPLATE.format(receipt=receipt)
            draw.text((HEADER_X, FOOTER_Y), footer_text, fill=FOOTER_TEXT_COLOR, font=font)

            img.save(img_path)

        # Concatenate frame images into H.264 MP4 video
        ffmpeg_concat_cmd = [
            FFMPEG_CMD,
            FFMPEG_ARG_Y,
            FFMPEG_ARG_FRAMERATE, str(fps),
            FFMPEG_ARG_INPUT, str(temp_dir / FRAME_GLOB_PATTERN),
            FFMPEG_ARG_VIDEO_CODEC, FFMPEG_CODEC_H264,
            FFMPEG_ARG_PIX_FORMAT, FFMPEG_PIX_FORMAT_YUV420P,
            str(output_path)
        ]
        res = subprocess.run(ffmpeg_concat_cmd, capture_output=True, text=True)
        if res.returncode != FFMPEG_SUCCESS_CODE:
            raise RuntimeError(FFMPEG_ERROR_TEMPLATE.format(stderr=res.stderr))

        return output_path
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
