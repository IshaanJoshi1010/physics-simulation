import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import TextBox, Button


class LineDrawer:
    def __init__(self, ax, x_quad, y_quad):
        self.ax = ax
        self.x = x_quad
        self.y = y_quad
        self.line = None
        self.angle = 0
        self.line_offset = [0, 0]
        self.snap_target_index = 100

        self.cid_key_press = ax.figure.canvas.mpl_connect(
            "key_press_event", self.on_key_press
        )

        # Angle input
        self.text_box_ax = plt.axes([0.6, 0.01, 0.3, 0.05])
        self.text_box = TextBox(self.text_box_ax, "Angle: ")
        self.text_box.on_submit(self.insert_line_at_angle)

        # SNAP button
        self.snap_button_ax = plt.axes([0.3, 0.01, 0.2, 0.05])
        self.snap_button = Button(self.snap_button_ax, "SNAP!")
        self.snap_button.on_clicked(self.snap)

        # TRIM button
        self.trim_button_ax = plt.axes([0.05, 0.01, 0.2, 0.05])
        self.trim_button = Button(self.trim_button_ax, "TRIM")
        self.trim_button.on_clicked(self.trim)

        # Snap x input
        self.snap_x_box_ax = plt.axes([0.45, 0.07, 0.4, 0.05])
        self.snap_x_box = TextBox(self.snap_x_box_ax, "Snap to x =")
        self.snap_x_box.on_submit(self.update_snap_index)

    def insert_line_at_angle(self, text):
        try:
            self.angle = float(text)
            rad = np.radians(self.angle)
            # Get current axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Compute maximum required length to span the entire diagonal of the plot
            full_length = np.hypot(xlim[1] - xlim[0], ylim[1] - ylim[0])

            x_end = full_length * np.cos(rad) / 2
            y_end = full_length * np.sin(rad) / 2

            if self.line:
                self.line.remove()

            self.line = Line2D(
                [-x_end + self.line_offset[0], x_end + self.line_offset[0]],
                [-y_end + self.line_offset[1], y_end + self.line_offset[1]],
                color="red",
            )
            self.ax.add_line(self.line)
            self.ax.figure.canvas.draw()
        except ValueError:
            print("Invalid input. Please enter a numeric angle.")

    def move_line(self, dx, dy):
        if self.line:
            x_data, y_data = self.line.get_data()
            new_x = [x + dx for x in x_data]
            new_y = [y + dy for y in y_data]
            self.line.set_data(new_x, new_y)
            self.ax.figure.canvas.draw()
        self.line_offset[0] += dx
        self.line_offset[1] += dy

    def rotate_line(self, deg):
        if self.line:
            self.angle += deg
            rad = np.radians(self.angle)
            length = 1
            x_end = length * np.cos(rad)
            y_end = length * np.sin(rad)
            self.line.set_data(
                [-x_end + self.line_offset[0], x_end + self.line_offset[0]],
                [-y_end + self.line_offset[1], y_end + self.line_offset[1]],
            )
            self.text_box.set_val(str(self.angle))
            self.ax.figure.canvas.draw()

    def on_key_press(self, event):
        if event.key == "ctrl+j":
            self.move_line(0, 0.0020)
        elif event.key == "ctrl+m":
            self.move_line(0, -0.0020)
        elif event.key == "ctrl+n":
            self.move_line(-0.0020, 0)
        elif event.key == "ctrl+,":
            self.move_line(0.0020, 0)
        elif event.key == "j":
            self.move_line(0, 0.0001)
        elif event.key == "m":
            self.move_line(0, -0.0001)
        elif event.key == "n":
            self.move_line(-0.0001, 0)
        elif event.key == ",":
            self.move_line(0.0001, 0)
        elif event.key == "[":
            self.rotate_line(1)
        elif event.key == "]":
            self.rotate_line(-1)

    def update_snap_index(self, text):
        try:
            x_val = float(text)
            idx = np.argmin(np.abs(self.x - x_val))
            self.snap_target_index = idx
            print(f"Updated snap index to point closest to x = {x_val}")
        except ValueError:
            print("Invalid input. Enter a numeric x-value.")

    def snap(self, event=None):
        if not self.line:
            print("No line to snap.")
            return
        idx = self.snap_target_index
        x_targ = self.x[idx]
        y_targ = self.y[idx]

        x_line, y_line = self.line.get_data()
        mx = (x_line[0] + x_line[1]) / 2
        my = (y_line[0] + y_line[1]) / 2

        dx = x_targ - mx
        dy = y_targ - my

        x_prime = [x + dx for x in x_line]
        y_prime = [y + dy for y in y_line]

        self.line.set_data(x_prime, y_prime)
        self.line_offset[0] += dx
        self.line_offset[1] += dy
        self.line.figure.canvas.draw()

    def trim(self, event=None):
        if self.line is None:
            print("Give an Angle")
            return

        x_line, y_line = self.line.get_data()
        x0, y0 = x_line[0], y_line[0]
        x1, y1 = x_line[1], y_line[1]
        dx = x1 - x0
        dy = y1 - y0

        def point_line_dist(xp, yp):
            t = ((xp - x0) * dx + (yp - y0) * dy) / (dx**2 + dy**2)
            t = np.clip(t, 0, 1)
            x_proj = x0 + t * dx
            y_proj = y0 + t * dy
            return np.sqrt((xp - x_proj) ** 2 + (yp - y_proj) ** 2)

        dists = point_line_dist(self.x, self.y)
        idxs = np.argsort(dists)[:2]
        idx1, idx2 = np.sort(idxs)

        self.line.set_data([self.x[idx1], self.x[idx2]], [self.y[idx1], self.y[idx2]])
        self.ax.figure.canvas.draw()
