
"""
Resource management utilities for PyDis.
Handles file paths in both development and PyInstaller environments.
"""
import sys
import os

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Path relative to the application root

    Returns:
     Absolute path to the resource

    Example:
        >>> icon_path = resource_path('imgs/pydislogo.png')
        >>> config_path = resource_path('config/settings.json')
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # if not running as PyInstaller bundle, use the project root
        # go up from utils to src to project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(os.path.dirname(current_dir))

    return os.path.join(base_path, relative_path)

def resource_exists(relative_path):
    """
    Check if a resource exists.

    Args:
        relative_path: Path relative to the application root

    Returns:
        bool: True if the resource exists, False otherwise
    """
    return os.path.exists(resource_path(relative_path))
