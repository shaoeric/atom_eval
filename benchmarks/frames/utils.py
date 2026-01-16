import re
import string


def normalize_answer(s):
    """
    Normalize answer for comparison, supporting both English and Chinese.
    """
    def remove_articles(text):
        # Remove English articles
        text = re.sub(r'\b(a|an|the)\b', ' ', text, flags=re.IGNORECASE)
        return text

    def white_space_fix(text):
        # Normalize whitespace for both English and Chinese
        # Replace multiple spaces/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def remove_punc(text):
        # Remove English punctuation
        exclude = set(string.punctuation)
        # Also remove common Chinese punctuation
        chinese_punc = set('，。！？；：、""''（）【】《》〈〉「」『』〔〕…—·')
        exclude.update(chinese_punc)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        # Only lowercase if text contains English characters
        # Preserve Chinese characters as-is
        if re.search(r'[a-zA-Z]', text):
            return text.lower()
        return text

    return white_space_fix(remove_articles(remove_punc(lower(s))))


GENERAL_ORM_PROMPT = """You are an expert in verifying if two answers are the same.
Your input is a problem and two answers, Answer 1 and Answer 2. You need to check if they are equivalent.
Your task is to determine if two answers are equivalent, without attempting to solve the original problem.
Compare the answers to verify they represent identical values or meaning, even when written in different forms or notations.

Your output must follow the following format:
1) Provide an explanation for why the answers are equivalent or not.
2) Then provide your final answer in the form of: [[YES]] or [[NO]]
"""  # noqa: E501

ORM_USER_TEMPLATE = """
Problem: {problem}
Answer 1: {answer_1}
Answer 2: {answer_2}
"""
