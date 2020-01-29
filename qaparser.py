# ref@w-index.q-number.q/a
from collections import namedtuple
import sys


REVEAL_HEAD = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

    <link rel="stylesheet" href="reset.css">
    <link rel="stylesheet" href="reveal.css">
    <link rel="stylesheet" href="black.css">

        <!-- Printing and PDF exports -->
    <script>
        var link = document.createElement( 'link' );
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : 'css/print/paper.css';
        document.getElementsByTagName( 'head' )[0].appendChild( link );
    </script>
</head>
<body>
    <div class="reveal">
        <div class="slides">"""

REVEAL_END = """</div>
</div>

<script src="reveal.js"></script>

<script>
// More info about config & dependencies:
// - https://github.com/hakimel/reveal.js#configuration
// - https://github.com/hakimel/reveal.js#dependencies
Reveal.initialize();
/*Reveal.initialize({
    dependencies: [
        { src: 'plugin/markdown/marked.js' },
        { src: 'plugin/markdown/markdown.js' },
        { src: 'plugin/notes/notes.js', async: true },
        { src: 'plugin/highlight/highlight.js', async: true }
    ]
}); */
</script>
</body>
</html>
"""

Question = namedtuple('Question', ['wref', 'qnum', 'type', 'contentref', 'content'])

def parse_question_address(line):
    address, content = line.split(' ', maxsplit=1)
    ref, qdata = address.split('@', maxsplit=1)
    qparts = qdata.split('.')
    return Question([int(y) for y in qparts[0].split('-')], int(qparts[1]), qparts[2], ref, content)

def read_af_text_line(line):
    address, content = line.split(' ', maxsplit=1)
    return (address, content)

def read_questions(fpath):
    out = []
    with open(fpath, 'r', encoding="UTF-8") as f:
        for l in f:
            line = l.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            out.append(parse_question_address(line))
    return out

def read_af_text(fpath, line_refs):
    out = {}
    with open(fpath, 'r', encoding="UTF-8") as f:
        for l in f:
            line = l.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            ref, content = line.split(' ', maxsplit=1)
            if ref in line_refs:
                out[ref] = content
    return out

def build_q_ref(q,t):
    return f"{q.contentref}@{'-'.join([str(x) for x in q.wref])}.{q.qnum}.{t}"

def swap_type(t):
    if t == 'a':
        return 'q'
    else:
        return 'a'

def pair_q_and_a(qs):
    out = []
    answers = [x for x in qs if x.type == 'a']
    questions = [x for x in qs if x.type == 'q']
    for q in questions:
        ref = build_q_ref(q, 'q')
        q_answers = [x for x in answers if build_q_ref(x, 'q') == ref]
        out.append((q, q_answers))
    return out

def reveal_slide(q, answers, text, bold_target_words):
    out = ['']
    for a in answers:
        if len(out) < 1:
            out.append('\t\t<li><em>' + a.content + '</em></li>')
        else:
            out.append(out[len(out) - 2] + '\n' + '\t\t<li><em>' + a.content + '</em></li>')

    return '\n'.join([
    f"""<section>
    <p style="font-size:1em;margin-bottom:1em;">{text}</p>
    <p><strong>{q.content}</strong></p>
    <ul>
    {a}
    </ul>
    </section>""" for a in out])

def reveal_output(qandas, text_lines, bold_target_words=False):
    print(REVEAL_HEAD)
    for t in text_lines.keys():
        qs = [(q, a) for (q,a) in qandas if q.contentref == t]
        text = text_lines[t]
        if len(qs) > 1:
            print("<section>")
            for q,a in qs:
                if bold_target_words:
                    words= text.split(' ')
                    if len(q.wref) > 1:
                        targeted_words = ' '.join(words[q.wref[0]:q.wref[1] + 1])
                        print(reveal_slide(q,a,text.replace(targeted_words, f"<strong>{targeted_words}</strong>"), bold_target_words))
                    else:
                        targeted_words = words[q.wref[0]]
                        print(reveal_slide(q,a,text.replace(targeted_words, f"<strong>{targeted_words}</strong>"), bold_target_words))
                else:
                    print(reveal_slide(q,a, text, bold_target_words))
            print("</section>")
        else:
            for q,a in qs:
                if bold_target_words:
                    words= text.split(' ')
                    if len(q.wref) > 1:
                        targeted_words = ' '.join(words[q.wref[0]:q.wref[1] + 1])
                        print(reveal_slide(q,a,text.replace(targeted_words, f"<strong>{targeted_words}</strong>"), bold_target_words))
                    else:
                        targeted_words = words[q.wref[0]]
                        print(reveal_slide(q,a,text.replace(targeted_words, f"<strong>{targeted_words}</strong>"), bold_target_words))
                else:
                    print(reveal_slide(q,a, text, bold_target_words))
    print(REVEAL_END)

def markdown_output(qandas, text_lines, bold_target_words=False, group_questions_by_text=True):
    if group_questions_by_text:
        for t in text_lines.keys():
            qs = [(q, a) for (q,a) in qandas if q.contentref == t]
            text = text_lines[t]
            print("## " + text)
            print()
            for q, answers in qs:
                print("Q: " + q.content)
                print()
                for a in answers:
                    print(f"* {a.content}")            
                print()
            print()
    else:
        for q, answers in qandas:
            text = text_lines[q.contentref]
            words= text.split(' ')
            if bold_target_words:
                if len(q.wref) > 1:
                    targeted_words = ' '.join(words[q.wref[0]:q.wref[1] + 1])
                    print("## " + text.replace(targeted_words, f"**{targeted_words}**"))
                else:
                    targeted_words = words[q.wref[0]]
                    print("## " + text.replace(targeted_words, f"**{targeted_words}**"))
            else:
                print("## " + text)
            print()

            print("Q: " + q.content)
            print()
            if len(answers) > 0:
                print("A:")
                print()
                for a in answers:
                    print(f"* {a.content}")
                    
            print()

if __name__ == '__main__':
    import argparse
    def str2bool(v):
        if isinstance(v, bool):
           return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    my_parser = argparse.ArgumentParser(prog="af-question-generator",
    usage='%(prog)s [options] question-path text-path')
    my_parser.add_argument("Question", metavar="question-path", type=str, help="path to question file")
    my_parser.add_argument("Text", metavar="text-path", type=str, help="path to 'text' file")
    my_parser.add_argument('--show-text', action='store', type=str2bool, default='False', help="repeat the text for each qustion (does not apply to reveal output)")
    my_parser.add_argument('--bold-text', action='store', type=str2bool, default='False', help="True to bold words in the text the question pertains to")
    my_parser.add_argument('--format', action='store', type=str, default='md', help="md for markdown (default); reveal for reveal.js output.")

    args = my_parser.parse_args()

    questions = read_questions(args.Question)
    refs = [x.contentref for x in questions]
    text_lines = read_af_text(args.Text, refs)
    paired_qs = pair_q_and_a(questions)
    if args.format.lower() == "reveal":
        reveal_output(paired_qs, text_lines, bool(args.bold_text) )
    else:
        markdown_output(paired_qs, text_lines, bool(args.bold_text), not bool(args.show_text))



#print(text_lines)
