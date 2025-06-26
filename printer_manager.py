"""
Printer Manager Module
Cross-platform printing functionality for Windows, Mac, and Linux.
"""

import platform
import subprocess
import pathlib
from typing import List, Dict, Optional, Tuple


class PrinterManager:
    """Manages cross-platform printing operations."""

    def __init__(self):
        """Initialize PrinterManager with platform detection."""
        self.system = platform.system()
        self.available_printers = []
        self.default_printer = None

    def get_system_type(self) -> str:
        """
        Get the current operating system type.

        Returns:
            str: 'Windows', 'Darwin' (Mac), 'Linux', or 'Unknown'
        """
        return self.system

    def list_printers(self) -> List[str]:
        """
        Get a list of available printers on the system.

        Returns:
            List[str]: List of printer names
        """
        try:
            if self.system == "Windows":
                return self._list_windows_printers()
            elif self.system == "Darwin":  # macOS
                return self._list_mac_printers()
            elif self.system == "Linux":
                return self._list_linux_printers()
            else:
                print(f"Unsupported operating system: {self.system}")
                return []
        except Exception as e:
            print(f"Error listing printers: {e}")
            return []

    def _list_windows_printers(self) -> List[str]:
        """List Windows printers using win32print or PowerShell fallback."""
        printers = []

        try:
            # Try using win32print first
            import win32print
            printer_info = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            printers = [printer[2] for printer in printer_info]
        except ImportError:
            # Fallback to PowerShell command
            try:
                cmd = ["powershell", "-Command",
                       "Get-Printer | Select-Object -ExpandProperty Name"]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True)
                printers = [line.strip()
                            for line in result.stdout.split('\n') if line.strip()]
            except subprocess.CalledProcessError as e:
                print(f"Error getting Windows printers via PowerShell: {e}")

        return printers

    def _list_mac_printers(self) -> List[str]:
        """List Mac printers using lpstat command."""
        try:
            cmd = ["lpstat", "-p"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            printers = []
            for line in result.stdout.split('\n'):
                if line.startswith('printer '):
                    printer_name = line.split()[1]
                    printers.append(printer_name)
            return printers
        except subprocess.CalledProcessError as e:
            print(f"Error getting Mac printers: {e}")
            return []

    def _list_linux_printers(self) -> List[str]:
        """List Linux printers using lpstat command."""
        try:
            cmd = ["lpstat", "-p"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            printers = []
            for line in result.stdout.split('\n'):
                if line.startswith('printer '):
                    printer_name = line.split()[1]
                    printers.append(printer_name)
            return printers
        except subprocess.CalledProcessError as e:
            print(f"Error getting Linux printers: {e}")
            return []

    def get_default_printer(self) -> Optional[str]:
        """
        Get the default printer name.

        Returns:
            Optional[str]: Default printer name or None if not found
        """
        try:
            if self.system == "Windows":
                return self._get_windows_default_printer()
            elif self.system in ["Darwin", "Linux"]:
                return self._get_unix_default_printer()
            else:
                return None
        except Exception as e:
            print(f"Error getting default printer: {e}")
            return None

    def _get_windows_default_printer(self) -> Optional[str]:
        """Get Windows default printer."""
        try:
            import win32print
            return win32print.GetDefaultPrinter()
        except ImportError:
            # Fallback to PowerShell
            try:
                cmd = ["powershell", "-Command",
                       "Get-WmiObject -Query 'SELECT * FROM Win32_Printer WHERE Default = True' | Select-Object -ExpandProperty Name"]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True)
                return result.stdout.strip()
            except subprocess.CalledProcessError:
                return None

    def _get_unix_default_printer(self) -> Optional[str]:
        """Get Unix/Linux/Mac default printer."""
        try:
            cmd = ["lpstat", "-d"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            for line in result.stdout.split('\n'):
                if 'system default destination:' in line:
                    return line.split(':')[-1].strip()
            return None
        except subprocess.CalledProcessError:
            return None

    def print_file(self, file_path: pathlib.Path, printer_name: Optional[str] = None,
                   print_options: Dict[str, str] = None) -> Tuple[bool, str]:
        """
        Print a PDF file to the specified printer.

        Args:
            file_path: Path to the PDF file to print
            printer_name: Name of the printer (uses default if None)
            print_options: Dictionary of print options

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        if not file_path.suffix.lower() == '.pdf':
            return False, f"Only PDF files are supported for printing"

        try:
            if self.system == "Windows":
                return self._print_windows(file_path, printer_name, print_options)
            elif self.system == "Darwin":  # macOS
                return self._print_mac(file_path, printer_name, print_options)
            elif self.system == "Linux":
                return self._print_linux(file_path, printer_name, print_options)
            else:
                return False, f"Printing not supported on {self.system}"
        except Exception as e:
            return False, f"Print error: {e}"

    def _print_windows(self, file_path: pathlib.Path, printer_name: Optional[str],
                       print_options: Dict[str, str]) -> Tuple[bool, str]:
        """Print file on Windows."""
        try:
            # Try using direct Windows printing
            import win32api
            import win32print

            if printer_name:
                win32print.SetDefaultPrinter(printer_name)

            # Print the PDF using Windows API
            win32api.ShellExecute(0, "print", str(file_path), None, ".", 0)
            return True, f"Sent to printer: {printer_name or 'default'}"

        except ImportError:
            # Fallback to command line printing
            try:
                cmd = ["powershell", "-Command",
                       f"Start-Process -FilePath '{file_path}' -Verb Print"]
                subprocess.run(cmd, check=True)
                return True, f"Sent to printer via PowerShell"
            except subprocess.CalledProcessError as e:
                return False, f"PowerShell print failed: {e}"

    def _print_mac(self, file_path: pathlib.Path, printer_name: Optional[str],
                   print_options: Dict[str, str]) -> Tuple[bool, str]:
        """Print file on macOS."""
        try:
            cmd = ["lpr"]

            if printer_name:
                cmd.extend(["-P", printer_name])

            # Add print options
            if print_options:
                for key, value in print_options.items():
                    cmd.extend(["-o", f"{key}={value}"])

            cmd.append(str(file_path))

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            return True, f"Sent to printer: {printer_name or 'default'}"

        except subprocess.CalledProcessError as e:
            return False, f"Mac print failed: {e}"

    def _print_linux(self, file_path: pathlib.Path, printer_name: Optional[str],
                     print_options: Dict[str, str]) -> Tuple[bool, str]:
        """Print file on Linux."""
        try:
            cmd = ["lpr"]

            if printer_name:
                cmd.extend(["-P", printer_name])

            # Add print options
            if print_options:
                for key, value in print_options.items():
                    cmd.extend(["-o", f"{key}={value}"])

            cmd.append(str(file_path))

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            return True, f"Sent to printer: {printer_name or 'default'}"

        except subprocess.CalledProcessError as e:
            return False, f"Linux print failed: {e}"

    def print_multiple_files(self, file_paths: List[pathlib.Path],
                             printer_name: Optional[str] = None,
                             print_options: Dict[str, str] = None,
                             progress_callback: Optional[callable] = None) -> Dict[str, Tuple[bool, str]]:
        """
        Print multiple PDF files.

        Args:
            file_paths: List of PDF file paths to print
            printer_name: Name of the printer (uses default if None)
            print_options: Dictionary of print options
            progress_callback: Optional callback for progress updates

        Returns:
            Dict[str, Tuple[bool, str]]: Results for each file
        """
        results = {}

        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(i + 1, len(file_paths),
                                  f"Printing {file_path.name}")

            success, message = self.print_file(
                file_path, printer_name, print_options)
            results[str(file_path)] = (success, message)

            if success:
                print(f"✓ Printed: {file_path.name}")
            else:
                print(f"✗ Failed: {file_path.name} - {message}")

        return results

    def check_printer_status(self, printer_name: str) -> Dict[str, str]:
        """
        Check the status of a specific printer.

        Args:
            printer_name: Name of the printer to check

        Returns:
            Dict[str, str]: Printer status information
        """
        try:
            if self.system in ["Darwin", "Linux"]:
                cmd = ["lpstat", "-p", printer_name]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True)

                status = {"name": printer_name, "available": True}
                if "disabled" in result.stdout.lower():
                    status["available"] = False
                    status["status"] = "disabled"
                elif "idle" in result.stdout.lower():
                    status["status"] = "idle"
                else:
                    status["status"] = "unknown"

                return status
            else:
                # For Windows, return basic info
                return {"name": printer_name, "available": True, "status": "unknown"}

        except subprocess.CalledProcessError:
            return {"name": printer_name, "available": False, "status": "not found"}

    def get_print_options_help(self) -> Dict[str, str]:
        """
        Get help information about available print options.

        Returns:
            Dict[str, str]: Print options and descriptions
        """
        return {
            "sides": "one-sided, two-sided-long-edge, two-sided-short-edge",
            "media": "a4, letter, legal, etc.",
            "orientation": "portrait, landscape",
            "quality": "draft, normal, high",
            "copies": "number of copies (1, 2, 3, etc.)",
            "page-ranges": "1-5, 1,3,5, etc.",
            "finishings": "staple-top-left, staple-top-right, staple-bottom-left, staple-bottom-right, staple-dual-left, staple-dual-top, staple-none"
        }
