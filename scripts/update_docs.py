#!/usr/bin/env python3
"""
Automatic Documentation Updater
Updates all documentation files from cli_data.yaml Single Source of Truth

This script regenerates all CLI documentation automatically:
- CLI_REFERENCE.md (complete reference)
- CLI_QUICK_START.md (quick start guide)
- CLI_EXAMPLES.md (detailed examples)
- README.md CLI section (between markers)

Usage:
    python scripts/update_docs.py [--force] [--check-only]
"""

import subprocess
import sys
import argparse
from pathlib import Path
from typing import List, Tuple
import re

def run_command(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run command and return (returncode, stdout, stderr)"""
    try:
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True,
            cwd=Path(__file__).parent.parent  # Run from project root
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_dependencies() -> bool:
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check if cli_data.yaml exists
    cli_data_path = Path(__file__).parent.parent / "docs" / "cli_data.yaml"
    if not cli_data_path.exists():
        print(f"❌ CLI data file not found: {cli_data_path}")
        return False
    
    # Check if doc_generator.py exists
    doc_gen_path = Path(__file__).parent.parent / "docs" / "doc_generator.py"
    if not doc_gen_path.exists():
        print(f"❌ Documentation generator not found: {doc_gen_path}")
        return False
    
    # Check if Python dependencies are available
    returncode, _, stderr = run_command([sys.executable, "-c", "import yaml, jinja2"])
    if returncode != 0:
        print(f"❌ Missing Python dependencies: {stderr}")
        print("Install with: pip install pyyaml jinja2")
        return False
    
    print("✅ All dependencies OK")
    return True

def generate_documentation() -> bool:
    """Generate all documentation files"""
    print("📚 Generating documentation files...")
    
    docs_to_generate = [
        ("markdown", "docs/CLI_REFERENCE.md", "CLI Reference Guide"),
        ("quickstart", "docs/CLI_QUICK_START.md", "Quick Start Guide"),
        ("examples", "docs/CLI_EXAMPLES.md", "Examples Guide")
    ]
    
    success = True
    
    for output_type, file_path, description in docs_to_generate:
        print(f"  📝 Generating {description}...")
        
        returncode, stdout, stderr = run_command([
            sys.executable, "docs/doc_generator.py",
            "--output", output_type,
            "--file", file_path
        ])
        
        if returncode == 0:
            print(f"    ✅ {description} generated successfully")
        else:
            print(f"    ❌ Failed to generate {description}")
            print(f"    Error: {stderr}")
            success = False
    
    return success

def update_readme_section() -> bool:
    """Update CLI section in README.md between markers"""
    print("📖 Updating README.md CLI section...")
    
    # Generate README section content
    returncode, readme_section, stderr = run_command([
        sys.executable, "docs/doc_generator.py",
        "--output", "readme"
    ])
    
    if returncode != 0:
        print(f"❌ Failed to generate README section: {stderr}")
        return False
    
    # Read current README
    readme_path = Path(__file__).parent.parent / "README.md"
    if not readme_path.exists():
        print(f"❌ README.md not found: {readme_path}")
        return False
    
    try:
        readme_content = readme_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading README.md: {e}")
        return False
    
    # Find markers
    start_marker = "<!-- CLI_SECTION_START -->"
    end_marker = "<!-- CLI_SECTION_END -->"
    
    if start_marker not in readme_content or end_marker not in readme_content:
        print(f"❌ CLI section markers not found in README.md")
        print(f"Add these markers where you want the CLI section:")
        print(f"  {start_marker}")
        print(f"  {end_marker}")
        return False
    
    # Replace section between markers
    try:
        before = readme_content.split(start_marker)[0]
        after = readme_content.split(end_marker)[1]
        
        new_content = f"{before}{start_marker}\n{readme_section.strip()}\n{end_marker}{after}"
        
        readme_path.write_text(new_content, encoding='utf-8')
        print("    ✅ README.md CLI section updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating README.md: {e}")
        return False

def check_documentation_sync() -> bool:
    """Check if documentation is in sync with cli_data.yaml"""
    print("🔄 Checking documentation synchronization...")
    
    cli_data_path = Path(__file__).parent.parent / "docs" / "cli_data.yaml"
    
    files_to_check = [
        "docs/CLI_REFERENCE.md",
        "docs/CLI_QUICK_START.md", 
        "docs/CLI_EXAMPLES.md"
    ]
    
    all_synced = True
    
    for file_path in files_to_check:
        doc_path = Path(__file__).parent.parent / file_path
        
        if not doc_path.exists():
            print(f"    ⚠️ Documentation file missing: {file_path}")
            all_synced = False
            continue
        
        # Check if doc file is newer than cli_data.yaml
        try:
            doc_mtime = doc_path.stat().st_mtime
            cli_data_mtime = cli_data_path.stat().st_mtime
            
            if cli_data_mtime > doc_mtime:
                print(f"    ⚠️ Documentation outdated: {file_path}")
                all_synced = False
            else:
                print(f"    ✅ Documentation up to date: {file_path}")
                
        except Exception as e:
            print(f"    ❌ Error checking {file_path}: {e}")
            all_synced = False
    
    return all_synced

def validate_generated_docs() -> bool:
    """Validate that generated documentation is correct"""
    print("🔍 Validating generated documentation...")
    
    # Check that all expected files exist
    expected_files = [
        "docs/CLI_REFERENCE.md",
        "docs/CLI_QUICK_START.md",
        "docs/CLI_EXAMPLES.md"
    ]
    
    all_valid = True
    
    for file_path in expected_files:
        doc_path = Path(__file__).parent.parent / file_path
        
        if not doc_path.exists():
            print(f"    ❌ Missing: {file_path}")
            all_valid = False
            continue
            
        try:
            content = doc_path.read_text(encoding='utf-8')
            
            # Basic validation checks
            if len(content) < 100:
                print(f"    ⚠️ Suspiciously short: {file_path} ({len(content)} chars)")
                all_valid = False
            elif "Audio Splitter Suite" not in content:
                print(f"    ⚠️ Missing project name in: {file_path}")
                all_valid = False
            else:
                print(f"    ✅ Valid: {file_path} ({len(content)} chars)")
                
        except Exception as e:
            print(f"    ❌ Error reading {file_path}: {e}")
            all_valid = False
    
    # Check README CLI section
    readme_path = Path(__file__).parent.parent / "README.md"
    if readme_path.exists():
        try:
            readme_content = readme_path.read_text(encoding='utf-8')
            if "<!-- CLI_SECTION_START -->" in readme_content and "<!-- CLI_SECTION_END -->" in readme_content:
                print("    ✅ README.md CLI section markers present")
            else:
                print("    ⚠️ README.md CLI section markers missing")
                all_valid = False
        except Exception as e:
            print(f"    ❌ Error checking README.md: {e}")
            all_valid = False
    
    return all_valid

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Update CLI documentation from cli_data.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/update_docs.py                    # Update all documentation
    python scripts/update_docs.py --check-only       # Only check if docs are synced
    python scripts/update_docs.py --force            # Force regeneration even if up to date
        """
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check if documentation is synchronized, do not update'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration even if documentation appears up to date'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate existing documentation, do not update'
    )
    
    args = parser.parse_args()
    
    print("📚 Audio Splitter Suite - Documentation Updater")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Validation only mode
    if args.validate_only:
        if validate_generated_docs():
            print("\n✅ All documentation is valid")
            return 0
        else:
            print("\n❌ Documentation validation failed")
            return 1
    
    # Check-only mode
    if args.check_only:
        if check_documentation_sync():
            print("\n✅ All documentation is synchronized")
            return 0
        else:
            print("\n⚠️ Documentation is out of sync - run without --check-only to update")
            return 1
    
    # Check if update is needed (unless forced)
    if not args.force:
        if check_documentation_sync():
            print("\n✅ Documentation is already up to date")
            print("Use --force to regenerate anyway")
            return 0
    
    print("\n🔄 Updating documentation...")
    
    # Generate documentation files
    if not generate_documentation():
        print("\n❌ Failed to generate documentation files")
        return 1
    
    # Update README section
    if not update_readme_section():
        print("\n❌ Failed to update README.md")
        return 1
    
    # Validate results
    if not validate_generated_docs():
        print("\n⚠️ Generated documentation may have issues")
        return 1
    
    print("\n✅ All documentation updated successfully!")
    print("\nGenerated files:")
    print("  📚 docs/CLI_REFERENCE.md")
    print("  🚀 docs/CLI_QUICK_START.md")
    print("  💡 docs/CLI_EXAMPLES.md")
    print("  📖 README.md (CLI section)")
    
    print("\nNext steps:")
    print("  1. Review the generated documentation")
    print("  2. Test CLI commands to ensure they work")
    print("  3. Commit the updated files to git")
    
    return 0

if __name__ == "__main__":
    exit(main())