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

## Usage

AskLiz2 currently provides a command-line interface (CLI) for either one-off queryies, or chatting with the document database. 

### Currently Implemented
run `python -m src.backend.main` to run the document ingestion / chunking / embedding / db-insertion / retrieval / display pipeline, for the query hardcoded in `src/backend/main.py`.

### Future CLI
There is also a CLI defined in `src/frontend/cli.py` that will be used to query or chat with the corpus in the future. At the moment it is not hooked up to the backend, but soon will be. Here are the commands you can run via the `src/frontend/cli` module:

1. **Single Query**

   To ask a single question and get results:

   ```bash
   python src/frontend/cli.py query "Your question here"
   ```

   Options:
   - `--num-results`: Specify the number of results to return (default is 3)
   - `--source-file`: Optionally specify a particular file to query from

   Example:
   ```bash
   python src/frontend/cli.py query "What is the main conclusion of the report?" --num-results 5
   ```

2. **Interactive Chat**

   To start an interactive chat session:

   ```bash
   python src/frontend/cli.py chat
   ```

   In chat mode, you can ask multiple questions in succession. The chat maintains context, potentially providing more relevant answers based on the conversation history. Type 'exit', 'quit', or 'bye' to end the chat session.

### Notes

- Currently, the CLI provides dummy responses. Actual document querying functionality will be implemented in future versions.
- The chat mode maintains a context of up to 10 recent interactions to inform its responses.

For more information on usage and available commands, you can use the built-in help:

```bash
python src/frontend/cli.py --help
```

Or for help on a specific command:

```bash
python src/frontend/cli.py query --help
python src/frontend/cli.py chat --help
```