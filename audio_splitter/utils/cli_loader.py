#!/usr/bin/env python3
"""
CLI Loader - Enhanced Parser Integration
Loads CLI configuration from YAML and integrates with argparse

This module provides enhanced CLI parsing functionality that reads
command definitions from cli_data.yaml, ensuring consistency between
documentation and actual CLI behavior.
"""

import argparse
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from rich.console import Console

console = Console()

class EnhancedCLILoader:
    """
    Enhanced CLI parser that loads command definitions from YAML
    Provides dynamic parser generation and help text integration
    """
    
    def __init__(self, data_file: Optional[str] = None):
        """Initialize with CLI data YAML file"""
        if data_file is None:
            # Default path relative to package root
            package_root = Path(__file__).parent.parent.parent
            data_file = package_root / "docs" / "cli_data.yaml"
        
        self.data_file = Path(data_file)
        self.cli_data = self._load_cli_data()
        
        # Extract main sections
        self.metadata = self.cli_data.get('metadata', {})
        self.global_info = self.cli_data.get('global_info', {})
        self.commands = self.cli_data.get('commands', {})
        self.global_options = self.cli_data.get('global_options', {})
        self.workflows = self.cli_data.get('workflows', {})
        self.help_info = self.cli_data.get('help_info', {})
    
    def _load_cli_data(self) -> Dict[str, Any]:
        """Load and validate CLI data from YAML"""
        if not self.data_file.exists():
            console.print(f"[yellow]Warning: CLI data file not found: {self.data_file}[/yellow]")
            console.print("[yellow]Using fallback parser configuration[/yellow]")
            return self._get_fallback_data()
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate required sections
            required_sections = ['metadata', 'global_info', 'commands']
            for section in required_sections:
                if section not in data:
                    console.print(f"[red]Error: Missing required section '{section}' in CLI data[/red]")
                    return self._get_fallback_data()
            
            return data
            
        except yaml.YAMLError as e:
            console.print(f"[red]Error parsing CLI data YAML: {e}[/red]")
            return self._get_fallback_data()
        except Exception as e:
            console.print(f"[red]Error loading CLI data: {e}[/red]")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Provide fallback CLI data if YAML file is unavailable"""
        return {
            'metadata': {'version': '2.0.0'},
            'global_info': {
                'program_name': 'Audio Splitter Suite',
                'executable': 'python main.py',
                'description': 'Professional audio processing CLI tool'
            },
            'commands': {
                'split': {'description': 'Split audio files into segments'},
                'convert': {'description': 'Convert between audio formats'},
                'metadata': {'description': 'Edit audio metadata'},
                'spectrogram': {'description': 'Generate spectrograms'},
                'channel': {'description': 'Convert audio channels'},
                'quality-settings': {'description': 'Manage quality settings'}
            }
        }
    
    def create_enhanced_parser(self) -> argparse.ArgumentParser:
        """Create enhanced ArgumentParser from YAML data"""
        
        # Main parser
        parser = argparse.ArgumentParser(
            prog=self.global_info.get('executable', 'audio-splitter'),
            description=self.global_info.get('description', ''),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._generate_epilog()
        )
        
        # Global options
        parser.add_argument(
            '--version', '-v',
            action='version',
            version=f"{self.global_info.get('program_name', 'Audio Splitter Suite')} {self.metadata.get('version', '2.0.0')}"
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='COMMAND'
        )
        
        # Add commands dynamically from YAML
        for cmd_name, cmd_data in self.commands.items():
            self._add_command_parser(subparsers, cmd_name, cmd_data)
        
        return parser
    
    def _add_command_parser(self, subparsers, cmd_name: str, cmd_data: Dict[str, Any]):
        """Add a command parser from YAML data"""
        
        # Create subparser
        cmd_parser = subparsers.add_parser(
            cmd_name,
            help=cmd_data.get('description', ''),
            description=cmd_data.get('description', ''),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._generate_command_epilog(cmd_name, cmd_data)
        )
        
        # Add arguments
        if 'arguments' in cmd_data:
            for arg_name, arg_data in cmd_data['arguments'].items():
                self._add_argument(cmd_parser, arg_name, arg_data)
        
        # Add options
        if 'options' in cmd_data:
            for opt_name, opt_data in cmd_data['options'].items():
                self._add_option(cmd_parser, opt_name, opt_data)
        
        # Handle subcommands (like quality-settings)
        if 'subcommands' in cmd_data:
            sub_subparsers = cmd_parser.add_subparsers(
                dest=f'{cmd_name}_action',
                help=f'{cmd_name} actions',
                metavar='ACTION'
            )
            
            for sub_name, sub_data in cmd_data['subcommands'].items():
                self._add_subcommand_parser(sub_subparsers, sub_name, sub_data)
    
    def _add_argument(self, parser: argparse.ArgumentParser, arg_name: str, arg_data: Dict[str, Any]):
        """Add positional argument to parser"""
        kwargs = {
            'help': arg_data.get('description', '')
        }
        
        # Handle argument type
        arg_type = arg_data.get('type', 'string')
        if arg_type == 'integer':
            kwargs['type'] = int
        elif arg_type == 'float':
            kwargs['type'] = float
        elif arg_type == 'choice':
            kwargs['choices'] = arg_data.get('choices', [])
        
        # Add metavar for better help display
        if 'formats_supported' in arg_data:
            kwargs['metavar'] = f"FILE ({','.join(arg_data['formats_supported'])})"
        
        parser.add_argument(arg_name, **kwargs)
    
    def _add_option(self, parser: argparse.ArgumentParser, opt_name: str, opt_data: Dict[str, Any]):
        """Add optional argument to parser"""
        flags = opt_data.get('flags', [f'--{opt_name}'])
        
        kwargs = {
            'help': opt_data.get('description', ''),
            'dest': opt_name
        }
        
        # Handle option type
        opt_type = opt_data.get('type', 'string')
        
        if opt_type == 'flag':
            kwargs['action'] = 'store_true'
        elif opt_type == 'integer':
            kwargs['type'] = int
        elif opt_type == 'float':
            kwargs['type'] = float
        elif opt_type == 'choice':
            kwargs['choices'] = opt_data.get('choices', [])
        elif opt_type == 'string[]':
            kwargs['nargs'] = '+'
        
        # Handle default values
        if 'default' in opt_data and opt_data['default'] is not None:
            kwargs['default'] = opt_data['default']
        
        # Handle required options
        if opt_data.get('required', False):
            kwargs['required'] = True
        
        # Add help for choices
        if 'choices_help' in opt_data:
            choices_info = opt_data['choices_help']
            if isinstance(choices_info, dict):
                help_text = kwargs['help']
                help_text += " Choices: " + ", ".join([f"{k}={v}" for k, v in choices_info.items()])
                kwargs['help'] = help_text
        
        parser.add_argument(*flags, **kwargs)
    
    def _add_subcommand_parser(self, subparsers, sub_name: str, sub_data: Dict[str, Any]):
        """Add subcommand parser (for commands like quality-settings)"""
        sub_parser = subparsers.add_parser(
            sub_name,
            help=sub_data.get('description', ''),
            description=sub_data.get('description', '')
        )
        
        # Add arguments for subcommand
        if 'arguments' in sub_data:
            for arg_name, arg_data in sub_data['arguments'].items():
                self._add_argument(sub_parser, arg_name, arg_data)
        
        # Add options for subcommand
        if 'options' in sub_data:
            for opt_name, opt_data in sub_data['options'].items():
                self._add_option(sub_parser, opt_name, opt_data)
    
    def _generate_epilog(self) -> str:
        """Generate epilog text for main parser"""
        examples = []
        
        # Add one example from each command
        for cmd_name, cmd_data in self.commands.items():
            if 'examples' in cmd_data and 'basic' in cmd_data['examples']:
                example = cmd_data['examples']['basic']
                examples.append(f"  {example['command']}")
                if len(examples) >= 3:  # Limit to 3 examples
                    break
        
        epilog_lines = [
            "Examples:",
            *examples,
            "",
            f"For detailed help: {self.global_info.get('executable', 'python main.py')} COMMAND --help"
        ]
        
        if self.help_info.get('examples_note'):
            epilog_lines.append(self.help_info['examples_note'])
        
        return "\n".join(epilog_lines)
    
    def _generate_command_epilog(self, cmd_name: str, cmd_data: Dict[str, Any]) -> str:
        """Generate epilog text for command parser"""
        epilog_lines = []
        
        # Add examples
        if 'examples' in cmd_data:
            epilog_lines.append("Examples:")
            for ex_name, ex_data in cmd_data['examples'].items():
                epilog_lines.append(f"  # {ex_data.get('title', '')}")
                epilog_lines.append(f"  {ex_data.get('command', '')}")
                epilog_lines.append("")
        
        # Add workflow info
        if 'workflows' in cmd_data:
            epilog_lines.append("Related workflows:")
            for wf_name, wf_data in cmd_data['workflows'].items():
                epilog_lines.append(f"  • {wf_data.get('title', '')}")
        
        return "\n".join(epilog_lines) if epilog_lines else ""
    
    def get_command_examples(self, command: str) -> List[Dict[str, str]]:
        """Get examples for a specific command"""
        if command not in self.commands:
            return []
        
        cmd_data = self.commands[command]
        examples = []
        
        if 'examples' in cmd_data:
            for ex_name, ex_data in cmd_data['examples'].items():
                examples.append({
                    'name': ex_name,
                    'title': ex_data.get('title', ''),
                    'command': ex_data.get('command', ''),
                    'description': ex_data.get('description', '')
                })
        
        return examples
    
    def get_command_workflows(self, command: str) -> List[Dict[str, Any]]:
        """Get workflows for a specific command"""
        if command not in self.commands:
            return []
        
        cmd_data = self.commands[command]
        workflows = []
        
        if 'workflows' in cmd_data:
            for wf_name, wf_data in cmd_data['workflows'].items():
                workflows.append({
                    'name': wf_name,
                    'title': wf_data.get('title', ''),
                    'description': wf_data.get('description', ''),
                    'steps': wf_data.get('steps', [])
                })
        
        return workflows
    
    def show_command_examples(self, command: str):
        """Display examples for a command using Rich console"""
        examples = self.get_command_examples(command)
        
        if not examples:
            console.print(f"[yellow]No examples available for command '{command}'[/yellow]")
            return
        
        console.print(f"\n[bold cyan]Examples for '{command}' command:[/bold cyan]")
        
        for example in examples:
            console.print(f"\n[yellow]{example['title']}:[/yellow]")
            if example['description']:
                console.print(f"[dim]{example['description']}[/dim]")
            console.print(f"[green]{example['command']}[/green]")
    
    def show_command_workflows(self, command: str):
        """Display workflows for a command using Rich console"""
        workflows = self.get_command_workflows(command)
        
        if not workflows:
            console.print(f"[yellow]No workflows available for command '{command}'[/yellow]")
            return
        
        console.print(f"\n[bold cyan]Workflows for '{command}' command:[/bold cyan]")
        
        for workflow in workflows:
            console.print(f"\n[bold yellow]{workflow['title']}[/bold yellow]")
            console.print(f"[dim]{workflow['description']}[/dim]")
            
            for step in workflow['steps']:
                console.print(f"\n[white]Step {step['step']}:[/white] {step['action']}")
                console.print(f"[green]  {step['command']}[/green]")
    
    def validate_arguments(self, args: argparse.Namespace) -> bool:
        """Validate parsed arguments against YAML constraints"""
        if not hasattr(args, 'command') or not args.command:
            return True  # No command to validate
        
        command = args.command
        if command not in self.commands:
            return True  # Unknown command, let argparse handle it
        
        cmd_data = self.commands[command]
        
        # Validate option dependencies
        if 'options' in cmd_data:
            for opt_name, opt_data in cmd_data['options'].items():
                if 'requires' in opt_data and hasattr(args, opt_name):
                    option_value = getattr(args, opt_name)
                    if option_value:  # Option is set
                        # Check if required options are also set
                        for required_opt in opt_data['requires']:
                            required_opt_name = required_opt.replace('--', '')
                            if not hasattr(args, required_opt_name) or not getattr(args, required_opt_name):
                                console.print(f"[red]Error: {opt_data['flags'][0]} requires {required_opt}[/red]")
                                return False
        
        return True

def create_enhanced_parser(data_file: Optional[str] = None) -> argparse.ArgumentParser:
    """
    Factory function to create enhanced CLI parser
    
    Args:
        data_file: Optional path to CLI data YAML file
        
    Returns:
        Configured ArgumentParser instance
    """
    loader = EnhancedCLILoader(data_file)
    return loader.create_enhanced_parser()

def get_cli_loader(data_file: Optional[str] = None) -> EnhancedCLILoader:
    """
    Factory function to get CLI loader instance
    
    Args:
        data_file: Optional path to CLI data YAML file
        
    Returns:
        EnhancedCLILoader instance
    """
    return EnhancedCLILoader(data_file)

# CLI integration helper functions
def show_examples(command: str, data_file: Optional[str] = None):
    """Show examples for a command"""
    loader = get_cli_loader(data_file)
    loader.show_command_examples(command)

def show_workflows(command: str, data_file: Optional[str] = None):
    """Show workflows for a command"""
    loader = get_cli_loader(data_file)
    loader.show_command_workflows(command)

def validate_args(args: argparse.Namespace, data_file: Optional[str] = None) -> bool:
    """Validate parsed arguments"""
    loader = get_cli_loader(data_file)
    return loader.validate_arguments(args)