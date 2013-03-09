import subprocess, os, sys, threading, Queue
from collections import namedtuple
import output_parser

includes_dir = os.path.dirname(os.path.abspath(__file__))

parser_path = os.path.join(includes_dir,'stanford-parser.jar')
model_path = os.path.join(includes_dir, 'englishPCFG.ser')

command = 'java -mx150m -cp "%s": edu.stanford.nlp.parser.lexparser.LexicalizedParser -sentences newline -outputFormat wordsAndTags,penn,typedDependencies "%s" -' % (parser_path, model_path)

handle = subprocess.Popen(command,
	bufsize=1,
	stdin=subprocess.PIPE,
	stdout=subprocess.PIPE,
	stderr=subprocess.PIPE,
	shell=True
)

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

#prevent OS buffers from being filled
#and save errors in case something dies
runlog = []
def ignore(handle):
	while True:
		line = handle.readline()
		if len(runlog) > 1000:
			runlog.pop(0)
		runlog.append(line)

t = threading.Thread(target=chunk_reader, args=(handle.stdout,))
t.daemon = True
t.start()
t = threading.Thread(target=ignore, args=(handle.stderr,))
t.daemon = True
t.start()

def checker(h):
	h.wait()
	print 'The parser subprocess has quit!'
	print 'Return code:', h.returncode
	print 'stderr:'
	print ''.join(runlog)

t = threading.Thread(target=checker, args=(handle,))
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