import os
import io
import tokenize
import re

data_dir = "../ProgramData"

def token_genrator(file):
    fopen = open(file, errors="ignore")
    str = fopen.read()
    str = comment_remover(str)
    str = io.StringIO(str)
    tokens = tokenize.generate_tokens(str.readline)
    return tokens

global_tokens = set()

def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s

    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)

for i in range(1, 105):
    data_subdir = data_dir + "/" + str(i)
    for file_name in os.listdir(data_subdir):
        tokens = token_genrator(data_subdir + "/" + file_name)
        try:
            for tok in tokens:
                global_tokens.add(tok.string)
        except IndentationError:
            print("Indent Error in Cpp File")

print(len(global_tokens))

output = open("../model/tokens", "w")
str = ""
for tok in global_tokens:
    str += tok + "\n"
output.write(str)
output.close()