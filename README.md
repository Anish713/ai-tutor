# AI Tutor For Students

## Introduction


- For more: [Check this Repository](https://github.com/Anish713/ai-tutor.git)

## Goals
Students can ask questions and system clears their confusions with clear answers like a tutor, and hence, AI Tutor. Main goals of this project are as follows:
1. Mathematical Problem Solving
2. Code Debugging Assistance
3. Answering AI related questions.

## Contributors
1. Anish Shrestha
2. Shashwot Shrestha
3. Rachana Subedi

## Project Architecture


# Status
## Known Issue
1. 

## High Level Next Steps
1. 


# Usage
## Installation
To begin this project, use the included `Makefile`

#### Creating Virtual Environment
This package is built using `python-3.11`. 
We recommend creating a virtual environment and using a matching version to ensure compatibility.
Example:
- `python -m venv .ai-tutor` with python 3.11, or
- `conda create -n .ai-tutor python=3.11` with anaconda.

Now, activate this virtual environment. Eg: `conda activate .ai-tutor` with anaconda or venv. Then you can install requirements with `pip install -r requirements.txt`.

#### pre-commit

`pre-commit` will automatically format and lint your code. You can install using this by using
`make use-pre-commit`. It will take effect on your next `git commit`

#### pip-tools

The method of managing dependencies in this package is using `pip-tools`. To begin, run `make use-pip-tools` to install. 

Then when adding a new package requirement, update the `requirements.in` file with 
the package name. You can include a specific version if desired but it is not necessary. 

To install and use the new dependency you can run `make deps-install` or equivalently `make`

If you have other packages installed in the environment that are no longer needed, you can you `make deps-sync` to ensure that your current development environment matches the `requirements` files. 

## Usage Instructions
1. Run ollama model locally. In separate terminal: 
- `ollama pull anishstha245/phi3_gsm8k`
- `ollama serve`
2. Activate previously created virtual environment. Eg: `conda activate .ai-tutor` with anaconda.
3. Create a .env file and insert API key as shown in .env.sample.
4. Navigate to directory src/ai_tutor_for_students.
5. Run the streamlit app with `streamlit run main.py` in terminal.

# Data Source
1. https://huggingface.co/datasets/openai/gsm8k
2. 

## Code Structure
## Artifacts Location
# Results
## Metrics Used
1. Accuracy
2. 
## Evaluation Results
