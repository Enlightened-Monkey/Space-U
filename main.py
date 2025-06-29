import subprocess
import sys
import shutil
from pathlib import Path
import argparse


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
    notebook_path = args.notebook
    doctype = args.type if args.type else "pdf"
    no_inputs = "--TemplateExporter.exclude_input=True" if args.no_inputs else ""

    notebook_path = Path(notebook_path)
    if not notebook_path.exists():
        print(f"Notebook {notebook_path} does not exist.")
        sys.exit(1)

    check_dependencies()

    cmd = [
        "jupyter", "nbconvert",
        "--to", doctype,
        "--allow-chromium-download",
        no_inputs,
        str(notebook_path)
    ]

    try:
        print(f"Generating report... {notebook_path}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Jupyter Notebook to PDF or HTML.")
    parser.add_argument("-p", "--path", dest="notebook", help="Path to the Jupyter notebook file")
    parser.add_argument("-t", "--type", dest="type", choices=["pdf", "html"], help="Output type (defaults to pdf)")
    parser.add_argument("--no-inputs", dest="no_inputs", action="store_true", help="Exclude code inputs from the output")

    args = parser.parse_args()

    convert_notebook_to_pdf(args)
