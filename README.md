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

1. **Single Query**

   To ask a single question and get results:

   ```bash
   python -m src.frontend.cli query "Your question here"
   ```

   Optional arguments that can be specified to tailor results can be viewed by running `python -m src.frontend.cli. query --help`

2. **Interactive Chat**

   To start an interactive chat session:

   ```bash
   python -m src.frontend.cli chat
   ```

   In chat mode, you can ask multiple questions in succession. The chat maintains context, potentially providing more relevant answers based on the conversation history. Type 'exit', 'quit', or 'bye' to end the chat session.

   Optional arguments that can be specified to tailor results can be viewed by running `python -m src.frontend.cli. chat --help`

### Notes

- Currently, both CLI commands (`query` and `chat`) are just performing (hybrid) retrieval, like RAG without the 'G' step. Synthesizing retrieved passages into a cohesive answer using an LLM is a future feature. My technical objective is to keep answers always grounded in specific retrieved source material passages.