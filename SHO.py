import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

# Default parameters for SHM
defaults = {
    "Amplitude": 1.0,
    "Mass": 1.0,
    "Spring Constant": 1.0,
    "Phase": 0.0,
    "Duration": 10.0,
    "FPS": 60,
}


class SHMSimulator:
    def __init__(self):
        self.params = defaults.copy()
        self.setup_ui()
        self.compute_shm()
        self.initialize_animation()
        plt.show()

    def setup_ui(self):
        pass  # Overridden in subclass

    def compute_shm(self):
        A = self.params["Amplitude"]
        m = self.params["Mass"]
        k = self.params["Spring Constant"]
        phi = self.params["Phase"]
        duration = self.params["Duration"]
        fps = self.params["FPS"]

        omega = np.sqrt(k / m)
        self.t = np.linspace(0, duration, int(fps * duration))
        self.x = A * np.cos(omega * self.t + phi)
        self.v = -A * omega * np.sin(omega * self.t + phi)

        self.kinetic_energy = 0.5 * m * self.v**2
        self.potential_energy = 0.5 * k * self.x**2

        max_x = max(abs(self.x.max()), abs(self.x.min()), 1.0) * 1.1
        max_v = max(abs(self.v.max()), abs(self.v.min()), 1.0) * 1.1
        max_energy = max(np.max(self.kinetic_energy + self.potential_energy), 1.0) * 1.1

        self.pos_ax.set_xlim(0, duration)
        self.vel_ax.set_xlim(0, duration)
        self.energy_ax.set_xlim(0, duration)

        self.pos_ax.set_ylim(-max_x, max_x)
        self.vel_ax.set_ylim(-max_v, max_v)
        self.energy_ax.set_ylim(0, max_energy)
        self.mass_ax.set_xlim(-max_x, max_x)

        # Reset plot data
        self.pos_line.set_data([], [])
        self.vel_line.set_data([], [])
        self.kinetic_line.set_data([], [])
        self.potential_line.set_data([], [])
        self.mass_plot.set_data([self.x[0]], [0])

    def update(self, frame):
        self.mass_plot.set_data([self.x[frame]], [0])
        self.pos_line.set_data(self.t[: frame + 1], self.x[: frame + 1])
        self.vel_line.set_data(self.t[: frame + 1], self.v[: frame + 1])
        self.kinetic_line.set_data(
            self.t[: frame + 1], self.kinetic_energy[: frame + 1]
        )
        self.potential_line.set_data(
            self.t[: frame + 1], self.potential_energy[: frame + 1]
        )
        return (
            self.mass_plot,
            self.pos_line,
            self.vel_line,
            self.kinetic_line,
            self.potential_line,
        )

    def submit(self, event):
        for key in self.sliders:
            value = self.sliders[key].val
            if key in ["Mass", "Spring Constant", "Duration", "FPS"] and value <= 0:
                print(f"Invalid input for {key}. Resetting to default: {defaults[key]}")
                self.sliders[key].set_val(defaults[key])
                self.params[key] = defaults[key]
            else:
                self.params[key] = value

        self.compute_shm()

        # Stop existing animation if running
        if self.animating:
            self.ani.event_source.stop()
            self.start_button.label.set_text("Start Animation")
            self.animating = False

        self.fig.canvas.draw_idle()

    def toggle_animation(self, event):
        if self.animating:
            self.ani.event_source.stop()
            self.start_button.label.set_text("Start Animation")
            self.animating = False
        else:
            self.ani = FuncAnimation(
                self.fig,
                self.update,
                frames=len(self.t),
                interval=1000 / self.params["FPS"],
                blit=True,
                repeat=True,
            )
            self.start_button.label.set_text("Stop Animation")
            self.animating = True
        self.fig.canvas.draw_idle()

    def clear_animation(self, event):
        if self.animating:
            self.ani.event_source.stop()
            self.start_button.label.set_text("Start Animation")
            self.animating = False

        self.pos_line.set_data([], [])
        self.vel_line.set_data([], [])
        self.kinetic_line.set_data([], [])
        self.potential_line.set_data([], [])
        self.mass_plot.set_data([0], [0])

        self.fig.canvas.draw_idle()

    def initialize_animation(self):
        self.ani = FuncAnimation(
            self.fig,
            self.update,
            frames=len(self.t),
            interval=1000 / self.params["FPS"],
            blit=True,
            repeat=True,
        )
        self.ani.event_source.stop()


