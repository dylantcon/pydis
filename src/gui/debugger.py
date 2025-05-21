"""
Debugger module for step-by-step execution of Python code.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from typing import List, Dict, Any, Callable, Optional
import threading

class StepExecutionControls(tk.Frame):
    """
    Controls for step-by-step execution.
    """
    
    def __init__(self, parent, on_step=None, on_run=None, on_stop=None, *args, **kwargs):
        """
        Initialize the StepExecutionControls widget.
        
        Args:
            parent: Parent widget
            on_step: Callback function for stepping
            on_run: Callback function for running
            on_stop: Callback function for stopping
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        self.on_step = on_step
        self.on_run = on_run
        self.on_stop = on_stop
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create buttons
        self.step_button = ttk.Button(self, text="Step", command=self._on_step_click)
        self.run_button = ttk.Button(self, text="Run", command=self._on_run_click)
        self.stop_button = ttk.Button(self, text="Stop", command=self._on_stop_click)
        
        # disable stop button initially
        self.stop_button.config(state=tk.DISABLED)
        
        # pack buttons
        self.step_button.pack(side=tk.LEFT, padx=5)
        self.run_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def _on_step_click(self):
        """Handle step button click."""
        if self.on_step:
            self.on_step()
            # enable stop button
            self.stop_button.config(state=tk.NORMAL)
    
    def _on_run_click(self):
        """Handle run button click."""
        if self.on_run:
            self.on_run()
            # enable stop button, disable step and run buttons
            self.stop_button.config(state=tk.NORMAL)
            self.step_button.config(state=tk.DISABLED)
            self.run_button.config(state=tk.DISABLED)
    
    def _on_stop_click(self):
        """Handle stop button click."""
        if self.on_stop:
            self.on_stop()
            # re-enable step and run buttons, disable stop button
            self.step_button.config(state=tk.NORMAL)
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
    
    def reset_state(self):
        """Reset the control state."""
        self.step_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

class VariableInspector(tk.Frame):
    """
    Component for inspecting variables during debugging.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the VariableInspector widget.
        
        Args:
            parent: Parent widget
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create a label
        self.label = ttk.Label(self, text="Variables:")
        self.label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        
        # create a treeview for variables
        columns = ("name", "value", "type", "scope")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        # define column headings
        self.tree.heading("name", text="Name")
        self.tree.heading("value", text="Value")
        self.tree.heading("type", text="Type")
        self.tree.heading("scope", text="Scope")
        
        # define column widths
        self.tree.column("name", width=100)
        self.tree.column("value", width=200)
        self.tree.column("type", width=100)
        self.tree.column("scope", width=80)
        
        # add scrollbars
        self.tree_scrollbar_y = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree_scrollbar_x = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=self.tree_scrollbar_y.set,
                          xscrollcommand=self.tree_scrollbar_x.set)
        
        # grid layout
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_variables(self, variables: List[Dict[str, Any]]):
        """
        Update the variables displayed in the inspector.
        
        Args:
            variables: List of variable dictionaries with name, value, type and scope
        """
        # clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # add the new variables
        for var in variables:
            # insert into the tree
            values = (
                var.get('name', ''),
                var.get('value', ''),
                var.get('type', ''),
                var.get('scope', '')
            )
            
            self.tree.insert('', tk.END, text='', values=values)
    
    def clear(self):
        """Clear all variables."""
        for item in self.tree.get_children():
            self.tree.delete(item)

class IOConsole(tk.Frame):
    """
    Component for displaying standard output and error.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the IOConsole widget.
        
        Args:
            parent: Parent widget
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create a notebook with tabs for stdout and stderr
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # create stdout frame
        self.stdout_frame = tk.Frame(self.notebook)
        self.stdout_text = tk.Text(self.stdout_frame, wrap=tk.WORD, height=10, padx=5, pady=5)
        self.stdout_scrollbar = ttk.Scrollbar(self.stdout_frame, command=self.stdout_text.yview)
        self.stdout_text.configure(yscrollcommand=self.stdout_scrollbar.set)
        
        self.stdout_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stdout_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # create stderr frame
        self.stderr_frame = tk.Frame(self.notebook)
        self.stderr_text = tk.Text(self.stderr_frame, wrap=tk.WORD, height=10, padx=5, pady=5)
        self.stderr_scrollbar = ttk.Scrollbar(self.stderr_frame, command=self.stderr_text.yview)
        self.stderr_text.configure(yscrollcommand=self.stderr_scrollbar.set)
        
        self.stderr_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stderr_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # set text widget colors
        self.stdout_text.configure(bg="#FFFFFF", state=tk.DISABLED)
        self.stderr_text.configure(bg="#FFEEEE", state=tk.DISABLED)
        
        # configure tags
        self.stdout_text.tag_configure("output", foreground="#000000")
        self.stderr_text.tag_configure("error", foreground="#CC0000")
        
        # add the frames to the notebook
        self.notebook.add(self.stdout_frame, text="Standard Output")
        self.notebook.add(self.stderr_frame, text="Standard Error")
    
    def update_stdout(self, text: str):
        """
        Update the stdout display.
        
        Args:
            text: Text to display
        """
        # enable editing
        self.stdout_text.configure(state=tk.NORMAL)
        
        # clear existing content
        self.stdout_text.delete("1.0", tk.END)
        
        # insert the new text
        self.stdout_text.insert(tk.END, text, "output")
        
        # disable editing
        self.stdout_text.configure(state=tk.DISABLED)
        
        # show stdout tab
        self.notebook.select(0)
    
    def update_stderr(self, text: str):
        """
        Update the stderr display.
        
        Args:
            text: Text to display
        """
        # enable editing
        self.stderr_text.configure(state=tk.NORMAL)
        
        # clear existing content
        self.stderr_text.delete("1.0", tk.END)
        
        # insert the new text
        self.stderr_text.insert(tk.END, text, "error")
        
        # disable editing
        self.stderr_text.configure(state=tk.DISABLED)
        
        # if there's error text, show stderr tab
        if text:
            self.notebook.select(1)
    
    def clear(self):
        """Clear both stdout and stderr."""
        # enable editing
        self.stdout_text.configure(state=tk.NORMAL)
        self.stderr_text.configure(state=tk.NORMAL)
        
        # clear existing content
        self.stdout_text.delete("1.0", tk.END)
        self.stderr_text.delete("1.0", tk.END)
        
        # disable editing
        self.stdout_text.configure(state=tk.DISABLED)
        self.stderr_text.configure(state=tk.DISABLED)

