#!/usr/bin/env python3

import argparse
import openai
import json


class GPT_DataPrep():

    final_output = []

    def __init__(self, filename, data_field='output', n=8,
                 outfile='results.json', model='gpt-4o-mini',
                 batchlen=4, maxtokens=8192, temp=0.7):
        self.filename = filename
        self.outfile = outfile
        self.model = model
        self.maxtokens = maxtokens
        self.temp = temp
        self.data_field = data_field
        self.n = n
        self.batchlen = batchlen
        self.context = '''
### Instruction:
Based on the following extract, generate five instruction-answer pairs.
Each instruction must ask to write about a specific topic contained in
the context.
Each answer must provide a relevant paragraph based on the information
found in the context.
Up to three paragraphs may be provided if the concept needs more
detailed explanation.
Only use concepts from the context to generate the instructions.
Instructions must never explicitly mention a context,
a system, a course, or an extract.
Instructions must be self-contained and general.
Answers must imitate the writing style of the context.

Provide your response in JSON format with the following structure:

[
    {{"instruction": "...", "output": "..."}},
]

### Input:
{}
'''
        return

    def run(self):
        with open(self.filename, 'rt') as fh:
            data = json.load(fh)
        print(f'[*] There are #{len(data)} records to process.')

        messages = []
        for i, line in enumerate(data):
            try:
                if i and not i % self.batchlen:
                    resp = self.query_model(messages)
                    self.process_responses(i, resp)
                    messages = []
                prompt = self.context.format(line[self.data_field])
                messages.append({
                    'role': 'user',
                    'content': prompt})
            except KeyboardInterrupt:
                print('\r\n[+] CTRL-C interrupt!')
                self.write_outfile()
                ans = input('[+] Continue (Y|N)?')
                if len(ans) > 0 and ans.upper()[0] == 'N':
                    break
        self.write_outfile()

    def write_outfile(self):
        with open(self.outfile, 'wt') as ofh:
            print(f'[+] Writing output file [{self.outfile}]')
            ofh.write((json.dumps(self.final_output, indent=4)))

    def process_responses(self, i, resp):
        for j, r in enumerate(resp):
            print(f'[+] Processing #{i:04d}.{j}')
            try:
                content = r.message.content.strip()
                if content.startswith('```json'):
                    output = json.loads(content[7:-3])
                else:
                    output = json.loads(content)
                for k in output:
                    self.final_output.append(k)
            except Exception as e:
                print(f'[-] Error: {e} ({r.message.content.strip()[:30]})')

    def query_model(self, messages):
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.maxtokens,
            temperature=self.temp,
            n=self.n
        )
        return response.choices


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename', default='',
        help='JSON file to read content from')
    parser.add_argument(
        '-o', '--outfile', default='results.json',
        help='JSON results output filename')
    parser.add_argument(
        '-m', '--maxtokens', type=int, default=8192,
        help='Maximum number of tokens to generate')
    args = parser.parse_args()
    GPT_DataPrep(
        args.filename,
        maxtokens=args.maxtokens,
        outfile=args.outfile).run()
