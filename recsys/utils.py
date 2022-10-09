def preprocess(text):
    clean_text = []
    for char in text:
        if char.isalpha() or char == " ":
            clean_text.append(char)
        else:
            clean_text.append(" ")

    text = " ".join("".join(clean_text).split())
    return text
