# AskLiz
For all your questions about the January 6th Select Committee's findings.
Current: query the final report
Future: query the set of deposition transcripts themselves, and maybe even the Jack Smith legal filings.

## Prerequisites / Installing the dev environment
Generate a requirements.txt file for your platform by running the following commands
```bash
python -m pip install --upgrade pip pip-tools wheel
pip-compile requirements.in -o requirements.txt --resolver=backtracking 
```

...then install them (ideally into your virtual environment) with:
```bash
pip install -r requirements.txt
```

### Secrets / API Keys.
To run successfully, you'll need to create a `secrets.yaml` file in the root directory of the project. It should look like [`secrets_example.yaml`](secrets_example.yaml), but with your actual values filled in.


## Usage
AskLiz2 is a minimal streamlit app providing a simple interface to query the final report of the January 6th Select Committee. To launch the app, run:

To ask a single question and get results:

```bash
PYTHONPATH=. streamlit run src/frontend/main.py
```