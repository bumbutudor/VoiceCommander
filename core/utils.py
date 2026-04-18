"""utilitare partajate"""


def normalize(text):
    """sterge diacriticele din text"""
    table = {
        "ă": "a", "â": "a", "î": "i", "ș": "s", "ț": "t",
        "Ă": "A", "Â": "A", "Î": "I", "Ș": "S", "Ț": "T",
        "ş": "s", "ţ": "t", "Ş": "S", "Ţ": "T",
    }
    for old, new in table.items():
        text = text.replace(old, new)
    return text
