import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Circle, Rectangle, Polygon
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches


class RigidBodyRotation:
    def __init__(self):
        self.setup_parameters()
        self.setup_plot()
        self.start_animation()

    def setup_parameters(self):
        # Simulation parameters
        self.dt = 0.02  # time step (s)
        self.t_max = 10.0  # simulation time (s)

        # Physical parameters
        self.mass = 1.0  # total mass (kg)
        self.radius = 0.5  # radius/length (m)
        self.torque = 1.0  # applied torque (N⋅m)
        self.moment_of_inertia = 0.0  # will be calculated based on object type

        # Object types and their properties
        self.object_types = {
            "Disk": {
                "shape": "disk",
                "I_factor": 0.5,
                "color": "blue",
            },  # I = 0.5 * m * r²
            "Ring": {"shape": "ring", "I_factor": 1.0, "color": "green"},  # I = m * r²
            "Rod": {
                "shape": "rod",
                "I_factor": 1 / 3,
                "color": "red",
            },  # I = (1/3) * m * L² (end rotation)
            "Sphere": {
                "shape": "sphere",
                "I_factor": 0.4,
                "color": "purple",
            },  # I = 0.4 * m * r²
        }
        self.current_type = "Disk"

        # Initial conditions
        self.theta = 0.0  # angular position (rad)
        self.omega = 0.0  # angular velocity (rad/s)
        self.alpha = 0.0  # angular acceleration (rad/s²)

        # Animation variables
        self.current_time = 0
        self.reset_simulation()

    def reset_simulation(self):
        """Reset simulation to initial conditions"""
        self.current_time = 0
        self.theta = 0.0
        self.omega = 0.0

        # Calculate moment of inertia based on object type
        if self.current_type == "Rod":
            # For rod rotating about end: I = (1/3) * m * L²
            self.moment_of_inertia = (1 / 3) * self.mass * (2 * self.radius) ** 2
        else:
            # For other shapes: I = factor * m * r²
            self.moment_of_inertia = (
                self.object_types[self.current_type]["I_factor"]
                * self.mass
                * self.radius**2
            )

        # Calculate angular acceleration: τ = I * α
        self.alpha = (
            self.torque / self.moment_of_inertia if self.moment_of_inertia > 0 else 0
        )

        # Arrays for plotting
        self.time_history = []
        self.theta_history = []
        self.omega_history = []
        self.alpha_history = []

    def update_physics(self):
        """Update angular position and velocity using physics equations"""
        # Update angular velocity: ω = ω₀ + α*t
        self.omega += self.alpha * self.dt

        # Update angular position: θ = θ₀ + ω*t
        self.theta += self.omega * self.dt

        # Keep theta in reasonable range for display
        if self.theta > 4 * np.pi:
            self.theta = self.theta % (2 * np.pi)

        # Update time
        self.current_time += self.dt

        # Store history for plotting
        self.time_history.append(self.current_time)
        self.theta_history.append(self.theta)
        self.omega_history.append(self.omega)
        self.alpha_history.append(self.alpha)

        # Limit history length to prevent memory issues
        if len(self.time_history) > 500:
            self.time_history.pop(0)
            self.theta_history.pop(0)
            self.omega_history.pop(0)
            self.alpha_history.pop(0)

    def setup_plot(self):
        # Create figure with subplots
        self.fig = plt.figure(figsize=(16, 10))

        # Main animation plot (left side, larger)
        self.ax_main = plt.subplot2grid((3, 3), (0, 0), rowspan=3, colspan=2)
        self.ax_main.set_xlim(-1.2, 1.2)
        self.ax_main.set_ylim(-1.2, 1.2)
        self.ax_main.set_aspect("equal")
        self.ax_main.grid(True, alpha=0.3)
        self.ax_main.set_title(
            "Rigid Body Rotation Simulation", fontsize=16, fontweight="bold"
        )

        # Add center point
        self.ax_main.plot(0, 0, "ko", markersize=8, label="Rotation Center")

        # Angular position vs time plot
        self.ax_pos = plt.subplot2grid((3, 3), (0, 2))
        self.ax_pos.set_xlabel("Time (s)")
        self.ax_pos.set_ylabel("θ (rad)")
        self.ax_pos.grid(True, alpha=0.3)
        self.ax_pos.set_title("Angular Position vs Time")

        # Angular velocity vs time plot
        self.ax_vel = plt.subplot2grid((3, 3), (1, 2))
        self.ax_vel.set_xlabel("Time (s)")
        self.ax_vel.set_ylabel("ω (rad/s)")
        self.ax_vel.grid(True, alpha=0.3)
        self.ax_vel.set_title("Angular Velocity vs Time")

        # Info panel
        self.ax_info = plt.subplot2grid((3, 3), (2, 2))
        self.ax_info.axis("off")

        # Create visual objects
        self.create_objects()

        # Add sliders and controls
        plt.subplots_adjust(bottom=0.25, right=0.95, left=0.08, top=0.92)

        # Slider positions
        slider_left = 0.15
        slider_width = 0.25
        slider_height = 0.02
        slider_spacing = 0.03

        ax_mass = plt.axes([slider_left, 0.18, slider_width, slider_height])
        ax_radius = plt.axes(
            [slider_left, 0.18 - slider_spacing, slider_width, slider_height]
        )
        ax_torque = plt.axes(
            [slider_left, 0.18 - 2 * slider_spacing, slider_width, slider_height]
        )

        self.slider_mass = Slider(
            ax_mass, "Mass (kg)", 0.1, 5.0, valinit=self.mass, valfmt="%.1f"
        )
        self.slider_radius = Slider(
            ax_radius, "Radius/Length (m)", 0.1, 1.0, valinit=self.radius, valfmt="%.1f"
        )
        self.slider_torque = Slider(
            ax_torque, "Torque (N⋅m)", 0.0, 5.0, valinit=self.torque, valfmt="%.1f"
        )

        # Add radio buttons for object type
        ax_radio = plt.axes([0.50, 0.08, 0.15, 0.15])
        self.radio = RadioButtons(ax_radio, list(self.object_types.keys()), active=0)

        # Add buttons
        ax_reset = plt.axes([0.70, 0.12, 0.08, 0.05])
        ax_pause = plt.axes([0.80, 0.12, 0.08, 0.05])

        self.button_reset = Button(ax_reset, "Reset")
        self.button_pause = Button(ax_pause, "Pause")

        # Connect widgets
        self.slider_mass.on_changed(self.update_parameters)
        self.slider_radius.on_changed(self.update_parameters)
        self.slider_torque.on_changed(self.update_parameters)
        self.radio.on_clicked(self.update_object_type)
        self.button_reset.on_clicked(self.reset_clicked)
        self.button_pause.on_clicked(self.pause_clicked)

        # Animation control
        self.paused = False

        # Create plot lines
        (self.line_theta,) = self.ax_pos.plot([], [], "b-", linewidth=2, label="θ")
        (self.line_omega,) = self.ax_vel.plot([], [], "r-", linewidth=2, label="ω")

        # Add legends
        self.ax_pos.legend(loc="upper left")
        self.ax_vel.legend(loc="upper left")

    def create_objects(self):
        """Create visual representation of the selected object"""
        # Clear existing objects
        for patch in list(self.ax_main.patches):
            patch.remove()

        # Clear existing lines
        for line in list(self.ax_main.lines):
            line.remove()

        # Add center point
        self.ax_main.plot(0, 0, "ko", markersize=8, label="Rotation Center")

        current_color = self.object_types[self.current_type]["color"]

        # Create object based on type - store multiple patches for complex objects
        self.object_patches = []

        if self.current_type == "Disk":
            # Solid disk with a radius line to show rotation
            disk = Circle(
                (0, 0),
                self.radius,
                fill=True,
                alpha=0.4,
                facecolor=current_color,
                edgecolor=current_color,
                linewidth=2,
            )
            self.ax_main.add_patch(disk)
            self.object_patches.append(disk)

        elif self.current_type == "Ring":
            # Hollow ring with spokes to show rotation
            outer_ring = Circle(
                (0, 0), self.radius, fill=False, color=current_color, linewidth=4
            )
            inner_ring = Circle(
                (0, 0), self.radius * 0.6, fill=False, color=current_color, linewidth=2
            )
            self.ax_main.add_patch(outer_ring)
            self.ax_main.add_patch(inner_ring)
            self.object_patches.extend([outer_ring, inner_ring])

        elif self.current_type == "Rod":
            # Rod rotating about center
            rod = Rectangle(
                (-self.radius, -0.05),
                2 * self.radius,
                0.1,
                fill=True,
                facecolor=current_color,
                edgecolor="black",
                linewidth=2,
            )
            self.ax_main.add_patch(rod)
            self.object_patches.append(rod)

        elif self.current_type == "Sphere":
            # Sphere with diameter line to show rotation
            sphere = Circle(
                (0, 0),
                self.radius,
                fill=True,
                alpha=0.4,
                facecolor=current_color,
                edgecolor=current_color,
                linewidth=2,
            )
            self.ax_main.add_patch(sphere)
            self.object_patches.append(sphere)

        # Add reference line to show rotation clearly
        (self.reference_line,) = self.ax_main.plot(
            [0, self.radius], [0, 0], "r-", linewidth=3, alpha=0.8
        )

        # Add a secondary reference line for better visibility
        (self.reference_line2,) = self.ax_main.plot(
            [0, -self.radius], [0, 0], "r-", linewidth=3, alpha=0.8
        )

        # Update axis limits based on object size
        limit = max(1.2, self.radius + 0.3)
        self.ax_main.set_xlim(-limit, limit)
        self.ax_main.set_ylim(-limit, limit)

    def update_parameters(self, val):
        """Update parameters when sliders change"""
        self.mass = self.slider_mass.val
        self.radius = self.slider_radius.val
        self.torque = self.slider_torque.val

        self.reset_simulation()
        self.create_objects()

    def update_object_type(self, label):
        """Update object type when radio button is clicked"""
        self.current_type = label
        self.reset_simulation()
        self.create_objects()

    def reset_clicked(self, event):
        """Reset button callback"""
        self.reset_simulation()
        # Clear plot histories
        self.line_theta.set_data([], [])
        self.line_omega.set_data([], [])
        # Clear the plot axes
        for ax in [self.ax_pos, self.ax_vel]:
            ax.clear()
            ax.grid(True, alpha=0.3)

        # Reset plot properties
        self.ax_pos.set_xlabel("Time (s)")
        self.ax_pos.set_ylabel("θ (rad)")
        self.ax_pos.set_title("Angular Position vs Time")

        self.ax_vel.set_xlabel("Time (s)")
        self.ax_vel.set_ylabel("ω (rad/s)")
        self.ax_vel.set_title("Angular Velocity vs Time")

        # Recreate plot lines
        (self.line_theta,) = self.ax_pos.plot([], [], "b-", linewidth=2, label="θ")
        (self.line_omega,) = self.ax_vel.plot([], [], "r-", linewidth=2, label="ω")

        self.ax_pos.legend(loc="upper left")
        self.ax_vel.legend(loc="upper left")

        # Reset object transforms
        import matplotlib.transforms as transforms

        for patch in self.object_patches:
            patch.set_transform(self.ax_main.transData)

    def pause_clicked(self, event):
        """Pause button callback"""
        self.paused = not self.paused
        self.button_pause.label.set_text("Resume" if self.paused else "Pause")

    def update_info_panel(self):
        """Update the information panel with current physics values"""
        self.ax_info.clear()
        self.ax_info.axis("off")

        # Calculate theoretical values for comparison
        theoretical_formulas = {
            "Disk": "I = ½mr²",
            "Ring": "I = mr²",
            "Rod": "I = ⅓mL²",
            "Sphere": "I = ⅖mr²",
        }

        info_text = f"""PHYSICS PARAMETERS:
Object: {self.current_type}
Formula: {theoretical_formulas[self.current_type]}
Mass: {self.mass:.1f} kg
Radius/Length: {self.radius:.1f} m
Torque: {self.torque:.1f} N⋅m

CALCULATED VALUES:
Moment of Inertia: {self.moment_of_inertia:.3f} kg⋅m²
Angular Acceleration: {self.alpha:.2f} rad/s²

CURRENT STATE:
Time: {self.current_time:.1f} s
Position: {self.theta:.2f} rad ({self.theta * 180 / np.pi:.1f}°)
Velocity: {self.omega:.2f} rad/s

NOTES:
• Larger I → slower acceleration
• Higher torque → faster acceleration
• Rod has highest I for same mass/size"""

        self.ax_info.text(
            0.05,
            0.95,
            info_text,
            transform=self.ax_info.transAxes,
            fontsize=8,
            verticalalignment="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5),
        )

    def animate_frame(self, frame):
        """Animation function called for each frame"""
        if not self.paused and self.current_time < self.t_max:
            self.update_physics()

        # Update object rotation - rotate all patches around center
        import matplotlib.transforms as transforms

        # Create rotation transform around the origin (0,0)
        rotation_transform = (
            transforms.Affine2D().rotate(self.theta) + self.ax_main.transData
        )

        # Apply rotation to all object patches
        for patch in self.object_patches:
            patch.set_transform(rotation_transform)

        # Update reference lines to show current orientation
        # Primary reference line
        ref_x = self.radius * np.cos(self.theta)
        ref_y = self.radius * np.sin(self.theta)
        self.reference_line.set_data([0, ref_x], [0, ref_y])

        # Secondary reference line (opposite direction)
        self.reference_line2.set_data([0, -ref_x], [0, -ref_y])

        # Update plots
        if len(self.time_history) > 1:
            self.line_theta.set_data(self.time_history, self.theta_history)
            self.line_omega.set_data(self.time_history, self.omega_history)

            # Update plot limits dynamically
            if len(self.time_history) > 10:
                for ax, data in [
                    (self.ax_pos, self.theta_history),
                    (self.ax_vel, self.omega_history),
                ]:
                    if data:
                        ax.set_xlim(min(self.time_history), max(self.time_history))
                        data_range = max(data) - min(data)
                        if data_range > 0:
                            ax.set_ylim(
                                min(data) - data_range * 0.1,
                                max(data) + data_range * 0.1,
                            )

        # Update info panel
        self.update_info_panel()

        return self.object_patches + [
            self.reference_line,
            self.reference_line2,
            self.line_theta,
            self.line_omega,
        ]

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
    print("🚀 Starting Rigid Body Rotation Simulation...")
    print("📊 Features:")
    print("  • Select object type: Disk, Ring, Rod, or Sphere")
    print("  • Adjust mass, radius/length, and applied torque")
    print("  • Watch real-time physics simulation")
    print("  • Compare moment of inertia effects")
    print("  • Reset or pause anytime")
    print("\n🎯 Key Physics Concepts:")
    print("  • Moment of Inertia (I) determines rotational resistance")
    print("  • Torque (τ) = I × Angular Acceleration (α)")
    print("  • Different shapes have different I formulas")
    print("  • Larger I → slower acceleration for same torque")

    try:
        simulation = RigidBodyRotation()
    except KeyboardInterrupt:
        print("\n⏹️  Simulation stopped by user")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback

        traceback.print_exc()
        plt.close("all")
