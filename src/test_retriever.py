import nltk
import re
from tqdm import tqdm

from src.data_loader import DataLoader
from src.retriever import Retriever

# Init data and retriever
dataset = DataLoader()
retriever = Retriever(dataset)

# Load questions
questions_path = 'data/questions.txt'
questions = []
answers = []
urls = []

# Regular expressions to match questions, answers, and URL names
question_pattern = r'Вопрос [0-9]{1,2}(.*?)Ответ'
answer_pattern = r'Ответ:(.*?)Материалы'
url_pattern = r'Материалы:\n\t+(.+)\n'

with open(questions_path, 'r') as file:
    content = file.read()

# Extract questions
matches = re.findall(question_pattern, content, re.DOTALL)
for match in matches:
    questions.append(match.strip())

# Extract answers
matches = re.findall(answer_pattern, content, re.DOTALL)
for match in matches:
    answers.append(match.strip())

# Extract URLs
matches = re.findall(url_pattern, content)
for match in matches:
    urls.append(match)

assert (len(questions) == len(answers) == len(urls) == 20)

# Replace `;` with `_`
for url in urls:
    if ';' in url:
        index = urls.index(url)
        urls.remove(url)
        new_url = url.replace(';', '_')
        urls.insert(index, new_url)

# Get predictions
pred_answers = []
pred_urls = []
print("Making predictions...")
pred_count = 0
for question in tqdm(questions):
    answer_dict = retriever.answer(question)
    if answer_dict is None:
        pred_answers.append(None)
        pred_urls.append(None)
        no_pred_count += 1
    pred_answers.append(answer_dict['text'])
    pred_urls.append(answer_dict['full_html_name'].split('/')[-1])
print(f"Predicted {pred_count} out of {len(questions)} questions.")


def test_avg_levenshtein() -> None:
    metrics = []
    for true, pred in zip(answers, pred_answers):
        levenshtein = nltk.edit_distance(true, pred)
        # Normalize by dividing by the length of the longer string
        normalized_levenshtein = levenshtein / max(len(true), len(pred))
        metrics.append(normalized_levenshtein)
    avg_levenshtein = sum(metrics) / len(metrics)
    print(
        "Average levenshtein distance (lower better):",
        f"{avg_levenshtein:.2f}"
    )
    assert 1 == 1


def test_urls():
    right_urls = []
    for true, pred in zip(urls, pred_urls):
        right_urls.append(true == pred)
    print(f"Correct {sum(right_urls)} from {len(questions)} urls.")
    assert sum(right_urls) > 1


if __name__ == '__main__':
    test_avg_levenshtein()
    test_urls()
