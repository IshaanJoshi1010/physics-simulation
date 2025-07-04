import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle


class ElasticCollision:
    def __init__(self):
        self.setup_parameters()
        self.setup_plot()
        self.animate()

    def setup_parameters(self):
        # Block parameters
        self.m1 = 1.0  # mass of block 1 (kg)
        self.m2 = 2.0  # mass of block 2 (kg)
        self.v1 = 2.0  # initial velocity of block 1 (m/s)
        self.v2 = -1.0  # initial velocity of block 2 (m/s)

        # Wall parameters
        self.wall_left = -5.0
        self.wall_right = 5.0

        # Block dimensions
        self.block_width = 0.5
        self.block_height = 0.5

        # Initial positions
        self.x1_init = -2.0  # initial position of block 1
        self.x2_init = 2.0  # initial position of block 2

        # Simulation parameters
        self.dt = 0.01  # smaller time step for smoother animation
        self.t_max = 20.0  # longer simulation time
        self.frame_skip = 2  # only show every nth frame for performance

        # Initialize simulation
        self.reset_simulation()

    def reset_simulation(self):
        """Reset the simulation with current parameters"""
        # Current state
        self.x1 = self.x1_init
        self.x2 = self.x2_init
        self.current_v1 = self.v1
        self.current_v2 = self.v2
        self.t = 0.0

        # For collision detection
        self.last_collision_time = -1.0
        self.collision_cooldown = 0.1  # prevent multiple collisions in short time

    def update_positions(self):
        """Update positions for one time step"""
        # Store previous positions
        prev_x1, prev_x2 = self.x1, self.x2

        # Update positions
        self.x1 += self.current_v1 * self.dt
        self.x2 += self.current_v2 * self.dt
        self.t += self.dt

        # Check wall collisions for block 1
        if self.x1 - self.block_width / 2 <= self.wall_left:
            self.x1 = self.wall_left + self.block_width / 2
            self.current_v1 = -self.current_v1
        elif self.x1 + self.block_width / 2 >= self.wall_right:
            self.x1 = self.wall_right - self.block_width / 2
            self.current_v1 = -self.current_v1

        # Check wall collisions for block 2
        if self.x2 - self.block_width / 2 <= self.wall_left:
            self.x2 = self.wall_left + self.block_width / 2
            self.current_v2 = -self.current_v2
        elif self.x2 + self.block_width / 2 >= self.wall_right:
            self.x2 = self.wall_right - self.block_width / 2
            self.current_v2 = -self.current_v2

        # Check block-block collision
        distance = abs(self.x1 - self.x2)
        if (
            distance <= self.block_width
            and self.t - self.last_collision_time > self.collision_cooldown
        ):
            # Only collide if blocks are moving toward each other
            relative_velocity = self.current_v1 - self.current_v2
            if (self.x1 < self.x2 and relative_velocity > 0) or (
                self.x1 > self.x2 and relative_velocity < 0
            ):
                # Separate blocks to prevent overlap
                overlap = self.block_width - distance
                if self.x1 < self.x2:
                    self.x1 -= overlap / 2
                    self.x2 += overlap / 2
                else:
                    self.x1 += overlap / 2
                    self.x2 -= overlap / 2

                # Calculate new velocities using elastic collision equations
                v1_new = (
                    (self.m1 - self.m2) * self.current_v1
                    + 2 * self.m2 * self.current_v2
                ) / (self.m1 + self.m2)
                v2_new = (
                    (self.m2 - self.m1) * self.current_v2
                    + 2 * self.m1 * self.current_v1
                ) / (self.m1 + self.m2)

                self.current_v1 = v1_new
                self.current_v2 = v2_new
                self.last_collision_time = self.t

    def setup_plot(self):
        # Create figure
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111)

        # Setup animation plot
        self.ax.set_xlim(self.wall_left - 1, self.wall_right + 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect("equal")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Elastic Collision Simulation", fontsize=14)
        self.ax.set_xlabel("Position (m)")

        # Draw walls
        self.ax.axvline(
            x=self.wall_left, color="black", linestyle="-", linewidth=3, alpha=0.8
        )
        self.ax.axvline(
            x=self.wall_right, color="black", linestyle="-", linewidth=3, alpha=0.8
        )

        # Create blocks
        self.block1 = Rectangle(
            (self.x1 - self.block_width / 2, -self.block_height / 2),
            self.block_width,
            self.block_height,
            color="blue",
            alpha=0.8,
            linewidth=2,
            edgecolor="darkblue",
        )
        self.block2 = Rectangle(
            (self.x2 - self.block_width / 2, -self.block_height / 2),
            self.block_width,
            self.block_height,
            color="red",
            alpha=0.8,
            linewidth=2,
            edgecolor="darkred",
        )
        self.ax.add_patch(self.block1)
        self.ax.add_patch(self.block2)

        # Add text for displaying values
        self.info_text = self.ax.text(
            0.02,
            0.95,
            "",
            transform=self.ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Add sliders
        plt.subplots_adjust(bottom=0.35)

        ax_m1 = plt.axes([0.15, 0.25, 0.5, 0.03])
        ax_m2 = plt.axes([0.15, 0.20, 0.5, 0.03])
        ax_v1 = plt.axes([0.15, 0.15, 0.5, 0.03])
        ax_v2 = plt.axes([0.15, 0.10, 0.5, 0.03])

        self.slider_m1 = Slider(
            ax_m1, "Mass 1 (kg)", 0.1, 5.0, valinit=self.m1, valfmt="%.1f"
        )
        self.slider_m2 = Slider(
            ax_m2, "Mass 2 (kg)", 0.1, 5.0, valinit=self.m2, valfmt="%.1f"
        )
        self.slider_v1 = Slider(
            ax_v1, "Initial Vel 1 (m/s)", -5.0, 5.0, valinit=self.v1, valfmt="%.1f"
        )
        self.slider_v2 = Slider(
            ax_v2, "Initial Vel 2 (m/s)", -5.0, 5.0, valinit=self.v2, valfmt="%.1f"
        )

        # Add buttons
        ax_reset = plt.axes([0.75, 0.20, 0.1, 0.06])
        ax_pause = plt.axes([0.75, 0.12, 0.1, 0.06])

        self.button_reset = Button(ax_reset, "Reset")
        self.button_pause = Button(ax_pause, "Pause")

        self.is_paused = False

        # Connect sliders and buttons
        self.slider_m1.on_changed(self.update_params)
        self.slider_m2.on_changed(self.update_params)
        self.slider_v1.on_changed(self.update_params)
        self.slider_v2.on_changed(self.update_params)
        self.button_reset.on_clicked(self.reset)
        self.button_pause.on_clicked(self.toggle_pause)

    def update_params(self, val):
        """Update parameters from sliders"""
        self.m1 = self.slider_m1.val
        self.m2 = self.slider_m2.val
        self.v1 = self.slider_v1.val
        self.v2 = self.slider_v2.val

    def reset(self, event):
        """Reset the simulation"""
        self.reset_simulation()
        self.is_paused = False
        self.button_pause.label.set_text("Pause")

    def toggle_pause(self, event):
        """Toggle pause/resume"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.button_pause.label.set_text("Resume")
        else:
            self.button_pause.label.set_text("Pause")

    def update_animation(self, frame):
        """Update animation frame"""
        if not self.is_paused:
            # Update physics multiple times per frame for smoother simulation
            for _ in range(self.frame_skip):
                self.update_positions()

        # Update block positions
        self.block1.set_xy((self.x1 - self.block_width / 2, -self.block_height / 2))
        self.block2.set_xy((self.x2 - self.block_width / 2, -self.block_height / 2))

        # Update info text
        info_str = (
            f"Time: {self.t:.1f}s\n"
            f"Block 1: m={self.m1:.1f}kg, v={self.current_v1:.2f}m/s\n"
            f"Block 2: m={self.m2:.1f}kg, v={self.current_v2:.2f}m/s\n"
            f"KE Total: {0.5 * self.m1 * self.current_v1**2 + 0.5 * self.m2 * self.current_v2**2:.2f}J"
        )
        self.info_text.set_text(info_str)

        return self.block1, self.block2, self.info_text

    def animate(self):
        """Start the animation"""
        # Create animation with continuous running
        self.anim = FuncAnimation(
            self.fig,
            self.update_animation,
            interval=20,  # 50 FPS
            blit=False,  # Disable blitting to prevent flickering
            repeat=True,
            cache_frame_data=False,  # Don't cache frames
        )

        plt.show()


if __name__ == "__main__":
    try:
        simulation = ElasticCollision()
    except KeyboardInterrupt:
        print("Simulation stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        plt.close("all")
