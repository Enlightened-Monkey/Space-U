import subprocess
import sys
import shutil
from pathlib import Path

def check_dependencies():
    """Checks for required packages."""
    if not shutil.which("jupyter"):
        print("Error: jupyter not found in PATH.")
        sys.exit(1)

    if not shutil.which("xelatex"):
        print("Warning: xelatex possibly not found in PATH.")

    try:
        import nbconvert
    except ImportError as e:
        print(f"Error: Required package '{e.name}' is not installed.")
        print("Please install it using: pip install nbconvert")
        sys.exit(1)

def convert_notebook_to_pdf(args):
    notebook_path = args[1]
    doctype = args[2] if len(args) > 2 else "pdf"
        


    notebook_path = Path(notebook_path)
    if not notebook_path.exists():
        print(f"Notebook {notebook_path} does not exist.")
        sys.exit(1)

    check_dependencies()

    cmd = [
        "jupyter", "nbconvert",
        "--to", doctype,
        "--allow-chromium-download",
        str(notebook_path)
    ]

    try:
        print(f"Generating report... {notebook_path}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <notebook.ipynb> <type>")
        sys.exit(1)

    convert_notebook_to_pdf(sys.argv)
