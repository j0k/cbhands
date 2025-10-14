"""Output formatting for cbhands v3.0.0."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import json
from datetime import datetime


class OutputFormatter(ABC):
    """Base class for output formatters."""
    
    @abstractmethod
    def format_success(self, message: str) -> str:
        """Format success message."""
        pass
    
    @abstractmethod
    def format_error(self, message: str) -> str:
        """Format error message."""
        pass
    
    @abstractmethod
    def format_warning(self, message: str) -> str:
        """Format warning message."""
        pass
    
    @abstractmethod
    def format_info(self, message: str) -> str:
        """Format info message."""
        pass
    
    @abstractmethod
    def format_data(self, data: Any) -> str:
        """Format data output."""
        pass
    
    @abstractmethod
    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Format table output."""
        pass


class BasicFormatter(OutputFormatter):
    """Basic text formatter."""
    
    def format_success(self, message: str) -> str:
        """Format success message."""
        return f"✅ {message}"
    
    def format_error(self, message: str) -> str:
        """Format error message."""
        return f"❌ {message}"
    
    def format_warning(self, message: str) -> str:
        """Format warning message."""
        return f"⚠️  {message}"
    
    def format_info(self, message: str) -> str:
        """Format info message."""
        return f"ℹ️  {message}"
    
    def format_data(self, data: Any) -> str:
        """Format data output."""
        if isinstance(data, dict):
            return json.dumps(data, indent=2, default=str)
        elif isinstance(data, list):
            return json.dumps(data, indent=2, default=str)
        else:
            return str(data)
    
    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Format table output."""
        if not headers or not rows:
            return ""
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Create table
        lines = []
        
        # Header
        header_line = " | ".join(header.ljust(width) for header, width in zip(headers, col_widths))
        lines.append(header_line)
        lines.append("-" * len(header_line))
        
        # Rows
        for row in rows:
            row_line = " | ".join(str(cell).ljust(width) for cell, width in zip(row, col_widths))
            lines.append(row_line)
        
        return "\n".join(lines)


class RichFormatter(OutputFormatter):
    """Rich formatter with colors and styling."""
    
    def __init__(self):
        """Initialize rich formatter."""
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.panel import Panel
            from rich.text import Text
            from rich import print as rich_print
            
            self.console = Console()
            self.Table = Table
            self.Panel = Panel
            self.Text = Text
            self.rich_print = rich_print
            self._rich_available = True
        except ImportError:
            self._rich_available = False
            # Fallback to basic formatter
            self._fallback = BasicFormatter()
    
    def format_success(self, message: str) -> str:
        """Format success message."""
        if self._rich_available:
            text = self.Text("✅ ", style="green bold") + self.Text(message, style="green")
            return str(text)
        return self._fallback.format_success(message)
    
    def format_error(self, message: str) -> str:
        """Format error message."""
        if self._rich_available:
            text = self.Text("❌ ", style="red bold") + self.Text(message, style="red")
            return str(text)
        return self._fallback.format_error(message)
    
    def format_warning(self, message: str) -> str:
        """Format warning message."""
        if self._rich_available:
            text = self.Text("⚠️  ", style="yellow bold") + self.Text(message, style="yellow")
            return str(text)
        return self._fallback.format_warning(message)
    
    def format_info(self, message: str) -> str:
        """Format info message."""
        if self._rich_available:
            text = self.Text("ℹ️  ", style="blue bold") + self.Text(message, style="blue")
            return str(text)
        return self._fallback.format_info(message)
    
    def format_data(self, data: Any) -> str:
        """Format data output."""
        if self._rich_available:
            if isinstance(data, dict):
                # Create a table for dict data
                table = self.Table(show_header=True, header_style="bold magenta")
                table.add_column("Key", style="cyan")
                table.add_column("Value", style="white")
                
                for key, value in data.items():
                    table.add_row(str(key), str(value))
                
                return str(table)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                # Create a table for list of dicts
                if not data:
                    return "[]"
                
                table = self.Table(show_header=True, header_style="bold magenta")
                headers = list(data[0].keys())
                for header in headers:
                    table.add_column(header, style="cyan")
                
                for row in data:
                    table.add_row(*[str(row.get(header, "")) for header in headers])
                
                return str(table)
            else:
                return json.dumps(data, indent=2, default=str)
        return self._fallback.format_data(data)
    
    def format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Format table output."""
        if self._rich_available:
            table = self.Table(show_header=True, header_style="bold magenta")
            
            # Add columns
            for header in headers:
                table.add_column(header, style="cyan")
            
            # Add rows
            for row in rows:
                table.add_row(*[str(cell) for cell in row])
            
            return str(table)
        return self._fallback.format_table(headers, rows)
    
    def print_success(self, message: str) -> None:
        """Print success message with rich formatting."""
        if self._rich_available:
            self.console.print(f"[green bold]✅[/green bold] [green]{message}[/green]")
        else:
            print(self.format_success(message))
    
    def print_error(self, message: str) -> None:
        """Print error message with rich formatting."""
        if self._rich_available:
            self.console.print(f"[red bold]❌[/red bold] [red]{message}[/red]")
        else:
            print(self.format_error(message))
    
    def print_warning(self, message: str) -> None:
        """Print warning message with rich formatting."""
        if self._rich_available:
            self.console.print(f"[yellow bold]⚠️[/yellow bold] [yellow]{message}[/yellow]")
        else:
            print(self.format_warning(message))
    
    def print_info(self, message: str) -> None:
        """Print info message with rich formatting."""
        if self._rich_available:
            self.console.print(f"[blue bold]ℹ️[/blue bold] [blue]{message}[/blue]")
        else:
            print(self.format_info(message))
    
    def print_data(self, data: Any) -> None:
        """Print data with rich formatting."""
        if self._rich_available:
            if isinstance(data, dict):
                table = self.Table(show_header=True, header_style="bold magenta")
                table.add_column("Key", style="cyan")
                table.add_column("Value", style="white")
                
                for key, value in data.items():
                    table.add_row(str(key), str(value))
                
                self.console.print(table)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                if not data:
                    self.console.print("[]")
                    return
                
                table = self.Table(show_header=True, header_style="bold magenta")
                headers = list(data[0].keys())
                for header in headers:
                    table.add_column(header, style="cyan")
                
                for row in data:
                    table.add_row(*[str(row.get(header, "")) for header in headers])
                
                self.console.print(table)
            else:
                self.console.print(json.dumps(data, indent=2, default=str))
        else:
            print(self.format_data(data))
