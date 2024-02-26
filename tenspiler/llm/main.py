import argparse
import json
import os
import re

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# reading arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument("--filename", type=str)
parser.add_argument("--source_code", type=str)
parser.add_argument("--dsl_code", type=str)
args = parser.parse_args()

dir = "./tenspiler"
filename = args.filename
source_code = open(args.source_code).read()
dsl_code = open(args.dsl_code).read()


# prompt for guessing the post conditions of a function. dsl_code is the set of functions and constants that can be used to rewrite the function. source_code is the function to be rewritten.
TEMPLATE_TEXT = f"""
Your task is to rewrite the given `test` C++ Function. You need to use only the set of provided functions and constants to achieve this. The rewritten program should be semantically equivalent to the `test` function.
```
#defined functions
{dsl_code}
```
```
//test function
{source_code}
```
"""

TEMPLATE_SYS = "You are a helpful expert in programming languages."

# call the completions endpoint to get the completions for the prompt
outputs = client.chat.completions.create(
    model="gpt-4",  # model to use
    messages=[
        {"role": "system", "content": TEMPLATE_SYS},
        {"role": "user", "content": TEMPLATE_TEXT},
    ],
    n=10,  # number of candidates,
)


# regex to extract the code from the completions
def extract(s):
    return [x for x in re.findall(r"```(?:python|assembly)?(.*)```", s, re.DOTALL)]


# extract the code from the completions
for idx, c in enumerate(outputs.choices):
    out = extract(c.message.content)
    if out:
        print(f"{idx}")
        print(out[0])
    print("=====")


if not os.path.exists(dir):
    os.makedirs(dir)

# saving prompt and completions to a file
with open(f"{dir}/{filename}.json", "w") as f:
    json.dump([c.message.content for c in outputs.choices], f, indent=4)

with open(f"{dir}/prompt_{filename}.txt", "w") as f:
    f.write(TEMPLATE_TEXT)
