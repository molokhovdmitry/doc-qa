from bs4 import BeautifulSoup
import re

def bf_parser(doc_path: str) -> dict:
    """
    Parses an HTML document and returns a dictionary with the title of the document as the key
    and the cleaned text as the value.

    Args:
        doc_path (str): The path to the HTML document.
    Returns:
        dict: A dictionary with the title of the document as the key and the cleaned text as the value. """

    parser_dict = {}

    with open(doc_path, 'r') as f:

        soup = BeautifulSoup(f, 'html.parser')

        title = soup.title.string
        body = soup.body

        text = body.get_text('\n')
        text = re.sub("\n+", '\n', text)
        text = re.sub("\s+", ' ', text)
        parser_dict[title] = text.lower()

    return parser_dict



