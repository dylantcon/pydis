"""
PyDis - Python Bytecode Disassembler Application

A GUI-based tool for disassembling Python code into bytecode,
with features for step-by-step execution, variable inspection, and I/O handling.

This is the main entry point for the application.
"""
import sys
import os
import tkinter as tk

# add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.app import PyDisApp

def main():
    """
    Main entry point for the PyDis application.
    """
    # create and run the application
    app = PyDisApp()
    app.mainloop()

if __name__ == "__main__":
    main()