class DebuggerPanel(tk.Frame):
    """
    A comprehensive debugging panel with execution controls, variable inspection, and I/O console.
    """
    
    def __init__(self, parent, on_step=None, on_run=None, on_stop=None, *args, **kwargs):
        """
        Initialize the DebuggerPanel widget.
        
        Args:
            parent: Parent widget
            on_step: Callback function for stepping
            on_run: Callback function for running
            on_stop: Callback function for stopping
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        self.on_step = on_step
        self.on_run = on_run
        self.on_stop = on_stop
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create the execution controls
        self.controls = StepExecutionControls(
            self, 
            on_step=self.on_step,
            on_run=self.on_run,
            on_stop=self.on_stop
        )
        self.controls.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # create a paned window for variable inspector and io console
        self.toggle_frame = ttk.Frame(self)
        self.toggle_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=0)

        self.toggle_button = tk.Button(
            self.toggle_frame, 
            text="Hide Variables",
            bg='black',
            fg='white',
            activebackground='#333333',
            activeforeground='white',
            command=self.toggle_variable_inspector
        )
        self.toggle_button.pack(side=tk.TOP, anchor=tk.NW, padx=5, pady=0)

        # create a paned window for variable inspector and IO console
        self.paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.paned.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # create the variable inspector
        self.variable_inspector = VariableInspector(self)

        # create the io console
        self.io_console = IOConsole(self)

        # add components to the paned window
        self.paned.add(self.variable_inspector, weight=1)
        self.paned.add(self.io_console, weight=1)

    def toggle_variable_inspector(self):
        """Toggle the visibility of the variable inspector"""

        # get current sash position
        current_position = self.paned.sashpos(0)

        if current_position > 10: # if visible (has non-minimal width)
            # store the current position before collapsing
            self._last_sash_position = current_position
            # move sash to minimum position
            self.paned.sashpos(0, 0)
            # update button text
            self.toggle_button.config(text="Show Variables")
        else:
            # if we have a stored sash position, restore it, otherwise use default
            restore_position = getattr(self, '_last_sash_position', int(self.winfo_width() * 0.5))
            self.paned.sashpos(0, restore_position)
            # update button text
            self.toggle_button.config(text="Hide Variables")
    
    def update_variables(self, variables: List[Dict[str, Any]]):
        """
        Update the variables displayed in the inspector.
        
        Args:
            variables: List of variable dictionaries
        """
        self.variable_inspector.update_variables(variables)
    
    def update_stdout(self, text: str):
        """
        Update the stdout display.
        
        Args:
            text: Text to display
        """
        self.io_console.update_stdout(text)
    
    def update_stderr(self, text: str):
        """
        Update the stderr display.
        
        Args:
            text: Text to display
        """
        self.io_console.update_stderr(text)
    
    def reset(self):
        """Reset the debugger state."""
        self.controls.reset_state()
        self.variable_inspector.clear()
        self.io_console.clear()
