import subprocess
import sys
import os

def compile_and_run_file(input_file):
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    # Run the compiler on the input file
    output_file = input_file
    compiler_command = ['python', 'src/compiler.py', input_file]
    try:
        subprocess.run(compiler_command, check=True)
        print(f"Compilation successful. Output generated: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed with error: {e}")
        return

    # Run the compiled output file
    run_command = ['python', output_file]
    try:
        subprocess.run(run_command, check=True)
        print(f"Script {input_file} executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Execution failed with error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_compiler.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    compile_and_run_file(input_file)

if __name__ == "__main__":
    main()