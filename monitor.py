import os
import time
import heapq
import curses

def get_system_cpu():
    try:
        with open("/proc/stat", "r") as f:
            fields = [int(x) for x in f.readline().split()[1:]]
        total_ticks = sum(fields)
        idle_ticks = fields[3] + fields[4]
        return total_ticks, idle_ticks
    except (FileNotFoundError, PermissionError):
        return 0, 0

def get_system_ram():
    mem_total = 0
    mem_avail = 0
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    mem_total = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    mem_avail = int(line.split()[1])
    except (FileNotFoundError, PermissionError):
        pass
    mem_used = mem_total - mem_avail
    ram_percent = (mem_used / mem_total) * 100 if mem_total > 0 else 0.0
    return mem_total, mem_used, ram_percent

def get_system_net():
    rx_total = 0
    tx_total = 0
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()[2:]
        for line in lines:
            if ":" not in line:
                continue
            iface, data = line.split(":", 1)
            if iface.strip() == "lo":
                continue
            parts = data.split()
            rx_total += int(parts[0])
            tx_total += int(parts[8])
    except (FileNotFoundError, PermissionError):
        pass
    return rx_total, tx_total

def read_process(pid):
    name = f"pid_{pid}"
    rss_kb = 0
    total_ticks = 0
    total_io_bytes = 0
    num_threads = 1

    try:
        with open(f"/proc/{pid}/status", "r") as f:
            for line in f:
                if line.startswith("Name:"):
                    name = line.split()[1]
                elif line.startswith("VmRSS:"):
                    rss_kb = int(line.split()[1])
                elif line.startswith("Threads:"):
                    num_threads = int(line.split()[1])
    except (FileNotFoundError, PermissionError):
        return None

    try:
        with open(f"/proc/{pid}/stat", "r") as f:
            parts = f.readline().split()
        total_ticks = int(parts[13]) + int(parts[14])
    except (FileNotFoundError, PermissionError, IndexError):
        return None

    try:
        with open(f"/proc/{pid}/io", "r") as f:
            for line in f:
                if line.startswith("read_bytes:") or line.startswith("write_bytes:"):
                    total_io_bytes += int(line.split()[1])
    except (FileNotFoundError, PermissionError):
        total_io_bytes = 0

    return {
        "pid": pid,
        "name": name,
        "threads": num_threads,
        "rss_kb": rss_kb,
        "ticks": total_ticks,
        "io_bytes": total_io_bytes
    }

def make_bar(percent, max_blocks=16):
    filled = int((percent / 100) * max_blocks)
    filled = max(0, min(max_blocks, filled))
    return "█" * filled + "░" * (max_blocks - filled)

