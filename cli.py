import subprocess

def main():
    # Define the command to invoke PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",  # Bundle everything into a single executable
        "Main.py"  # The name of your Python script
    ]

    # Run the command
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
