import subprocess
import glob, os

# Get all .pas files in test/*/*.pas
files = glob.glob('test/*/*.pas')

# Iterate over each file and run the command
for file in files:
    command = ["python3", "src/driver_ast_decorated.py", file]
    
    if 'milestone-1' in file:
        continue

    # Run the command for each file
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Print the result for this specific file
    print(f"Running for file: {file}\n")
    subprocess.run(f"cat {os.getcwd()}/{file}", shell=True, check=True)
    print("\n\nSTDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("=" * 40)  # Separator between runs
