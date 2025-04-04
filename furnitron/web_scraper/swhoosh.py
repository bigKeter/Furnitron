from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.writing import AsyncWriter
import os


def create_search_index(index_dir, schema):
    """
    Creates or opens a search index directory.

    :param index_dir: The directory where the search index is stored or will be created.
    :param schema: The schema to be used for creating the index.
    :return: The index object.
    """
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    if not exists_in(index_dir):
        return create_in(index_dir, schema)
    return open_dir(index_dir)


def add_data_to_index(index_dir, file_path):
    """
    Adds data from a file to the search index.

    :param index_dir: The directory where the search index is located.
    :param file_path: The path to the file containing the data to be indexed.
    """
    try:
        ix = open_dir(index_dir)
        writer = AsyncWriter(ix)
        with open(file_path, "r") as file:
            current_url = ""
            for line in file:
                line = line.strip()
                if line.startswith("URL:"):
                    current_url = line.split("URL:")[1].strip()  # Capture the URL
                elif line:
                    writer.add_document(
                        url=current_url, content=line
                    )  # Index both URL and content
        writer.commit()
    except Exception as e:
        print(f"Error adding data to index: {e}")


# Define a schema for the index
schema = Schema(
    url=ID(stored=True), content=TEXT(stored=True)
)  # URL and content fields

# Example usage
index_dir = "indexdir"
index = create_search_index(index_dir, schema)
