import nltk
import re
from tqdm import tqdm
import argparse

from src.retriever import Retriever

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    '-s',
    '--show_results',
    action='store_true',
    help="Outputs all results"
)
args = parser.parse_args()

# Init data and retriever
retriever = Retriever()

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
no_pred_count = 0
for question in tqdm(questions):
    answer_dict = retriever.answer(question)
    if answer_dict is None:
        pred_answers.append(None)
        pred_urls.append(None)
        no_pred_count += 1
    else:
        pred_answers.append(answer_dict['text'])
        pred_urls.append(answer_dict['full_html_name'].split('/')[-1])
print(
    f"Predicted {len(questions) - no_pred_count}",
    f"out of {len(questions)} questions."
)

# Init metric list for `test_avg_levenshtein`
metrics = []


def test_avg_levenshtein() -> None:
    """
    Calculates average normalized Levenshtein distance
    for true and predicted answers.
    """
    for true, pred in zip(answers, pred_answers):
        levenshtein = nltk.edit_distance(true, pred)
        # Normalize by dividing by the length of the longer string
        normalized_levenshtein = levenshtein / max(len(true), len(pred))
        metrics.append(normalized_levenshtein)
    avg_levenshtein = sum(metrics) / len(metrics)
    print(
        "Average levenshtein distance from 0 to 1 (lower is better):",
        f"{avg_levenshtein:.2f}"
    )
    assert avg_levenshtein < 0.8


def test_urls():
    """Counts predicted urls."""
    right_urls = []
    for true, pred in zip(urls, pred_urls):
        right_urls.append(true == pred)
    print(f"Correct {sum(right_urls)}/{len(questions)} urls.")
    assert sum(right_urls) >= 4


if __name__ == '__main__':
    test_avg_levenshtein()
    test_urls()

    # Show predictions
    if args.show_results:
        for question, ans, pred_ans, url, pred_url, metric in zip(
            questions, answers, pred_answers, urls, pred_urls, metrics
        ):
            print("Question:")
            print(question)
            print("Answer:")
            print(ans)
            print("Prediction:")
            print(pred_ans)
            print(f"Metric (lower is better): {metric:.3f}")
            print("URL:")
            print(url)
            print("Prediction URL:")
            print(pred_url)
            print("*" * 80 + "\n")
