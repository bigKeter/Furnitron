import os
import tempfile
import glob
import time
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
import streamlit as st
from main import produce_output, init_chrome_driver, init_model_and_tokenizer
from swhoosh import add_data_to_index
from analysis import create_temp_file_without_urls, count_categories
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize driver, model, tokenizer, and device
driver = init_chrome_driver()
model, tokenizer, device = init_model_and_tokenizer()


# Function to generate the output file path based on the uploaded file's name
def generate_output_file_path(uploaded_file):
    base_name = os.path.splitext(uploaded_file.name)[0]
    return f"{base_name}_output.txt"


# Function to list all .txt files in the output directory
def list_output_files(directory):
    return glob.glob(os.path.join(directory, "*.txt"))


# Streamlit UI
def main():
    st.title("Furnitron 3000")

    # File uploader for URLS_FILE
    urls_file = st.file_uploader("Upload a file containing URLs", type=["csv", "txt"])

    if urls_file:
        # Generate output file path
        output_file = generate_output_file_path(urls_file)

        # When the 'Start Scraping' button is clicked
        if st.button("Start Scraping"):
            # Save the uploaded file to a temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".csv", mode="w"
            ) as fp:
                fp.write(urls_file.getvalue().decode("utf-8"))
                temp_urls_file = fp.name

            st.write("Scraping started... Please wait.")
            # Start timer
            start_time = time.time()

            produce_output(
                temp_urls_file, output_file, driver, model, tokenizer, device
            )

            # End timer
            end_time = time.time()
            duration = end_time - start_time
            mins, secs = divmod(duration, 60)
            st.write(
                f"Scraping completed in {int(mins)} minutes and {int(secs)} seconds."
            )

            # Clean up the temporary file
            os.unlink(temp_urls_file)

    # Dropdown to select the output file for viewing results
    output_dir = "furnitron/data/inference_output"
    output_files = list_output_files(output_dir)
    selected_file = st.selectbox("Select an output file to view results", output_files)

    # Show the contents of the selected file
    if st.button("Show Results"):
        if selected_file and os.path.exists(selected_file):
            with open(selected_file, "r") as file:
                st.text_area("Scraping Results", file.read(), height=600)
        else:
            st.write("No results to display yet.")

    index_dir = "indexdir"

    # Index for search
    if st.button("Index Data"):
        for file_path in output_files:
            add_data_to_index(index_dir, file_path)
        st.write("Data indexing completed.")

    # Search
    search_query = st.text_input("Enter a keyword to search")
    try:
        if st.button("Search"):
            ix = open_dir(index_dir)
            with ix.searcher() as searcher:
                query = QueryParser("content", ix.schema).parse(search_query)
                results = searcher.search(query, limit=50)

                # Group results by URL
                results_by_url = {}
                for result in results:
                    url = result["url"]
                    content = result["content"]
                    if url not in results_by_url:
                        results_by_url[url] = []
                    results_by_url[url].append(content)

                # Display results in expanders
                for url, contents in results_by_url.items():
                    with st.expander(f"URL: {url}"):
                        for content in contents:
                            st.write(content)

                if not results:
                    st.write("No results found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    if st.button("Analyze Data"):
        output_files = list_output_files(output_dir)
        temp_file_path = create_temp_file_without_urls(output_files)

        # Frequency Analysis
        category_counts = count_categories(temp_file_path)
        df = pd.DataFrame(category_counts.items(), columns=["Item", "Count"])
        df = df.sort_values("Count", ascending=False)

        # Displaying the Bar Chart
        st.bar_chart(
            df.set_index("Item")
        )  # This line creates and displays the bar chart

        # Word Cloud Generation (remains the same)
        text = " ".join(df["Item"])
        wordcloud = WordCloud(width=800, height=400).generate(text)
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        st.pyplot(plt)

        # Optionally delete the temporary file
        os.remove(temp_file_path)


if __name__ == "__main__":
    main()
