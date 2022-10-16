#!/usr/bin/env python3

from datetime import date
import os.path
import os
import sys

APPEND_WORDS = False # when appending words, update a table of contents manually
GEN_FILE = './gen.txt'
GENS_DIR = './gens/'
OUTPUT_DIR = './../_words/'


def get_words():
    with open(GEN_FILE, 'r') as gen:
        lines = gen.readlines()
        return [line.replace('\n', '') for line in lines if len(line) > 1]


def get_head_template(d):
    if APPEND_WORDS:
        return ''
    return '''---
layout: post
title: {0}
---

Words that I added to Anki on {0}.

The contents were automatically generated except notes part.
'''.format(d)


def get_table_of_contents(words):
    if APPEND_WORDS:
        return ''
    result = '# word list\n'
    for word in words:
        id_word = word.lower().replace(' ', '-').replace('.', '').replace('\'', '')
        result = result + '- [{0}](#{1})\n'.format(word, id_word)
    return result + '\n'


def get_words_template(words):
    result = ''
    for word in words:
        item = '''---

# {0}
## definitions
[Cambridge](https://dictionary.cambridge.org/us/dictionary/english/{0})
|
[Wiktionary](https://en.wiktionary.org/wiki/{0}#English)
|
[Weblio](https://ejje.weblio.jp/content_find?query={0}&searchType=exact)
|
[OED](https://www.oed.com/search?q={0})
|
[Images](https://www.google.com/search?tbm=isch&q={0})
|
[Youglish](https://youglish.com/pronounce/{0}/english/us)

## notes
FIXME

'''.format(word)
        result = result + item

    return result


def write_gens(d):
    with open(GEN_FILE, 'r') as gen:
        with open('{}{}.txt'.format(GENS_DIR, d), 'a') as out:
            out.write(gen.read())


def main():
    today = date.today()
    d = today.isoformat()

    if not os.path.exists(GEN_FILE):
        print('Error: gen file {} not found'.format(GEN_FILE), file=sys.stderr)
        sys.exit(0)

    if not os.path.exists(GENS_DIR):
        print('Error: gens directory {} not found'.format(GENS_DIR), file=sys.stderr)
        sys.exit(0)

    post_filename = '{}{}-words.md'.format(OUTPUT_DIR, d)

    if APPEND_WORDS:
        if not os.path.exists(post_filename):
            print('Error: file {} must exist when APPEND_WORDS is True'.format(post_filename), file=sys.stderr)
            sys.exit(0)
    else:
        if os.path.exists(post_filename):
            print('Error: file {} already exists'.format(post_filename), file=sys.stderr)
            sys.exit(0)

    words = get_words()
    if len(words) == 0:
        print('Error: no words are found in file {}'.format(GEN_FILE), file=sys.stderr)
        sys.exit(0)

    template = \
        get_head_template(d) + \
        get_table_of_contents(words) + \
        get_words_template(words)

    with open(post_filename, 'a') as out:
        out.write(template)

    write_gens(d)

    if APPEND_WORDS:
        print('Successfully appended words {} to {}'.format(words, post_filename), file=sys.stderr)
    else:
        print('Successfully wrote words {} to {}'.format(words, post_filename), file=sys.stderr)


if __name__ == '__main__':
    main()
