#!/usr/bin/env python3
"""
Documentation Generator - Single Source of Truth System
Generates documentation from cli_data.yaml for multiple outputs

Author: Audio Splitter Suite Team
Version: 1.0.0
"""

import yaml
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from jinja2 import Template
import textwrap

class CLIDocGenerator:
    """
    Generates documentation from centralized CLI data YAML file
    Supports multiple output formats: help text, markdown, README sections
    """
    
    def __init__(self, data_file: str = "docs/cli_data.yaml"):
        """Initialize generator with YAML data file"""
        self.data_file = Path(data_file)
        if not self.data_file.exists():
            raise FileNotFoundError(f"CLI data file not found: {data_file}")
            
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.data = yaml.safe_load(f)
            
        self.metadata = self.data.get('metadata', {})
        self.global_info = self.data.get('global_info', {})
        self.commands = self.data.get('commands', {})
        self.workflows = self.data.get('workflows', {})
        self.help_info = self.data.get('help_info', {})
        self.troubleshooting = self.data.get('troubleshooting', {})
    
    def generate_help_text(self, command: str = None) -> str:
        """Generate help text for argparse integration"""
        if command and command in self.commands:
            return self._generate_command_help(command)
        return self._generate_global_help()
    
    def _generate_global_help(self) -> str:
        """Generate global help text"""
        help_lines = [
            f"{self.global_info.get('program_name', 'Audio Splitter Suite')}",
            f"Version: {self.metadata.get('version', '2.0.0')}",
            "",
            self.global_info.get('description', ''),
            "",
            "Available Commands:",
        ]
        
        for cmd_name, cmd_data in self.commands.items():
            help_lines.append(f"  {cmd_name:<15} {cmd_data.get('description', '')}")
        
        help_lines.extend([
            "",
            "Global Options:",
            "  --version, -v   Show version information",
            "",
            "Use 'python main.py COMMAND --help' for command-specific help",
            "",
            "Examples:",
            f"  {self.global_info.get('executable', 'python main.py')} split audio.wav -s \"0:30-1:30:intro\"",
            f"  {self.global_info.get('executable', 'python main.py')} convert input.wav -o output.mp3 -f mp3",
            f"  {self.global_info.get('executable', 'python main.py')} --version"
        ])
        
        return "\n".join(help_lines)
    
    def _generate_command_help(self, command: str) -> str:
        """Generate help text for specific command"""
        if command not in self.commands:
            return f"Command '{command}' not found"
            
        cmd_data = self.commands[command]
        help_lines = [
            f"Command: {command}",
            f"Description: {cmd_data.get('description', '')}",
            "",
            f"Usage: {cmd_data.get('usage', '')}",
            ""
        ]
        
        # Arguments
        if 'arguments' in cmd_data:
            help_lines.append("Arguments:")
            for arg_name, arg_data in cmd_data['arguments'].items():
                required = " (required)" if arg_data.get('required', False) else ""
                help_lines.append(f"  {arg_name.upper():<15} {arg_data.get('description', '')}{required}")
            help_lines.append("")
        
        # Options
        if 'options' in cmd_data:
            help_lines.append("Options:")
            for opt_name, opt_data in cmd_data['options'].items():
                flags = ", ".join(opt_data.get('flags', []))
                default = f" (default: {opt_data.get('default')})" if opt_data.get('default') is not None else ""
                help_lines.append(f"  {flags:<20} {opt_data.get('description', '')}{default}")
            help_lines.append("")
        
        # Examples
        if 'examples' in cmd_data:
            help_lines.append("Examples:")
            for ex_name, ex_data in cmd_data['examples'].items():
                help_lines.append(f"  # {ex_data.get('title', '')}")
                help_lines.append(f"  {ex_data.get('command', '')}")
                if ex_data.get('description'):
                    help_lines.append(f"  # {ex_data.get('description')}")
                help_lines.append("")
        
        return "\n".join(help_lines)
    
    def generate_markdown_guide(self) -> str:
        """Generate complete CLI guide in markdown format"""
        template = Template("""# CLI Reference Guide - {{ global_info.program_name }}

> **Generated from cli_data.yaml** - Version {{ metadata.version }}  
> Last updated: {{ metadata.last_updated }}

## Overview

{{ global_info.description }}

## Quick Start

```bash
# Show version
{{ global_info.executable }} --version

# Interactive mode (no arguments)
{{ global_info.executable }}

# Command line mode
{{ global_info.executable }} COMMAND [OPTIONS]
```

## Global Options

| Option | Description |
|--------|-------------|
{% for opt_name, opt_data in global_options.items() -%}
| `{{ opt_data.flags | join(', ') }}` | {{ opt_data.description }} |
{% endfor %}

## Commands Reference

{% for cmd_name, cmd_data in commands.items() %}
### `{{ cmd_name }}` - {{ cmd_data.description }}

**Category:** {{ cmd_data.category | replace('_', ' ') | title }}

**Usage:**
```bash
{{ cmd_data.usage }}
```

{% if cmd_data.arguments -%}
**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
{% for arg_name, arg_data in cmd_data.arguments.items() -%}
| `{{ arg_name.upper() }}` | {{ arg_data.type }} | {{ '✓' if arg_data.required else '○' }} | {{ arg_data.description }} |
{% endfor %}
{% endif %}

{% if cmd_data.options -%}
**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
{% for opt_name, opt_data in cmd_data.options.items() -%}
| `{{ opt_data.flags | join(', ') }}` | {{ opt_data.type }} | {{ opt_data.default if opt_data.default is not none else 'None' }} | {{ opt_data.description }} |
{% endfor %}
{% endif %}

{% if cmd_data.examples -%}
**Examples:**

{% for ex_name, ex_data in cmd_data.examples.items() -%}
**{{ ex_data.title }}:**
```bash
{{ ex_data.command }}
```
{{ ex_data.description }}

{% endfor %}
{% endif %}

{% if cmd_data.workflows -%}
**Workflows:**

{% for wf_name, wf_data in cmd_data.workflows.items() -%}
**{{ wf_data.title }}:**

{{ wf_data.description }}

{% for step in wf_data.steps -%}
{{ step.step }}. {{ step.action }}:
   ```bash
   {{ step.command }}
   ```

{% endfor %}
{% endfor %}
{% endif %}

{% if cmd_data.subcommands -%}
**Subcommands:**

{% for sub_name, sub_data in cmd_data.subcommands.items() -%}
#### `{{ cmd_name }} {{ sub_name }}`

{{ sub_data.description }}

{% if sub_data.arguments -%}
**Arguments:**
{% for arg_name, arg_data in sub_data.arguments.items() -%}
- `{{ arg_name.upper() }}` ({{ arg_data.type }}) - {{ arg_data.description }}
{% endfor %}
{% endif %}

{% if sub_data.options -%}
**Options:**
{% for opt_name, opt_data in sub_data.options.items() -%}
- `{{ opt_data.flags | join(', ') }}` - {{ opt_data.description }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

---

{% endfor %}

## Complete Workflows

{% for wf_name, wf_data in workflows.items() %}
### {{ wf_data.title }}

**Category:** {{ wf_data.category | replace('_', ' ') | title }}

{{ wf_data.description }}

{% for step in wf_data.steps -%}
**Step {{ step.step }}:** {{ step.description }}
```bash
{{ step.command }}
```

{% endfor %}

---

{% endfor %}

## Troubleshooting

### Common Errors

{% for error_name, error_data in troubleshooting.common_errors.items() %}
#### {{ error_data.error }}

**Solution:** {{ error_data.solution }}

**Example:**
```bash
{{ error_data.example }}
```

{% endfor %}

## Additional Help

{{ help_info.examples_note }}

{{ help_info.workflows_note }}

{{ help_info.quality_note }}

**Supported Formats:** {{ help_info.formats_note }}

---

*Generated automatically from cli_data.yaml*
""")
        
        return template.render(**self.data)
    
    def generate_readme_section(self) -> str:
        """Generate CLI section for README.md"""
        template = Template("""
## 🖥️ Command Line Interface

{{ global_info.program_name }} provides a powerful command-line interface for all audio processing needs.

### Quick Start

```bash
# Interactive mode (recommended for beginners)
{{ global_info.executable }}

# Command line mode
{{ global_info.executable }} COMMAND [OPTIONS]

# Show version
{{ global_info.executable }} --version
```

### Available Commands

| Command | Description | Category |
|---------|-------------|----------|
{% for cmd_name, cmd_data in commands.items() -%}
| `{{ cmd_name }}` | {{ cmd_data.description }} | {{ cmd_data.category | replace('_', ' ') | title }} |
{% endfor %}

### Quick Examples

{% for cmd_name, cmd_data in commands.items() -%}
{% if cmd_data.examples.basic -%}
```bash
# {{ cmd_data.examples.basic.title }}
{{ cmd_data.examples.basic.command }}
```

{% endif -%}
{% endfor %}

### Professional Workflows

{% for wf_name, wf_data in (workflows.items() | list)[:2] -%}
**{{ wf_data.title }}:**
```bash
# {{ wf_data.description }}
{% for step in wf_data.steps -%}
{{ step.command }}
{% endfor %}
```

{% endfor %}

### Getting Help

- **General help:** `{{ global_info.executable }} --help`
- **Command help:** `{{ global_info.executable }} COMMAND --help`
- **Complete reference:** See [CLI Reference Guide](docs/CLI_REFERENCE.md)
- **Examples:** See [CLI Examples](docs/CLI_EXAMPLES.md)

""")
        
        return template.render(**self.data)
    
    def generate_quick_start_guide(self) -> str:
        """Generate quick start guide"""
        template = Template("""# Quick Start Guide - {{ global_info.program_name }}

Get started with {{ global_info.program_name }} in 5 minutes.

## Installation Check

```bash
# Verify installation
{{ global_info.executable }} --version
# Should output: {{ global_info.program_name }} {{ metadata.version }}
```

## Choose Your Mode

### Interactive Mode (Recommended for Beginners)
```bash
{{ global_info.executable }}
```
Follow the menu prompts for guided operation.

### Command Line Mode (For Advanced Users)
```bash
{{ global_info.executable }} COMMAND [OPTIONS]
```

## Essential Commands

{% for cmd_name, cmd_data in (commands.items() | list)[:4] -%}
### {{ loop.index }}. {{ cmd_data.description }}

```bash
{{ cmd_data.examples.basic.command if cmd_data.examples.basic else cmd_data.usage }}
```

{% endfor %}

## Your First Workflow

Let's process an audio file step by step:

```bash
# 1. Split audio into segments
{{ global_info.executable }} split my_audio.wav -s "0:00-2:00:intro" "2:00-5:00:main"

# 2. Convert to different format
{{ global_info.executable }} convert intro.wav -o intro.mp3 -f mp3

# 3. Add metadata
{{ global_info.executable }} metadata intro.mp3 --title "Introduction" --artist "My Name"

# 4. Generate spectrogram for analysis
{{ global_info.executable }} spectrogram intro.mp3 -o intro_spectrum.png
```

## Next Steps

- Read the [Complete CLI Reference](CLI_REFERENCE.md)
- Explore [Advanced Examples](CLI_EXAMPLES.md)
- Configure [Quality Settings]({{ global_info.executable }} quality-settings show)

## Getting Help

```bash
# General help
{{ global_info.executable }} --help

# Command-specific help
{{ global_info.executable }} split --help
{{ global_info.executable }} convert --help
```

Happy audio processing! 🎵
""")
        
        return template.render(**self.data)
    
    def generate_examples_guide(self) -> str:
        """Generate detailed examples guide"""
        template = Template("""# CLI Examples Guide - {{ global_info.program_name }}

Real-world examples and use cases for {{ global_info.program_name }}.

## Basic Operations

{% for cmd_name, cmd_data in commands.items() %}
### {{ cmd_data.description }}

{% for ex_name, ex_data in cmd_data.examples.items() -%}
**{{ ex_data.title }}:**
```bash
{{ ex_data.command }}
```
{{ ex_data.description }}

{% endfor %}
{% endfor %}

## Professional Workflows

{% for wf_name, wf_data in workflows.items() %}
### {{ wf_data.title }}

**Use Case:** {{ wf_data.description }}

{% for step in wf_data.steps -%}
**Step {{ step.step }}:** {{ step.description }}
```bash
{{ step.command }}
```

{% endfor %}

---

{% endfor %}

## Common Use Cases

### Podcast Production
```bash
# Complete podcast workflow
{{ global_info.executable }} split raw_recording.wav -s "0:00-45:00:episode1" "47:00-90:00:episode2"
{{ global_info.executable }} metadata episode1.wav --title "Episode 1" --artist "My Podcast"
{{ global_info.executable }} convert episode1.wav -o episode1.mp3 -f mp3 --quality vbr_high
```

### Music Album Processing
```bash
# Album mastering workflow
{{ global_info.executable }} convert ./masters --output ./archive -f flac --quality high --batch
{{ global_info.executable }} convert ./archive --output ./distribution -f mp3 --quality 320k --batch
```

### Audio Analysis
```bash
# Generate spectrograms for analysis
{{ global_info.executable }} spectrogram audio.wav --enhanced --show-quality-metrics
{{ global_info.executable }} spectrogram audio.wav --type dual --output-dir ./analysis
```

## Batch Processing

### Convert Entire Directory
```bash
# Recursive conversion
{{ global_info.executable }} convert ./audio_collection --output ./converted -f mp3 --batch --recursive
```

### Batch Metadata Update
```bash
# Apply metadata to all files in directory
for file in *.mp3; do
    {{ global_info.executable }} metadata "$file" --album "My Album" --artist "Artist Name"
done
```

## Quality Validation

### High-Quality Processing
```bash
# Professional quality validation
{{ global_info.executable }} convert input.wav -o output.flac -f flac --quality-validation --show-metrics
{{ global_info.executable }} split audio.wav -s "0:00-5:00:segment" --enhanced --quality-validation
```

### Configure Quality Settings
```bash
# Set studio quality profile
{{ global_info.executable }} quality-settings set-profile studio

# Custom thresholds
{{ global_info.executable }} quality-settings set-thresholds --thd -80.0 --snr 100.0
```

## Advanced Tips

### Time Format Examples
```bash
# Various time formats supported
{{ global_info.executable }} split audio.wav -s "1:30-2:45:segment1"      # MM:SS
{{ global_info.executable }} split audio.wav -s "1:30:45-2:15:30:segment2" # HH:MM:SS
{{ global_info.executable }} split audio.wav -s "90.5-165.75:segment3"    # Seconds
```

### Output Organization
```bash
# Organized output structure
mkdir -p output/{{archive,distribution,analysis}}
{{ global_info.executable }} convert masters/ -o output/archive -f flac --batch
{{ global_info.executable }} convert output/archive -o output/distribution -f mp3 --batch
{{ global_info.executable }} spectrogram output/archive/*.flac --output-dir output/analysis
```

## Troubleshooting Examples

{% for error_name, error_data in troubleshooting.common_errors.items() %}
### {{ error_data.error }}

**Problem:** {{ error_data.solution }}

**Solution:**
```bash
{{ error_data.example }}
```

{% endfor %}

---

*Need more help? Use `{{ global_info.executable }} COMMAND --help` for detailed command documentation.*
""")
        
        return template.render(**self.data)
    
    def generate_argparse_data(self) -> Dict[str, Any]:
        """Generate structured data for argparse integration"""
        parser_data = {
            'program_name': self.global_info.get('program_name', 'Audio Splitter Suite'),
            'description': self.global_info.get('description', ''),
            'version': self.metadata.get('version', '2.0.0'),
            'commands': {}
        }
        
        for cmd_name, cmd_data in self.commands.items():
            cmd_parser_data = {
                'name': cmd_name,
                'help': cmd_data.get('description', ''),
                'description': cmd_data.get('description', ''),
                'arguments': [],
                'options': []
            }
            
            # Add arguments
            if 'arguments' in cmd_data:
                for arg_name, arg_data in cmd_data['arguments'].items():
                    arg_info = {
                        'name': arg_name,
                        'help': arg_data.get('description', ''),
                        'type': arg_data.get('type', 'str'),
                        'required': arg_data.get('required', False)
                    }
                    cmd_parser_data['arguments'].append(arg_info)
            
            # Add options
            if 'options' in cmd_data:
                for opt_name, opt_data in cmd_data['options'].items():
                    opt_info = {
                        'name': opt_name,
                        'flags': opt_data.get('flags', []),
                        'help': opt_data.get('description', ''),
                        'type': opt_data.get('type', 'str'),
                        'default': opt_data.get('default'),
                        'choices': opt_data.get('choices'),
                        'required': opt_data.get('required', False)
                    }
                    cmd_parser_data['options'].append(opt_info)
            
            parser_data['commands'][cmd_name] = cmd_parser_data
        
        return parser_data

