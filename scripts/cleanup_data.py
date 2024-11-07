#!/usr/bin/env python3

import argparse
import json
import html
import re
from bs4 import BeautifulSoup


class Convert():

    output_json = []
    def __init__(self, filename, ins='', maxlen=1024):
        self.filename = filename
        self.maxlen = maxlen - 40
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
            output = re.sub(r' +', ' ', BeautifulSoup(b['content'], "html.parser").get_text())
            if created is None:
                created = ''
            metadata = f"""

The following information describes this blog.

Title: "{title}"
Taxonomies: "{taxonomies}"
Creation Date: "{created}"
"""

            output = re.sub(r' +', ' ', BeautifulSoup(b['content'], "html.parser").get_text())
            if len(output) < 200 or \
                    re.match(r'^(?:\[embed\])?https?://.+', output) or \
                    'webcast' in taxonomies.lower() or \
                    'podcast' in taxonomies.lower():
                continue

            parsed = self.parse_content(output)
            for item in parsed:
                self.output_json.append({
                    'input': '', 
                    'instruction': self.ins + metadata,
                    'output': item
                })
        print(json.dumps(self.output_json, indent=4))

    def parse_content(self, content):
        res = []
        content = re.sub(r'(?i)https?://[a-z0-9\-\.]+?', '', content)
        tokens = re.findall(r"([\-\w'!?\.]+)\b", content)

        if len(tokens) > self.maxlen:
            for i in range(len(tokens) // self.maxlen):
                s = i * self.maxlen
                e = i * self.maxlen + self.maxlen
                res.append(' '.join(tokens[s:e]))
        else:
            res.append(' '.join(tokens))
        return res


if __name__ == '__main__':
    instructions = '''\
You are an information security expert and have deep technical knowledge
in the information security domain. You have the extensive knowledge of
an experienced senior information security consultant. You thoroughly understand a
diverse amount of information security concepts including encryption, hashing,
risk analysis, penetration testing, red teaming, purple teaming,
web application testing, source code analysis, internal and external network testing.

Take a step back and think step-by-step about how to achieve the best possible results.
Be very precise, and avoid the temptation to repeat yourself.
Provide a response to the input provided using one of the options below.

1. Respond to a technical inquiry giving both a summary, and detailed examples.
2. Summarize or retrieve an existing blog post.
3. Explain technical concepts whenever possible.
4. Provide references for further reading if they exist.

Utilize the blog article meta data listed below as part of your response if applicable.


'''
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='json file of input data')
    parser.add_argument(
            '-m', '--maxlen', type=int,
            default=4096, help='max output len')
    args = parser.parse_args()
    Convert(args.filename, ins=instructions, maxlen=args.maxlen).run()
