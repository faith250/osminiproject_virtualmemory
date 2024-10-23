from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# FIFO Page Replacement Algorithm
def fifo(pages, capacity):
    memory = []
    page_faults = 0
    iterations = []
    
    for page in pages:
        current_memory = list(memory)  # Copy current state of memory
        if page not in memory:
            page_faults += 1
            if len(memory) >= capacity:
                memory.pop(0)
            memory.append(page)
        iterations.append({'page': page, 'memory': current_memory, 'page_fault': page_faults})
    
    return page_faults, iterations

# LRU Page Replacement Algorithm
def lru(pages, capacity):
    memory = []
    page_faults = 0
    recent_usage = {}
    iterations = []
    
    for i, page in enumerate(pages):
        current_memory = list(memory)
        if page not in memory:
            page_faults += 1
            if len(memory) >= capacity:
                lru_page = min(recent_usage, key=recent_usage.get)
                memory.remove(lru_page)
                del recent_usage[lru_page]
            memory.append(page)
        recent_usage[page] = i
        iterations.append({'page': page, 'memory': current_memory, 'page_fault': page_faults})
    
    return page_faults, iterations

# Optimal Page Replacement Algorithm
def optimal(pages, capacity):
    memory = []
    page_faults = 0
    iterations = []
    
    for i, page in enumerate(pages):
        current_memory = list(memory)
        if page not in memory:
            page_faults += 1
            if len(memory) >= capacity:
                future = pages[i+1:]
                farthest_page = None
                farthest_index = -1
                for mem_page in memory:
                    if mem_page not in future:
                        farthest_page = mem_page
                        break
                    index = future.index(mem_page)
                    if index > farthest_index:
                        farthest_index = index
                        farthest_page = mem_page
                memory.remove(farthest_page)
            memory.append(page)
        iterations.append({'page': page, 'memory': current_memory, 'page_fault': page_faults})
    
    return page_faults, iterations

# Clock Page Replacement Algorithm
def clock(pages, capacity):
    memory = [None] * capacity
    reference_bits = [0] * capacity
    pointer = 0
    page_faults = 0
    iterations = []
    
    for page in pages:
        current_memory = list(memory)
        if page not in memory:
            page_faults += 1
            while reference_bits[pointer] == 1:
                reference_bits[pointer] = 0
                pointer = (pointer + 1) % capacity
            memory[pointer] = page
            reference_bits[pointer] = 1
            pointer = (pointer + 1) % capacity
        else:
            reference_bits[memory.index(page)] = 1
        iterations.append({'page': page, 'memory': current_memory, 'page_fault': page_faults})
    
    return page_faults, iterations

# Route to display form and results
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pages = list(map(int, request.form["pages"].split(",")))
        capacity = int(request.form["capacity"])
        
        fifo_faults, fifo_iterations = fifo(pages, capacity)
        lru_faults, lru_iterations = lru(pages, capacity)
        opt_faults, opt_iterations = optimal(pages, capacity)
        clock_faults, clock_iterations = clock(pages, capacity)
        
        # Create bar chart
        algorithms = ['FIFO', 'LRU', 'Optimal', 'Clock']
        page_faults = [fifo_faults, lru_faults, opt_faults, clock_faults]
        plt.figure(figsize=(10, 5))
        plt.bar(algorithms, page_faults, color=['blue', 'green', 'red', 'purple'])
        plt.xlabel('Page Replacement Algorithm')
        plt.ylabel('Number of Page Faults')
        plt.title('Comparison of Page Faults Across Different Algorithms')
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url1 = base64.b64encode(img.getvalue()).decode()

        # Create line graph for page faults over time
        plt.figure(figsize=(10, 6))
        plt.plot([x['page_fault'] for x in fifo_iterations], label="FIFO", marker='o')
        plt.plot([x['page_fault'] for x in lru_iterations], label="LRU", marker='s')
        plt.plot([x['page_fault'] for x in opt_iterations], label="Optimal", marker='^')
        plt.plot([x['page_fault'] for x in clock_iterations], label="Clock", marker='x')
        plt.title("Page Faults Over Time")
        plt.xlabel("Page Requests")
        plt.ylabel("Cumulative Page Faults")
        plt.legend()
        img2 = io.BytesIO()
        plt.savefig(img2, format='png')
        img2.seek(0)
        plot_url2 = base64.b64encode(img2.getvalue()).decode()

        return render_template("index.html", fifo_iterations=fifo_iterations, lru_iterations=lru_iterations,
                               opt_iterations=opt_iterations, clock_iterations=clock_iterations, plot_url1=plot_url1, plot_url2=plot_url2)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
