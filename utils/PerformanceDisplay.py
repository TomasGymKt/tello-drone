import time

from UI.Elements import Container, Text, TextStyle
from utils.models import Color


class PerformanceDisplay:
    def __init__(self, refresh_period=0.15, scan_fps_period=10.0, scan_time_period=10.0, draw_fps_period=10.0):
        self.refresh_period = refresh_period
        self.scan_fps_period = scan_fps_period
        self.scan_time_period = scan_time_period
        self.draw_fps_period = draw_fps_period

        self._last_refresh_at = 0.0
        self._scan_fps_text = "Scan FPS: --.-"
        self._scan_time_text = "Scan time: --.- ms"
        self._draw_fps_text = "Draw FPS: --.-"
        self._last_draw_frame_at = None
        self._last_scan_finished_at = None
        self._latest_scan_fps: float | None = None
        self._latest_draw_fps: float | None = None

        self._scan_fps_stats_started_at  = time.perf_counter()
        self._scan_time_stats_started_at = time.perf_counter()
        self._draw_fps_stats_started_at  = time.perf_counter()

        self._min_scan_fps: float | None = None
        self._max_scan_fps: float | None = None
        self._min_scan_time: float | None = None
        self._max_scan_time: float | None = None
        self._min_draw_fps: float | None = None
        self._max_draw_fps: float | None = None
        
        self._minmax_scan_fps_text = "Min: --.- FPS | Max: --.- FPS"
        self._minmax_scan_time_text = "Min: --.- ms | Max: --.- ms"
        self._minmax_draw_fps_text = "Min: --.- FPS | Max: --.- FPS"

        self._ui_container = Container()

        self.scan_fps_Text: Text  = self._ui_container.add(Text(7, 7 , self._scan_fps_text , TextStyle(Color(0, 255, 0))))
        self.scan_time_Text: Text = self._ui_container.add(Text(7, 63, self._scan_time_text, TextStyle(Color(0, 255, 0), fontSize=0.45)))
        self.draw_fps_Text: Text  = self._ui_container.add(Text(7, -7, self._draw_fps_text , TextStyle(Color(0, 255, 0), fontSize=0.35)))
        self.minmax_scan_fps_Text: Text  = self._ui_container.add(Text(7, 33, self._minmax_scan_fps_text , TextStyle(Color(0, 255, 0), fontSize=0.35)))
        self.minmax_scan_time_Text: Text = self._ui_container.add(Text(7, 85, self._minmax_scan_time_text, TextStyle(Color(0, 255, 0), fontSize=0.35)))
        self.minmax_draw_fps_Text: Text  = self._ui_container.add(Text(120, -7, self._minmax_draw_fps_text , TextStyle(Color(0, 255, 0), fontSize=0.35)))

    def _update_draw_fps(self, current_time: float):
        if self._last_draw_frame_at is not None:
            frame_dt = current_time - self._last_draw_frame_at
            if frame_dt > 0:
                instant_fps = 1 / frame_dt

                if self._latest_draw_fps is None:
                    self._latest_draw_fps = instant_fps
                else:
                    self._latest_draw_fps = self._latest_draw_fps * 0.7 + instant_fps * 0.3

                if self._min_draw_fps is None or instant_fps < self._min_draw_fps:
                    self._min_draw_fps = instant_fps

                if self._max_draw_fps is None or instant_fps > self._max_draw_fps:
                    self._max_draw_fps = instant_fps

        self._last_draw_frame_at = current_time
    
    def _update_scan_fps(self, last_scan_finished_at: float | None):
        if last_scan_finished_at is not None and last_scan_finished_at != self._last_scan_finished_at:
            if self._last_scan_finished_at is not None:
                scan_dt = last_scan_finished_at - self._last_scan_finished_at
                if scan_dt > 0:
                    instant_scan_fps = 1 / scan_dt

                    if self._latest_scan_fps is None:
                        self._latest_scan_fps = instant_scan_fps
                    else:
                        self._latest_scan_fps = self._latest_scan_fps * 0.7 + instant_scan_fps * 0.3

                    if self._min_scan_fps is None or instant_scan_fps < self._min_scan_fps:
                        self._min_scan_fps = instant_scan_fps

                    if self._max_scan_fps is None or instant_scan_fps > self._max_scan_fps:
                        self._max_scan_fps = instant_scan_fps

            self._last_scan_finished_at = last_scan_finished_at
    
    def _update_minmax(self, current_time: float, last_scan_ms: float | None):
        if last_scan_ms is not None:
            if self._min_scan_time is None or last_scan_ms < self._min_scan_time:
                self._min_scan_time = last_scan_ms

            if self._max_scan_time is None or last_scan_ms > self._max_scan_time:
                self._max_scan_time = last_scan_ms

        if current_time - self._scan_fps_stats_started_at >= self.scan_fps_period:
            self._min_scan_fps = None
            self._max_scan_fps = None
            self._scan_fps_stats_started_at = current_time

        if current_time - self._scan_time_stats_started_at >= self.scan_time_period:
            self._min_scan_time = None
            self._max_scan_time = None
            self._scan_time_stats_started_at = current_time

        if current_time - self._draw_fps_stats_started_at >= self.draw_fps_period:
            self._min_draw_fps = None
            self._max_draw_fps = None
            self._draw_fps_stats_started_at = current_time
    
    def _update_text(self, current_time: float, last_scan_ms: float | None):
        if current_time - self._last_refresh_at >= self.refresh_period:
            scan_fps_text = "--.-"  if self._latest_scan_fps is None else f"{self._latest_scan_fps:.1f}"
            scan_time_text = "--.-" if last_scan_ms is None else f"{last_scan_ms:.1f}"
            draw_fps_text = "--.-"  if self._latest_draw_fps is None else f"{self._latest_draw_fps:.1f}"
            
            min_scan_fps_text =  "--.-" if self._min_scan_fps  is None else f"{self._min_scan_fps :.1f}"
            min_scan_time_text = "--.-" if self._min_scan_time is None else f"{self._min_scan_time:.1f}"
            min_draw_fps_text =  "--.-" if self._min_draw_fps  is None else f"{self._min_draw_fps :.1f}"
            max_scan_fps_text =  "--.-" if self._max_scan_fps  is None else f"{self._max_scan_fps :.1f}"
            max_scan_time_text = "--.-" if self._max_scan_time is None else f"{self._max_scan_time:.1f}"
            max_draw_fps_text =  "--.-" if self._max_draw_fps  is None else f"{self._max_draw_fps :.1f}"

            self._scan_fps_text = f"FPS: {scan_fps_text}"
            self._scan_time_text = f"{scan_time_text} ms"
            self._draw_fps_text = f"Draw FPS: {draw_fps_text}"
            
            self._minmax_scan_fps_text  = f"Min: {min_scan_fps_text} FPS | Max: {max_scan_fps_text} FPS"
            self._minmax_scan_time_text = f"Min: {min_scan_time_text} ms | Max: {max_scan_time_text} ms"
            self._minmax_draw_fps_text  = f"Min: {min_draw_fps_text} FPS | Max: {max_draw_fps_text} FPS"

            self._last_refresh_at = current_time

    def update(self, last_scan_finished_at: float | None, last_scan_ms: float | None):
        current_time = time.perf_counter()
        
        self._update_draw_fps(current_time)
        self._update_scan_fps(last_scan_finished_at)
        self._update_minmax(current_time, last_scan_ms)
        self._update_text(current_time, last_scan_ms)

        self.scan_fps_Text .set_text(self._scan_fps_text )
        self.scan_time_Text.set_text(self._scan_time_text)
        self.draw_fps_Text .set_text(self._draw_fps_text )
        self.minmax_scan_fps_Text .set_text(self._minmax_scan_fps_text )
        self.minmax_scan_time_Text.set_text(self._minmax_scan_time_text)
        self.minmax_draw_fps_Text .set_text(self._minmax_draw_fps_text )
    
    @property
    def container(self):
        return self._ui_container
    
