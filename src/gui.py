"""Tkinter terminal view."""

import tkinter as tk
from tkinter.scrolledtext import ScrolledText


class Terminal:
    """Display command input and output in a graphical window."""

    def __init__(self, shell, name="VFS"):
        """Construct the terminal widgets."""
        self.shell = shell
        self.root = tk.Tk()
        self.root.title(f"Shell emulator — {name}")
        self.root.geometry("900x600")
        self.output = ScrolledText(self.root, state="disabled")
        self.output.pack(fill="both", expand=True)
        self.entry = tk.Entry(self.root, font=("Consolas", 12))
        self.entry.pack(fill="x")
        self.entry.bind("<Return>", self.submit)
        self.entry.focus_set()

    def write(self, text):
        """Append text without allowing users to edit the transcript."""
        self.output.configure(state="normal")
        self.output.insert("end", text + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def run_line(self, line):
        """Show an entered command and render its result."""
        self.write(f"{self.shell.cwd} $ {line}")
        result = self.shell.execute(line)
        if self.shell.clear_requested:
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.configure(state="disabled")
        if result:
            self.write(result)
        if not self.shell.running:
            self.root.destroy()

    def submit(self, event=None):
        """Execute the line typed by the user."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.run_line(line)

    def run(self):
        """Start processing GUI events."""
        self.root.mainloop()
