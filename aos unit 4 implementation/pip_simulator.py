import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import List, Dict, Optional

class Task:
    def __init__(self, name: str, base_priority: int):
        self.name = name
        self.base_priority = base_priority
        self.effective_priority = base_priority
        self.state = "Ready"
        self.held_resources: List[str] = []

    def inherit_priority(self, new_priority: int):
        self.effective_priority = max(self.effective_priority, new_priority)

    def restore_priority(self):
        self.effective_priority = self.base_priority

class Resource:
    def __init__(self, name: str):
        self.name = name
        self.owner: Optional[str] = None  # task name
        self.waiting_queue: List[str] = []  # task names, ordered by priority descending

class ProtocolManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.resources: Dict[str, Resource] = {}
        self.event_log: List[str] = []
        self.demo_steps = []
        self.current_step = 0
        self.is_demo_mode = False

    def add_task(self, name: str, priority: int):
        if name in self.tasks:
            raise ValueError(f"Task {name} already exists")
        self.tasks[name] = Task(name, priority)
        self.log_event(f"Added task {name} with priority {priority}")

    def add_resource(self, name: str):
        if name in self.resources:
            raise ValueError(f"Resource {name} already exists")
        self.resources[name] = Resource(name)
        self.log_event(f"Added resource {name}")

    def request_resource(self, task_name: str, resource_name: str):
        if task_name not in self.tasks or resource_name not in self.resources:
            raise ValueError("Invalid task or resource")
        task = self.tasks[task_name]
        resource = self.resources[resource_name]
        if resource.owner is None:
            # grant
            resource.owner = task_name
            task.held_resources.append(resource_name)
            task.state = "Holding Resource"
            self.log_event(f"{task_name} acquired {resource_name}")
        elif self.tasks[resource.owner].effective_priority > task.effective_priority:
            # wait
            resource.waiting_queue.append(task_name)
            resource.waiting_queue.sort(key=lambda t: self.tasks[t].effective_priority, reverse=True)
            task.state = "Waiting"
            self.log_event(f"{task_name} waiting for {resource_name}")
        else:
            # lower priority owner, inherit
            owner_task = self.tasks[resource.owner]
            owner_task.inherit_priority(task.effective_priority)
            resource.waiting_queue.append(task_name)
            resource.waiting_queue.sort(key=lambda t: self.tasks[t].effective_priority, reverse=True)
            task.state = "Waiting"
            self.log_event(f"{task_name} waiting for {resource_name}, {resource.owner} inherited priority {task.effective_priority}")

    def release_resource(self, task_name: str, resource_name: str):
        if task_name not in self.tasks or resource_name not in self.resources:
            raise ValueError("Invalid task or resource")
        task = self.tasks[task_name]
        resource = self.resources[resource_name]
        if resource.owner != task_name:
            raise ValueError(f"{task_name} does not own {resource_name}")
        task.held_resources.remove(resource_name)
        # restore priority if no more inheritance needed
        if not self.needs_inheritance(task_name):
            task.restore_priority()
        # assign to next waiting
        if resource.waiting_queue:
            next_task = resource.waiting_queue.pop(0)
            resource.owner = next_task
            self.tasks[next_task].held_resources.append(resource_name)
            self.tasks[next_task].state = "Holding Resource"
            self.log_event(f"{resource_name} assigned to {next_task}")
        else:
            resource.owner = None
            self.log_event(f"{task_name} released {resource_name}")
        task.state = "Ready"  # assume back to ready

    def needs_inheritance(self, task_name: str) -> bool:
        # check if any resource held by task has waiting tasks
        for res_name in self.tasks[task_name].held_resources:
            res = self.resources[res_name]
            if res.waiting_queue:
                return True
        return False

    def reset(self):
        self.tasks.clear()
        self.resources.clear()
        self.event_log.clear()

    def setup_demo(self):
        self.demo_steps = [
            lambda: self.add_task("Ti", 5),
            lambda: self.add_task("Tj", 10),
            lambda: self.add_resource("CR"),
            lambda: self.request_resource("Ti", "CR"),
            lambda: self.request_resource("Tj", "CR"),
            lambda: self.release_resource("Ti", "CR")
        ]
        self.current_step = 0
        self.is_demo_mode = True

    def run_demo(self):
        # run all steps
        self.reset()
        self.setup_demo()
        for step in self.demo_steps:
            step()
        self.is_demo_mode = False

    def start_demo(self):
        self.reset()
        self.setup_demo()

    def next_step(self):
        if self.is_demo_mode and self.current_step < len(self.demo_steps):
            self.demo_steps[self.current_step]()
            self.current_step += 1
            if self.current_step >= len(self.demo_steps):
                self.is_demo_mode = False

    def log_event(self, msg: str):
        self.event_log.append(msg)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Priority Inheritance Protocol Simulator")
        self.geometry("1200x800")
        self.protocol_manager = ProtocolManager()
        self.create_widgets()

    def create_widgets(self):
        # Left panel: inputs
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        # Task input
        ctk.CTkLabel(self.left_frame, text="Add Task").pack(pady=5)
        self.task_name_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Task Name")
        self.task_name_entry.pack(pady=5)
        self.task_priority_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Base Priority")
        self.task_priority_entry.pack(pady=5)
        ctk.CTkButton(self.left_frame, text="Add Task", command=self.add_task).pack(pady=5)
        # Resource input
        ctk.CTkLabel(self.left_frame, text="Add Resource").pack(pady=5)
        self.resource_name_entry = ctk.CTkEntry(self.left_frame, placeholder_text="Resource Name")
        self.resource_name_entry.pack(pady=5)
        ctk.CTkButton(self.left_frame, text="Add Resource", command=self.add_resource).pack(pady=5)

        # Center panel: controls
        self.center_frame = ctk.CTkFrame(self)
        self.center_frame.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkButton(self.center_frame, text="Request Resource", command=self.request_resource).pack(pady=10)
        self.request_task_combo = ctk.CTkComboBox(self.center_frame, values=[])
        self.request_task_combo.pack(pady=5)
        self.request_resource_combo = ctk.CTkComboBox(self.center_frame, values=[])
        self.request_resource_combo.pack(pady=5)
        ctk.CTkButton(self.center_frame, text="Release Resource", command=self.release_resource).pack(pady=10)
        self.release_task_combo = ctk.CTkComboBox(self.center_frame, values=[])
        self.release_task_combo.pack(pady=5)
        self.release_resource_combo = ctk.CTkComboBox(self.center_frame, values=[])
        self.release_resource_combo.pack(pady=5)
        ctk.CTkButton(self.center_frame, text="Reset Simulation", command=self.reset_simulation).pack(pady=10)
        ctk.CTkButton(self.center_frame, text="Run Demo Scenario", command=self.run_demo).pack(pady=10)
        ctk.CTkButton(self.center_frame, text="Start Step-by-Step Demo", command=self.start_demo).pack(pady=10)
        self.step_indicator = ctk.CTkLabel(self.center_frame, text="Step: 0/0")
        self.step_indicator.pack(pady=5)
        # Extra
        ctk.CTkButton(self.center_frame, text="Next Step", command=self.next_step).pack(pady=10)
        ctk.CTkButton(self.center_frame, text="Export Log", command=self.export_log).pack(pady=10)

        # Right panel: status
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        # Task table
        ctk.CTkLabel(self.right_frame, text="Tasks").pack(pady=5)
        self.task_table = ctk.CTkTextbox(self.right_frame, wrap="none")
        self.task_table.pack(fill="both", expand=True, pady=5)
        # Resource table
        ctk.CTkLabel(self.right_frame, text="Resources").pack(pady=5)
        self.resource_table = ctk.CTkTextbox(self.right_frame, wrap="none")
        self.resource_table.pack(fill="both", expand=True, pady=5)
        # Event log
        ctk.CTkLabel(self.right_frame, text="Event Log").pack(pady=5)
        self.event_log_text = ctk.CTkTextbox(self.right_frame)
        self.event_log_text.pack(fill="both", expand=True, pady=5)
        # Diagram canvas
        self.canvas = ctk.CTkCanvas(self.right_frame, width=400, height=200, bg="gray20")
        self.canvas.pack(pady=5)
        self.update_displays()

    def add_task(self):
        name = self.task_name_entry.get()
        try:
            priority = int(self.task_priority_entry.get())
            self.protocol_manager.add_task(name, priority)
            self.update_displays()
            self.task_name_entry.delete(0, "end")
            self.task_priority_entry.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def add_resource(self):
        name = self.resource_name_entry.get()
        try:
            self.protocol_manager.add_resource(name)
            self.update_displays()
            self.resource_name_entry.delete(0, "end")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def request_resource(self):
        task = self.request_task_combo.get()
        res = self.request_resource_combo.get()
        try:
            self.protocol_manager.request_resource(task, res)
            self.update_displays()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def release_resource(self):
        task = self.release_task_combo.get()
        res = self.release_resource_combo.get()
        try:
            self.protocol_manager.release_resource(task, res)
            self.update_displays()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def reset_simulation(self):
        self.protocol_manager.reset()
        self.update_displays()

    def run_demo(self):
        self.protocol_manager.run_demo()
        self.update_displays()

    def start_demo(self):
        self.protocol_manager.start_demo()
        self.update_displays()

    def next_step(self):
        self.protocol_manager.next_step()
        self.update_displays()

    def export_log(self):
        log = "\n".join(self.protocol_manager.event_log)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write(log)

    def update_displays(self):
        # Update combos
        task_list = list(self.protocol_manager.tasks.keys())
        res_list = list(self.protocol_manager.resources.keys())
        release_task_list = [t for t in self.protocol_manager.tasks.keys() if self.protocol_manager.tasks[t].held_resources]
        self.request_task_combo.configure(values=task_list, state="normal" if task_list and res_list else "disabled")
        self.request_resource_combo.configure(values=res_list, state="normal" if task_list and res_list else "disabled")
        self.release_task_combo.configure(values=release_task_list, state="normal" if release_task_list else "disabled")
        self.release_resource_combo.configure(values=res_list, state="normal" if release_task_list else "disabled")
        # Task table
        self.task_table.delete("1.0", "end")
        self.task_table.insert("1.0", "Name\tBase\tEff\tState\tHeld\n")
        for task in self.protocol_manager.tasks.values():
            self.task_table.insert("end", f"{task.name}\t{task.base_priority}\t{task.effective_priority}\t{task.state}\t{', '.join(task.held_resources)}\n")
        # Resource table
        self.resource_table.delete("1.0", "end")
        self.resource_table.insert("1.0", "Name\tOwner\tWaiting\n")
        for res in self.protocol_manager.resources.values():
            self.resource_table.insert("end", f"{res.name}\t{res.owner or 'None'}\t{', '.join(res.waiting_queue)}\n")
        # Event log
        self.event_log_text.delete("1.0", "end")
        self.event_log_text.insert("1.0", "\n".join(self.protocol_manager.event_log))
        # Step indicator
        self.step_indicator.configure(text=f"Step: {self.protocol_manager.current_step}/{len(self.protocol_manager.demo_steps)}")
        # Canvas diagram
        self.canvas.delete("all")
        # Draw tasks as circles
        x = 50
        for task in self.protocol_manager.tasks.values():
            color = "green" if task.state == "Ready" else "blue" if task.state == "Holding Resource" else "red" if task.state == "Waiting" else "yellow"
            self.canvas.create_oval(x-20, 50-20, x+20, 50+20, fill=color)
            self.canvas.create_text(x, 50, text=task.name)
            x += 60
        # Draw resource as box
        if self.protocol_manager.resources:
            res = next(iter(self.protocol_manager.resources.values()))
            self.canvas.create_rectangle(200, 100, 300, 150, fill="orange")
            self.canvas.create_text(250, 125, text=f"{res.name}\nOwner: {res.owner or 'None'}")

if __name__ == "__main__":
    app = App()
    app.mainloop()