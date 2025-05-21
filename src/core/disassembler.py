"""
Disassembler module for handling Python bytecode disassembly operations.
"""
import dis
import io
import sys
import traceback
import types
from typing import Tuple, List, Dict, Any, Optional

class Disassembler:
    """
    Handles disassembly of Python code into bytecode representation.
    """
    
    @staticmethod
    def disassemble_code(source_code: str) -> Tuple[str, Optional[Exception]]:
        """
        Disassembles the provided Python source code into bytecode.
        
        Args:
            source_code: Python source code as a string
            
        Returns:
            Tuple containing:
                - Disassembled bytecode as string
                - Exception if one occurred during compilation, None otherwise
        """
        try:
            # compile the source code
            compiled_code = compile(source_code, '<string>', 'exec')
            
            # capture the disassembly output
            output = io.StringIO()
            dis.dis(compiled_code, file=output)
            disassembled = output.getvalue()
            
            return disassembled, None
            
        except Exception as e:
            return str(e), e
    
    @staticmethod
    def get_bytecode_details(source_code: str) -> Tuple[List[Dict[str, Any]], Optional[Exception]]:
        """
        Gets detailed bytecode information including opcodes, line numbers, and arguments.
        
        Args:
            source_code: Python source code as a string
            
        Returns:
            Tuple containing:
                - List of dictionaries with bytecode instruction details
                - Exception if one occurred during compilation, None otherwise
        """
        try:
            # compile the source code
            compiled_code = compile(source_code, '<string>', 'exec')
            
            # get bytecode details
            instructions = []
            
            for instruction in dis.get_instructions(compiled_code):
                instructions.append({
                    'offset': instruction.offset,
                    'opcode': instruction.opcode,
                    'opname': instruction.opname,
                    'arg': instruction.arg,
                    'argval': instruction.argval,
                    'argrepr': instruction.argrepr,
                    'starts_line': instruction.starts_line,
                })
            
            return instructions, None
            
        except Exception as e:
            return [], e
    
    @staticmethod
    def disassemble_file(file_path: str) -> Tuple[str, Optional[Exception]]:
        """
        Disassembles Python code from a file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Tuple containing:
                - Disassembled bytecode as string
                - Exception if one occurred, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            return Disassembler.disassemble_code(source_code)
            
        except Exception as e:
            return str(e), e
