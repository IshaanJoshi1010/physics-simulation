import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Circle


class AtwoodMachine:
    def __init__(self):
        self.setup_parameters()
        self.setup_plot()
        self.start_animation()

    def setup_parameters(self):
        # Simulation parameters
        self.dt = 0.02  # time step (s)
        self.t_max = 10.0  # simulation time (s)

        # Physical parameters
        self.m1 = 1.0  # mass 1 (kg)
        self.m2 = 2.0  # mass 2 (kg)
        self.g = 9.81  # gravitational acceleration (m/s²)
        self.pulley_radius = 0.3  # pulley radius (m)
        self.string_length = 4.0  # total string length (m)

        # Initial conditions
        self.y1_0 = 1.5  # initial height of mass 1 (m)
        self.y2_0 = -1.5  # initial height of mass 2 (m)

        # Animation variables
        self.current_time = 0
        self.reset_simulation()

    def reset_simulation(self):
        """Reset simulation to initial conditions"""
        self.current_time = 0
        self.y1 = self.y1_0  # current position of mass 1
        self.y2 = self.y2_0  # current position of mass 2
        self.v1 = 0.0  # current velocity of mass 1
        self.v2 = 0.0  # current velocity of mass 2

        # Calculate physics
        self.acceleration = (self.m2 - self.m1) * self.g / (self.m1 + self.m2)
        self.tension = 2 * self.m1 * self.m2 * self.g / (self.m1 + self.m2)

        # Arrays for plotting
        self.time_history = []
        self.y1_history = []
        self.y2_history = []
        self.v1_history = []
        self.v2_history = []

    def update_physics(self):
        """Update positions and velocities using physics equations"""
        # Update velocities (mass 1 accelerates in direction of net force)
        self.v1 += self.acceleration * self.dt
        self.v2 -= self.acceleration * self.dt  # opposite direction

        # Update positions
        self.y1 += self.v1 * self.dt
        self.y2 += self.v2 * self.dt

        # Enforce string constraint (masses stay connected)
        # The distance between masses should equal string length
        current_separation = abs(self.y1 - self.y2)
        if current_separation > self.string_length:
            # Adjust positions to maintain string length
            midpoint = (self.y1 + self.y2) / 2
            if self.y1 > self.y2:
                self.y1 = midpoint + self.string_length / 2
                self.y2 = midpoint - self.string_length / 2
            else:
                self.y1 = midpoint - self.string_length / 2
                self.y2 = midpoint + self.string_length / 2

        # Update time
        self.current_time += self.dt

        # Store history for plotting
        self.time_history.append(self.current_time)
        self.y1_history.append(self.y1)
        self.y2_history.append(self.y2)
        self.v1_history.append(self.v1)
        self.v2_history.append(self.v2)

        # Limit history length to prevent memory issues
        if len(self.time_history) > 500:
            self.time_history.pop(0)
            self.y1_history.pop(0)
            self.y2_history.pop(0)
            self.v1_history.pop(0)
            self.v2_history.pop(0)

    def setup_plot(self):
        # Create figure with subplots
        self.fig = plt.figure(figsize=(14, 10))

        # Main animation plot (left side, larger)
        self.ax_main = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
        self.ax_main.set_xlim(-1.5, 1.5)
        self.ax_main.set_ylim(-3, 3)
        self.ax_main.set_aspect("equal")
        self.ax_main.grid(True, alpha=0.3)
        self.ax_main.set_title(
            "Atwood Machine Animation", fontsize=14, fontweight="bold"
        )
        self.ax_main.set_xlabel("Position (m)")
        self.ax_main.set_ylabel("Height (m)")

        # Position vs time plot
        self.ax_pos = plt.subplot2grid((3, 2), (0, 1))
        self.ax_pos.set_xlabel("Time (s)")
        self.ax_pos.set_ylabel("Position (m)")
        self.ax_pos.grid(True, alpha=0.3)
        self.ax_pos.set_title("Position vs Time")

        # Velocity vs time plot
        self.ax_vel = plt.subplot2grid((3, 2), (1, 1))
        self.ax_vel.set_xlabel("Time (s)")
        self.ax_vel.set_ylabel("Velocity (m/s)")
        self.ax_vel.grid(True, alpha=0.3)
        self.ax_vel.set_title("Velocity vs Time")

        # Info panel
        self.ax_info = plt.subplot2grid((3, 2), (2, 1))
        self.ax_info.axis("off")

        # Create visual objects
        self.create_objects()

        # Add sliders
        plt.subplots_adjust(bottom=0.25, right=0.95, left=0.08)

        # Slider positions
        slider_left = 0.15
        slider_width = 0.3
        slider_height = 0.02

        ax_m1 = plt.axes([slider_left, 0.15, slider_width, slider_height])
        ax_m2 = plt.axes([slider_left, 0.12, slider_width, slider_height])
        ax_length = plt.axes([slider_left, 0.09, slider_width, slider_height])

        self.slider_m1 = Slider(
            ax_m1, "Mass 1 (kg)", 0.1, 5.0, valinit=self.m1, valfmt="%.1f"
        )
        self.slider_m2 = Slider(
            ax_m2, "Mass 2 (kg)", 0.1, 5.0, valinit=self.m2, valfmt="%.1f"
        )
        self.slider_length = Slider(
            ax_length, "String (m)", 2.0, 6.0, valinit=self.string_length, valfmt="%.1f"
        )

        # Add buttons
        ax_reset = plt.axes([0.55, 0.12, 0.08, 0.05])
        ax_pause = plt.axes([0.65, 0.12, 0.08, 0.05])

        self.button_reset = Button(ax_reset, "Reset")
        self.button_pause = Button(ax_pause, "Pause")

        # Connect widgets
        self.slider_m1.on_changed(self.update_parameters)
        self.slider_m2.on_changed(self.update_parameters)
        self.slider_length.on_changed(self.update_parameters)
        self.button_reset.on_clicked(self.reset_clicked)
        self.button_pause.on_clicked(self.pause_clicked)

        # Animation control
        self.paused = False

        # Create plot lines
        (self.line_y1,) = self.ax_pos.plot(
            [], [], "b-", linewidth=2, label=f"Mass 1 ({self.m1:.1f} kg)"
        )
        (self.line_y2,) = self.ax_pos.plot(
            [], [], "r-", linewidth=2, label=f"Mass 2 ({self.m2:.1f} kg)"
        )
        (self.line_v1,) = self.ax_vel.plot(
            [], [], "b-", linewidth=2, label=f"Mass 1 velocity"
        )
        (self.line_v2,) = self.ax_vel.plot(
            [], [], "r-", linewidth=2, label=f"Mass 2 velocity"
        )

        # Add legends
        self.ax_pos.legend(loc="upper right")
        self.ax_vel.legend(loc="upper right")

    def create_objects(self):
        # Create pulley (fixed at origin)
        self.pulley = Circle(
            (0, 0), self.pulley_radius, fill=False, color="black", linewidth=3
        )
        self.ax_main.add_patch(self.pulley)

        # Create masses (circles with size proportional to mass)
        mass1_size = 0.1 + self.m1 * 0.05
        mass2_size = 0.1 + self.m2 * 0.05

        self.mass1 = Circle((-0.5, self.y1), mass1_size, color="blue", alpha=0.8)
        self.mass2 = Circle((0.5, self.y2), mass2_size, color="red", alpha=0.8)
        self.ax_main.add_patch(self.mass1)
        self.ax_main.add_patch(self.mass2)

        # Create strings
        (self.string1,) = self.ax_main.plot(
            [-self.pulley_radius, -0.5], [0, self.y1], "k-", linewidth=2
        )
        (self.string2,) = self.ax_main.plot(
            [self.pulley_radius, 0.5], [0, self.y2], "k-", linewidth=2
        )

        # Add mass labels
        self.mass1_text = self.ax_main.text(
            -0.5,
            self.y1 - 0.3,
            f"m₁\n{self.m1:.1f}kg",
            ha="center",
            va="top",
            fontweight="bold",
        )
        self.mass2_text = self.ax_main.text(
            0.5,
            self.y2 - 0.3,
            f"m₂\n{self.m2:.1f}kg",
            ha="center",
            va="top",
            fontweight="bold",
        )

    def update_parameters(self, val):
        """Update parameters when sliders change"""
        self.m1 = self.slider_m1.val
        self.m2 = self.slider_m2.val
        self.string_length = self.slider_length.val

        # Update mass sizes
        mass1_size = 0.1 + self.m1 * 0.05
        mass2_size = 0.1 + self.m2 * 0.05
        self.mass1.set_radius(mass1_size)
        self.mass2.set_radius(mass2_size)

        # Update labels
        self.line_y1.set_label(f"Mass 1 ({self.m1:.1f} kg)")
        self.line_y2.set_label(f"Mass 2 ({self.m2:.1f} kg)")
        self.ax_pos.legend(loc="upper right")

        self.reset_simulation()

    def reset_clicked(self, event):
        """Reset button callback"""
        self.reset_simulation()
        # Clear plot histories
        self.line_y1.set_data([], [])
        self.line_y2.set_data([], [])
        self.line_v1.set_data([], [])
        self.line_v2.set_data([], [])

    def pause_clicked(self, event):
        """Pause button callback"""
        self.paused = not self.paused
        self.button_pause.label.set_text("Resume" if self.paused else "Pause")

    def update_info_panel(self):
        """Update the information panel with current physics values"""
        self.ax_info.clear()
        self.ax_info.axis("off")

        info_text = f"""Physics Information:
        
Acceleration: {self.acceleration:.2f} m/s²
String Tension: {self.tension:.2f} N
        
Current State:
Time: {self.current_time:.1f} s
Mass 1: y={self.y1:.2f}m, v={self.v1:.2f}m/s
Mass 2: y={self.y2:.2f}m, v={self.v2:.2f}m/s

Net Force on System:
F_net = (m₂ - m₁)g = {(self.m2 - self.m1) * self.g:.1f} N
        """

        self.ax_info.text(
            0.05,
            0.95,
            info_text,
            transform=self.ax_info.transAxes,
            fontsize=9,
            verticalalignment="top",
            fontfamily="monospace",
        )

    def animate_frame(self, frame):
        """Animation function called for each frame"""
        if not self.paused and self.current_time < self.t_max:
            self.update_physics()

        # Update mass positions
        self.mass1.center = (-0.5, self.y1)
        self.mass2.center = (0.5, self.y2)

        # Update strings
        self.string1.set_data([-self.pulley_radius, -0.5], [0, self.y1])
        self.string2.set_data([self.pulley_radius, 0.5], [0, self.y2])

        # Update mass labels
        self.mass1_text.set_position((-0.5, self.y1 - 0.3))
        self.mass1_text.set_text(f"m₁\n{self.m1:.1f}kg")
        self.mass2_text.set_position((0.5, self.y2 - 0.3))
        self.mass2_text.set_text(f"m₂\n{self.m2:.1f}kg")

        # Update plots
        if len(self.time_history) > 1:
            self.line_y1.set_data(self.time_history, self.y1_history)
            self.line_y2.set_data(self.time_history, self.y2_history)
            self.line_v1.set_data(self.time_history, self.v1_history)
            self.line_v2.set_data(self.time_history, self.v2_history)

            # Update plot limits
            if len(self.time_history) > 10:
                for ax in [self.ax_pos, self.ax_vel]:
                    ax.relim()
                    ax.autoscale_view()

        # Update info panel
        self.update_info_panel()

        return (
            self.mass1,
            self.mass2,
            self.string1,
            self.string2,
            self.mass1_text,
            self.mass2_text,
            self.line_y1,
            self.line_y2,
            self.line_v1,
            self.line_v2,
        )

    def start_animation(self):
        """Start the animation"""
        self.animation = FuncAnimation(
            self.fig,
            self.animate_frame,
            interval=50,
            blit=False,
            cache_frame_data=False,
        )

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    print("Starting Atwood Machine Simulation...")
    print("Use sliders to adjust masses and string length")
    print("Click Reset to restart, Pause to pause/resume")

    try:
        machine = AtwoodMachine()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        plt.close("all")
