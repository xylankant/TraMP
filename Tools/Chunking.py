# coding: utf-8
from Config import *

class Chunker (object):
	""" chunking a POS-Tagged sentence into chunks we care about """
	
	def __init__ (self, posSet):
		""" Class initialiser """
		self.posSet = posSet
	
	def chunk (self, tagged):
		print("Chunker chunk was called for\n\t" + str(tagged))
		""" chunk a tagged text according to the chunkers set of pos tags """
		chunked = []
		curChunk = []
		# go through list of tagged items, keep track of previous item
		lastWasInPos = False
		for item in tagged:
			word, tag = item
			# we care about this tag
			if tag in self.posSet:
				# collect larger chunk
				if lastWasInPos:
					curChunk.append(item)
				# start new chunk with this item
				else:
					# we collected a chunk we don't care for before; add it to our chunks
					if curChunk:
						chunked.append(tuple(curChunk))
						curChunk = []
					curChunk.append(True)
					curChunk.append(item)
					lastWasInPos = True
			# we don't care about this tag
			else:
				# collect larger chunk
				if not lastWasInPos:
					if not curChunk:
						curChunk.append(False)
					curChunk.append(item)
				# we collected a chunk we do care for before; add it to out chunks
				else:
					if curChunk:
						chunked.append(tuple(curChunk))
						curChunk = []
					curChunk.append(False)
					curChunk.append(item)
					lastWasInPos = False
		# make sure we get everything
		if curChunk:
			chunked.append(tuple(curChunk))
		return tuple(chunked)
		
