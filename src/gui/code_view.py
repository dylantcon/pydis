"""
Code view module for displaying and editing Python code.
"""
import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as tkfont
from typing import Callable, Optional
import re

class CodeView(tk.Frame):
    """
    A text editor component with syntax highlighting for Python code.
    """
    
    def __init__(self, parent, *args, **kwargs):
        """
        Initialize the CodeView widget.
        
        Args:
            parent: Parent widget
            *args, **kwargs: Additional arguments to pass to tk.Frame
        """
        super().__init__(parent, *args, **kwargs)
        self._setup_ui()
        self._setup_tags()
        self._setup_bindings()
        
        # keep track of the last highlight position
        self._last_highlight_pos = "1.0"
        
        # a list of line numbers with errors or highlights
        self.highlighted_lines = set()
    
    def _setup_ui(self):
        """Set up the UI components."""
        # create a frame for the line numbers
        self.line_frame = tk.Frame(self, width=30, bg="#F0F0F0")
        self.line_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # create a text widget for line numbers
        self.line_numbers = tk.Text(self.line_frame, width=4, padx=5, pady=5, 
                                  bg="#F0F0F0", fg="#606060", 
                                  highlightthickness=0, bd=0)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.configure(state=tk.DISABLED)
        
        # create a text widget for code
        self.text = scrolledtext.ScrolledText(self, padx=5, pady=5, wrap=tk.NONE,
                                            undo=True, maxundo=-1)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # configure the font - use monospace
        font = tkfont.Font(family="Courier New", size=10)
        self.text.configure(font=font)
        self.line_numbers.configure(font=font)
        
        # configure tab size (4 spaces)
        self.text.configure(tabs=font.measure(' ' * 4))
        
        # add a vertical scrollbar
        self.text_scrollbar = self.text.vbar
        
        # bind the scrollbar to the line numbers
        self.text_scrollbar.config(command=self._on_text_scroll)
    
    def _setup_tags(self):
        """Set up text tags for syntax highlighting."""
        # define color scheme
        self.text.tag_configure("keyword", foreground="#0033B3")  # blue
        self.text.tag_configure("string", foreground="#067D17")   # green
        self.text.tag_configure("comment", foreground="#8C8C8C")  # gray
        self.text.tag_configure("function", foreground="#7D0552") # purple
        self.text.tag_configure("class", foreground="#7D0552")    # purple
        self.text.tag_configure("number", foreground="#1750EB")   # light blue
        self.text.tag_configure("background", background="#FFFFFF") # white background
        self.text.tag_configure("error_line", background="#FFE6E6") # light red background for errors
        self.text.tag_configure("highlight_line", background="#E6F3FF") # light blue background for highlights
        
        # define patterns for syntax highlighting
        self.patterns = [
            # keywords
            (r'\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|'
             r'elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|'
             r'not|or|pass|raise|return|try|while|with|yield)\b', 'keyword'),
            
            # strings (triple quoted)
            (r'""".*?"""', 'string'),
            (r"'''.*?'''", 'string'),
            
            # strings (single line)
            (r'"[^"\\]*(?:\\.[^"\\]*)*"', 'string'),
            (r"'[^'\\]*(?:\\.[^'\\]*)*'", 'string'),
            
            # comments
            (r'#.*$', 'comment'),
            
            # functions
            (r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'function'),
            
            # classes
            (r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'class'),
            
            # numbers
            (r'\b[0-9]+\b', 'number'),
        ]
    
    def _setup_bindings(self):
        """Set up event bindings."""
        # syntax highlighting
        self.text.bind("<KeyRelease>", self._on_key_release)
        
        # update line numbers on text change
        self.text.bind("<<Modified>>", self._on_text_modified)
        
        # update line numbers on window configuration change
        self.bind("<Configure>", self._on_configure)
    
    def _on_text_scroll(self, *args):
        """Handle scrolling of text widget to update line numbers."""
        self.line_numbers.yview(*args)
    
    def _on_key_release(self, event):
        """Apply syntax highlighting on key release."""
        # skip special keys
        if event.keysym in ("Up", "Down", "Left", "Right", "Home", "End",
                          "Prior", "Next", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return
            
        # apply syntax highlighting
        self._highlight_syntax()
        
        # update line numbers
        self._update_line_numbers()
    
    def _on_text_modified(self, event):
        """Handle changes to the text widget."""
        # always update line numbers
        self._update_line_numbers()
        
        # mark as unmodified to avoid infinite loop
        self.text.edit_modified(False)
        
        # apply syntax highlighting
        self._highlight_syntax()
    
    def _on_configure(self, event):
        """Handle window configuration changes."""
        # update line numbers when widget is resized
        self._update_line_numbers()
    
    def _update_line_numbers(self):
        """Update the line numbers in the sidebar."""
        # get text content
        text_content = self.text.get("1.0", tk.END)
        
        # count the number of lines
        num_lines = text_content.count("\n") + 1
        
        # enable editing of line numbers
        self.line_numbers.configure(state=tk.NORMAL)
        
        # clear current line numbers
        self.line_numbers.delete("1.0", tk.END)
        
        # add new line numbers
        for i in range(1, num_lines + 1):
            if i in self.highlighted_lines:
                self.line_numbers.insert(tk.END, f"{i}\n", "highlight")
            else:
                self.line_numbers.insert(tk.END, f"{i}\n")
        
        # synchronize with text widget scroll position
        self.line_numbers.yview_moveto(self.text.yview()[0])
        
        # disable editing of line numbers
        self.line_numbers.configure(state=tk.DISABLED)
    
    def _highlight_syntax(self):
        """Apply syntax highlighting to the Python code."""
        # remove existing tags
        for tag in ["keyword", "string", "comment", "function", "class", "number"]:
            self.text.tag_remove(tag, "1.0", tk.END)
        
        # get text content
        content = self.text.get("1.0", tk.END)
        
        # apply syntax highlighting
        for pattern, tag in self.patterns:
            self._highlight_pattern(pattern, tag, content)
    
    def _highlight_pattern(self, pattern, tag, content):
        """
        Apply a specific tag to all matches of a pattern.
        
        Args:
            pattern: Regular expression pattern to match
            tag: Text tag to apply
            content: Text content to search in
        """
        # find all matches
        for match in re.finditer(pattern, content, re.MULTILINE):
            start_index = f"1.0+{match.start()}c"
            end_index = f"1.0+{match.end()}c"
            
            # apply the tag
            self.text.tag_add(tag, start_index, end_index)
    
    def get_text(self) -> str:
        """
        Get the current text content.
        
        Returns:
            Current text content as string
        """
        return self.text.get("1.0", tk.END)
    
    def set_text(self, content: str):
        """
        Set the text content.
        
        Args:
            content: Text content to set
        """
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
        self._highlight_syntax()
        self._update_line_numbers()
    
    def highlight_line(self, line_number: int, error: bool = False):
        """
        Highlight a specific line.
        
        Args:
            line_number: Line number to highlight (1-based)
            error: Whether to highlight as an error
        """
        # remove existing highlights
        self.text.tag_remove("error_line", "1.0", tk.END)
        self.text.tag_remove("highlight_line", "1.0", tk.END)
        
        # calculate the start and end positions
        start_pos = f"{line_number}.0"
        end_pos = f"{line_number + 1}.0"
        
        # apply highlighting
        if error:
            self.text.tag_add("error_line", start_pos, end_pos)
            self.highlighted_lines.add(line_number)
        else:
            self.text.tag_add("highlight_line", start_pos, end_pos)
            self.highlighted_lines.add(line_number)
        
        # update line numbers
        self._update_line_numbers()
        
        # ensure the line is visible
        self.text.see(start_pos)
    
    def clear_highlights(self):
        """Clear all highlights."""
        self.text.tag_remove("error_line", "1.0", tk.END)
        self.text.tag_remove("highlight_line", "1.0", tk.END)
        self.highlighted_lines.clear()
        self._update_line_numbers()
