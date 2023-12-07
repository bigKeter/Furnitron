# Results and Improvements 📈

## Results 🏆

### Extracting Product Names 🔍

Aside from scraping, my scraper had to face an extra challenge: extracting product names from web pages that were inaccessible. By intelligently leveraging DOM traversal, the tool successfully navigated this obstacle. 🚀

#### Visual Demonstration 📷

**Before Extraction**:

Here's what the webpage looked like initially. Notice the limited accessibility and the absence of direct product listings.

<p align="center">
  <img src="furnitron\screenshots\WebSite.JPG" alt="Webpage before extraction" width="75%">
  <br>
  <i>Initial view of the webpage, showing limited accessibility.</i>
</p>

**After Extraction**:

Despite these limitations, our scraper successfully extracted potential product names. Below is a snapshot of the extracted names, showcasing the effectiveness of our approach.

<p align="center">
  <img src="furnitron\screenshots\WebSiteFurnitureRegardlessOfPage.JPG" alt="Extracted product names" width="60%">
  <br>
  <i>Snapshot of the extracted product names, sorted by URL.</i>
</p>

### Model Performance Metrics 📊

#### Epoch Summary

The final model's performance over various training epochs is summarized in the tables below. The key metrics include loss, accuracy, precision, recall, and F1-score.

| Epoch      | Loss   | Accuracy | Precision | Recall | F1-Score |
|------------|--------|----------|-----------|--------|----------|
| Epoch 0    | 0.2171 | 0.9991   | 0.9982    | 1.0000 | 0.9991   |
| Epoch 1    | 0.1119 | 0.9991   | 0.9982    | 1.0000 | 0.9991   |
| Epoch 2    | 0.0076 | 0.9991   | 0.9982    | 1.0000 | 0.9991   |

### Graphical Analysis 📈

#### Loss Function Evolution

This graph shows the evolution of the loss function over the training epochs, illustrating how the model's performance improved over time.

<p align="center">
  <img src="furnitron\screenshots\LossGraph.JPG" alt="Loss Function Graph" width="75%">
</p>

#### Accuracy Evolution

This graph demonstrates the accuracy metric over the same period, providing a clear view of the model's increasing accuracy.

<p align="center">
  <img src="furnitron\screenshots\AccuracyGraph.JPG" alt="Accuracy Graph" width="75%">
</p>

#### Recall Evolution

This graph demonstrates the recall metric over the same period, providing a clear view of the model's increasing recall.

<p align="center">
  <img src="furnitron\screenshots\RecallGraph.JPG" alt="Recall Graph" width="75%">
</p>

### Web Scraping Duration Comparison ⏱️

- **Optimization Impact**: The scraping time was considerably reduced from an average of 7.2 seconds/page to 2.5 seconds/page, with a significant increase in extracted product names (from 60 to 4,000).

<p align="center">
  <img src="furnitron\screenshots\ScrapeGif.gif" alt="Scrape GIF" width="75%"/>
  <br>
  <em>Scraping websites, adding product names to the output file and logging the scraping time (56 websites scraped)</em>
</p>

## Code Robustness and Clarity 🛠️

- **Structured Code**: Well-commented and structured for ease of understanding and maintenance.
- **Efficient Error Handling**: Advanced handling of network issues, timeouts, and exceptions.

## Criteria Fulfillment ✔️

- **Decision-Making Process**: Detailed explanations of the thought process and strategic decisions.
- **Code Extendability**: Concise, documented, and structured for easy future extensions.
- **Output Presentation**: Clear, metric-based presentation of outputs, showcasing real-world applicability.

## Possible Improvements 🌟

- **Batch Size Optimization**: Plans to align batch size with available datasets for maximized efficiency.
- **Multiprocessing and Concurrency**: Incorporate multiprocessing and concurrent requests in future iterations to enhance speed.
- **Model Refinement**: Continuous training strategies for reducing false positives and adapting to diverse naming conventions.

## Conclusion 🎉

This project demonstrates a functional and effective approach to extracting product names from furniture store websites. It stands as a testament to both technical prowess and strategic problem-solving abilities.

## Further Considerations 🔍

### Future Optimization: Multiprocessing and Concurrent URL Access 💡

In future iterations of this project, a significant enhancement to consider is the integration of multiprocessing and concurrent URL access. This approach aims to drastically improve the scraping speed and overall efficiency, particularly when dealing with extensive datasets.

#### Multiprocessing Implementation:

- **Task Distribution**: The scraping task would be divided across multiple processes, each handling a subset of URLs. This method leverages the multi-core architecture of modern processors, ensuring that each core can independently execute a part of the task, thereby reducing the overall scraping time.

- **Inter-process Communication**: Careful management of inter-process communication will be crucial. This might involve setting up shared memory spaces or using messaging protocols to enable data exchange between processes, especially for aggregated results and error handling.

#### Concurrent URL Access:

- **Asynchronous Requests**: Implementing asynchronous requests allows the scraper to initiate and manage multiple URL requests simultaneously. This concurrency enables the program to not remain idle while waiting for a response from a server, thereby optimizing the use of network resources and time.

- **Batch Processing for Model Inference**: Although the scraping can be parallelized, model inference, particularly when using a GPU, might still need to be sequential due to hardware limitations. Here, a balanced approach is required to maximize GPU utilization without causing memory bottlenecks. This might involve batching a set of scraped data from multiple processes and then feeding it into the model in a synchronized manner.

### Sequential vs. Parallel Inference ⚖️

- **Inference Strategy**: A key consideration is whether to run model inferences in parallel across multiple GPUs (if available) or to stick with sequential processing on a single GPU. Parallel GPU processing can significantly speed up model inference but requires careful management of GPU memory and might introduce complexity in synchronizing results across different hardware.
