import tkinter as tk
from tkinter import ttk
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import datetime
import json
import time
from collections import deque
from node.logger import ops_logger


# Data storage for plots
class SensorData:
    def __init__(self, max_points=100):
        self.max_points = max_points
        self.timestamps = deque(maxlen=max_points)
        self.temperature = deque(maxlen=max_points)
        self.ph = deque(maxlen=max_points)
        self.lock = threading.Lock()

    def add_data(self, data):
        with self.lock:
            self.timestamps.append(datetime.datetime.now())
            self.temperature.append(data.get("temperature", 0))
            self.ph.append(data.get("ph", 0))

    def get_data(self):
        with self.lock:
            return {
                "timestamps": list(self.timestamps),
                "temperature": list(self.temperature),
                "ph": list(self.ph),
            }


class LakewatchGUI:
    def __init__(self, root, data_queue):
        self.root = root
        self.data_queue = data_queue
        self.sensor_data = SensorData()

        self.root.title("Lakewatch Node Monitor")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        self.setup_ui()
        self.update_data()

    def setup_ui(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top info panel
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Node Information")
        self.info_frame.pack(fill=tk.X, padx=5, pady=5)

        # Node ID and coordinates
        self.node_id_var = tk.StringVar(value="Node ID: --")
        ttk.Label(
            self.info_frame, textvariable=self.node_id_var, font=("Arial", 12)
        ).pack(anchor=tk.W, padx=10, pady=2)

        self.location_var = tk.StringVar(value="Location: --")
        ttk.Label(
            self.info_frame, textvariable=self.location_var, font=("Arial", 12)
        ).pack(anchor=tk.W, padx=10, pady=2)

        # Current sensor readings frame
        self.readings_frame = ttk.LabelFrame(self.main_frame, text="Current Readings")
        self.readings_frame.pack(fill=tk.X, padx=5, pady=5)

        # Temperature and pH display
        self.temp_frame = ttk.Frame(self.readings_frame)
        self.temp_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.temp_frame, text="Temperature:", font=("Arial", 14)).pack(
            side=tk.LEFT, padx=10
        )
        self.temp_var = tk.StringVar(value="-- °C")
        self.temp_label = ttk.Label(
            self.temp_frame, textvariable=self.temp_var, font=("Arial", 18, "bold")
        )
        self.temp_label.pack(side=tk.LEFT, padx=10)

        self.ph_frame = ttk.Frame(self.readings_frame)
        self.ph_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.ph_frame, text="pH Level:", font=("Arial", 14)).pack(
            side=tk.LEFT, padx=10
        )
        self.ph_var = tk.StringVar(value="--")
        self.ph_label = ttk.Label(
            self.ph_frame, textvariable=self.ph_var, font=("Arial", 18, "bold")
        )
        self.ph_label.pack(side=tk.LEFT, padx=10)

        # Status frame
        self.status_frame = ttk.Frame(self.readings_frame)
        self.status_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(self.status_frame, text="Last Update:", font=("Arial", 12)).pack(
            side=tk.LEFT, padx=10
        )
        self.last_update_var = tk.StringVar(value="--")
        ttk.Label(
            self.status_frame, textvariable=self.last_update_var, font=("Arial", 12)
        ).pack(side=tk.LEFT, padx=10)

        # Connection status
        self.connection_var = tk.StringVar(value="Status: Not connected")
        self.connection_label = ttk.Label(
            self.status_frame, textvariable=self.connection_var, font=("Arial", 12)
        )
        self.connection_label.pack(side=tk.RIGHT, padx=20)

        # Graphs frame
        self.graphs_frame = ttk.LabelFrame(self.main_frame, text="Sensor History")
        self.graphs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create figure for plots
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.subplots_adjust(bottom=0.15)

        # Temperature plot
        self.temp_plot = self.figure.add_subplot(211)
        self.temp_plot.set_title("Temperature History")
        self.temp_plot.set_ylabel("Temperature (°C)")
        self.temp_plot.grid(True)

        # pH plot
        self.ph_plot = self.figure.add_subplot(212)
        self.ph_plot.set_title("pH History")
        self.ph_plot.set_ylabel("pH Level")
        self.ph_plot.set_xlabel("Time")
        self.ph_plot.grid(True)

        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Control panel
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Clear button
        self.clear_btn = ttk.Button(
            self.control_frame, text="Clear Data", command=self.clear_data
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Exit button
        self.exit_btn = ttk.Button(
            self.control_frame, text="Exit", command=self.root.quit
        )
        self.exit_btn.pack(side=tk.RIGHT, padx=5)

        # Configure style
        style = ttk.Style()
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabelframe", background="#f0f0f0")
        style.configure(
            "TLabelframe.Label", background="#f0f0f0", font=("Arial", 12, "bold")
        )

    def update_plots(self):
        # Get data
        data = self.sensor_data.get_data()

        # Clear plots
        self.temp_plot.clear()
        self.ph_plot.clear()

        # Set titles and grid
        self.temp_plot.set_title("Temperature History")
        self.temp_plot.set_ylabel("Temperature (°C)")
        self.temp_plot.grid(True)

        self.ph_plot.set_title("pH History")
        self.ph_plot.set_ylabel("pH Level")
        self.ph_plot.set_xlabel("Time")
        self.ph_plot.grid(True)

        # Plot data if available
        if data["timestamps"]:
            self.temp_plot.plot(data["timestamps"], data["temperature"], "r-")
            self.ph_plot.plot(data["timestamps"], data["ph"], "b-")

            # Format x-axis labels
            for plot in [self.temp_plot, self.ph_plot]:
                plot.tick_params(axis="x", rotation=45)
                plt.setp(plot.get_xticklabels(), fontsize=8)

        # Update canvas
        self.canvas.draw()

    def update_data(self):
        try:
            # Check for new data
            has_received_data = False
            while not self.data_queue.empty():
                data = self.data_queue.get_nowait()
                has_received_data = True

                # Update metadata
                self.node_id_var.set(f"Node ID: {data.get('node_id', '--')}")

                # Extract coordinates from CONFIG since they aren't in the sensor data
                from node.settings import CONFIG

                self.location_var.set(
                    f"Location: {CONFIG.get('latitude', 0)}, {CONFIG.get('longitude', 0)}"
                )

                # Extract data correctly from payload if available
                payload = data.get("payload", {})
                temp = payload.get("temperature", 0)
                ph = payload.get("ph", 0)

                # Update current readings
                self.temp_var.set(f"{temp:.2f} °C")
                self.ph_var.set(f"{ph:.2f}")

                # Update status
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.last_update_var.set(current_time)

                # Add to history data
                self.sensor_data.add_data({"temperature": temp, "ph": ph})

                # Update plots
                self.update_plots()

            # Update connection status based on whether we're receiving data
            if has_received_data:
                self.connection_var.set("Status: Connected")
                self.connection_label.configure(foreground="green")
            else:
                # No data received in this cycle
                # Check when the last update was, if too old, show as disconnected
                last_update = self.last_update_var.get()
                if last_update == "--":
                    self.connection_var.set("Status: Not connected")
                    self.connection_label.configure(foreground="red")

        except Exception as e:
            ops_logger.error(f"Error updating GUI data: {e}")
            self.connection_var.set("Status: Error")
            self.connection_label.configure(foreground="red")

        # Schedule next update
        self.root.after(500, self.update_data)

    def clear_data(self):
        # Create new sensor data object to clear history
        self.sensor_data = SensorData()
        # Update plots
        self.update_plots()


def data_collector(data_queue):
    """Simulate data collection for testing without actual sensors"""
    import random
    from node.settings import CONFIG

    while True:
        try:
            # Generate simulated data
            data = {
                "node_id": CONFIG["node_id"],
                "latitude": CONFIG["latitude"],
                "longitude": CONFIG["longitude"],
                "temperature": random.uniform(20, 30),
                "ph": random.uniform(6.5, 8.5),
            }

            # Put data in queue
            data_queue.put(data)

            # Sleep for a short time
            time.sleep(1)
        except Exception as e:
            ops_logger.error(f"Error in data collector thread: {e}")


def actual_data_collector(data_queue):
    """Collect actual data from sensors"""
    from node.read import read_gpio_sensors
    import asyncio

    async def read_data():
        while True:
            try:
                # Read actual sensor data
                data = await read_gpio_sensors()

                # Put data in queue
                data_queue.put(data)

                # Sleep for a short time
                await asyncio.sleep(1)
            except Exception as e:
                ops_logger.error(f"Error in actual data collector: {e}")

    asyncio.run(read_data())


def start_gui(use_test_data=False):
    """Start the GUI application"""
    ops_logger.info("Starting Lakewatch GUI...")

    # Create queue for thread communication
    data_queue = queue.Queue()

    # Start data collection in a separate thread
    collector_func = data_collector if use_test_data else actual_data_collector
    data_thread = threading.Thread(
        target=collector_func, args=(data_queue,), daemon=True
    )
    data_thread.start()

    # Create root window
    root = tk.Tk()

    # Set icon if available
    try:
        root.iconbitmap("node/assets/icon.ico")
    except:
        pass

    # Create application
    app = LakewatchGUI(root, data_queue)

    # Run the main loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        ops_logger.info("GUI terminated by user")
    except Exception as e:
        ops_logger.error(f"Error in GUI main loop: {e}")

    ops_logger.info("GUI closed")


if __name__ == "__main__":
    # When run directly, use test data
    start_gui(use_test_data=True)
