# coding: utf-8

from Tools import *
from Config import *

class TraMPer (object):
	""" TraMPer tries to translate (parts of) an English input to Portuguese """
	
	def __init__ (self, mempath=memory, posSet=tagset):
		""" Class initialiser """
		self._tagger = Tagging.Tagger(en_gram)
		self._chunker = Chunking.Chunker(posSet)
		self._memory = Memory.ShelveMemory(mempath)
		self._parser = Parsing.Parser(en_gram)
		self._translator = Translation.GoogleTranslator()
		self._dictTranslator = Translation.DictionaryTranslator(trans_dict)
		self._transferer = Transfer.Transferer(self._dictTranslator, trans_regex, trans_trees)
	
	def translate(self, sentence):
		''' translate a sentence '''
		ret = ""
		# tag and chunk sentence
		print("TraMPer translate was called for\n\t" + sentence)
		tagged = self._tagger.tag(sentence)
		print("TraMPer received tags\n\t" + str(tagged))
		chunkItems = self._chunker.chunk(tagged)
		print("TraMPer received chunks\n\t" + str(chunkItems))
		# check translation memory for exact occurence of chunks
		queryResult = self._memory.query(chunkItems)
		print("TraMPer received query result\n\t" + str(queryResult))
		if queryResult:
			# we have seen that before
			i = 0
			for chunk in chunkItems:
				print(chunk)
				if chunk[0]:
					qItem = queryResult[i]
					print(qItem)
					for word in qItem:
						w,t = word
						ret += w + " "
					i += 1
				else:
					ret += "["
					for w,t in chunk[1:]:
						ret += w + " "
					ret = ret.strip() + "] "
			print("\nTraMP returning translation for\n\t" + sentence + "\n\t" + ret)
			return ret
		else:
			# check transfer for items
			transferedItems = []
			for item in chunkItems:
				if item[0]:
					iResult = self._memory.query(item)
					if iResult:
						transferedItems.append(iResult)
						print("TraMPer got result\n\t" + str(iResult))
						for word in iResult:
							ret += word[0] + " "
						continue
					tItem = self._transferer.transfer(item)
					print("TraMPer received transfered item\n\t" + str(tItem))
					if not tItem:
						translation = self._translator.translate(item)
						print("TraMPer received translation\n\t" + str(translation))
						tItem = translation[-1][1]
						print("TITEM: " + str(tItem))
					transferedItems.append(tItem)
					if tItem:
						for word in tItem:
							ret += str(word[0]) + " "
					else:
						ret += "_ "
					
				else:
					ret += "[" 
					for word,tag in item[1:]:
						ret += word + " "
					ret = ret.strip() + "] "
			# add new sentence to translation memory
			for item in transferedItems:
				if item:
					self._memory.memorize(chunkItems, transferedItems)
					break
		print("\nTraMP returning translation for\n\t" + sentence + "\n\t" + ret)
		return ret

stanford_parser_home = None
global running
running = False

def startJvm():
	import jpype
	import os
	global running
	if not running:
		print("starting jvm with " + stanford_home)
		os.environ.setdefault("STANFORD_PARSER_HOME", stanford_home)#"/home/philip/Dropbox/RuPa-Project/TraMP/Tools/Parsing/stanfordParser/")
		global stanford_parser_home
		stanford_parser_home = os.environ["STANFORD_PARSER_HOME"]
		jpype.startJVM(jpype.getDefaultJVMPath(),
					   "-ea",
					   "-Djava.class.path=%s/stanford-parser.jar" % (stanford_parser_home),)
		running = True 
startJvm()

def exportMXPOST():
	import os
	
		
