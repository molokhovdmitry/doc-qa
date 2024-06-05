# `retriever`

`Retriever` class usage example:
```
from src.retriever import Retriever

# Initialize the retriever
retriever = Retriever(ZIP_PATH)

# Answer the question
question = 'Question to the documents'
answer = retriever.answer(question)
```
`answer` will be a `dict`:
```
{
    'text': 'Answer to the question from documents.',
    'url': 'url',
    'full_html_name': Full html name with department and extension,
    'department': 'department'
}
```
To reset the vectorstore delete the `chroma` directory.

# `test_retriever`
Tests for `retriever`. Outputs average normalized Levenshtein distance and counts correctly predicted urls.

Launch with:
```
python -m src.test_retriever
```
or
```
python -m src.test_retriever --show_results
```
or
```
python -m pytest -s
```

Best results on PEC data: 0.72 avg Levenshtein and 9/20 correct urls.
