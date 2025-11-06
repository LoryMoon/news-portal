from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

CENSORED_WORDS = [
    'редиска', 'плохой', 'ужасный', 'отвратительный',
    'неприличный', 'брань', 'ругательство'
]


@register.filter
@stringfilter
def censor(value):
    """
    Фильтр для цензурирования текста. Заменяет буквы нежелательных слов на '*'
    """
    if not isinstance(value, str):
        raise ValueError(f"Фильтр 'censor' можно применять только к строкам, получен: {type(value)}")

    words = value.split()
    censored_words = []

    for word in words:
        clean_word = ''.join(char for char in word if char.isalpha())

        if clean_word.lower() in [w.lower() for w in CENSORED_WORDS]:
            if len(clean_word) > 1:
                censored_word = clean_word[0] + '*' * (len(clean_word) - 1)
            else:
                censored_word = '*'

            result_word = word.replace(clean_word, censored_word)
            censored_words.append(result_word)
        else:
            censored_words.append(word)

    return ' '.join(censored_words)