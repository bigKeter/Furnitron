import time
import logging
import torch
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import streamlit as st
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants and Configuration
MODEL_PATH = "furnitron/models/model_20231204_195024_4"
TOKENIZER_PATH = "distilbert-base-uncased"
URLS_FILE = "furnitron/data/scraper_input/furniture_stores_pages_test.csv"
OUTPUT_FILE = "furnitron/data/inference_output/product_names.txt"
BATCH_SIZE = 64
TIMEOUT = 10


# Cache the Chromedriver path
@st.cache_resource
def get_chromedriver_path():
    return shutil.which('chromedriver')

# Cache and get webdriver options
@st.cache_resource
def get_webdriver_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    return chrome_options
@st.cache_resource
def init_chrome_driver():
    """
    Initialize and return a WebDriver for Chromium with specific options for headless browsing.
    """
    chrome_options = get_webdriver_options()

    # Using local Chromedriver if available, else use ChromeDriverManager
    driver_path = get_chromedriver_path()
    if driver_path is None:
        driver_service = Service(ChromeDriverManager().install())
    else:
        driver_service = Service(executable_path=driver_path)

    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    driver.set_page_load_timeout(TIMEOUT)  # Set page load timeout
    driver.set_script_timeout(TIMEOUT)  # Set script timeout

    return driver

@st.cache_resource
def init_model_and_tokenizer():
    """
    Initialize and return the PyTorch model, tokenizer, and device for the scraping task.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_PATH, local_files_only=True
    ).to(device)
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
    return model, tokenizer, device


def get_all_leaf_nodes_text(driver):
    """
    Execute a JavaScript script to collect all text from leaf nodes of the webpage.

    Args:
    driver (webdriver): Selenium WebDriver used to control the browser.

    Returns:
    list: A list of strings, each representing text from a leaf node.
    """
    script = """
    // JavaScript function to recursively get text from all leaf nodes
    function getAllLeafNodesText(element) {
        let nodes = [];
        if (element.hasChildNodes()) {
            for (let child of element.childNodes) {
                nodes = nodes.concat(getAllLeafNodesText(child));
            }
        } else if (element.nodeType === Node.TEXT_NODE && element.textContent.trim() !== "") {
            nodes.push(element.textContent.trim());
        }
        return nodes;
    }
    return getAllLeafNodesText(document.body);
    """
    return driver.execute_script(script)


def filter_text(text):
    """
    Filter a given text based on predefined conditions.

    Args:
    text (str): The text to be filtered.

    Returns:
    bool: True if the text meets the conditions, False otherwise.
    """
    conditions = [
        lambda t: t.strip(),  # Text should not be empty or whitespace
        lambda t: len(t.split()) <= 10,  # Text should not be too long
    ]
    return all(cond(text) for cond in conditions)


def get_candidate_names(leaf_nodes_text):
    """
    Extract candidate names from leaf node texts based on filtering criteria.

    Args:
    leaf_nodes_text (list): List of text from leaf nodes.

    Returns:
    list: List of filtered candidate names.
    """
    return [text for text in leaf_nodes_text if filter_text(text)]


def model_inference(names, model, tokenizer, device):
    """
    Perform model inference on a list of names to identify relevant product names.

    Args:
    names (list): List of candidate names.
    model (PreTrainedModel): PyTorch model for sequence classification.
    tokenizer (PreTrainedTokenizer): Tokenizer for the model.
    device (torch.device): Computational device (CPU or GPU).

    Returns:
    list: List of identified product names.
    """
    product_names = []
    for i in range(0, len(names), BATCH_SIZE):
        batch = names[i : i + BATCH_SIZE]
        tokenized = tokenizer(batch, padding=True, truncation=True)
        model.eval()  # Set model to evaluation mode
        with torch.no_grad():  # Disable gradient calculation for efficiency
            input_ids = torch.tensor(tokenized["input_ids"]).to(device)
            attention_mask = torch.tensor(tokenized["attention_mask"]).to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            is_furniture = outputs.logits.argmax(axis=1).tolist()
        # Add the names identified as product names to the list
        product_names.extend([batch[i] for i in range(len(batch)) if is_furniture[i]])
    return product_names


def scrape_product_names(url, driver, model, tokenizer, device):
    """
    Scrape product names from a given URL using the provided WebDriver and model.

    Args:
    url (str): URL to scrape.
    driver (webdriver): Selenium WebDriver.
    model (PreTrainedModel): PyTorch model for sequence classification.
    tokenizer (PreTrainedTokenizer): Tokenizer for the model.
    device (torch.device): Computational device (CPU or GPU).

    Returns:
    list: List of identified product names, if any.
    """
    logging.info(f"Processing URL: {url}")
    try:
        driver.get(url)
        # Wait until the page body is loaded
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        leaf_nodes_text = get_all_leaf_nodes_text(driver)
        candidate_names = get_candidate_names(leaf_nodes_text)
        return model_inference(candidate_names, model, tokenizer, device)
    except (TimeoutException, StaleElementReferenceException) as e:
        logging.error(f"Error encountered: {e}")
    except WebDriverException as e:
        logging.error(f"WebDriverException for URL {url}: {e}")


def produce_output(URLS_FILE, OUTPUT_FILE_NAME, driver, model, tokenizer, device):
    # Define the directory where the output file will be saved
    output_directory = "furnitron/data/inference_output"

    # Ensure that the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Construct the full path for the output file within the output directory
    output_file_path = os.path.join(output_directory, OUTPUT_FILE_NAME)

    with open(output_file_path, "w", encoding="utf-8") as output_file:
        with open(URLS_FILE, "r", encoding="utf-8") as file:
            urls = file.read().splitlines()

            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, url in enumerate(urls):
                try:
                    product_names = scrape_product_names(
                        url, driver, model, tokenizer, device
                    )
                    if product_names:
                        # Write the identified product names to the output file
                        output_file.write(f"\nURL: {url}\n")
                        output_file.writelines([f"{name}\n" for name in product_names])
                except WebDriverException as e:
                    logging.error(f"WebDriverException for URL {url}: {e}")
                progress_bar.progress((i + 1) / len(urls))
                status_text.text(f"Processing URL {i+1} of {len(urls)}")


def main():
    """
    Main function to orchestrate the web scraping process.
    """
    driver = init_chrome_driver()
    model, tokenizer, device = init_model_and_tokenizer()

    start_time = time.time()

    produce_output(URLS_FILE, OUTPUT_FILE, driver, model, tokenizer, device)

    driver.quit()

    end_time = time.time()
    duration = end_time - start_time
    mins, secs = divmod(duration, 60)
    logging.info(f"Total scraping time: {int(mins)} minutes and {int(secs)} seconds")


if __name__ == "__main__":
    main()
