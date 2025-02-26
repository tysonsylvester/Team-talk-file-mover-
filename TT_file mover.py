import os
import re
import shutil

def get_base_directory():
    """Get the base directory path from the user."""
    while True:
        base_dir = input("Please enter the full base directory path for TeamTalk recordings: ")
        
        # Check if the provided path is valid
        if not os.path.exists(base_dir):
            print(f"Error: The directory '{base_dir}' does not exist. Please check the path and try again.")
            continue
        
        # Check if the directory is empty
        if not os.listdir(base_dir):
            print(f"Error: The directory '{base_dir}' is empty. Please provide a directory with files.")
            continue
        
        print(f"Using directory: {base_dir}")  # Confirm with the user
        return base_dir

def handle_existing_files():
    """Ask the user whether they want to replace existing files."""
    while True:
        choice = input("There are conflicting files. Do you want to replace all existing files? (Y/N): ").strip().lower()
        if choice == 'y':
            return True  # Replace all files
        elif choice == 'n':
            return False  # Don't replace any files
        else:
            print("Invalid input. Please enter 'Y' for Yes or 'N' for No.")

def organize_recordings(base_dir):
    """Organize recordings by date, time, and type."""
    files_moved = 0
    files_found = 0
    files_skipped = 0  # Track skipped files due to conflicts or no match
    conflicts = 0  # Track how many conflicts (files that already exist)
    replace_files = None  # This will hold the user's choice to replace files or not

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.mp3', '.wav')):
                files_found += 1
                filename = os.path.basename(file)

                # Match date (YYYYMMDD) and time (HHMMSS) in filename (e.g., 20250226-144644)
                match = re.search(r'(\d{8})-(\d{6})', filename)
                if match:
                    date = match.group(1)  # Extract YYYYMMDD
                    time = match.group(2)  # Extract HHMMSS
                    year, month, day = date[:4], date[4:6], date[6:8]
                    hour, minute, second = time[:2], time[2:4], time[4:6]

                    # Create a directory structure based on year, month, day, and time
                    target_dir = os.path.join(base_dir, year, month, day, f"{hour}-{minute}-{second}")

                    # Check if the file has the '#<number>' part for Isolated Recording
                    if '#' in filename:
                        target_dir = os.path.join(target_dir, 'Isolated Recordings')
                    else:
                        target_dir = os.path.join(target_dir, 'Conferences')

                    # Create the target directory if it does not exist
                    os.makedirs(target_dir, exist_ok=True)

                    target_file_path = os.path.join(target_dir, filename)

                    # Check if the file already exists
                    if os.path.exists(target_file_path):
                        conflicts += 1
                        if replace_files is None:  # Ask only once
                            replace_files = handle_existing_files()
                        if replace_files:
                            shutil.move(os.path.join(root, file), target_file_path)
                            files_moved += 1
                        else:
                            files_skipped += 1
                    else:
                        # No conflict, simply move the file
                        shutil.move(os.path.join(root, file), target_file_path)
                        files_moved += 1
                else:
                    files_skipped += 1  # If file doesn't match the expected pattern, skip it

    # Provide a concise summary of the results
    print(f"\nSummary:")
    print(f"Total files found: {files_found}")
    print(f"Total conflicts (files that already existed): {conflicts}")
    print(f"Files replaced: {files_moved}")
    print(f"Files skipped (due to no match or user choice): {files_skipped}")

def main():
    base_dir = get_base_directory()
    organize_recordings(base_dir)

if __name__ == "__main__":
    main()
