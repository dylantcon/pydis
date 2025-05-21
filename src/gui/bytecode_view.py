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
        
        # dictionary to map Python line numbers to bytecode lines
        self.line_map = {}
    
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
            item_values = self.tree.item(item_id, "values")
            if item_values and len(item_values) > 1:
                try:
                    item_offset = int(item_values[1])  # offset value
                    # find the instruction in the text view
                    self._highlight_instruction_in_text(item_offset)
                except (ValueError, TypeError):
                    pass
    
    def _highlight_instruction_in_text(self, offset: int):
        """
        Highlight the instruction with the given offset in the text view.
        
        Args:
            offset: The bytecode offset to highlight
        """
        # remove existing highlights
        self.text_view.tag_remove("highlight", "1.0", tk.END)
        
        # Ensure offset is an integer for string formatting
        try:
            offset = int(offset)
        except (ValueError, TypeError):
            return
        
        # Find the instruction in the text
        text_content = self.text_view.get("1.0", tk.END)
        
        # Look for lines that contain the offset
        pattern = r'(?m)^.*?\b' + str(offset) + r'\b.*$'
        match = re.search(pattern, text_content)
        
        if match:
            # Find the line number where the match was found
            line_num = text_content.count('\n', 0, match.start()) + 1
            start_pos = f"{line_num}.0"
            end_pos = f"{line_num + 1}.0"
            
            # Apply highlighting
            self.text_view.tag_add("highlight", start_pos, end_pos)
            
            # Make sure the highlighted part is visible
            self.text_view.see(start_pos)
    
    def _build_line_map(self, bytecode_text: str):
        """
        Build a mapping of Python line numbers to bytecode text lines.
        
        Args:
            bytecode_text: The disassembled bytecode text
        """
        self.line_map = {}
        
        # Split the bytecode text into lines
        lines = bytecode_text.split('\n')
        
        # Process each line
        for i, line in enumerate(lines):
            # Match line number at beginning of line, allowing for spacing variations
            # Example format: "  90           LOAD_NAME"
            line_match = re.match(r'^\s*(\d+)\s+', line)
            if line_match:
                try:
                    line_num = int(line_match.group(1))
                    
                    # Add to the line map
                    if line_num not in self.line_map:
                        self.line_map[line_num] = []
                    
                    self.line_map[line_num].append(i)
                except (ValueError, TypeError):
                    pass
                    
        # Debug the line map (consider removing in production)
        # print(f"Built line map with {len(self.line_map)} line numbers")
        # for k, v in self.line_map.items():
        #     print(f"Line {k}: {v}")
    
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
        
        # build the line map
        self._build_line_map(bytecode_text)
    
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
        # Convert offset to int to ensure type compatibility
        try:
            offset = int(offset)
        except (ValueError, TypeError):
            return
        
        # find and select the item in the tree
        for item in self.tree.get_children():
            # Get the offset value from the tree item
            item_values = self.tree.item(item, "values")
            if not item_values or len(item_values) < 2:
                continue
                
            try:
                item_offset = int(item_values[1])  # offset value
                if item_offset == offset:
                    # select the item
                    self.tree.selection_set(item)
                    self.tree.see(item)
                    
                    # highlight in the text view
                    self._highlight_instruction_in_text(offset)
                    break
            except (ValueError, TypeError):
                continue
    
    def highlight_line_number(self, line_number: int):
        """
        Highlight all bytecode instructions for a specific Python line number.
        
        Args:
            line_number: Python source code line number
        """
        # Convert line_number to int to ensure type compatibility
        try:
            line_number = int(line_number)
        except (ValueError, TypeError):
            return
        
        # Clear previous highlights
        self.text_view.tag_remove("highlight", "1.0", tk.END)
        
        # Ensure we're on the Bytecode Text tab
        self.notebook.select(0)  # Index 0 is the Bytecode Text tab
        
        # Get all lines that match this Python line number
        highlighted = False
        
        # Try our line map first - this is the most reliable method
        if line_number in self.line_map:
            # Highlight each bytecode line for this Python line
            for line_idx in self.line_map[line_number]:
                # Convert to 1-based indexing for text widget
                start_pos = f"{line_idx + 1}.0"
                end_pos = f"{line_idx + 1}.end"
                
                # Apply highlighting
                self.text_view.tag_add("highlight", start_pos, end_pos)
                highlighted = True
                
                # Ensure the first highlighted line is visible
                if line_idx == self.line_map[line_number][0]:
                    self.text_view.see(start_pos)
        
        # If line map didn't work, try direct text search
        if not highlighted:
            text_content = self.text_view.get("1.0", tk.END)
            lines = text_content.split('\n')
            
            # Look for lines that start with the line number
            # This pattern handles the actual format of the bytecode text
            pattern = r'^\s*' + str(line_number) + r'\s+'
            
            # Find and highlight matching lines
            for i, line in enumerate(lines):
                if re.match(pattern, line):
                    start_pos = f"{i + 1}.0"
                    end_pos = f"{i + 1}.end"
                    
                    # Apply highlighting
                    self.text_view.tag_add("highlight", start_pos, end_pos)
                    highlighted = True
                    
                    # Ensure visibility
                    self.text_view.see(start_pos)
        
        # If still no highlighting, try fuzzy match as last resort
        if not highlighted:
            # Find closest matching line number
            closest_line = None
            closest_diff = float('inf')
            
            for py_line in self.line_map.keys():
                diff = abs(py_line - line_number)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_line = py_line
            
            # If we found a close match, use it
            if closest_line is not None and closest_diff <= 5:  # within 5 lines
                self.highlight_line_number(closest_line)
    
    def clear_highlights(self):
        """Clear all highlights."""
        self.text_view.tag_remove("highlight", "1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())
