# Register a source

This tutorial will explain how to reference a new source to QALITA Platform.

Requirements :

* [Python (>3.12)](https://www.python.org/)
* [QALITA Platfrom Account](https://cloud.platform.qalita.io/signup)
* QALITA Agent deployed locally
  * [Deploy an agent locally on Windows](https://doc.qalita.io/docs/cli/quick-start)
  * [Deploy an agent locally on Linux/MacOS](https://doc.qalita.io/docs/cli/quick-start)
  * [Deploy an agent locally with Docker](https://doc.qalita.io/docs/cli/docker)

# 1. Fetch a source to be registered

First we need to download a dataset, for our tutorial we will download a synthetic dataset from [Hugging Face](https://huggingface.co/).

* 1.1 Download [healthcare admissions](https://huggingface.co/datasets/syncora/synthetic-healthcare-admissions/resolve/main/Healthcare_Syncora_Synthetic%201.csv?download=true)
* 1.2 Rename to `Healthcare_Syncora_Synthetic 1.csv`
* 1.3 Save it where you want

# 2.1 Register from Terminal commandline

* 2.1.1 Open your terminal
* 2.1.2 Make sure you are logged in `qalita agent login`
* 2.1.3 Type `qalita source add`
  * Source name = `Healthcare_Syncora_Synthetic`
  * Source Type = `csv`
  * Source description = 
  ```
  This synthetic healthcare dataset simulates hospital admission records including demographics, billing, medications, and lab results.
  ```

# 2.2 Register from Agent GUI

