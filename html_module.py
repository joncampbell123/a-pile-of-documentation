
def html_escape(e):
    r = ""
    for c in e:
        if c == '&':
            r = r + "&amp;"
        elif c == '<':
            r = r + "&lt;"
        elif c == '>':
            r = r + "&gt;"
        elif c == '"':
            r = r + "&quot;"
        elif c == '\'':
            r = r + "&apos;"
        else:
            r = r + c
    #
    return r

