"""
Toolbar module for the application.
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

class Toolbar(tk.Frame):
    """
    Toolbar with common actions for the pydis application.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the Toolbar widget.
        
        Args:
            parent: Parent widget
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        
        # callbacks
        self._callbacks = {
            'new': None,
            'open': None,
            'save': None,
            'save_bytecode': None,
            'disassemble': None,
            'execute': None,
            'debug': None,
            'toggle_code': None,
        }
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # configure style for buttons
        self.configure(bg="#f0f0f0")
        
        # file operations
        self.file_frame = tk.Frame(self, bg="#f0f0f0")
        self.file_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(self.file_frame, text="File:").pack(side=tk.LEFT, padx=2)
        
        self.new_button = ttk.Button(self.file_frame, text="New", 
                                    command=lambda: self._trigger_callback('new'))
        self.new_button.pack(side=tk.LEFT, padx=2)
        
        self.open_button = ttk.Button(self.file_frame, text="Open", 
                                     command=lambda: self._trigger_callback('open'))
        self.open_button.pack(side=tk.LEFT, padx=2)
        
        self.save_button = ttk.Button(self.file_frame, text="Save", 
                                     command=lambda: self._trigger_callback('save'))
        self.save_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # bytecode operations
        self.bytecode_frame = tk.Frame(self, bg="#f0f0f0")
        self.bytecode_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(self.bytecode_frame, text="Bytecode:").pack(side=tk.LEFT, padx=2)
        
        self.disassemble_button = ttk.Button(self.bytecode_frame, text="Disassemble", 
                                           command=lambda: self._trigger_callback('disassemble'))
        self.disassemble_button.pack(side=tk.LEFT, padx=2)
        
        self.save_bytecode_button = ttk.Button(self.bytecode_frame, text="Save Bytecode", 
                                             command=lambda: self._trigger_callback('save_bytecode'))
        self.save_bytecode_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # execution operations
        self.execution_frame = tk.Frame(self, bg="#f0f0f0")
        self.execution_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(self.execution_frame, text="Execution:").pack(side=tk.LEFT, padx=2)
        
        self.execute_button = ttk.Button(self.execution_frame, text="Execute", 
                                       command=lambda: self._trigger_callback('execute'))
        self.execute_button.pack(side=tk.LEFT, padx=2)
        
        self.debug_button = ttk.Button(self.execution_frame, text="Debug", 
                                      command=lambda: self._trigger_callback('debug'))
        self.debug_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        
        # view operations
        self.view_frame = tk.Frame(self, bg="#f0f0f0")
        self.view_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(self.view_frame, text="View:").pack(side=tk.LEFT, padx=2)
        
        self.toggle_code_button = ttk.Button(self.view_frame, text="Toggle Code", 
                                           command=lambda: self._trigger_callback('toggle_code'))
        self.toggle_code_button.pack(side=tk.LEFT, padx=2)
        
        # disable certain buttons initially
        self.save_bytecode_button.config(state=tk.DISABLED)
    
    def _trigger_callback(self, name: str):
        """
        Trigger a callback function.
        
        Args:
            name: Name of the callback to trigger
        """
        callback = self._callbacks.get(name)
        if callback:
            callback()
    
    def set_callback(self, name: str, callback: Callable):
        """
        Set a callback function.
        
        Args:
            name: Name of the callback to set
            callback: Callback function
        """
        self._callbacks[name] = callback
    
    def enable_bytecode_operations(self, enable: bool = True):
        """
        Enable or disable bytecode operations.
        
        Args:
            enable: Whether to enable the operations
        """
        state = tk.NORMAL if enable else tk.DISABLED
        self.save_bytecode_button.config(state=state)
    
    def set_toggle_code_text(self, text: str):
        """
        Set the text of the toggle code button.
        
        Args:
            text: Text to set
        """
        self.toggle_code_button.config(text=text)
