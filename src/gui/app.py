"""
Main application window for the pydis application.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from typing import Optional

from src.core.disassembler import Disassembler
from src.core.executor import Executor
from src.core.file_handler import FileHandler
from src.gui.code_view import CodeView
from src.gui.bytecode_view import BytecodeView
from src.gui.toolbar import Toolbar
from src.gui.debugger import DebuggerPanel

class PyDisApp(tk.Tk):
    """
    Main application window for the pydis application.
    """
    
    def __init__(self):
        """Initialize the application window."""
        super().__init__()

        # Set window properties
        self.title("PyDis - Python Bytecode Disassembler")
        self.geometry("1200x800")
        self.minsize(800, 600)

        # Initialize core components
        self.disassembler = Disassembler()
        self.executor = Executor()
        self.file_handler = FileHandler()

        # Initialize state variables
        self.current_file = None
        self.bytecode_generated = False
        self.code_view_visible = True

        # Set up the UI
        self._setup_ui()

        # Set up event bindings
        self._setup_bindings()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create toolbar
        self.toolbar = Toolbar(self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # set up toolbar callbacks
        self._setup_toolbar_callbacks()
        
        # create main vertical layout
        self.main_vertical = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.main_vertical.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # create the horizontal paned window for code and bytecode
        self.code_bytecode_paned = ttk.PanedWindow(self.main_vertical, orient=tk.HORIZONTAL)
        
        # create the code view
        self.code_frame = ttk.LabelFrame(self.code_bytecode_paned, text="Python Code")
        self.code_view = CodeView(self.code_frame)
        self.code_view.pack(fill=tk.BOTH, expand=True)
        
        # create the bytecode view
        self.bytecode_frame = ttk.LabelFrame(self.code_bytecode_paned, text="Python Bytecode")
        self.bytecode_view = BytecodeView(self.bytecode_frame)
        self.bytecode_view.pack(fill=tk.BOTH, expand=True)
        
        # add frames to the horizontal paned window
        self.code_bytecode_paned.add(self.code_frame, weight=1)
        self.code_bytecode_paned.add(self.bytecode_frame, weight=1)
        
        # add the code/bytecode panes to the main vertical layout
        self.main_vertical.add(self.code_bytecode_paned, weight=3)
        
        # create the console panel
        self.console_frame = ttk.LabelFrame(self.main_vertical, text="Console")
        
        # create a horizontal paned window for console components
        self.console_paned = ttk.PanedWindow(self.console_frame, orient=tk.HORIZONTAL)
        self.console_paned.pack(fill=tk.BOTH, expand=True)
        
        # create execution controls
        self.execution_controls = ttk.Frame(self.console_frame)
        self.execution_controls.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # create the debugger panel
        self.debugger_panel = DebuggerPanel(
            self.console_frame,
            on_step=self._on_debug_step,
            on_run=self._on_debug_run,
            on_stop=self._on_debug_stop
        )
        self.debugger_panel.pack(fill=tk.BOTH, expand=True)
        
        # add the console frame to the main vertical layout
        self.main_vertical.add(self.console_frame, weight=1)
        
        # create status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # configure the default view (hide debug controls initially)
        self._reset_console_mode()

    def _reset_console_mode(self, mode="normal"):
        """
        Reset the console to a specific mode.
        
        Args:
            mode: "normal" or "debug"
        """
        # reset the debugger panel
        self.debugger_panel.reset()
        
        if mode == "normal":
            # hide step controls for normal execution
            self.debugger_panel.controls.step_button.pack_forget()
            self.debugger_panel.controls.run_button.pack_forget()
            self.debugger_panel.controls.stop_button.pack_forget()
        else:
            # show step controls for debugging
            self.debugger_panel.controls.step_button.pack(side=tk.LEFT, padx=5)
            self.debugger_panel.controls.run_button.pack(side=tk.LEFT, padx=5)
            self.debugger_panel.controls.stop_button.pack(side=tk.LEFT, padx=5)
            self.debugger_panel.controls.reset_state()
    
    def _setup_toolbar_callbacks(self):
        """Set up callbacks for toolbar buttons."""
        self.toolbar.set_callback('new', self._on_new)
        self.toolbar.set_callback('open', self._on_open)
        self.toolbar.set_callback('save', self._on_save)
        self.toolbar.set_callback('save_bytecode', self._on_save_bytecode)
        self.toolbar.set_callback('disassemble', self._on_disassemble)
        self.toolbar.set_callback('execute', self._on_execute)
        self.toolbar.set_callback('debug', self._on_debug)
        self.toolbar.set_callback('toggle_code', self._on_toggle_code)
    
    def _setup_bindings(self):
        """Set up event bindings."""
        # keyboard shortcuts
        self.bind("<Control-n>", lambda e: self._on_new())
        self.bind("<Control-o>", lambda e: self._on_open())
        self.bind("<Control-s>", lambda e: self._on_save())
        self.bind("<F5>", lambda e: self._on_execute())
        self.bind("<F9>", lambda e: self._on_disassemble())
        self.bind("<F10>", lambda e: self._on_debug())
    
    def _on_new(self):
        """Handle new file action."""
        # check if there are unsaved changes
        if self._check_unsaved_changes():
            return
        
        # clear the code view
        self.code_view.set_text("")
        
        # reset state
        self.current_file = None
        self.bytecode_generated = False
        self.toolbar.enable_bytecode_operations(False)
        
        # update status
        self._update_status("New file created")
    
    def _on_open(self):
        """Handle open file action."""
        # check if there are unsaved changes
        if self._check_unsaved_changes():
            return
        
        # show file dialog
        file_path = filedialog.askopenfilename(
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        
        if file_path:
            # read the file
            content, error = self.file_handler.read_python_file(file_path)
            
            if error:
                messagebox.showerror("Error", f"Failed to open file: {error}")
                return
            
            # set the code
            self.code_view.set_text(content)
            
            # update state
            self.current_file = file_path
            self.bytecode_generated = False
            self.toolbar.enable_bytecode_operations(False)
            
            # update status
            self._update_status(f"Opened {os.path.basename(file_path)}")
    
    def _on_save(self):
        """Handle save file action."""
        if not self.current_file:
            # if no current file, use save as
            return self._on_save_as()
        
        # get the code
        code = self.code_view.get_text()
        
        # save the file
        error = self.file_handler.save_python_file(self.current_file, code)
        
        if error:
            messagebox.showerror("Error", f"Failed to save file: {error}")
            return
        
        # update status
        self._update_status(f"Saved {os.path.basename(self.current_file)}")
        
        return True
    
    def _on_save_as(self):
        """Handle save as action."""
        # show file dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return False
        
        # get the code
        code = self.code_view.get_text()
        
        # save the file
        error = self.file_handler.save_python_file(file_path, code)
        
        if error:
            messagebox.showerror("Error", f"Failed to save file: {error}")
            return False
        
        # update state
        self.current_file = file_path
        
        # update status
        self._update_status(f"Saved {os.path.basename(file_path)}")
        
        return True
    
    def _on_save_bytecode(self):
        """Handle save bytecode action."""
        if not self.bytecode_generated:
            messagebox.showinfo("Info", "Please disassemble the code first.")
            return
        
        # show file dialog with options
        file_types = [
            ("Text Files", "*.txt"),
            ("Binary Bytecode", "*.pyc"),
            ("JSON Files", "*.json"),
            ("Markdown Report", "*.md"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=file_types
        )
        
        if not file_path:
            return
        
        # determine the file type based on extension
        _, ext = os.path.splitext(file_path)
        
        # get the code
        code = self.code_view.get_text()
        
        # get bytecode text
        bytecode_text, _ = self.disassembler.disassemble_code(code)
        
        # get bytecode instructions
        instructions, _ = self.disassembler.get_bytecode_details(code)
        
        # save based on file type
        error = None
        
        if ext.lower() == '.txt':
            error = self.file_handler.save_bytecode_text(file_path, bytecode_text)
        elif ext.lower() == '.pyc':
            error = self.file_handler.save_bytecode_binary(file_path, code)
        elif ext.lower() == '.json':
            error = self.file_handler.save_bytecode_json(file_path, instructions)
        elif ext.lower() == '.md':
            error = self.file_handler.export_bytecode_report(file_path, code, bytecode_text, instructions)
        else:
            # default to text
            error = self.file_handler.save_bytecode_text(file_path, bytecode_text)
        
        if error:
            messagebox.showerror("Error", f"Failed to save bytecode: {error}")
            return
        
        # update status
        self._update_status(f"Saved bytecode to {os.path.basename(file_path)}")
    
    def _on_disassemble(self):
        """Handle disassemble action."""
        # get the code
        code = self.code_view.get_text()
        
        if not code.strip():
            messagebox.showinfo("Info", "No code to disassemble.")
            return
        
        # disassemble the code
        bytecode_text, error = self.disassembler.disassemble_code(code)
        
        if error:
            messagebox.showerror("Error", f"Failed to disassemble code: {error}")
            return
        
        # get detailed bytecode information
        instructions, error = self.disassembler.get_bytecode_details(code)
        
        if error:
            messagebox.showerror("Error", f"Failed to get bytecode details: {error}")
            return
        
        # update the bytecode view
        self.bytecode_view.set_bytecode_text(bytecode_text)
        self.bytecode_view.set_bytecode_instructions(instructions)
        
        # update state
        self.bytecode_generated = True
        self.toolbar.enable_bytecode_operations(True)
        
        # update status
        self._update_status("Code disassembled")
    
    def _on_execute(self):
        """Handle execute action."""
        # get the code
        code = self.code_view.get_text()
        
        if not code.strip():
            messagebox.showinfo("Info", "No code to execute.")
            return
        
        # reset the console to normal mode
        self._reset_console_mode("normal")
        
        # execute the code
        locals_dict, stdout, stderr, error = self.executor.execute_code(code)
        
        # update the console with results
        self.debugger_panel.update_variables(
            [{'name': name, 'value': repr(value), 'type': type(value).__name__, 'scope': 'local'} 
             for name, value in locals_dict.items()]
        )
        self.debugger_panel.update_stdout(stdout)
        self.debugger_panel.update_stderr(stderr)
        
        # update status
        if error:
            self._update_status(f"Execution failed: {type(error).__name__}")
        else:
            self._update_status("Code executed successfully")
    
    def _on_debug(self):
        """Handle debug action."""
        # get the code
        code = self.code_view.get_text()
        
        if not code.strip():
            messagebox.showinfo("Info", "No code to debug.")
            return
        
        # make sure bytecode is disassembled
        if not self.bytecode_generated:
            self._on_disassemble()
        
        # reset the console to debug mode
        self._reset_console_mode("debug")
        
        # set up for step-by-step execution
        self.executor.execute_step_by_step(code)
        
        # update status
        self._update_status("Debugging started")
    
    def _on_debug_step(self):
        """Handle debug step action."""
        # execute the next step
        self.executor.step()
        
        # update the ui with the current state
        self._update_debug_ui()
    
    def _on_debug_run(self):
        """Handle debug run action."""
        # start a background thread to run the execution
        import threading
        
        def run_execution():
            while self.executor._is_running and not self.executor._should_stop:
                self.executor.step()
                
                # update the ui periodically
                self.after(100, self._update_debug_ui)
        
        # start the thread
        thread = threading.Thread(target=run_execution)
        thread.daemon = True
        thread.start()
    
    def _on_debug_stop(self):
        """Handle debug stop action."""
        # stop the execution
        self.executor.stop_execution()
        
        # update the ui with the final state
        self._update_debug_ui()
        
        # update status
        self._update_status("Debugging stopped")
    
    def _update_debug_ui(self):
        """Update the debug UI with the current execution state."""
        # get the current state
        state = self.executor.get_current_state()
        
        # update the debugger panel
        self.debugger_panel.update_stdout(state['stdout'])
        self.debugger_panel.update_stderr(state['stderr'])
        
        # update variable inspector
        variables = self.executor.get_variable_info()
        self.debugger_panel.update_variables(variables)
        
        # update code highlighting if there's a current line
        if state['execution_trace']:
            latest_step = state['execution_trace'][-1]
            lineno = latest_step.get('lineno')
            
            if lineno:
                # highlight the line in the code view
                self.code_view.highlight_line(lineno)
                
                # find and highlight corresponding bytecode instructions
                self._highlight_bytecode_for_line(lineno)
    
    def _highlight_bytecode_for_line(self, line_number: int):
        """
        Highlight bytecode instructions associated with a Python line number.
        
        Args:
            line_number: Python source code line number
        """
        # clear previous highlights
        self.bytecode_view.clear_highlights()
        
        # find all bytecode instructions for this line
        highlighted = False
        
        # check if there are instructions
        if not hasattr(self.bytecode_view, 'instructions') or not self.bytecode_view.instructions:
            return
            
        # find the first instruction for this line
        for instr in self.bytecode_view.instructions:
            if instr.get('starts_line') == line_number:
                # highlight this instruction
                self.bytecode_view.highlight_instruction(instr.get('offset'))
                highlighted = True
                break
        
        # if no exact match, try to find the closest instruction
        if not highlighted:
            prev_line = 0
            best_instr = None
            
            for instr in self.bytecode_view.instructions:
                starts_line = instr.get('starts_line')
                if starts_line is not None and prev_line < starts_line <= line_number:
                    prev_line = starts_line
                    best_instr = instr
            
            if best_instr:
                self.bytecode_view.highlight_instruction(best_instr.get('offset'))
    
    def _on_toggle_code(self):
        """Handle toggle code view action."""
        if self.code_view_visible:
            # hide code view
            self.code_bytecode_paned.forget(self.code_frame)
            self.toolbar.set_toggle_code_text("Show Code")
            self.code_view_visible = False
        else:
            # show code view
            self.code_bytecode_paned.insert(0, self.code_frame, weight=1)
            self.toolbar.set_toggle_code_text("Hide Code")
            self.code_view_visible = True
    
    def _check_unsaved_changes(self) -> bool:
        """
        Check if there are unsaved changes and prompt the user to save.
        
        Returns:
            True if operation should be cancelled, False otherwise
        """
        # for now, always assume there are changes if there's code
        code = self.code_view.get_text().strip()
        if not code:
            return False
        
        # ask the user if they want to save
        response = messagebox.askyesnocancel("Unsaved Changes", 
                                           "Do you want to save changes before continuing?")
        
        if response is None:  # cancel
            return True
        elif response:  # yes
            return not self._on_save()
        else:  # no
            return False
    
    def _update_status(self, message: str):
        """
        Update the status bar message.
        
        Args:
            message: Message to display
        """
        self.status_bar.config(text=message)
        
        # clear the message after a delay
        self.after(5000, lambda: self.status_bar.config(text="Ready"))