def main():
    """CLI interface for the documentation generator"""
    parser = argparse.ArgumentParser(
        description='Generate documentation from CLI data YAML',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--output', 
        choices=['help', 'markdown', 'readme', 'quickstart', 'examples', 'argparse'],
        required=True,
        help='Type of documentation to generate'
    )
    
    parser.add_argument(
        '--command', 
        help='Specific command for help output'
    )
    
    parser.add_argument(
        '--file', 
        help='Output file path'
    )
    
    parser.add_argument(
        '--data-file',
        default='docs/cli_data.yaml',
        help='Path to CLI data YAML file'
    )
    
    args = parser.parse_args()
    
    try:
        generator = CLIDocGenerator(args.data_file)
        
        if args.output == 'help':
            content = generator.generate_help_text(args.command)
        elif args.output == 'markdown':
            content = generator.generate_markdown_guide()
        elif args.output == 'readme':
            content = generator.generate_readme_section()
        elif args.output == 'quickstart':
            content = generator.generate_quick_start_guide()
        elif args.output == 'examples':
            content = generator.generate_examples_guide()
        elif args.output == 'argparse':
            content = json.dumps(generator.generate_argparse_data(), indent=2)
        
        if args.file:
            output_path = Path(args.file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding='utf-8')
            print(f"✅ Documentation generated: {args.file}")
        else:
            print(content)
            
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())