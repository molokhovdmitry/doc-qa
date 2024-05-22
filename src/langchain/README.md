`Retriever` class usage example:
```
from src.data.data_loader import DataLoader
from src.langchain.retriever import Retriever

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
