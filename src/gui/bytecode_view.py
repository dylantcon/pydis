"""
Bytecode view module for displaying Python bytecode.
"""
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from typing import List, Dict, Any, Optional
import re

class BytecodeView(tk.Frame):
    """
    A component for displaying Python bytecode.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the BytecodeView widget.
        
        Args:
            parent: Parent widget
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        self._setup_ui()
        self._setup_bindings()
        
        # keep track of the current instruction
        self.current_instruction = None
        
        # store the full instruction list
        self.instructions = []
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create a notebook with different views
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # create frames for each view
        self.text_frame = tk.Frame(self.notebook)
        self.table_frame = tk.Frame(self.notebook)
        
        # add the frames to the notebook
        self.notebook.add(self.text_frame, text="Bytecode Text")
        self.notebook.add(self.table_frame, text="Instruction Table")
        
        # set up the text view
        self.text_view = tk.Text(self.text_frame, wrap=tk.NONE, padx=5, pady=5)
        self.text_scrollbar_y = tk.Scrollbar(self.text_frame, command=self.text_view.yview)
        self.text_scrollbar_x = tk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL, 
                                          command=self.text_view.xview)
        
        self.text_view.configure(yscrollcommand=self.text_scrollbar_y.set, 
                               xscrollcommand=self.text_scrollbar_x.set)
        
        # grid layout for text view
        self.text_view.grid(row=0, column=0, sticky="nsew")
        self.text_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.text_scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # configure grid weights for text frame
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)
        
        # set up the table view
        self.tree = ttk.Treeview(self.table_frame, columns=("line", "offset", "opcode", "opname", 
                                                         "arg", "argval", "argrepr"))
        
        # define column headings
        self.tree.heading("#0", text="")
        self.tree.heading("line", text="Line")
        self.tree.heading("offset", text="Offset")
        self.tree.heading("opcode", text="Op Code")
        self.tree.heading("opname", text="Operation")
        self.tree.heading("arg", text="Arg")
        self.tree.heading("argval", text="Arg Value")
        self.tree.heading("argrepr", text="Arg Repr")
        
        # define column widths
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("line", width=50)
        self.tree.column("offset", width=60)
        self.tree.column("opcode", width=60)
        self.tree.column("opname", width=120)
        self.tree.column("arg", width=60)
        self.tree.column("argval", width=150)
        self.tree.column("argrepr", width=150)
        
        # add scrollbars for the table
        self.tree_scrollbar_y = tk.Scrollbar(self.table_frame, command=self.tree.yview)
        self.tree_scrollbar_x = tk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, 
                                          command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=self.tree_scrollbar_y.set,
                          xscrollcommand=self.tree_scrollbar_x.set)
        
        # grid layout for table view
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree_scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # configure grid weights for table frame
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)
        
        # configure the font for text view - use monospace
        font = tkfont.Font(family="Courier New", size=10)
        self.text_view.configure(font=font)
        
        # configure tags for highlighting
        self.text_view.tag_configure("highlight", background="#E6F3FF")
        self.text_view.tag_configure("instruction_line", background="#E6F3FF")
        
        # make the text view read-only
        self.text_view.configure(state=tk.DISABLED)
    
    def _setup_bindings(self):
        """Set up event bindings."""
        # handle tree view item selection
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
    
    def _on_tree_select(self, event):
        """Handle selection of an instruction in the tree view."""
        selected_items = self.tree.selection()
        if selected_items:
            item_id = selected_items[0]
            item_index = int(self.tree.item(item_id, "values")[1])  # offset value
            
            # find the instruction in the text view
            self._highlight_instruction_in_text(item_index)
    
    def _highlight_instruction_in_text(self, offset: int):
        """
        Highlight the instruction with the given offset in the text view.
        
        Args:
            offset: The bytecode offset to highlight
        """
        # remove existing highlights
        self.text_view.tag_remove("highlight", "1.0", tk.END)
        
        # find the instruction in the text
        text_content = self.text_view.get("1.0", tk.END)
        pattern = r"(\d+\s+)" + str(offset) + r"\s+"
        
        match = re.search(pattern, text_content)
        if match:
            start_index = f"1.0+{match.start()}c"
            
            # find the end of line
            line_end = self.text_view.search("\n", start_index, tk.END)
            if not line_end:
                line_end = tk.END
            
            # apply highlighting
            self.text_view.tag_add("highlight", start_index, line_end)
            
            # ensure the highlighted part is visible
            self.text_view.see(start_index)
    
    def set_bytecode_text(self, bytecode_text: str):
        """
        Set the bytecode text in the text view.
        
        Args:
            bytecode_text: Disassembled bytecode text
        """
        # enable editing temporarily
        self.text_view.configure(state=tk.NORMAL)
        
        # clear existing content
        self.text_view.delete("1.0", tk.END)
        
        # insert the new bytecode
        self.text_view.insert(tk.END, bytecode_text)
        
        # make read-only again
        self.text_view.configure(state=tk.DISABLED)
    
    def set_bytecode_instructions(self, instructions: List[Dict[str, Any]]):
        """
        Set the bytecode instructions in the table view.
        
        Args:
            instructions: List of bytecode instruction dictionaries
        """
        # store the instructions
        self.instructions = instructions
        
        # clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # add the new instructions
        for i, instr in enumerate(instructions):
            values = (
                instr.get('starts_line', ''),
                instr.get('offset', ''),
                instr.get('opcode', ''),
                instr.get('opname', ''),
                instr.get('arg', ''),
                instr.get('argval', ''),
                instr.get('argrepr', '')
            )
            
            # insert into the tree
            self.tree.insert('', tk.END, text='', values=values, tags=('instruction',))
    
    def highlight_instruction(self, offset: int):
        """
        Highlight a specific instruction by its offset.
        
        Args:
            offset: Bytecode offset of the instruction to highlight
        """
        # find and select the item in the tree
        for item in self.tree.get_children():
            item_offset = int(self.tree.item(item, "values")[1])  # offset value
            if item_offset == offset:
                # select the item
                self.tree.selection_set(item)
                self.tree.see(item)
                
                # highlight in the text view
                self._highlight_instruction_in_text(offset)
                break
    
    def clear_highlights(self):
        """Clear all highlights."""
        self.text_view.tag_remove("highlight", "1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())
