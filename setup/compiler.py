import subprocess
import os
import sys

def compile_tailwind():
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    tailwind_bin = os.path.join(setup_dir, "tailwindcss")
    input_css = os.path.join(setup_dir, "css", "src.css")
    output_css = os.path.abspath(os.path.join("app", "static", "css", "app.css"))
    config = os.path.join(setup_dir, "tailwind.config.js")

    if not os.path.exists(tailwind_bin):
        sys.exit("Tailwind CLI binary not found in Setup/. Please add it.")

    return subprocess.Popen([
        tailwind_bin,
        "-i", input_css,
        "-o", output_css,
        "--config", config,
        "--watch"
    ])