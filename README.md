Physics Simulations

An interactive suite of educational physics simulations built with Python, using Tkinter for the GUI and Matplotlib for visualization. Ideal for exploring and teaching fundamental physics concepts.

🔬 Simulations Included

Projectile Motion – Explore trajectories with customizable parameters.
Snap Line Tool – Draw and snap lines to curves for geometric analysis.
Simple Harmonic Motion (SHO) – Visualize oscillatory motion and energy transitions.
Elastic Collisions – Study momentum and energy conservation in 1D collisions.
Atwood's Machine – Simulate a pulley system with adjustable masses.
Rigid Body Rotation – Observe rotation with different mass distributions.

Getting Started

1. Clone the Repository
2. Install Dependencies
Requires Python 3.8+.

pip install matplotlib numpy


3. (Optional) Set Up Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install matplotlib numpy

Running the App

Start the main menu:

python home_screen.py
A GUI will launch with buttons for each simulation. Click a button to explore that concept. The main menu will return when a simulation window is closed.

Project Structure

home_screen.py            # Main GUI launcher
projectile_motion.py      # Projectile motion simulation
snap_line.py              # Line drawing and snapping tool
SHO.py                    # Simple harmonic motion simulator
elastic_collision.py      # Elastic collision demo
atwood_machine.py         # Atwood’s machine simulation
rigid_body_rotation.py    # Rigid body rotation module
(Add any extra files or modules here as needed.)

Requirements

Python 3.8+
Tkinter (typically included with Python)
Matplotlib
NumPy

Contributing

Contributions are welcome! Please open an issue to suggest major changes before submitting a pull request.
