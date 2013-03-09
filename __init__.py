import subprocess, os, sys, threading, Queue
from collections import namedtuple
import output_parser

handle = subprocess.Popen('java -mx150m -cp stanford-parser.jar: edu.stanford.nlp.parser.lexparser.LexicalizedParser -sentences newline -outputFormat wordsAndTags,penn,typedDependencies englishPCFG.ser -',
	bufsize=1,
	stdin=subprocess.PIPE,
	stdout=subprocess.PIPE,
	stderr=subprocess.PIPE,
	shell=True)

#for returning results the chunk-reader sees between threads
results = Queue.Queue()

def chunk_reader(handle):
	buffered = ''
	triplet = []
	while True:
		line = handle.readline()
		if line.strip() == '':
			if len(triplet) == 2:
				results.put(triplet + [buffered.strip()])
				triplet = []
			else:
				triplet.append(buffered.strip())
			buffered = ''
		else:
			buffered += line

def echo(handle):
	while True:
		line = handle.readline()
		sys.stdout.write(line)

#prevent buffers from being filled
def ignore(handle):
	while True:
		line = handle.readline()

t = threading.Thread(target=chunk_reader, args=(handle.stdout,))
t.daemon = True
t.start()
t = threading.Thread(target=ignore, args=(handle.stderr,))
t.daemon = True
t.start()

Parse = namedtuple('Parse', ['wordlist', 'tree', 'dependency_list'])

def parse(sentence, parse_output=True):
	#sentences are line buffered
	sentence = sentence.replace('\n', ' ').strip()
	#no need to flush this since the handle is line buffered
	handle.stdin.write('%s\n' % sentence)
	if not parse_output:
		return results.get()
	return Parse(*output_parser.parse_triplet(*results.get()))