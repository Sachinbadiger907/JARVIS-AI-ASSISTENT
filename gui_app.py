"""
Jarvis GUI - "Stark Industries" style dashboard.
Opens only when told to ("open jarvis"). Press ESC to close.
"""

import tkinter as tk
import math
import random
import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import status_bridge

BG = "#03040a"
BLUE = "#00c8ff"
BLUE_DIM = "#0a4a5a"
RED = "#ff3b3b"
PURPLE = "#a855f7"
PINK = "#ec4899"
TEXT_DIM = "#4a7a8a"
PANEL_BORDER = "#0d3a4a"
TERMINAL_BG = "#050a12"

FAKE_LOGS = [
    "SYSTEM CHECK ... OK",
    "VOICE MODULE ... ACTIVE",
    "AI CORE ... READY",
    "MEMORY SYNC ... COMPLETE",
    "NETWORK ... CONNECTED",
    "SCANNING ENVIRONMENT ...",
    "ALL SYSTEMS NOMINAL",
    "AWAITING COMMAND ...",
    "SENSOR ARRAY ... ONLINE",
    "SECURITY PROTOCOL ... ENGAGED",
]


class Gauge:
    """A circular percentage gauge like CPU/RAM/GPU meters."""

    def __init__(self, canvas, x, y, radius, color, label, value):
        self.canvas = canvas
        self.x, self.y, self.radius = x, y, radius
        self.color = color
        self.label = label
        self.value = value

    def draw(self):
        r = self.radius

        self.canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r,
                                 outline=BLUE_DIM, width=3, tags="gauge")

        extent = -3.6 * self.value
        self.canvas.create_arc(self.x - r, self.y - r, self.x + r, self.y + r,
                                start=90, extent=extent, style="arc",
                                outline=self.color, width=3, tags="gauge")

        self.canvas.create_text(self.x, self.y, text=f"{self.value}%",
                                 fill=self.color, font=("Consolas", 11, "bold"), tags="gauge")
        self.canvas.create_text(self.x, self.y + r + 16, text=self.label,
                                 fill=TEXT_DIM, font=("Consolas", 9), tags="gauge")


