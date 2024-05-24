import os
import pandas as pd
import nltk

CURDIR = os.getcwd()
def answer_test(search_text: str,
                model_answer_text: str,
                question_csv='/data/questions.csv') -> str | float:
    """
    This function finds a similar question in a pandas DataFrame ['Question'] and returns [source_name].

    :param search_text: The reference question.
    :param model_answer_text: The model answer.
    :param question_csv: The path to the CSV file with reference questions.
    :return: The matching scope of comparison between model_answer_text and reference_text.
    """

    anwsers_path = CURDIR + question_csv

    with open(anwsers_path, 'r') as file:
        df = pd.read_csv(file)
        search_text = search_text.replace(' ', '').lower()
        df['Вопрос_tmp'] = df['Вопрос'].str.replace(' ', '').str.lower()
        similar_text = df[df['Вопрос_tmp'].str.contains(search_text, case=False)]
        if len(similar_text) == 0:
            return 'No similar question found. Check your question and try again.'
        # quest = similar_text['Вопрос'].values[0]
        # answ = similar_text['Ответ'].values[0]
        source_name = similar_text['Материалы'].values[0]

        levenshtein_distance = nltk.edit_distance(source_name, model_answer_text)
        match_score = 1 - (levenshtein_distance / max(len(source_name), len(model_answer_text)))

        print(f"Matching scope: {match_score:.2f}")

    return match_score

