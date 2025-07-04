import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from snap_line import LineDrawer
from projectile_motion import ProjectileMotion
from SHO import ImprovedSHMSimulator
from elastic_collision import ElasticCollision
from atwood_machine import AtwoodMachine
from rigid_body_rotation import RigidBodyRotation


class HomeScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Physics Simulations")
        self.root.geometry("1000x600")

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(
            self.main_frame, text="Physics Simulations", font=("Helvetica", 24, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=4, pady=20)

        self.create_buttons()

        style = ttk.Style()
        style.configure("Sim.TButton", font=("Helvetica", 12), padding=10)

        self.root.mainloop()

    def create_buttons(self):
        simulations = [
            (
                "Projectile Motion",
                "Simulate projectile trajectories\nwith adjustable parameters",
                self.launch_projectile,
            ),
            (
                "Snap Line Tool",
                "Interactive line drawing tool\nwith snapping and trimming features",
                self.launch_snapline,
            ),
            (
                "Simple Harmonic Motion",
                "Simulate mass-spring system\nwith energy visualization",
                self.launch_shm,
            ),
            (
                "Elastic Collisions",
                "Study conservation of energy and momentum\nin elastic collisions",
                self.launch_collision,
            ),
            (
                "Atwood's Machine",
                "Simulate two masses connected by a string over a pulley",
                self.launch_atwood,
            ),
            (
                "Rigid Body Rotation",
                "Study rotational motion of different objects\nwith variable mass distribution",
                self.launch_rotation,
            ),
        ]

        for i, (title, desc, command) in enumerate(simulations):
            row = (i // 2) * 2 + 1
            col = i % 2

            btn = ttk.Button(
                self.main_frame, text=title, style="Sim.TButton", command=command
            )
            btn.grid(row=row, column=col, padx=10, pady=10)

            desc_label = ttk.Label(
                self.main_frame, text=desc, wraplength=300, justify="center"
            )
            desc_label.grid(row=row + 1, column=col, padx=10, pady=5)

    def launch_projectile(self):
        self.root.withdraw()
        projectile = ProjectileMotion()
        plt.show()
        self.root.deiconify()

    def launch_snapline(self):
        self.root.withdraw()
        fig, ax = plt.subplots()
        fig.subplots_adjust(bottom=0.25)
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-1.0, 1.0)
        ax.grid()
        x_quad = np.linspace(-0.9, 0.9, 200)
        y_quad = (2 * (x_quad**2)) - 0.4
        ax.plot(x_quad, y_quad, label="Quadratic Curve", color="blue")
        ax.set_xlabel("Time")
        ax.set_ylabel("Acceleration")
        line_drawer = LineDrawer(ax, x_quad, y_quad)
        line_drawer.snap_target_index = len(x_quad) // 2
        ax.legend()
        plt.show()
        self.root.deiconify()

    def launch_shm(self):
        self.root.withdraw()
        sim = ImprovedSHMSimulator()
        plt.show()
        self.root.deiconify()

    def launch_collision(self):
        self.root.withdraw()
        sim = ElasticCollision()
        plt.show()
        self.root.deiconify()

    def launch_atwood(self):
        self.root.withdraw()
        atwood = AtwoodMachine()
        plt.show()
        self.root.deiconify()

    def launch_rotation(self):
        self.root.withdraw()
        rotation = RigidBodyRotation()
        plt.show()
        self.root.deiconify()


if __name__ == "__main__":
    HomeScreen()
