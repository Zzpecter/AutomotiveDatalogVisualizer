# 🚗 Automotive Datalog Visualizer (ECU Map Analyzer)

## Overview

The **Automotive Datalog Visualizer** is a PyQt5-based desktop application designed to process, aggregate, and visualize high-frequency Electronic Control Unit (ECU) datalogs (CSV files). It converts raw vehicle operational data (RPM, MAP, AFR, etc.) into a cohesive, color-coded **Map Table** format, essential for calibrating engine management systems (like MegaSquirt, Haltech, or custom systems).

The application uses a **grid snapping** algorithm to aggregate data points into predefined RPM vs. Manifold Absolute Pressure (MAP) cells, allowing users to quickly assess calibration quality and data density in key areas of the engine map. 

---

## ✨ Features

* **Custom Map Grid:** Visualizes data aligned to a user-defined RPM vs. MAP grid (breakpoints) defined in `constants.py`.
* **Grid Snapping & Aggregation:** Automatically calculates the **Average** Wideband Air/Fuel Ratio (**AFR**) for all recorded data points within each map cell.
* **Multi-Layer Viewing:** Switch between three crucial visualization modes:
    * **Average AFR:** Shows the measured average AFR per cell, color-coded using a standard tuning colormap (e.g., Rich in Blue, Lean in Red).
    * **Deviation:** Displays the numerical difference (Error) between the measured Average AFR and the **Target AFR Map** loaded from `constants.py`. **Crucial for tuning corrections.**
    * **Hit Count:** Displays the number of data samples collected in each cell, indicating data density and statistical confidence.
* **Advanced Filtering:** Filter data by **Coolant Temperature** (Cold/Warm) and **Throttle Position Sensor (TPS)** status (Closed, >0%, Wide Open Throttle [WOT]).
* **Intuitive Interface:** Presents data in a spreadsheet-like view with the X-axis (RPM) labels on top, mimicking standard ECU tuning software interfaces.

---

## 🚀 Getting Started

### Prerequisites

You need Python 3.8 or higher. All dependencies can be installed using `pip`:

```bash
pip install pandas numpy matplotlib pyqt5
```

### Installation and Run

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/Zzpecter/AutomotiveDatalogVisualizer.git](https://github.com/Zzpecter/AutomotiveDatalogVisualizer.git)
    cd AutomotiveDatalogVisualizer
    ```

2.  **Define Target Map:**
    Ensure your target AFR values and map breakpoints (`X_TICKS`, `Y_TICKS`) are correctly defined within the configuration file. This step is critical as the application relies on these values for grid alignment and the **Deviation** calculation.
    ```
    datalog_visualizer/config/constants.py
    ```

3.  **Run the Application:**
    Execute the main entry point script from the repository root:
    ```bash
    python datalog_visualizer/main.py
    ```

---

## 🛠️ Project Structure and Scalability

The project adheres to the **Model-View-Controller (MVC)** pattern to ensure high scalability and testability. This modularity allows for easy updates to the data processing logic without affecting the user interface.

| Folder/File | Role | Responsibility |
| :--- | :--- | :--- |
| `datalog_visualizer/config/` | **Configuration** | Stores static variables, **Target AFR Map**, and grid definitions. |
| `datalog_visualizer/model/` | **Model (Logic)** | Contains the `DataProcessor` class, which handles file loading, filtering, **grid snapping**, aggregation, and mathematical matrix calculations. |
| `datalog_visualizer/view/` | **View (Presentation)** | Contains the `MainWindow` (UI layout, button handlers) and `PlotCanvas` (Matplotlib drawing and axis setup). |
| `datalog_visualizer/main.py` | **Entry Point** | The application entry point that initializes the PyQt environment and the `MainWindow`. |

---

## ⚙️ Log File Requirements

Your input CSV log file must contain the following columns with **exact spelling and spacing** for the application to function correctly:

| Column Header | Description |
| :--- | :--- |
| ` RPM` | Engine speed (X-axis). |
| ` MAP` | Manifold Absolute Pressure (Load/Y-axis). |
| ` Int. WB AFR` | Measured Wideband Air/Fuel Ratio (Value/Color). |
| ` Coolant Temp.` | Engine Coolant Temperature (Filter). |
| ` TPS` | Throttle Position Sensor percentage (Filter). |

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for new features (e.g., error correction suggestions, 3D plotting), please feel free to fork the repository and open a pull request.

---

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
