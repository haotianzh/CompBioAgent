**Author:** Haotian Zhang

**Date:** 2025-05-26

**Description:**
This is an initial draft of **CompBioAgent**, currently implementing only the dot plot functionality. Further development is planned to extend its capabilities.

---

### Folder Structure

* **`plot_h5ad.py`**: A script for generating various plots for single-cell RNA-seq data. It accepts a JSON file as input or can be invoked with a JSON object.
* **`test_tool_calling.json`**: An example JSON file demonstrating how to call `plot_h5ad.py`.
* **`test_azure_LLM.py`**: Azure OPENAI test.
* **`prompt.py`**: A prompt template used to instruct the LLM to extract information from user queries.
* **`compbioagent.py`**: The main entry point of the project.