def run_monitor(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_CYAN, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)
    curses.init_pair(5, curses.COLOR_MAGENTA, -1)

    prev_proc_ticks = {}
    prev_proc_io = {}

    prev_system_ticks, prev_idle_ticks = get_system_cpu()
    prev_net_rx, prev_net_tx = get_system_net()

    sort_mode = "CPU"

    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            break
        elif ch in (ord('c'), ord('C')):
            sort_mode = "CPU"
        elif ch in (ord('m'), ord('M')):
            sort_mode = "MEMORY"
        elif ch in (ord('d'), ord('D')):
            sort_mode = "DISK I/O"

        current_system_ticks, current_idle_ticks = get_system_cpu()
        delta_total = current_system_ticks - prev_system_ticks
        delta_idle = current_idle_ticks - prev_idle_ticks
        prev_system_ticks = current_system_ticks
        prev_idle_ticks = current_idle_ticks

        sys_cpu_percent = ((delta_total - delta_idle) / delta_total) * 100 if delta_total > 0 else 0.0
        mem_total, mem_used, sys_ram_percent = get_system_ram()

        current_net_rx, current_net_tx = get_system_net()
        net_rx_rate = (current_net_rx - prev_net_rx) / 1024
        net_tx_rate = (current_net_tx - prev_net_tx) / 1024
        prev_net_rx = current_net_rx
        prev_net_tx = current_net_tx

        current_pids = set()
        procs = []

        with os.scandir("/proc") as entries:
            for entry in entries:
                if not entry.name.isdigit():
                    continue

                pid = int(entry.name)
                current_pids.add(pid)

                proc = read_process(pid)
                if proc is None:
                    continue

                if pid in prev_proc_ticks and delta_total > 0:
                    delta_ticks = proc["ticks"] - prev_proc_ticks[pid]
                    cpu_percent = (delta_ticks / delta_total) * 100
                else:
                    cpu_percent = 0.0

                if pid in prev_proc_io:
                    delta_io = proc["io_bytes"] - prev_proc_io[pid]
                    io_mb_s = delta_io / (1024 * 1024)
                else:
                    io_mb_s = 0.0

                prev_proc_ticks[pid] = proc["ticks"]
                prev_proc_io[pid] = proc["io_bytes"]

                proc["cpu_percent"] = cpu_percent
                proc["io_mb_s"] = io_mb_s
                procs.append(proc)

        dead_pids = (set(prev_proc_ticks.keys()) | set(prev_proc_io.keys())) - current_pids
        for pid in dead_pids:
            prev_proc_ticks.pop(pid, None)
            prev_proc_io.pop(pid, None)

        if sort_mode == "CPU":
            key_fn = lambda p: p["cpu_percent"]
        elif sort_mode == "MEMORY":
            key_fn = lambda p: p["rss_kb"]
        else:
            key_fn = lambda p: p["io_mb_s"]

        max_y, max_x = stdscr.getmaxyx()
        display_count = min(12, max(1, max_y - 13))
        top_procs = heapq.nlargest(display_count, procs, key=key_fn)

        stdscr.erase()

        width = min(max_x - 1, 80)
        box_top = "┌" + "─" * (width - 2) + "┐"
        box_mid = "├" + "─" * (width - 2) + "┤"
        box_bot = "└" + "─" * (width - 2) + "┘"

        stdscr.addstr(0, 0, box_top, curses.color_pair(4))
        title = " SYS-PULSE :: PRODUCTION LINUX MONITOR ".center(width - 2)
        stdscr.addstr(1, 0, f"│{title}│", curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(2, 0, box_mid, curses.color_pair(4))

        sys_cpu_bar = make_bar(sys_cpu_percent, 18)
        sys_ram_bar = make_bar(sys_ram_percent, 18)

        cpu_line = f" CPU  [{sys_cpu_bar}]  {sys_cpu_percent:5.1f}%".ljust(width - 2)
        ram_line = f" RAM  [{sys_ram_bar}]  {sys_ram_percent:5.1f}% ({mem_used // 1024} MB / {mem_total // 1024} MB)".ljust(width - 2)
        net_line = f" NET  ▼ RX: {net_rx_rate:7.1f} KB/s   ▲ TX: {net_tx_rate:7.1f} KB/s".ljust(width - 2)

        stdscr.addstr(3, 0, f"│{cpu_line}│", curses.color_pair(1))
        stdscr.addstr(4, 0, f"│{ram_line}│", curses.color_pair(2))
        stdscr.addstr(5, 0, f"│{net_line}│", curses.color_pair(5))
        stdscr.addstr(6, 0, box_mid, curses.color_pair(4))

        controls = f" [C] Sort CPU  [M] Sort RAM  [D] Sort Disk  |  [Q] Quit  |  Mode: [{sort_mode}]"
        stdscr.addstr(7, 0, f"│{controls.ljust(width - 2)}│", curses.color_pair(4) | curses.A_BOLD)
        stdscr.addstr(8, 0, box_mid, curses.color_pair(4))

        header = f" {'PID':<7} {'NAME':<15} {'THR':<5} {'CPU %':<9} {'MEMORY':<11} {'DISK I/O':<11} {'METER'}"
        stdscr.addstr(9, 0, f"│{header.ljust(width - 2)}│", curses.color_pair(3) | curses.A_BOLD)

        row = 10
        for p in top_procs:
            if row >= max_y - 2:
                break
            cpu_val = f"{p['cpu_percent']:.1f}%"
            mem_mb = f"{p['rss_kb'] / 1024:.1f} MB"
            io_val = f"{p['io_mb_s']:.2f} MB/s"

            if sort_mode == "CPU":
                pct = min(100.0, p['cpu_percent'])
            elif sort_mode == "MEMORY":
                pct = min(100.0, ((p['rss_kb'] / 1024) / max(1, (mem_total / 1024))) * 100 * 5)
            else:
                pct = min(100.0, (p['io_mb_s'] / 5.0) * 100)

            proc_meter = f"[{make_bar(pct, 10)}]"
            line = f" {p['pid']:<7} {p['name'][:14]:<15} {p['threads']:<5} {cpu_val:<9} {mem_mb:<11} {io_val:<11} {proc_meter}"
            stdscr.addstr(row, 0, f"│{line.ljust(width - 2)}│", curses.color_pair(4))
            row += 1

        stdscr.addstr(row, 0, box_bot, curses.color_pair(4))
        stdscr.refresh()

if __name__ == "__main__":
    try:
        curses.wrapper(run_monitor)
    except KeyboardInterrupt:
        pass
    print("Exiting Resource Monitor. 👋")