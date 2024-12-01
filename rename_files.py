import os
import re
import shutil

from ollama import AsyncClient
import logging
import argparse
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Ensure real-time logging
    ]
)
logger = logging.getLogger(__name__)


async def create_old_files_directory(directory):
    old_files_dir = os.path.join(directory, "after-rename-to-delete")
    os.makedirs(old_files_dir, exist_ok=True)
    return old_files_dir


async def move_to_old_files_directory(old_files_dir, file_path, filename):
    # Check if file still exists
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} no longer exists. Skipping move.")
        return None
    # Handle potential filename conflicts
    counter = 1
    new_file_path = os.path.join(old_files_dir, filename)
    base_name, ext = os.path.splitext(filename)

    while os.path.exists(new_file_path):
        new_filename = f"{base_name}_{counter}{ext}"
        new_file_path = os.path.join(old_files_dir, new_filename)
        counter += 1

    try:
        shutil.move(file_path, new_file_path)
        return new_file_path
    except Exception as e:
        logger.error(f"Error moving file {file_path}: {e}")
        return None


async def rename_file(file_path, new_file_name):
    # Check if file still exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} no longer exists")
    directory = os.path.dirname(file_path)
    new_file_path = os.path.join(directory, new_file_name)

    # Additional checks to prevent overwriting existing files
    counter = 1
    base_name, ext = os.path.splitext(new_file_name)
    while os.path.exists(new_file_path):
        new_file_name = f"{base_name}_{counter}{ext}"
        new_file_path = os.path.join(directory, new_file_name)
        counter += 1

    os.rename(file_path, new_file_path)
    return new_file_name


async def analyze_content_and_rename(file_path, filename, old_files_dir):
    # Verify file exists before processing
    if not os.path.exists(file_path):
        logger.warning(f"File {file_path} no longer exists.")
        return 0, filename, "File does not exist"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        return 0, filename, str(e)

    prompt = f"""
    The following text is from a file in a software development project:

    ```
    {content}
    ```

    Suggest a file name using the following pattern:

    `<Type> - <Action> - <Component> - <Short Description>.<Extension>`

    Where:

    * **Type:**  task, issue, doc, snippet, review, idea
    * **Action:** create, fix, update, review, discuss, complete
    * **Component:** backend, frontend, database, api, auth, testing, or a more specific component name
    * **Short Description:** A concise summary of the file's content.
    * **Extension:** Based on the content (e.g., .md, .txt, .py). If unsure, use .md

    Provide only the file name as output, maximum 128 characters, lowercase. 
    """

    try:
        client = AsyncClient()
        response = await client.generate(
            "qwen2.5-coder:7b",  # Updated model
            prompt,
            options={
                "num_predict": 128,  # Limit output length
            }
        )
        suggested_name = response["response"].strip().lower()
    except Exception as e:
        logger.error(f"Error generating new filename for {filename}: {e}")
        return 0, filename, str(e)

    # Extract original file extension and remove it from suggested name
    original_name, original_ext = os.path.splitext(filename)
    # Remove any existing extensions from suggested name
    suggested_name = re.sub(r"\.\w+$", "", suggested_name)
    suggested_name = f"{suggested_name}{original_ext}"

    # Enhanced validation and fixing
    forbidden_chars = r'[<>/\\\|\?\*\:\"\+\%\!\@]'
    suggested_name = re.sub(forbidden_chars, "_", suggested_name)
    suggested_name = suggested_name.strip()
    suggested_name = re.sub(r"\s+", "-", suggested_name)
    suggested_name = re.sub(r"-{2,}", "-", suggested_name)
    suggested_name = re.sub(r"^-+", "", suggested_name)
    suggested_name = re.sub(r"-+$", "", suggested_name)
    suggested_name = suggested_name.strip('`')

    if not suggested_name:
        suggested_name = f"untitled_{os.path.splitext(filename)[0]}"

    try:
        # Verify file exists before renaming
        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} disappeared before renaming.")
            return 0, filename, "File disappeared"
        new_filename = await rename_file(file_path, suggested_name)
        # Move original file to old files directory
        await move_to_old_files_directory(old_files_dir, file_path, filename)
        return 1, new_filename, "Success"
    except Exception as e:
        logger.error(f"Error renaming {filename}: {e}")
        return 0, filename, str(e)


