from collections import Counter
import tempfile


def create_temp_file_without_urls(output_files):
    """
    Creates a temporary file consolidating content from multiple files,
    excluding lines starting with 'URL:'.

    Args:
        output_files (list of str): List of file paths to process.

    Returns:
        str: Path to the temporary file.
    """
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        for file_path in output_files:
            try:
                with open(file_path, "r") as file:
                    for line in file:
                        if not line.startswith("URL:"):
                            temp_file.write(line)
            except IOError as e:
                print(f"Error reading file {file_path}: {e}")
        return temp_file.name


def count_categories(file_path):
    """
    Counts occurrences of each category in a file. Assumes each line in the file
    represents a separate category.

    Args:
        file_path (str): Path to the file for processing.

    Returns:
        Counter: Counts of each category.
    """
    try:
        with open(file_path, "r") as file:
            categories = [line.strip() for line in file if line.strip()]
        return Counter(categories)
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return Counter()