class JarvisHUD:

    def __init__(self, root):

        self.root = root
        self.root.title("JARVIS")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg=BG)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()
        self.cx = self.width // 2
        self.cy = int(self.height * 0.42)

        self.canvas = tk.Canvas(root, width=self.width, height=self.height,
                                 bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.angle = 0
        self.pulse = 0
        self.log_lines = list(FAKE_LOGS[:6])
        self.log_timer = 0
        self.gauges = [
            Gauge(self.canvas, self.width * 0.10, self.height * 0.28, 45, BLUE, "CPU", 24),
            Gauge(self.canvas, self.width * 0.18, self.height * 0.40, 55, RED, "MEMORY", 96),
            Gauge(self.canvas, self.width * 0.10, self.height * 0.52, 45, BLUE, "GPU", 21),
        ]

        self.draw_static()
        self.animate()

    def draw_static(self):
        self.canvas.create_text(50, 30, text="STARK INDUSTRIES", fill=BLUE,
                                 font=("Consolas", 13, "bold"), anchor="w")
        self.canvas.create_text(self.width - 50, 30, text="ESC TO CLOSE", fill=TEXT_DIM,
                                 font=("Consolas", 10), anchor="e")
        self.canvas.create_line(30, 55, self.width - 30, 55, fill=PANEL_BORDER)

    def draw_gauges(self):
        self.canvas.delete("gauge")
        for g in self.gauges:
            g.draw()

    def draw_center_core(self):

        self.canvas.delete("core")

        status = status_bridge.get_status()

        if status == "listening":
            pulse_speed = 3.0
            pulse_amount = 14
            glow_color = "#00ffee"
            status_text = "STATUS: LISTENING"
        elif status == "speaking":
            pulse_speed = 5.0
            pulse_amount = 20
            glow_color = "#ffffff"
            status_text = "STATUS: SPEAKING"
        else:
            pulse_speed = 1.0
            pulse_amount = 6
            glow_color = BLUE
            status_text = "STATUS: ONLINE"

        r_outer = min(self.width, self.height) * 0.17

        for i in range(0, 360, 6):
            a = math.radians(i + self.angle)
            length = r_outer + pulse_amount * math.sin(math.radians(i * 3 + self.pulse * pulse_speed * 40))
            x1 = self.cx + (r_outer - 20) * math.cos(a)
            y1 = self.cy + (r_outer - 20) * math.sin(a)
            x2 = self.cx + length * math.cos(a)
            y2 = self.cy + length * math.sin(a)

            t = (i % 120) / 120
            color = PURPLE if t < 0.5 else PINK
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, tags="core")

        for i, r in enumerate([r_outer - 20, r_outer - 35, r_outer - 50]):
            self.canvas.create_oval(self.cx - r, self.cy - r, self.cx + r, self.cy + r,
                                     outline=glow_color, width=1, tags="core")

        core_r = r_outer - 65
        pulse_r = core_r + pulse_amount * 0.5 * math.sin(self.pulse * pulse_speed)
        self.canvas.create_oval(self.cx - pulse_r, self.cy - pulse_r,
                                 self.cx + pulse_r, self.cy + pulse_r,
                                 fill="#0a0520", outline=glow_color, width=3, tags="core")

        self.canvas.create_text(self.cx, self.cy, text="JARVIS", fill=glow_color,
                                 font=("Consolas", 17, "bold"), tags="core")
        self.canvas.create_text(self.cx, self.cy + r_outer + 28, text=status_text,
                                 fill=glow_color, font=("Consolas", 13, "bold"), tags="core")

    def draw_terminal(self):

        self.canvas.delete("terminal")

        box_x1 = self.cx - 320
        box_y1 = self.cy + 110
        box_x2 = self.cx + 320
        box_y2 = box_y1 + 170

        self.canvas.create_rectangle(box_x1, box_y1, box_x2, box_y2,
                                      fill=TERMINAL_BG, outline=PANEL_BORDER, width=2, tags="terminal")

        for i, line in enumerate(self.log_lines[-9:]):
            self.canvas.create_text(box_x1 + 14, box_y1 + 16 + i * 18,
                                     text=f"> {line}", fill=BLUE, anchor="w",
                                     font=("Consolas", 10), tags="terminal")

    def draw_right_panel(self):

        self.canvas.delete("rightpanel")

        rx = self.width - 130
        ry = self.height * 0.30

        # Fingerprint-style icon (concentric wavy arcs)
        for i, r in enumerate(range(15, 55, 8)):
            self.canvas.create_arc(rx - r, ry - r, rx + r, ry + r,
                                    start=30, extent=300, style="arc",
                                    outline=BLUE, width=2, tags="rightpanel")
        self.canvas.create_text(rx, ry + 70, text="ID VERIFIED", fill=TEXT_DIM,
                                 font=("Consolas", 9), tags="rightpanel")

        # Waveform bars
        wf_y = self.height * 0.52
        for i in range(20):
            x = rx - 60 + i * 6
            h = 10 + 20 * abs(math.sin(self.pulse + i * 0.4))
            self.canvas.create_line(x, wf_y, x, wf_y - h, fill=BLUE, width=2, tags="rightpanel")

        # Clock + date
        now = datetime.datetime.now()
        self.canvas.create_text(rx, self.height * 0.65, text=now.strftime("%H:%M:%S"),
                                 fill=BLUE, font=("Consolas", 18, "bold"), tags="rightpanel")
        self.canvas.create_text(rx, self.height * 0.68, text=now.strftime("%d %b %Y"),
                                 fill=TEXT_DIM, font=("Consolas", 10), tags="rightpanel")

        # Bottom empty panel box
        box_y1 = self.height * 0.70
        box_y2 = self.height * 0.92
        self.canvas.create_rectangle(rx - 120, box_y1, rx + 120, box_y2,
                                      fill="#050a12", outline=PANEL_BORDER, width=2, tags="rightpanel")
        self.canvas.create_text(rx, box_y1 + 18, text="AUX PANEL", fill=TEXT_DIM,
                                 font=("Consolas", 10), tags="rightpanel")

    def update_logs(self):
        self.log_timer += 1
        if self.log_timer > 90:
            self.log_timer = 0
            self.log_lines.append(random.choice(FAKE_LOGS))
            self.log_lines = self.log_lines[-7:]

    def animate(self):
        self.angle = (self.angle + 0.8) % 360
        self.pulse += 0.08
        self.update_logs()

        self.draw_gauges()
        self.draw_center_core()
        self.draw_terminal()
        self.draw_right_panel()

        self.root.after(30, self.animate)


if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisHUD(root)
    root.mainloop()