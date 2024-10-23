import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from tabulate import tabulate  # To create table-like formatted text

# Page Replacement Algorithms
def fifo(pages, capacity):
    memory = []
    page_faults = 0
    page_fault_list = []
    output_list = [["Iteration", "Page", "Memory", "Page Fault"]]
    for i, page in enumerate(pages):
        page_fault = "No"
        if page not in memory:
            page_faults += 1
            page_fault = "Yes"
            if len(memory) >= capacity:
                memory.pop(0)
            memory.append(page)
        output_list.append([i + 1, page, memory.copy(), page_fault])
        page_fault_list.append(page_faults)
    return page_faults, page_fault_list, output_list

def lru(pages, capacity):
    memory = []
    page_faults = 0
    page_fault_list = []
    recent_usage = {}
    output_list = [["Iteration", "Page", "Memory", "Page Fault"]]
    for i, page in enumerate(pages):
        page_fault = "No"
        if page not in memory:
            page_faults += 1
            page_fault = "Yes"
            if len(memory) >= capacity:
                lru_page = min(recent_usage, key=recent_usage.get)
                memory.remove(lru_page)
                del recent_usage[lru_page]
            memory.append(page)
        recent_usage[page] = i
        output_list.append([i + 1, page, memory.copy(), page_fault])
        page_fault_list.append(page_faults)
    return page_faults, page_fault_list, output_list

def optimal(pages, capacity):
    memory = []
    page_faults = 0
    page_fault_list = []
    output_list = [["Iteration", "Page", "Memory", "Page Fault"]]
    for i, page in enumerate(pages):
        page_fault = "No"
        if page not in memory:
            page_faults += 1
            page_fault = "Yes"
            if len(memory) >= capacity:
                furthest_page = -1
                furthest_index = -1
                for mem_page in memory:
                    if mem_page not in pages[i:]:
                        furthest_page = mem_page
                        break
                    else:
                        index = pages[i:].index(mem_page)
                        if index > furthest_index:
                            furthest_index = index
                            furthest_page = mem_page
                memory.remove(furthest_page)
            memory.append(page)
        output_list.append([i + 1, page, memory.copy(), page_fault])
        page_fault_list.append(page_faults)
    return page_faults, page_fault_list, output_list

def clock(pages, capacity):
    memory = []
    page_faults = 0
    page_fault_list = []
    pointer = 0
    used_bit = {}
    output_list = [["Iteration", "Page", "Memory", "Page Fault"]]
    for i, page in enumerate(pages):
        page_fault = "No"
        if page not in memory:
            page_faults += 1
            page_fault = "Yes"
            if len(memory) >= capacity:
                while used_bit.get(memory[pointer], 0) == 1:
                    used_bit[memory[pointer]] = 0
                    pointer = (pointer + 1) % capacity
                memory[pointer] = page
                pointer = (pointer + 1) % capacity
            else:
                memory.append(page)
            used_bit[page] = 1
        else:
            used_bit[page] = 1
        output_list.append([i + 1, page, memory.copy(), page_fault])
        page_fault_list.append(page_faults)
    return page_faults, page_fault_list, output_list

# GUI and main application logic
class PageReplacementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Page Replacement Algorithms")
        self.root.geometry("1200x600")

        # Input fields for pages and capacity
        tk.Label(root, text="Enter Page Sequence (comma separated):").pack(pady=5)
        self.pages_input = tk.Entry(root, width=50)
        self.pages_input.pack(pady=2)

        tk.Label(root, text="Enter Memory Capacity:").pack(pady=5)
        self.capacity_input = tk.Entry(root, width=50)
        self.capacity_input.pack(pady=2)

        # Button to execute
        tk.Button(root, text="Run All Algorithms", command=self.run_all_algorithms).pack(pady=10)

        # Output frames for each algorithm
        self.output_frames = {name: tk.Frame(root) for name in ["FIFO", "LRU", "Optimal", "Clock"]}
        
        # Create a label for each frame and arrange them in a horizontal manner
        for name, frame in self.output_frames.items():
            frame.pack(side=tk.LEFT, padx=5, pady=5)  # Reduced padx for less spacing
            tk.Label(frame, text=name, font=("Helvetica", 14)).pack(pady=2)  # Reduced pady
            output_text = tk.Text(frame, height=20, width=40)  # Adjust the width here
            output_text.pack()
            frame.output_text = output_text  # Store a reference for later use

        # Graph button
        tk.Button(root, text="Show Comparison Graph", command=self.show_comparison_graph).pack(pady=10)

        # Variables to hold results
        self.fault_lists = {}
        self.algorithm_names = ["FIFO", "LRU", "Optimal", "Clock"]

    def run_all_algorithms(self):
        pages = self.pages_input.get()
        capacity = self.capacity_input.get()

        try:
            pages = list(map(int, pages.split(',')))
            capacity = int(capacity)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers for pages and capacity.")
            return

        # Run all algorithms and collect outputs
        fifo_faults, fifo_list, fifo_output = fifo(pages, capacity)
        lru_faults, lru_list, lru_output = lru(pages, capacity)
        optimal_faults, optimal_list, optimal_output = optimal(pages, capacity)
        clock_faults, clock_list, clock_output = clock(pages, capacity)

        # Store the results for graph comparison
        self.fault_lists["FIFO"] = fifo_list
        self.fault_lists["LRU"] = lru_list
        self.fault_lists["Optimal"] = optimal_list
        self.fault_lists["Clock"] = clock_list

        # Update the output text areas in each frame
        self.update_output_text("FIFO", fifo_output)
        self.update_output_text("LRU", lru_output)
        self.update_output_text("Optimal", optimal_output)
        self.update_output_text("Clock", clock_output)

    def update_output_text(self, algorithm_name, output):
        table = tabulate(output, headers="firstrow", tablefmt="grid")
        self.output_frames[algorithm_name].output_text.delete(1.0, tk.END)
        self.output_frames[algorithm_name].output_text.insert(tk.END, table)

    def show_comparison_graph(self):
        if not self.fault_lists:
            messagebox.showerror("Error", "No data to plot. Please run the algorithms first.")
            return

        plt.figure(figsize=(10, 6))

        for algorithm in self.algorithm_names:
            plt.plot(self.fault_lists[algorithm], marker='o', label=algorithm)

        plt.title("Page Faults Comparison Across Algorithms")
        plt.xlabel("Page Requests")
        plt.ylabel("Cumulative Page Faults")
        plt.legend()
        plt.show()

# Create the main window
root = tk.Tk()
app = PageReplacementApp(root)
root.mainloop()
