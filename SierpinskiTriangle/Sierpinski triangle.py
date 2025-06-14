import tkinter as tk
from tkinter import ttk
import random
import math
import time

class SierpinskiTriangle:
    def __init__(self, root):
        self.root = root
        self.root.title("Sierpinski Triangle Generator")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        self.vertices = [
            (400, 100),   # Top vertex
            (200, 400),   # Bottom left
            (600, 400)    # Bottom right
        ]
        
        # Current state
        self.current_point = None
        self.points = []
        self.max_iterations = 1000
        self.current_iteration = 0
        self.is_running = False
        self.speed = 50
        
        # Zoom and pan
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        
        self.setup_ui()
        self.draw_initial_triangle()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#3c3c3c', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(control_frame, text="Sierpinski Triangle Generator", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#3c3c3c')
        title_label.pack(pady=10)
        
        # Controls row 1
        controls1 = tk.Frame(control_frame, bg='#3c3c3c')
        controls1.pack(pady=5)
        
        tk.Label(controls1, text="Iterations:", fg='white', bg='#3c3c3c').pack(side=tk.LEFT, padx=5)
        self.iterations_var = tk.StringVar(value="5000")
        iterations_entry = tk.Entry(controls1, textvariable=self.iterations_var, width=8, 
                                   bg='#4c4c4c', fg='white', insertbackground='white')
        iterations_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(controls1, text="Speed:", fg='white', bg='#3c3c3c').pack(side=tk.LEFT, padx=(20, 5))
        self.speed_var = tk.IntVar(value=50)
        speed_scale = tk.Scale(controls1, from_=1, to=2000, orient=tk.HORIZONTAL, 
                              variable=self.speed_var, bg='#4c4c4c', fg='white',
                              highlightbackground='#3c3c3c', length=150)
        speed_scale.pack(side=tk.LEFT, padx=5)
        
        # Controls row 2
        controls2 = tk.Frame(control_frame, bg='#3c3c3c')
        controls2.pack(pady=5)
        
        self.start_btn = tk.Button(controls2, text="Start", command=self.start_generation,
                                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                                  relief=tk.FLAT, padx=20)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(controls2, text="Stop", command=self.stop_generation,
                                 bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                                 relief=tk.FLAT, padx=20)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(controls2, text="Reset", command=self.reset,
                                  bg='#FF9800', fg='white', font=('Arial', 10, 'bold'),
                                  relief=tk.FLAT, padx=20)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.random_btn = tk.Button(controls2, text="Random Point", command=self.set_random_point,
                                   bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                                   relief=tk.FLAT, padx=20)
        self.random_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        progress_frame = tk.Frame(control_frame, bg='#3c3c3c')
        progress_frame.pack(fill=tk.X, pady=5, padx=20)
        
        tk.Label(progress_frame, text="Progress:", fg='white', bg='#3c3c3c').pack(side=tk.LEFT)
        self.progress_var = tk.StringVar(value="0 / 0")
        self.progress_label = tk.Label(progress_frame, textvariable=self.progress_var, 
                                      fg='#4CAF50', bg='#3c3c3c', font=('Arial', 10, 'bold'))
        self.progress_label.pack(side=tk.RIGHT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10)
        
        # Canvas frame
        canvas_frame = tk.Frame(main_frame, bg='#2b2b2b', relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas
        self.canvas = tk.Canvas(canvas_frame, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # Linux
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # Linux
        self.canvas.bind("<ButtonPress-2>", self.start_pan)  # Middle mouse button
        self.canvas.bind("<B2-Motion>", self.pan_canvas)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)  # Right mouse button
        self.canvas.bind("<B3-Motion>", self.pan_canvas)
        
        # Instructions
        instructions = ("Instructions: Click on canvas to set starting point, or use 'Random Point' button.\n"
                       "Mouse wheel to zoom, right-click and drag to pan.")
        tk.Label(main_frame, text=instructions, fg='#888888', bg='#2b2b2b', 
                font=('Arial', 9)).pack(pady=5)
        
    def draw_initial_triangle(self):
        self.canvas.delete("all")
        
        # Draw triangle vertices
        for i, vertex in enumerate(self.vertices):
            x, y = self.transform_point(vertex)
            self.canvas.create_oval(x-4, y-4, x+4, y+4, fill='red', outline='darkred', width=2)
            self.canvas.create_text(x, y-15, text=f"V{i+1}", fill='white', font=('Arial', 10, 'bold'))
        
        for i in range(3):
            x1, y1 = self.transform_point(self.vertices[i])
            x2, y2 = self.transform_point(self.vertices[(i+1) % 3])
            self.canvas.create_line(x1, y1, x2, y2, fill='gray', width=1, dash=(5, 5))
        
        if self.current_point:
            x, y = self.transform_point(self.current_point)
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill='yellow', outline='orange', width=2)
            
        for point in self.points:
            x, y = self.transform_point(point)
            self.canvas.create_oval(x-1, y-1, x+1, y+1, fill='lime', outline='')
    
    def transform_point(self, point):
        """Transform point based on zoom and pan"""
        x, y = point
        x = (x + self.pan_x) * self.zoom_factor + self.canvas.winfo_width() / 2
        y = (y + self.pan_y) * self.zoom_factor + self.canvas.winfo_height() / 2
        return x, y
    
    def inverse_transform_point(self, screen_x, screen_y):
        """Transform screen coordinates back to world coordinates"""
        x = (screen_x - self.canvas.winfo_width() / 2) / self.zoom_factor - self.pan_x
        y = (screen_y - self.canvas.winfo_height() / 2) / self.zoom_factor - self.pan_y
        return x, y
    
    def on_canvas_click(self, event):
        if not self.is_running:
            world_x, world_y = self.inverse_transform_point(event.x, event.y)
            self.current_point = (world_x, world_y)
            self.draw_initial_triangle()
    
    def on_mouse_wheel(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        
        self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
        self.draw_initial_triangle()
    
    def start_pan(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
    
    def pan_canvas(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        
        self.pan_x += dx / self.zoom_factor
        self.pan_y += dy / self.zoom_factor
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        self.draw_initial_triangle()
    
    def set_random_point(self):
        if not self.is_running:
            x = random.uniform(200, 600)
            y = random.uniform(150, 350)
            self.current_point = (x, y)
            self.draw_initial_triangle()
    
    def start_generation(self):
        if self.current_point is None:
            self.set_random_point()
        
        try:
            self.max_iterations = int(self.iterations_var.get())
        except ValueError:
            self.max_iterations = 5000
            self.iterations_var.set("5000")
        
        self.is_running = True
        self.current_iteration = 0
        self.points = []
        self.progress_bar['maximum'] = self.max_iterations
        self.start_btn.config(state='disabled')
        
        self.generate_step()
    
    def stop_generation(self):
        self.is_running = False
        self.start_btn.config(state='normal')
    
    def reset(self):
        self.is_running = False
        self.current_point = None
        self.points = []
        self.current_iteration = 0
        self.progress_bar['value'] = 0
        self.progress_var.set("0 / 0")
        self.start_btn.config(state='normal')
        self.draw_initial_triangle()
    
    def generate_step(self):
        if not self.is_running or self.current_iteration >= self.max_iterations:
            self.is_running = False
            self.start_btn.config(state='normal')
            return
        
        chosen_vertex = random.choice(self.vertices)
        
        new_x = (self.current_point[0] + chosen_vertex[0]) / 2
        new_y = (self.current_point[1] + chosen_vertex[1]) / 2
        
        self.current_point = (new_x, new_y)
        self.points.append(self.current_point)
        
        self.current_iteration += 1
        self.progress_bar['value'] = self.current_iteration
        self.progress_var.set(f"{self.current_iteration} / {self.max_iterations}")
        
        if self.current_iteration % max(1, self.max_iterations // 100) == 0:
            self.draw_initial_triangle()
            self.root.update_idletasks()

        self.speed = self.speed_var.get()
        self.root.after(max(1, 201 - self.speed), self.generate_step)

if __name__ == "__main__":
    root = tk.Tk()
    app = SierpinskiTriangle(root)
    root.mainloop()