stanford_parser_pipe
====================

An interface to the [Stanford Parser](http://nlp.stanford.edu/software/lex-parser.shtml) in Python using pipes.

This module uses `subprocess` to open a pipe to `edu.stanford.nlp.parser.lexparser.LexicalizedParser` and
parse sentences through writing to stdin / reading from stdout. It's a little bit messy but relatively
functional.

The repository includes `englishPCFG.ser`, a model included in the Stanford Parser by default (in the `stanford-parser-2.0.4-models.jar` archive), and `stanford-parser.jar`, which is the main jarfile for the parser. Both of these files are from the
2.0.4 release, which is recent as of March 8th 2013.

Additionally, data for the Stanford dependency hierarchy comes from [Stefanie Tellex
at MIT](http://projects.csail.mit.edu/spatial/Stanford_Parser).

## Documentation

This module has one relevant method: `parse(sentence, parse_output=True)`.

`parse_output` refers not to the parsing of the sentences but the parse of the
output from the parser. The parser is asked for tokens and tags, Penn treebank
form, and the dependency relations. If `False` the parser's output will be returned
as three strings (word/tag, parse tree, and dependency list respectively).

If `True` the output will be munged a bit to put it in a friendlier format
for Python. The result will be a structure of nested tuples, rooted with
a Parse:

```
Parse
	.wordlist = [list of W]
	.tree = nested P objects
	.dependency_list = [list of R]

W (word)
	.index = 0-indexed position in sentence
	.word = original word
	.tag = POS tag

See useful documents on what this is.
R (relation)
	.relation = relationship
	.relation_set = set of relationship + every relation above it in the
		heirarchy
	.governor = word (W) or None for ROOT.
	.dependent = word (W)

See useful documents for what the different tags are.
T (tree?)
	.tag = tag (either a POS or clause tag)
	.children = [list of T or plaintext word]
```

```
>>> import stanford_parser_pipe

>>> stanford_parser_pipe.parse('This one is short.', parse_output=False)
['This/DT one/NN is/VBZ short/JJ ./.', '(ROOT\n  (S\n    (NP (DT This) (NN one))\n    (VP (VBZ is)\n      (ADJP (JJ short)))\n    (. .)))', 'det(one-2, This-1)\nnsubj(short-4, one-2)\ncop(short-4, is-3)\nroot(ROOT-0, short-4)']

>>> stanford_parser_pipe.parse('This one is short.')
Parse(
	wordlist=[
		W(index=0, word='This', tag='DT'),
		W(index=1, word='one', tag='NN'),
		W(index=2, word='is', tag='VBZ'),
		W(index=3, word='short', tag='JJ'),
		W(index=4, word='.', tag='.')
	],
	tree=
		T(tag='ROOT',children=[T(tag='S', children=[T(tag='NP', children=[T(tag='DT', children=['This']), T(tag='NN', children=['one'])]), T(tag='VP', children=[T(tag='VBZ', children=['is']), T(tag='ADJP', children=[T(tag='JJ', children=['short'])])]), T(tag='.', children=['.'])])]),
	dependency_list=[
		R(relation='det', relation_set=set(['dep', 'det', 'mod']), governor=W(index=1, word='one', tag='NN'), dependent=W(index=0, word='This', tag='DT')),
		R(relation='nsubj', relation_set=set(['dep', 'arg', 'subj', 'nsubj']), governor=W(index=3, word='short', tag='JJ'), dependent=W(index=1, word='one', tag='NN')),
		R(relation='cop', relation_set=set(['dep', 'cop', 'aux']), governor=W(index=3, word='short', tag='JJ'), dependent=W(index=2, word='is', tag='VBZ')),
		R(relation='root', relation_set=set(['root']), governor=None, dependent=W(index=3, word='short', tag='JJ'))
	]
)
```

## Useful documents

[What are dependencies?](http://nlp.stanford.edu/software/stanford-dependencies.shtml)
[Dependencies manual](http://nlp.stanford.edu/software/dependencies_manual.pdf)
[Penn treebank tags](http://bulba.sdsu.edu/jeanette/thesis/PennTags.html)

## Contact

[Made by Sam Birch](http://sbirch.net)

## TODO

- Slashes are escaped into \\/
- Words in parse tree should be word references (DFS traversal of parse tree should yield word order?)