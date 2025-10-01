"""Screen capture and board extraction utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import numpy as np
from mss import mss

from .config import Region


@dataclass
class BoardState:
    grid: np.ndarray  # shape (20, 10), 0 empty, 1 filled


class BoardCapture:
    """Capture the TETR.IO board and extract grid occupancy."""

    def __init__(self, board_region: Region):
        if board_region.width <= 0 or board_region.height <= 0:
            raise ValueError("Board region is not configured. Run the calibration first.")
        self._region = board_region
        self._sct = mss()

    def _grab_frame(self) -> np.ndarray:
        bbox = {
            "left": self._region.left,
            "top": self._region.top,
            "width": self._region.width,
            "height": self._region.height,
        }
        raw = self._sct.grab(bbox)
        frame = np.array(raw)
        return frame[:, :, :3]

    def capture_board(self) -> BoardState:
        frame = self._grab_frame()
        grid = self._grid_from_frame(frame)
        return BoardState(grid=grid)

    def _grid_from_frame(self, frame: np.ndarray) -> np.ndarray:
        height, width, _ = frame.shape
        cell_height = height / 20
        cell_width = width / 10

        grid = np.zeros((20, 10), dtype=np.uint8)

        for row in range(20):
            for col in range(10):
                center_y = int((row + 0.5) * cell_height)
                center_x = int((col + 0.5) * cell_width)
                center_y = min(center_y, height - 1)
                center_x = min(center_x, width - 1)
                pixel = frame[center_y, center_x]
                occupied = self._is_occupied(pixel)
                grid[row, col] = 1 if occupied else 0

        return grid

    @staticmethod
    def _is_occupied(pixel: np.ndarray) -> bool:
        # TETR.IO empty cells are very dark, so we can threshold the brightness.
        brightness = pixel.mean() / 255.0
        return brightness > 0.12


class PreviewCapture:
    """Capture the preview region and infer the next piece queue.

    The detection logic is intentionally simple and expects the preview area to
    contain square thumbnails on a dark background. We quantise the dominant
    colour of each thumbnail to map it back to piece identifiers.
    """

    _PIECE_COLOURS = {
        "I": np.array([0, 240, 240]),
        "J": np.array([0, 0, 240]),
        "L": np.array([240, 160, 0]),
        "O": np.array([240, 240, 0]),
        "S": np.array([0, 240, 0]),
        "T": np.array([160, 0, 240]),
        "Z": np.array([240, 0, 0]),
    }

    def __init__(self, preview_region: Region):
        if preview_region.width <= 0 or preview_region.height <= 0:
            raise ValueError("Preview region is not configured. Run the calibration first.")
        self._region = preview_region
        self._sct = mss()

    def capture_queue(self, *, max_pieces: int = 5) -> List[str]:
        frame = self._grab_frame()
        return self._pieces_from_frame(frame, max_pieces=max_pieces)

    def _grab_frame(self) -> np.ndarray:
        bbox = {
            "left": self._region.left,
            "top": self._region.top,
            "width": self._region.width,
            "height": self._region.height,
        }
        raw = self._sct.grab(bbox)
        return np.array(raw)[:, :, :3]

    def _pieces_from_frame(self, frame: np.ndarray, *, max_pieces: int) -> List[str]:
        height, width, _ = frame.shape
        slot_height = height / max_pieces
        slot_width = width
        pieces: List[str] = []

        for index in range(max_pieces):
            y0 = int(index * slot_height)
            y1 = int((index + 1) * slot_height)
            x0 = 0
            x1 = int(slot_width)
            tile = frame[y0:y1, x0:x1]
            if tile.size == 0:
                continue
            dominant_colour = tile.reshape(-1, 3).mean(axis=0)
            piece = self._closest_piece(dominant_colour)
            pieces.append(piece)

        return pieces

    def _closest_piece(self, colour: np.ndarray) -> str:
        best_piece = "I"
        best_distance = float("inf")
        for piece, ref_colour in self._PIECE_COLOURS.items():
            distance = np.linalg.norm(colour - ref_colour)
            if distance < best_distance:
                best_piece = piece
                best_distance = distance
        return best_piece