class ImprovedSHMSimulator(SHMSimulator):
    def setup_ui(self):
        self.fig = plt.figure(figsize=(8, 12))

        self.mass_ax = self.fig.add_subplot(4, 1, 1)
        self.pos_ax = self.fig.add_subplot(4, 1, 2)
        self.vel_ax = self.fig.add_subplot(4, 1, 3)
        self.energy_ax = self.fig.add_subplot(4, 1, 4)

        self.fig.subplots_adjust(bottom=0.35, hspace=0.5)

        (self.mass_plot,) = self.mass_ax.plot([], [], "o", markersize=20)
        (self.pos_line,) = self.pos_ax.plot([], [], label="Position (m)")
        (self.vel_line,) = self.vel_ax.plot([], [], label="Velocity (m/s)")
        (self.kinetic_line,) = self.energy_ax.plot(
            [], [], label="Kinetic Energy", color="blue"
        )
        (self.potential_line,) = self.energy_ax.plot(
            [], [], label="Potential Energy", color="orange"
        )

        self.mass_ax.axis("off")
        self.mass_ax.set_title("Mass on Spring")

        self.pos_ax.set_xlabel("Time (s)")
        self.pos_ax.set_ylabel("Position (m)")
        self.pos_ax.set_title("Position vs Time")
        self.pos_ax.grid(True)
        self.pos_ax.legend()

        self.vel_ax.set_xlabel("Time (s)")
        self.vel_ax.set_ylabel("Velocity (m/s)")
        self.vel_ax.set_title("Velocity vs Time")
        self.vel_ax.grid(True)
        self.vel_ax.legend()

        self.energy_ax.set_xlabel("Time (s)")
        self.energy_ax.set_ylabel("Energy (J)")
        self.energy_ax.set_title("Kinetic & Potential Energy vs Time")
        self.energy_ax.grid(True)
        self.energy_ax.legend()

        slider_params = {
            "Amplitude": (0.1, 5.0, defaults["Amplitude"]),
            "Mass": (0.1, 10.0, defaults["Mass"]),
            "Spring Constant": (0.1, 10.0, defaults["Spring Constant"]),
            "Phase": (-np.pi, np.pi, defaults["Phase"]),
            "Duration": (1.0, 20.0, defaults["Duration"]),
            "FPS": (10, 120, defaults["FPS"]),
        }

        self.sliders = {}
        for i, (key, (vmin, vmax, vinit)) in enumerate(slider_params.items()):
            axslider = plt.axes([0.15, 0.01 + i * 0.03, 0.65, 0.025])
            self.sliders[key] = Slider(
                axslider,
                key,
                vmin,
                vmax,
                valinit=vinit,
                valstep=0.1 if key != "FPS" else 1,
            )

        # Submit button
        ax_submit = plt.axes([0.87, 0.3, 0.12, 0.04])
        self.submit_button = Button(ax_submit, "Submit")
        self.submit_button.on_clicked(self.submit)

        # Start/Stop button
        ax_start = plt.axes([0.84, 0.25, 0.15, 0.04])
        self.start_button = Button(ax_start, "Start Animation")
        self.start_button.on_clicked(self.toggle_animation)

        # Clear button
        ax_clear = plt.axes([0.87, 0.2, 0.12, 0.04])
        self.clear_button = Button(ax_clear, "Clear")
        self.clear_button.on_clicked(self.clear_animation)

        self.animating = False
        self.fig.tight_layout(rect=[0, 0.3, 1, 0.95])


if __name__ == "__main__":
    sim = ImprovedSHMSimulator()
