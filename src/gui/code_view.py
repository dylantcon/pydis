"""
Code view module for displaying and editing Python code.
"""
import tkinter as tk
from tkinter import scrolledtext
import tkinter.font as tkfont
from typing import Callable, Optional
import re

class LineNumbers(tk.Canvas):
    """A canvas widget to display line numbers with perfect alignment."""
    
    def __init__(self, parent, text_widget, *args, **kwargs):
        tk.Canvas.__init__(self, parent, *args, **kwargs, 
                         highlightthickness=0, bd=0)
        self.text_widget = text_widget
        self.font = None
        self.highlighted_lines = set()
        
        # configure appearance
        self.configure(bg="#F0F0F0", width=40)
        
        # bind text widget events to update line numbers
        self.text_widget.bind("<<Modified>>", self._on_text_modified)
        self.text_widget.bind("<Configure>", self._on_text_configure)
        
        # intercept scroll events
        self.bind("<MouseWheel>", self._on_mouse_wheel)
        self.bind("<Button-4>", self._on_mouse_wheel)
        self.bind("<Button-5>", self._on_mouse_wheel)
    
    def set_font(self, font):
        """Set the font for line numbers, matching the text widget."""
        self.font = font
    
    def set_highlighted_lines(self, highlighted_lines):
        """Set the lines to be highlighted."""
        self.highlighted_lines = highlighted_lines
        self.redraw()
    
    def _on_text_modified(self, event=None):
        """Handle text modifications."""
        # mark as unmodified to avoid infinite loop
        self.text_widget.edit_modified(False)
        self.redraw()
    
    def _on_text_configure(self, event=None):
        """Handle text widget configuration changes."""
        self.redraw()
    
    def _on_mouse_wheel(self, event):
        """Redirect mouse wheel events to text widget."""
        self.text_widget.event_generate("<MouseWheel>", 
                                     delta=event.delta if hasattr(event, 'delta') else 0,
                                     x=0, y=0)
        return "break"
    
    def redraw(self):
        """Redraw the line numbers."""
        self.delete("all")  # clear existing content
        
        # get text content
        text_content = self.text_widget.get("1.0", "end-1c")
        num_lines = text_content.count("\n") + 1
        
        # calculate text metrics for alignment
        y_offset = int(self.text_widget.cget("pady"))  # get text widget padding
        line_height = self.font.metrics("linespace")
        
        # get current view of text widget to only draw visible lines
        first_visible_line = int(self.text_widget.index("@0,0").split('.')[0])
        last_visible_index = self.text_widget.index("@0,%d" % self.text_widget.winfo_height())
        last_visible_line = int(last_visible_index.split('.')[0])
        
        # draw only visible line numbers
        for line_num in range(first_visible_line, min(last_visible_line + 1, num_lines + 1)):
            # get the y coordinate of this line in the text widget
            y = self.text_widget.dlineinfo("%d.0" % line_num)
            if y is None:
                continue
                
            y = y[1]  # y coordinate is the second element
            
            # choose color based on whether line is highlighted
            text_color = "#0066CC" if line_num in self.highlighted_lines else "#606060"
            
            # right-align line numbers with a fixed width
            self.create_text(
                self.winfo_width() - 5,  # align to right edge with 5px padding
                y,
                anchor="ne",
                text=f"{line_num}",
                font=self.font,
                fill=text_color
            )
            
        # update the canvas size to match the text widget
        self.configure(height=self.text_widget.winfo_height())


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
        # configure grid layout for precise control
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # create text widget with vertical scrollbar
        self.text = tk.Text(self, padx=5, pady=5, wrap=tk.NONE,
                         undo=True, maxundo=-1)
        self.text.grid(row=0, column=1, sticky="nsew")
        
        # create vertical scrollbar for the text widget
        self.text_scrollbar_y = tk.Scrollbar(self, orient=tk.VERTICAL, 
                                          command=self._on_scroll_y)
        self.text_scrollbar_y.grid(row=0, column=2, sticky="ns")
        
        # create horizontal scrollbar for the text widget
        self.text_scrollbar_x = tk.Scrollbar(self, orient=tk.HORIZONTAL, 
                                          command=self.text.xview)
        self.text_scrollbar_x.grid(row=1, column=1, sticky="ew")
        
        # configure text widget to use scrollbars
        self.text.configure(yscrollcommand=self._on_text_scroll,
                          xscrollcommand=self.text_scrollbar_x.set)
        
        # configure font - use monospace
        self.font = tkfont.Font(family="Courier New", size=10)
        self.text.configure(font=self.font)
        
        # configure tab size (4 spaces)
        self.text.configure(tabs=self.font.measure(' ' * 4))
        
        # create line numbers using canvas
        self.line_numbers = LineNumbers(self, self.text, bg="#F0F0F0")
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        self.line_numbers.set_font(self.font)
    
    def _on_scroll_y(self, *args):
        """Handle vertical scrolling."""
        self.text.yview(*args)
        self.line_numbers.redraw()
    
    def _on_text_scroll(self, *args):
        """Handle text scrolling."""
        # update scrollbar position
        self.text_scrollbar_y.set(*args)
        
        # update line numbers
        self.line_numbers.redraw()
    
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
        
        # update on configure
        self.bind("<Configure>", self._on_configure)
    
    def _on_key_release(self, event):
        """Apply syntax highlighting on key release."""
        # skip special keys
        if event.keysym in ("Up", "Down", "Left", "Right", "Home", "End",
                          "Prior", "Next", "Shift_L", "Shift_R", "Control_L", "Control_R"):
            return
            
        # apply syntax highlighting
        self._highlight_syntax()
    
    def _on_configure(self, event):
        """Handle window configuration changes."""
        # redraw line numbers when widget is resized
        self.line_numbers.redraw()
    
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
        self.line_numbers.redraw()
    
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

        # reset the highlighted_lines set
        self.highlighted_lines.clear()
        
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
        
        # update line numbers highlighting
        self.line_numbers.set_highlighted_lines(self.highlighted_lines)
        
        # ensure the line is visible
        self.text.see(start_pos)
    
    def clear_highlights(self):
        """Clear all highlights."""
        self.text.tag_remove("error_line", "1.0", tk.END)
        self.text.tag_remove("highlight_line", "1.0", tk.END)
        self.highlighted_lines.clear()
        self.line_numbers.set_highlighted_lines(self.highlighted_lines)
