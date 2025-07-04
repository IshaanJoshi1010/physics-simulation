import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation


class ProjectileMotion:
    def __init__(self):
        self.g = 9.81
        self.anim = None
        self.setup_parameters()
        self.setup_plot()
        self.animate()

    def setup_parameters(self):
        self.v0 = 20.0
        self.angle = 45.0
        self.h0 = 0.0
        self.dt = 0.05
        self.update_trajectory()

    def update_trajectory(self):
        theta = np.radians(self.angle)
        self.v0x = self.v0 * np.cos(theta)
        self.v0y = self.v0 * np.sin(theta)
        self.time_of_flight = (
            self.v0y + np.sqrt(self.v0y**2 + 2 * self.g * self.h0)
        ) / self.g
        self.time = np.arange(0, self.time_of_flight + self.dt, self.dt)
        self.x = self.v0x * self.time
        self.y = self.h0 + self.v0y * self.time - 0.5 * self.g * self.time**2
        self.max_height = self.h0 + (self.v0y**2) / (2 * self.g)
        self.range = self.v0x * self.time_of_flight

    def setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        plt.subplots_adjust(bottom=0.3)
        (self.line,) = self.ax.plot([], [], "b-", lw=2)
        (self.particle,) = self.ax.plot([], [], "ro", markersize=10)
        self.ax.set_xlim(0, 50)
        self.ax.set_ylim(0, 30)
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.grid(True)
        self.ax.set_title("Projectile Motion Simulator")

        ax_v0 = plt.axes([0.2, 0.2, 0.6, 0.03])
        ax_angle = plt.axes([0.2, 0.15, 0.6, 0.03])
        ax_h0 = plt.axes([0.2, 0.1, 0.6, 0.03])

        self.slider_v0 = Slider(ax_v0, "Initial Velocity (m/s)", 1, 50, valinit=self.v0)
        self.slider_angle = Slider(
            ax_angle, "Launch Angle (degrees)", 0, 90, valinit=self.angle
        )
        self.slider_h0 = Slider(ax_h0, "Initial Height (m)", 0, 20, valinit=self.h0)

        ax_reset = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.button_reset = Button(ax_reset, "Reset")

        self.slider_v0.on_changed(self.update)
        self.slider_angle.on_changed(self.update)
        self.slider_h0.on_changed(self.update)
        self.button_reset.on_clicked(self.reset)

    def update(self, val):
        self.v0 = self.slider_v0.val
        self.angle = self.slider_angle.val
        self.h0 = self.slider_h0.val
        self.update_trajectory()
        self.ax.set_xlim(0, max(50, self.range * 1.2))
        self.ax.set_ylim(0, max(30, self.max_height * 1.2))
        if self.anim:
            self.anim.event_source.stop()
        self.animate()

    def reset(self, event):
        self.slider_v0.reset()
        self.slider_angle.reset()
        self.slider_h0.reset()

    def animate(self):
        def init():
            self.line.set_data([], [])
            self.particle.set_data([], [])
            return self.line, self.particle

        def update(frame):
            self.line.set_data(self.x[:frame], self.y[:frame])
            self.particle.set_data([self.x[frame]], [self.y[frame]])
            return self.line, self.particle

        self.anim = FuncAnimation(
            self.fig,
            update,
            frames=len(self.time),
            init_func=init,
            blit=True,
            interval=20,
        )
        plt.show()


if __name__ == "__main__":
    ProjectileMotion()
