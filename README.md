# ⚡ sys-pulse

**A lightweight, zero-dependency Linux system resource monitor and process viewer built from scratch in Python.**

`sys-pulse` is a terminal-based system monitoring tool inspired by [`htop`](https://htop.dev/). It reads Linux kernel statistics directly from the `/proc` virtual filesystem and uses Python's built-in `curses` module to display real-time system resource usage and process information.

The project demonstrates low-level Linux system introspection, process monitoring, performance metrics collection, and terminal UI development without third-party Python dependencies.

---

## ✨ Features

### 📊 Real-Time System Monitoring

* **CPU Usage:** Monitor overall CPU utilization in real time.
* **Memory Usage:** Track RAM consumption, total memory, and available memory.
* **Network Throughput:** Monitor incoming (RX) and outgoing (TX) network traffic.
* **Disk I/O:** Display process-level disk I/O statistics and throughput.

### 🔍 Process Viewer

* View running processes with their PIDs and names.
* Monitor per-process CPU utilization.
* Track memory consumption for individual processes.
* Display thread counts and disk I/O activity.
* Sort processes by CPU usage, memory consumption, or disk activity.

### 🖥️ Terminal User Interface

* Interactive terminal interface powered by Python's built-in `curses` module.
* Dynamic resource usage bars.
* Continuously refreshed system statistics.
* Keyboard-based navigation and sorting.

### ⚙️ Lightweight Architecture

* Built using Python's standard library.
* No third-party Python packages required.
* Reads kernel statistics directly from Linux virtual filesystems.
* Designed for efficient monitoring with minimal overhead.

---

## 🖼️ Interface Preview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                   SYS-PULSE :: PRODUCTION LINUX MONITOR                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ CPU  [██████░░░░░░░░░░░░]  28.4%                                            │
│ RAM  [██████████░░░░░░░░]  48.2% (3850 MB / 7980 MB)                        │
│ NET  ▼ RX:   145.2 KB/s   ▲ TX:    32.8 KB/s                                 │
├──────────────────────────────────────────────────────────────────────────────┤
│ [C] Sort CPU  [M] Sort RAM  [D] Sort Disk  |  [Q] Quit  |  Mode: [CPU]       │
├──────────────────────────────────────────────────────────────────────────────┤
│ PID     NAME            THR   CPU %     MEMORY      DISK I/O    METER        │
│ 1234    python3         4     42.5%     120.1 MB    4.80 MB/s   [████░░░░░░] │
│ 567     chrome          32    18.2%     412.3 MB    0.15 MB/s   [█░░░░░░░░░] │
│ 890     code            18     6.1%     285.5 MB    0.45 MB/s   [░░░░░░░░░░] │
└──────────────────────────────────────────────────────────────────────────────┘
```

*Illustrative interface preview. Actual metrics and appearance may vary depending on your implementation and system.*

---

## 🛠️ Tech Stack

| Technology           | Purpose                                      |
| -------------------- | -------------------------------------------- |
| Python 3             | Core implementation                          |
| `curses`             | Interactive terminal user interface          |
| `/proc`              | CPU, memory, process, and network statistics |
| `/proc/[pid]/stat`   | Process-level statistics                     |
| `/proc/[pid]/status` | Process metadata and memory information      |
| `/proc/[pid]/io`     | Process-level I/O counters                   |
| `/proc/net/dev`      | Network interface statistics                 |
| `/proc/meminfo`      | System memory statistics                     |
| `/proc/stat`         | System-wide CPU statistics                   |

*The exact interfaces used depend on the implementation.*

---

## 📋 Prerequisites

Before running `sys-pulse`, ensure you have:

* A Linux operating system with the `/proc` filesystem enabled.
* Python 3 installed.
* A terminal that supports the `curses` interface.

On Debian or Ubuntu, install the required system package if `curses` is unavailable:

```bash
sudo apt update
sudo apt install python3 python3-curses
```

Most standard Linux Python installations already include `curses`.

**Note:** Native Windows terminals do not provide the same Linux `/proc` interfaces. Use a Linux machine, a Linux virtual machine, or WSL with the required Python components available.

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sys-pulse.git
cd sys-pulse
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Run the Application

If your entry-point file is named `main.py`:

```bash
python3 main.py
```

If your entry-point file has a different name, replace `main.py` with the appropriate filename.

No `pip install` command should be necessary if the project uses only Python's standard library.

---

## 🎮 Keyboard Controls

| Key | Action                         |
| --- | ------------------------------ |
| `C` | Sort processes by CPU usage    |
| `M` | Sort processes by memory usage |
| `D` | Sort processes by disk I/O     |
| `Q` | Quit the application           |

Controls are based on the illustrated interface; adjust this section if your implementation uses different key bindings.

---

## 🧠 How It Works

`sys-pulse` collects system statistics directly from Linux's virtual filesystem instead of relying on high-level monitoring libraries.

### 1. CPU Utilization

Linux exposes cumulative CPU time counters through `/proc/stat`.

The monitor samples these counters at successive intervals and calculates CPU utilization from the differences between samples.

This approach allows CPU usage to be estimated without external monitoring packages.

### 2. Memory Monitoring

The `/proc/meminfo` file exposes information about physical memory, including total and available RAM.

`sys-pulse` uses these values to calculate memory utilization and present the results as readable metrics and progress bars.

### 3. Process Enumeration

Linux exposes information about individual processes under `/proc/[pid]/`.

The application can inspect process metadata and statistics to build a process table containing identifiers, names, CPU usage, memory consumption, and thread counts.

Processes may disappear while being inspected, so robust implementations should handle inaccessible or vanished process entries gracefully.

### 4. Network Throughput

Network interface counters are available through `/proc/net/dev`.

By sampling received and transmitted byte counters over time, the monitor can calculate approximate RX and TX throughput.

### 5. Disk I/O Monitoring

Process-level I/O counters can be obtained from `/proc/[pid]/io`.

Comparing successive counter readings provides an estimate of process I/O activity over a sampling interval.

These counters represent I/O accounting, not necessarily physical disk throughput. The distinction matters when interpreting the displayed metrics.

### 6. Terminal Rendering

Python's built-in `curses` module handles terminal rendering and keyboard input.

The interface periodically refreshes resource statistics and process information, allowing the user to monitor system activity interactively.

---

## 🏗️ Project Structure

An example structure for the project:

```text
sys-pulse/
├── main.py           # Application entry point
├── README.md         # Project documentation
└── .gitignore        # Git exclusions
```

As the project grows, the implementation could be separated into modules:

```text
sys-pulse/
├── main.py
├── collectors/
│   ├── cpu.py
│   ├── memory.py
│   ├── network.py
│   ├── disk.py
│   └── processes.py
├── ui/
│   └── dashboard.py
├── README.md
└── .gitignore
```

The modular structure is a suggested extension, not a claim about the current repository layout.

---

## 🔒 Limitations

* **Linux-specific:** The implementation depends on Linux `/proc` interfaces.
* **Sampling intervals:** CPU utilization and network throughput are estimates calculated from successive samples.
* **Process permissions:** Some process information may be inaccessible because of system permissions or security restrictions.
* **Process lifecycle:** Processes may terminate or change state while their statistics are being collected.
* **Disk I/O interpretation:** Process I/O counters do not necessarily correspond directly to physical disk throughput.
* **Terminal compatibility:** The interface depends on terminal capabilities supported by `curses`.

---

## 🎯 Learning Objectives

This project explores several practical systems programming concepts:

* Linux virtual filesystems and kernel-exposed metrics.
* Process enumeration and monitoring.
* CPU utilization calculations using cumulative counters.
* Memory accounting and resource utilization.
* Network traffic measurement.
* Process-level I/O accounting.
* Terminal interfaces using `curses`.
* Efficient periodic sampling and refreshing.
* Error handling for changing process states and restricted access.
* Building useful Linux utilities without third-party dependencies.

---

## 🛣️ Potential Future Improvements

* [ ] Add CPU usage per core.
* [ ] Display CPU frequency and system load averages.
* [ ] Add process search and filtering.
* [ ] Support process selection and termination with confirmation.
* [ ] Implement configurable refresh intervals.
* [ ] Add memory usage indicators for individual processes.
* [ ] Improve terminal resizing and small-terminal handling.
* [ ] Add color-coded alerts for high resource utilization.
* [ ] Implement historical resource usage graphs.
* [ ] Add unit tests for metric calculations and `/proc` parsers.
* [ ] Benchmark monitoring overhead under heavy process loads.
* [ ] Add optional process-tree visualization.

These are possible extensions and are not necessarily implemented in the current version.

---

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes on Linux.
4. Submit a pull request describing the changes.

---

## 📄 License

Choose an open-source license before distributing the project. For example, the MIT License permits broad reuse while requiring preservation of its copyright and license notice.

If you choose MIT, add a `LICENSE` file containing the complete MIT License text and update this section accordingly.

---

## 👨‍💻 Author

**Pratham Bhuta**

GitHub: Add your GitHub profile or repository link here.

---

*sys-pulse — Linux system visibility, directly from `/proc`.*