async def collect_files_to_rename(directory):
    files_to_rename = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.startswith("новый") and f.endswith(".txt")
    ]
    # Verify files exist
    files_to_rename = [f for f in files_to_rename if os.path.exists(f)]
    return files_to_rename


async def sequential_rename(files_to_rename, directory):
    # Create old files directory
    old_files_dir = await create_old_files_directory(directory)

    total_files = len(files_to_rename)
    renamed_count = 0
    failed_count = 0
    failed_files = []

    for i, filename in enumerate(files_to_rename, 1):
        file_path = os.path.join(directory, filename)
        success, result_filename, message = await analyze_content_and_rename(file_path, filename, old_files_dir)

        if success:
            renamed_count += 1
            logger.info(f"[{i}/{total_files}] Renamed: {filename} -> {result_filename}")
        else:
            failed_count += 1
            failed_files.append((filename, message))
            logger.warning(f"[{i}/{total_files}] Failed: {filename} - {message}")

        # Periodic progress update
        if i % 10 == 0 or i == total_files:
            logger.info(f"Progress: {renamed_count} renamed, {failed_count} failed")

    return renamed_count, failed_count, failed_files


async def parallel_rename(files_to_rename, directory, parallel_count):
    # Create old files directory
    old_files_dir = await create_old_files_directory(directory)

    total_files = len(files_to_rename)
    semaphore = asyncio.Semaphore(parallel_count)

    async def rename_with_semaphore(file_path, filename):
        async with semaphore:
            return await analyze_content_and_rename(file_path, filename, old_files_dir)

    # Prepare rename tasks
    rename_tasks = []
    for filename in files_to_rename:
        file_path = os.path.join(directory, filename)
        rename_tasks.append(rename_with_semaphore(file_path, filename))

    # Run tasks and collect results
    results = await asyncio.gather(*rename_tasks)

    renamed_count = 0
    failed_count = 0
    failed_files = []

    for i, (success, result_filename, message) in enumerate(results, 1):
        if success:
            renamed_count += 1
            logger.info(f"[{i}/{total_files}] Renamed: {result_filename}")
        else:
            failed_count += 1
            failed_files.append((result_filename, message))
            logger.warning(f"[{i}/{total_files}] Failed: {result_filename} - {message}")

        # Periodic progress update
        if i % 10 == 0 or i == total_files:
            logger.info(f"Progress: {renamed_count} renamed, {failed_count} failed")

    return renamed_count, failed_count, failed_files


async def main():
    parser = argparse.ArgumentParser(description="Rename files using Ollama.")
    parser.add_argument("directory", nargs="?", default=os.getcwd(),
                        help="Directory containing files to rename (defaults to current directory)")
    parser.add_argument("-p", "--parallel", type=int, default=0,
                        help="Number of parallel rename operations (default: sequential)")
    args = parser.parse_args()

    directory = args.directory

    if not os.path.isdir(directory):
        logger.error(f"Error: Directory '{directory}' not found.")
        return

    # Collect files to rename
    files_to_rename = await collect_files_to_rename(directory)

    if not files_to_rename:
        logger.info("No files found to rename.")
        return

    logger.info(f"Found {len(files_to_rename)} files to rename")

    # Choose rename method
    if args.parallel > 0:
        logger.info(f"Running in parallel mode with {args.parallel} concurrent tasks")
        renamed_count, failed_count, failed_files = await parallel_rename(
            files_to_rename, directory, args.parallel
        )
    else:
        logger.info("Running in sequential mode")
        renamed_count, failed_count, failed_files = await sequential_rename(
            files_to_rename, directory
        )

    # Final summary
    logger.info("\n--- Renaming Operation Summary ---")
    logger.info(f"Total files processed: {len(files_to_rename)}")
    logger.info(f"Successfully renamed: {renamed_count}")
    logger.info(f"Failed to rename: {failed_count}")

    if failed_files:
        logger.warning("\nFiles that failed to rename:")
        for file, error in failed_files:
            logger.warning(f"  - {file}: {error}")


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("\nOperation interrupted by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
