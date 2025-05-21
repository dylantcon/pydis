"""
Executor module for handling code execution, both standard Python and bytecode execution.
"""
import sys
import io
import traceback
import builtins
import types
from typing import Tuple, Dict, Any, List, Optional
import threading
import time

class Executor:
    """
    Handles execution of Python code and provides debugging capabilities.
    """
    
    def __init__(self):
        """Initialize the executor with clean state."""
        self.reset()
    
    def reset(self):
        """Reset the execution state."""
        self.globals = {'__builtins__': builtins}
        self.locals = {}
        self.stdout_capture = io.StringIO()
        self.stderr_capture = io.StringIO()
        self.execution_trace = []
        self._is_running = False
        self._should_stop = False
        self._execution_thread = None
        self._step_event = threading.Event()
        self._step_complete_event = threading.Event()
        self._current_frame = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
    
    def execute_code(self, source_code: str) -> Tuple[Dict[str, Any], str, str, Optional[Exception]]:
        """
        Execute Python code and capture results.
        
        Args:
            source_code: Python source code as a string
            
        Returns:
            Tuple containing:
                - Dictionary of local variables after execution
                - Captured stdout content
                - Captured stderr content
                - Exception if one occurred, None otherwise
        """
        self.reset()
        
        # redirect stdout and stderr
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
        
        exception = None
        try:
            # compile and execute the code
            compiled_code = compile(source_code, '<string>', 'exec')
            exec(compiled_code, self.globals, self.locals)
        except Exception as e:
            exception = e
            traceback.print_exc(file=self.stderr_capture)
        finally:
            # restore stdout and stderr
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
        
        # return execution results
        return (
            self.locals.copy(),
            self.stdout_capture.getvalue(),
            self.stderr_capture.getvalue(),
            exception
        )
    
    def _trace_function(self, frame, event, arg):
        """Trace function for debugging execution."""
        if self._should_stop:
            return None
            
        if event == 'line':
            # store current frame for inspection
            self._current_frame = frame
            
            # record execution step
            self.execution_trace.append({
                'event': event,
                'filename': frame.f_code.co_filename,
                'lineno': frame.f_lineno,
                'function': frame.f_code.co_name,
                'locals': {k: repr(v) for k, v in frame.f_locals.items()},
                'globals': {k: repr(v) for k, v in frame.f_globals.items() 
                           if k != '__builtins__' and not k.startswith('_')}
            })
            
            # wait for step command in step mode
            self._step_event.clear()
            self._step_complete_event.set()
            self._step_event.wait()
            self._step_complete_event.clear()
            
        return self._trace_function
    
    def execute_step_by_step(self, source_code: str):
        """
        Set up for step-by-step execution.
        
        Args:
            source_code: Python source code to execute
        """
        self.reset()
        self._is_running = True
        self._should_stop = False
        
        # start execution in a separate thread
        self._execution_thread = threading.Thread(
            target=self._run_with_trace,
            args=(source_code,)
        )
        self._execution_thread.daemon = True
        self._execution_thread.start()
    
    def _run_with_trace(self, source_code: str):
        """
        Run code with tracing enabled for step-by-step execution.
        
        Args:
            source_code: Python source code to execute
        """
        # redirect stdout and stderr
        sys.stdout = self.stdout_capture
        sys.stderr = self.stderr_capture
        
        try:
            # set up the trace function
            sys.settrace(self._trace_function)
            
            # compile and execute the code
            compiled_code = compile(source_code, '<string>', 'exec')
            exec(compiled_code, self.globals, self.locals)
            
        except Exception as e:
            traceback.print_exc(file=self.stderr_capture)
            
        finally:
            # clean up
            sys.settrace(None)
            sys.stdout = self._original_stdout
            sys.stderr = self._original_stderr
            self._is_running = False
            self._step_complete_event.set()  # ensure we don't deadlock
    
    def step(self):
        """Execute the next step in step-by-step mode."""
        if self._is_running:
            self._step_event.set()
            self._step_complete_event.wait(timeout=1.0)
    
    def stop_execution(self):
        """Stop the current execution."""
        self._should_stop = True
        if self._is_running:
            self._step_event.set()  # unblock if waiting
            if self._execution_thread and self._execution_thread.is_alive():
                self._execution_thread.join(timeout=1.0)
            self._is_running = False
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get the current execution state.
        
        Returns:
            Dictionary with current execution state information
        """
        return {
            'is_running': self._is_running,
            'stdout': self.stdout_capture.getvalue(),
            'stderr': self.stderr_capture.getvalue(),
            'locals': self.locals.copy(),
            'globals': {k: v for k, v in self.globals.items() 
                      if k != '__builtins__' and not k.startswith('_')},
            'execution_trace': self.execution_trace.copy()
        }
    
    def get_variable_info(self) -> List[Dict[str, Any]]:
        """
        Get information about variables in the current execution scope.
        
        Returns:
            List of dictionaries with variable information
        """
        variables = []
        
        # add local variables
        for name, value in self.locals.items():
            variables.append({
                'name': name,
                'value': repr(value),
                'type': type(value).__name__,
                'scope': 'local'
            })
        
        # add global variables (excluding builtins and private ones)
        for name, value in self.globals.items():
            if name != '__builtins__' and not name.startswith('_'):
                variables.append({
                    'name': name,
                    'value': repr(value),
                    'type': type(value).__name__,
                    'scope': 'global'
                })
        
        return variables
