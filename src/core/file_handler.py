"""
File handler module for managing file operations.
"""
import os
from typing import Tuple, Optional, Dict, Any
import json
import marshal
import importlib.util
import dis

class FileHandler:
    """
    Handles file operations for the pydis application.
    """
    
    @staticmethod
    def read_python_file(file_path: str) -> Tuple[str, Optional[Exception]]:
        """
        Read Python source code from a file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Tuple containing:
                - File content as string
                - Exception if one occurred, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, None
        except Exception as e:
            return "", e
    
    @staticmethod
    def save_python_file(file_path: str, content: str) -> Optional[Exception]:
        """
        Save Python source code to a file.
        
        Args:
            file_path: Path where the file should be saved
            content: Python source code to save
            
        Returns:
            Exception if one occurred, None otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return None
        except Exception as e:
            return e
    
    @staticmethod
    def save_bytecode_text(file_path: str, bytecode_text: str) -> Optional[Exception]:
        """
        Save disassembled bytecode text to a file.
        
        Args:
            file_path: Path where the file should be saved
            bytecode_text: Disassembled bytecode text
            
        Returns:
            Exception if one occurred, None otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(bytecode_text)
            return None
        except Exception as e:
            return e
    
    @staticmethod
    def save_bytecode_binary(file_path: str, source_code: str) -> Optional[Exception]:
        """
        Compile Python code and save the binary bytecode (.pyc format).
        
        Args:
            file_path: Path where the file should be saved
            source_code: Python source code
            
        Returns:
            Exception if one occurred, None otherwise
        """
        try:
            # compile the source code
            compiled_code = compile(source_code, '<string>', 'exec')
            
            # save the compiled bytecode
            with open(file_path, 'wb') as f:
                marshal.dump(compiled_code, f)
                
            return None
        except Exception as e:
            return e
    
    @staticmethod
    def save_bytecode_json(file_path: str, instructions: list) -> Optional[Exception]:
        """
        Save bytecode instructions as JSON.
        
        Args:
            file_path: Path where the file should be saved
            instructions: List of bytecode instruction dictionaries
            
        Returns:
            Exception if one occurred, None otherwise
        """
        try:
            # convert instructions to JSON-compatible format
            serializable_instructions = []
            for instr in instructions:
                serializable_instr = {k: str(v) if not isinstance(v, (int, str, bool, type(None))) else v 
                                      for k, v in instr.items()}
                serializable_instructions.append(serializable_instr)
            
            # save as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_instructions, f, indent=2)
                
            return None
        except Exception as e:
            return e
    
    @staticmethod
    def export_bytecode_report(file_path: str, source_code: str, bytecode_text: str, 
                              instructions: list) -> Optional[Exception]:
        """
        Export a comprehensive bytecode report including source, disassembly, and instruction details.
        
        Args:
            file_path: Path where the file should be saved
            source_code: Original Python source code
            bytecode_text: Disassembled bytecode text
            instructions: List of bytecode instruction dictionaries
            
        Returns:
            Exception if one occurred, None otherwise
        """
        try:
            # prepare the report content
            report = [
                "# python Bytecode Report\n",
                "## original Source Code\n```python\n",
                source_code,
                "\n```\n\n",
                "## disassembled Bytecode\n```\n",
                bytecode_text,
                "\n```\n\n",
                "## instruction Details\n\n"
            ]
            
            # add instruction details
            for instr in instructions:
                line = instr.get('starts_line', '-')
                offset = instr.get('offset', '-')
                opname = instr.get('opname', '-')
                arg = instr.get('arg', '-')
                argval = instr.get('argval', '-')
                argrepr = instr.get('argrepr', '-')
                
                report.append(f"| {line} | {offset} | {opname} | {arg} | {argval} | {argrepr} |\n")
            
            # save the report
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(report)
                
            return None
        except Exception as e:
            return e
