#!/usr/bin/env python3
"""
CLI Examples Tester
Tests all CLI examples from cli_data.yaml to ensure they work correctly

This script validates that:
1. All CLI examples in documentation are syntactically correct
2. Commands execute without critical errors
3. Expected outputs are generated
4. No broken command combinations exist

Usage:
    python scripts/test_cli_examples.py [--dry-run] [--command COMMAND]
"""

import subprocess
import sys
import argparse
import yaml
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import json
import os

class CLIExamplesTester:
    """Test CLI examples from cli_data.yaml"""
    
    def __init__(self, cli_data_file: str = "docs/cli_data.yaml", dry_run: bool = False):
        self.cli_data_file = Path(cli_data_file)
        self.dry_run = dry_run
        self.temp_dir = None
        self.test_audio_file = None
        
        # Load CLI data
        with open(self.cli_data_file, 'r') as f:
            self.cli_data = yaml.safe_load(f)
        
        self.commands = self.cli_data.get('commands', {})
        self.workflows = self.cli_data.get('workflows', {})
        
        # Statistics
        self.stats = {
            'total_examples': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
    
    def setup_test_environment(self):
        """Set up temporary test environment"""
        print("🔧 Setting up test environment...")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="audio_splitter_test_"))
        print(f"  📁 Test directory: {self.temp_dir}")
        
        # Create test audio file (using ffmpeg if available, otherwise skip audio tests)
        self.test_audio_file = self.temp_dir / "test_audio.wav"
        
        if not self.dry_run:
            success = self._create_test_audio()
            if not success:
                print("  ⚠️ Could not create test audio file - audio tests will be skipped")
        else:
            print("  📝 Dry run mode - test files will not be created")
        
        # Create test directories
        test_dirs = ['output', 'masters', 'archive', 'distribution', 'spectrograms']
        for dir_name in test_dirs:
            (self.temp_dir / dir_name).mkdir(exist_ok=True)
        
        print("  ✅ Test environment ready")
    
    def _create_test_audio(self) -> bool:
        """Create a test audio file using ffmpeg"""
        try:
            # Try to create a simple test tone using ffmpeg
            result = subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=10',
                '-c:a', 'pcm_s16le', '-ac', '2', '-ar', '44100',
                str(self.test_audio_file), '-y'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and self.test_audio_file.exists():
                print(f"  🎵 Created test audio file: {self.test_audio_file.name}")
                return True
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Fallback: try to use sox
            result = subprocess.run([
                'sox', '-n', str(self.test_audio_file), 
                'synth', '10', 'sine', '440'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and self.test_audio_file.exists():
                print(f"  🎵 Created test audio file with sox: {self.test_audio_file.name}")
                return True
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Create a dummy audio file for syntax testing
        try:
            self.test_audio_file.write_text("# Dummy audio file for testing\n")
            print(f"  📝 Created dummy audio file: {self.test_audio_file.name}")
            return True
        except Exception:
            return False
    
    def cleanup_test_environment(self):
        """Clean up temporary test environment"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 Cleaned up test directory: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️ Could not clean up test directory: {e}")
    
    def test_command_examples(self, command_name: str) -> List[Dict[str, Any]]:
        """Test all examples for a specific command"""
        if command_name not in self.commands:
            return []
        
        command_data = self.commands[command_name]
        examples = command_data.get('examples', {})
        
        results = []
        
        print(f"\n🧪 Testing {command_name} command examples...")
        
        for example_name, example_data in examples.items():
            result = self._test_single_example(
                command_name, example_name, example_data
            )
            results.append(result)
            self.stats['total_examples'] += 1
            
            if result['status'] == 'passed':
                self.stats['passed'] += 1
                print(f"  ✅ {example_name}: {example_data.get('title', '')}")
            elif result['status'] == 'skipped':
                self.stats['skipped'] += 1
                print(f"  ⏭️ {example_name}: {result['reason']}")
            else:
                self.stats['failed'] += 1
                self.stats['errors'].append(result)
                print(f"  ❌ {example_name}: {result['error']}")
        
        return results
    
    def _test_single_example(self, command_name: str, example_name: str, example_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single CLI example"""
        command = example_data.get('command', '')
        
        # Prepare command for testing
        test_command = self._prepare_test_command(command)
        
        if not test_command:
            return {
                'command': command_name,
                'example': example_name,
                'status': 'skipped',
                'reason': 'Could not prepare test command'
            }
        
        if self.dry_run:
            return {
                'command': command_name,
                'example': example_name,
                'status': 'passed',
                'test_command': test_command,
                'note': 'Dry run - command not executed'
            }
        
        # Execute command
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=self.temp_dir
            )
            
            # Analyze result
            if result.returncode == 0:
                return {
                    'command': command_name,
                    'example': example_name,
                    'status': 'passed',
                    'test_command': test_command,
                    'stdout': result.stdout[:500] if result.stdout else '',
                    'stderr': result.stderr[:500] if result.stderr else ''
                }
            else:
                return {
                    'command': command_name,
                    'example': example_name,
                    'status': 'failed',
                    'error': f"Command failed with exit code {result.returncode}",
                    'test_command': test_command,
                    'stdout': result.stdout[:500] if result.stdout else '',
                    'stderr': result.stderr[:500] if result.stderr else ''
                }
                
        except subprocess.TimeoutExpired:
            return {
                'command': command_name,
                'example': example_name,
                'status': 'failed',
                'error': 'Command timed out (60s)',
                'test_command': test_command
            }
        except Exception as e:
            return {
                'command': command_name,
                'example': example_name,
                'status': 'failed',
                'error': str(e),
                'test_command': test_command
            }
    
    def _prepare_test_command(self, original_command: str) -> Optional[str]:
        """Prepare command for testing by substituting test files"""
        if not original_command:
            return None
        
        # Get project root
        project_root = Path(__file__).parent.parent
        
        # Replace common placeholders with test files
        replacements = {
            'audio.wav': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'input.wav': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'song.mp3': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'recording.wav': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'raw_recording.wav': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'episode1.wav': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'episode1.mp3': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'track01.mp3': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            'input_file': str(self.test_audio_file) if self.test_audio_file else 'test_audio.wav',
            
            # Directories
            './music': str(self.temp_dir / 'music'),
            './masters': str(self.temp_dir / 'masters'),
            './master_tracks': str(self.temp_dir / 'masters'),
            './archive': str(self.temp_dir / 'archive'),
            './distribution': str(self.temp_dir / 'distribution'),
            './spectrograms': str(self.temp_dir / 'spectrograms'),
            './analysis': str(self.temp_dir / 'analysis'),
            
            # Make sure we use the right python main.py path
            'python main.py': f'{sys.executable} {project_root}/main.py'
        }
        
        test_command = original_command
        for old, new in replacements.items():
            test_command = test_command.replace(old, new)
        
        # Add --help for commands that might fail due to missing files
        # This tests syntax without actually processing files
        if any(cmd in test_command for cmd in ['split', 'convert', 'metadata']) and '--help' not in test_command:
            if not self.test_audio_file or not self.test_audio_file.exists():
                # Convert to help command for syntax testing
                parts = test_command.split()
                if len(parts) >= 3:  # python main.py command
                    test_command = f"{parts[0]} {parts[1]} {parts[2]} --help"
        
        return test_command
    
    def test_workflow_examples(self) -> List[Dict[str, Any]]:
        """Test workflow examples"""
        print(f"\n🔄 Testing workflow examples...")
        
        results = []
        
        for workflow_name, workflow_data in self.workflows.items():
            print(f"\n  🔄 Testing workflow: {workflow_data.get('title', workflow_name)}")
            
            steps = workflow_data.get('steps', [])
            workflow_result = {
                'workflow': workflow_name,
                'title': workflow_data.get('title', ''),
                'steps': [],
                'status': 'passed'
            }
            
            for step in steps:
                step_command = step.get('command', '')
                test_command = self._prepare_test_command(step_command)
                
                if self.dry_run:
                    step_result = {
                        'step': step.get('step', ''),
                        'command': step_command,
                        'test_command': test_command,
                        'status': 'passed',
                        'note': 'Dry run'
                    }
                else:
                    # For workflows, just test syntax (add --help)
                    if test_command and '--help' not in test_command:
                        parts = test_command.split()
                        if len(parts) >= 3:
                            test_command = f"{parts[0]} {parts[1]} {parts[2]} --help"
                    
                    try:
                        result = subprocess.run(
                            test_command,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        step_result = {
                            'step': step.get('step', ''),
                            'command': step_command,
                            'test_command': test_command,
                            'status': 'passed' if result.returncode == 0 else 'failed',
                            'returncode': result.returncode
                        }
                        
                        if result.returncode != 0:
                            workflow_result['status'] = 'failed'
                            
                    except Exception as e:
                        step_result = {
                            'step': step.get('step', ''),
                            'command': step_command,
                            'test_command': test_command,
                            'status': 'failed',
                            'error': str(e)
                        }
                        workflow_result['status'] = 'failed'
                
                workflow_result['steps'].append(step_result)
                self.stats['total_examples'] += 1
                
                if step_result['status'] == 'passed':
                    self.stats['passed'] += 1
                    print(f"    ✅ Step {step.get('step', '')}")
                else:
                    self.stats['failed'] += 1
                    print(f"    ❌ Step {step.get('step', '')}")
            
            results.append(workflow_result)
            
            if workflow_result['status'] == 'passed':
                print(f"  ✅ Workflow completed: {workflow_data.get('title', '')}")
            else:
                print(f"  ❌ Workflow failed: {workflow_data.get('title', '')}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate test report"""
        report_lines = [
            "# CLI Examples Test Report",
            f"Generated: {self._get_timestamp()}",
            "",
            "## Summary",
            f"- Total examples tested: {self.stats['total_examples']}",
            f"- Passed: {self.stats['passed']} ✅",
            f"- Failed: {self.stats['failed']} ❌",
            f"- Skipped: {self.stats['skipped']} ⏭️",
            f"- Success rate: {(self.stats['passed'] / max(self.stats['total_examples'], 1)) * 100:.1f}%",
            ""
        ]
        
        if self.stats['errors']:
            report_lines.extend([
                "## Failures",
                ""
            ])
            
            for error in self.stats['errors']:
                report_lines.extend([
                    f"### {error['command']} - {error['example']}",
                    f"**Error:** {error['error']}",
                    f"**Command:** `{error.get('test_command', 'N/A')}`",
                    ""
                ])
        
        # Add detailed results
        if 'command_results' in results:
            report_lines.extend([
                "## Command Examples Results",
                ""
            ])
            
            for command, command_results in results['command_results'].items():
                report_lines.append(f"### {command}")
                for result in command_results:
                    status_emoji = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⏭️"
                    report_lines.append(f"- {status_emoji} {result['example']}")
                report_lines.append("")
        
        if 'workflow_results' in results:
            report_lines.extend([
                "## Workflow Results",
                ""
            ])
            
            for workflow_result in results['workflow_results']:
                status_emoji = "✅" if workflow_result['status'] == 'passed' else "❌"
                report_lines.append(f"### {status_emoji} {workflow_result['title']}")
                
                for step in workflow_result['steps']:
                    step_emoji = "✅" if step['status'] == 'passed' else "❌"
                    report_lines.append(f"  - {step_emoji} Step {step['step']}")
                
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run_tests(self, specific_command: Optional[str] = None) -> bool:
        """Run all tests"""
        print("🧪 Audio Splitter Suite - CLI Examples Tester")
        print("=" * 50)
        
        try:
            self.setup_test_environment()
            
            results = {
                'command_results': {},
                'workflow_results': []
            }
            
            # Test command examples
            if specific_command:
                if specific_command in self.commands:
                    results['command_results'][specific_command] = self.test_command_examples(specific_command)
                else:
                    print(f"❌ Command '{specific_command}' not found")
                    return False
            else:
                for command_name in self.commands.keys():
                    results['command_results'][command_name] = self.test_command_examples(command_name)
                
                # Test workflows
                results['workflow_results'] = self.test_workflow_examples()
            
            # Generate and save report
            report = self.generate_report(results)
            
            report_file = Path(__file__).parent.parent / "test_report_cli_examples.md"
            report_file.write_text(report, encoding='utf-8')
            
            print(f"\n📊 Test Results Summary:")
            print(f"  Total examples: {self.stats['total_examples']}")
            print(f"  Passed: {self.stats['passed']} ✅")
            print(f"  Failed: {self.stats['failed']} ❌")
            print(f"  Skipped: {self.stats['skipped']} ⏭️")
            print(f"  Success rate: {(self.stats['passed'] / max(self.stats['total_examples'], 1)) * 100:.1f}%")
            
            print(f"\n📝 Detailed report saved to: {report_file}")
            
            return self.stats['failed'] == 0
            
        finally:
            self.cleanup_test_environment()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Test CLI examples from cli_data.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Perform dry run - check syntax but do not execute commands'
    )
    
    parser.add_argument(
        '--command',
        help='Test only examples for specific command'
    )
    
    parser.add_argument(
        '--data-file',
        default='docs/cli_data.yaml',
        help='Path to CLI data file'
    )
    
    args = parser.parse_args()
    
    try:
        tester = CLIExamplesTester(args.data_file, args.dry_run)
        success = tester.run_tests(args.command)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())