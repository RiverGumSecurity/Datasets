#!/usr/bin/env python3

import argparse
import json
import html
import re
from bs4 import BeautifulSoup


class Convert():

    output_json = []
    def __init__(self, filename, ins=''):
        self.filename = filename
        self.ins = ins

    def run(self):
        with open(self.filename, 'rt') as fh:
            content = json.load(fh)
        for b in content:
            if not b['title'] or not b['taxonomies']:
                continue
            title = html.unescape(
                re.sub(r'[^\x20-\x5b\x5d-\x7a]+', '', b['title'].strip()))
            taxonomies = html.unescape(
                re.sub(r'[^\x20-\x5b\x5d-\x7a]+', '', ', '.join(b['taxonomies'])).strip())
            created = b['date_created']
            content = re.sub(r' +', ' ', BeautifulSoup(b['content'], "html.parser").get_text())
            content = re.sub(r'\n{2,}', '\n\n', content)
            content = re.sub(r'^\n', '', content)
            content = re.sub(r'\u00a0', ' ', content)
            if created is None:
                created = ''
            inp = f"""\
Title: "{title}"
Taxonomies: "{taxonomies}"
Creation Date: "{created}"
"""

            if len(content) < 200 or \
                    re.match(r'^(?:\[embed\])?https?://.+', content) or \
                    'webcast' in taxonomies.lower() or \
                    'podcast' in taxonomies.lower():
                continue

            self.output_json.append({
                    'input': '', 
                    'instruction': self.ins,
                    'output': inp + content
                })

        print(json.dumps(self.output_json, indent=4))



if __name__ == '__main__':
    instructions = '''\
Below is an instruction that describes a task, paired with an input that provides further context.
You are an information security expert and have deep technical knowledge
in the information security domain.  Using the input provided, pick from one of the following options.
1. Write a new blog post using the provided input as a title.
2. Summarize or retrieve an existing blog post in its entirety.
3. Explain technical concepts in summary, and in detail if asked.
4. Provide references for further reading if possible.
'''
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='json file of input data')
    args = parser.parse_args()
    Convert(args.filename, ins=instructions).run()
