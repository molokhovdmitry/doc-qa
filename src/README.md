# `bot`

# `retriever`

`Retriever` class usage example:
```
from src.data_loader import DataLoader
from src.retriever import Retriever

# Initialize dataset and retriever
dataset = DataLoader()
retriever = Retriever(dataset)

# Answer the question
question = 'Question to the documents'
answer = retriever.answer(question)
```
`answer` will be a `dict`:
```
{
    'text': 'Answer to the question from documents.',
    'url': 'url',
    'department': 'department'
}
```
To reset the vectorstore delete `chroma` directory.

# `data_loader`

`DataLoader` class takes path to `.zip` file as an input, extracts the files with changed file names, matches `.html` file names to names in `.txt` files and creates an iterable object.

Assuming we are starting the app from the project root directory with:
```
python -m src.bot
```
We can use the class like this:
```
data = DataLoader(
    zip_path='data/data.zip',
    extract_dir='data/extracted'
)
```
And then iterate through the files in a loop:
```
for file in data:
    print(file)
```
Where `file` is a `Dict`:
```
{
    'source': 'path to file',
    'name': 'actual file name without extension',
    'full_html_name': 'full file name',
    'department': 'department name',
    'url': 'url'
}
```

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
