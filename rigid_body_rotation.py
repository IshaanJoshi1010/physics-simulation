import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
import matplotlib.transforms as transforms


class RigidBodyRotation:
    def __init__(self):
        self.setup_parameters()
        self.setup_plot()
        self.start_animation()

    def setup_parameters(self):
        self.dt = 0.02
        self.t_max = 10.0
        self.mass = 1.0
        self.radius = 0.5
        self.torque = 1.0
        self.moment_of_inertia = 0.0
        self.object_types = {
            "Disk": {"shape": "disk", "I_factor": 0.5, "color": "blue"},
            "Ring": {"shape": "ring", "I_factor": 1.0, "color": "green"},
            "Rod": {"shape": "rod", "I_factor": 1 / 3, "color": "red"},
            "Sphere": {"shape": "sphere", "I_factor": 0.4, "color": "purple"},
        }
        self.current_type = "Disk"
        self.theta = 0.0
        self.omega = 0.0
        self.alpha = 0.0
        self.current_time = 0
        self.reset_simulation()

    def reset_simulation(self):
        self.current_time = 0
        self.theta = 0.0
        self.omega = 0.0
        if self.current_type == "Rod":
            self.moment_of_inertia = (1 / 3) * self.mass * (2 * self.radius) ** 2
        else:
            self.moment_of_inertia = (
                self.object_types[self.current_type]["I_factor"]
                * self.mass
                * self.radius**2
            )
        self.alpha = self.torque / self.moment_of_inertia
        self.time_history = []
        self.theta_history = []
        self.omega_history = []
        self.alpha_history = []

    def setup_plot(self):
        self.fig = plt.figure(figsize=(12, 8))

        gs = self.fig.add_gridspec(3, 2, height_ratios=[2, 1, 0.5], width_ratios=[1, 1])

        self.ax_main = self.fig.add_subplot(gs[0:2, 0])
        self.ax_main.set_xlim(-2, 2)
        self.ax_main.set_ylim(-2, 2)
        self.ax_main.set_aspect("equal")
        self.ax_main.grid(True, alpha=0.3)
        self.ax_main.set_title("Rigid Body Rotation", fontsize=14, fontweight="bold")

        self.ax_theta = self.fig.add_subplot(gs[0, 1])
        self.ax_theta.set_xlabel("Time (s)")
        self.ax_theta.set_ylabel("Angle (rad)")
        self.ax_theta.grid(True, alpha=0.3)
        self.ax_theta.set_title("Angular Position vs Time")

        self.ax_omega = self.fig.add_subplot(gs[1, 1])
        self.ax_omega.set_xlabel("Time (s)")
        self.ax_omega.set_ylabel("Angular Velocity (rad/s)")
        self.ax_omega.grid(True, alpha=0.3)
        self.ax_omega.set_title("Angular Velocity vs Time")

        self.ax_info = self.fig.add_subplot(gs[2, :])
        self.ax_info.axis("off")

        plt.subplots_adjust(bottom=0.25, right=0.95, left=0.08, top=0.92, hspace=0.3)

        slider_left = 0.15
        slider_width = 0.3
        slider_height = 0.02
        slider_spacing = 0.03

        ax_mass = plt.axes([slider_left, 0.08, slider_width, slider_height])
        ax_radius = plt.axes(
            [slider_left, 0.08 - slider_spacing, slider_width, slider_height]
        )
        ax_torque = plt.axes(
            [slider_left, 0.08 - 2 * slider_spacing, slider_width, slider_height]
        )

        self.slider_mass = Slider(
            ax_mass, "Mass (kg)", 0.1, 5.0, valinit=self.mass, valfmt="%.1f"
        )
        self.slider_radius = Slider(
            ax_radius, "Radius (m)", 0.1, 1.0, valinit=self.radius, valfmt="%.1f"
        )
        self.slider_torque = Slider(
            ax_torque, "Torque (N⋅m)", 0.1, 5.0, valinit=self.torque, valfmt="%.1f"
        )

        ax_type = plt.axes([0.55, 0.15, 0.3, 0.1])
        self.radio_type = RadioButtons(
            ax_type,
            list(self.object_types.keys()),
            active=0,
            activecolor=self.object_types["Disk"]["color"],
        )

        ax_reset = plt.axes([0.70, 0.02, 0.08, 0.05])
        ax_pause = plt.axes([0.80, 0.02, 0.08, 0.05])

        self.button_reset = Button(ax_reset, "Reset")
        self.button_pause = Button(ax_pause, "Pause")

        self.slider_mass.on_changed(self.update_parameters)
        self.slider_radius.on_changed(self.update_parameters)
        self.slider_torque.on_changed(self.update_parameters)
        self.radio_type.on_clicked(self.update_type)
        self.button_reset.on_clicked(self.reset_clicked)
        self.button_pause.on_clicked(self.pause_clicked)

        self.paused = False

        (self.line_theta,) = self.ax_theta.plot(
            [], [], "b-", linewidth=2, label="Angle"
        )
        (self.line_omega,) = self.ax_omega.plot(
            [], [], "r-", linewidth=2, label="Angular Velocity"
        )

        self.ax_theta.legend(loc="upper left")
        self.ax_omega.legend(loc="upper left")

    def create_objects(self):
        for patch in list(self.ax_main.patches):
            patch.remove()
        for line in list(self.ax_main.lines):
            line.remove()

        self.ax_main.plot(0, 0, "ko", markersize=8, label="Rotation Center")
        current_color = self.object_types[self.current_type]["color"]
        self.object_patches = []

        rotation_transform = (
            transforms.Affine2D().rotate(self.theta) + self.ax_main.transData
        )

        if self.current_type == "Disk":
            disk = Circle(
                (0, 0),
                self.radius,
                fill=True,
                alpha=0.4,
                facecolor=current_color,
                edgecolor=current_color,
                linewidth=2,
            )
            disk.set_transform(rotation_transform)
            self.ax_main.add_patch(disk)
            self.object_patches.append(disk)

        elif self.current_type == "Ring":
            outer_ring = Circle(
                (0, 0), self.radius, fill=False, color=current_color, linewidth=4
            )
            inner_ring = Circle(
                (0, 0), self.radius * 0.6, fill=False, color=current_color, linewidth=2
            )
            outer_ring.set_transform(rotation_transform)
            inner_ring.set_transform(rotation_transform)
            self.ax_main.add_patch(outer_ring)
            self.ax_main.add_patch(inner_ring)
            self.object_patches.extend([outer_ring, inner_ring])

        elif self.current_type == "Rod":
            rod = Rectangle(
                (-self.radius, -0.05),
                2 * self.radius,
                0.1,
                fill=True,
                facecolor=current_color,
                edgecolor="black",
                linewidth=2,
            )
            rod.set_transform(rotation_transform)
            self.ax_main.add_patch(rod)
            self.object_patches.append(rod)

        elif self.current_type == "Sphere":
            sphere = Circle(
                (0, 0),
                self.radius,
                fill=True,
                facecolor=current_color,
                edgecolor="black",
                linewidth=2,
            )
            sphere.set_transform(rotation_transform)
            self.ax_main.add_patch(sphere)
            self.object_patches.append(sphere)

        self.ax_main.legend(loc="upper right")

    def update_physics(self):
        if not self.paused and self.current_time < self.t_max:
            self.omega += self.alpha * self.dt
            self.theta += self.omega * self.dt
            self.current_time += self.dt

            self.time_history.append(self.current_time)
            self.theta_history.append(self.theta)
            self.omega_history.append(self.omega)
            self.alpha_history.append(self.alpha)

            if len(self.time_history) > 500:
                self.time_history.pop(0)
                self.theta_history.pop(0)
                self.omega_history.pop(0)
                self.alpha_history.pop(0)

    def update_parameters(self, val):
        self.mass = self.slider_mass.val
        self.radius = self.slider_radius.val
        self.torque = self.slider_torque.val
        self.reset_simulation()
        self.create_objects()

    def update_type(self, label):
        self.current_type = label
        self.radio_type.activecolor = self.object_types[label]["color"]
        self.reset_simulation()
        self.create_objects()

    def reset_clicked(self, event):
        self.reset_simulation()
        self.line_theta.set_data([], [])
        self.line_omega.set_data([], [])
        for ax in [self.ax_theta, self.ax_omega]:
            ax.clear()
            ax.grid(True, alpha=0.3)

        self.ax_theta.set_xlabel("Time (s)")
        self.ax_theta.set_ylabel("Angle (rad)")
        self.ax_theta.set_title("Angular Position vs Time")

        self.ax_omega.set_xlabel("Time (s)")
        self.ax_omega.set_ylabel("Angular Velocity (rad/s)")
        self.ax_omega.set_title("Angular Velocity vs Time")

        (self.line_theta,) = self.ax_theta.plot(
            [], [], "b-", linewidth=2, label="Angle"
        )
        (self.line_omega,) = self.ax_omega.plot(
            [], [], "r-", linewidth=2, label="Angular Velocity"
        )

        self.ax_theta.legend(loc="upper left")
        self.ax_omega.legend(loc="upper left")

        self.create_objects()

    def pause_clicked(self, event):
        self.paused = not self.paused
        self.button_pause.label.set_text("Resume" if self.paused else "Pause")

    def update_info_panel(self):
        self.ax_info.clear()
        self.ax_info.axis("off")

        info_text = f"""PHYSICS PARAMETERS:
Mass: {self.mass:.1f} kg
Radius: {self.radius:.1f} m
Torque: {self.torque:.1f} N⋅m
Moment of Inertia: {self.moment_of_inertia:.3f} kg⋅m²

CURRENT STATE:
Time: {self.current_time:.1f} s
Angle: {self.theta:.2f} rad
Angular Velocity: {self.omega:.2f} rad/s
Angular Acceleration: {self.alpha:.2f} rad/s²

OBJECT TYPE: {self.current_type}"""

        self.ax_info.text(
            0.05,
            0.95,
            info_text,
            transform=self.ax_info.transAxes,
            fontsize=10,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5),
        )

    def animate_frame(self, frame):
        self.update_physics()
        self.create_objects()

        if len(self.time_history) > 1:
            self.line_theta.set_data(self.time_history, self.theta_history)
            self.line_omega.set_data(self.time_history, self.omega_history)

            if len(self.time_history) > 10:
                for ax, data in [
                    (self.ax_theta, self.theta_history),
                    (self.ax_omega, self.omega_history),
                ]:
                    if data:
                        ax.set_xlim(min(self.time_history), max(self.time_history))
                        data_range = max(data) - min(data)
                        if data_range > 0:
                            ax.set_ylim(
                                min(data) - data_range * 0.1,
                                max(data) + data_range * 0.1,
                            )

        self.update_info_panel()

        return (
            self.ax_main.patches
            + self.ax_main.lines
            + [self.line_theta, self.line_omega]
        )

    def start_animation(self):
        self.animation = FuncAnimation(
            self.fig,
            self.animate_frame,
            interval=50,
            blit=False,
            cache_frame_data=False,
        )
        plt.show()


if __name__ == "__main__":
    RigidBodyRotation()
