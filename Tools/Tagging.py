# coding: utf-8
#import nltk
#import nltk.corpus
#from nltk.corpus import brown
#from nltk.corpus import treebank
#import nltk.tag
#from nltk import tokenize
#from nltk import word_tokenize
#from nltk import pos_tag
from Aelius.AnotaCorpus import anota_sentencas
from Aelius.Extras import carrega
from Aelius.Toqueniza import TOK_PORT_MM as tok
from Parsing import *
from Config import *
import os

class Tagger (object):
	""" Tags an english or portuguese sentence (also does tokenizing). default is english"""
	
	def __init__ (self, model):
		# portuguese tagger is Maximum Entropy Markov Model
		self._mxpost = carrega("AeliusMaxEntMM")
		self.parser = Parser(model)
		# self._mxpost = mxpost_home
		
		try:
			classpath = os.environ["CLASSPATH"]
			if not mxpost_home in classpath:
				classpath += ":" + mxpost_home + mxpost_jar
			os.environ["CLASSPATH"] = classpath
		except Exception:
			os.environ["CLASSPATH"] = mxpost_home + mxpost_jar
		try:
			path = os.environ["PATH"]
			if not mxpost_home in path:
				path += ":" + mxpost_home
			os.environ["PATH"] = path
		except Exception:
			os.environ["PATH"] = mxpost_home
		
		print("classpath is " + os.environ["CLASSPATH"])
		print("path is " + os.environ["PATH"])

	def __concat(self, term, preTerm):
		return (str(term.value()), str(preTerm.value()))
		
	def tag (self, sentence, lang="en"):
		print("Tagger tag was called for\n\t" + sentence + "\nlang: " + lang)
		# tag an english sentence, using python nltk
		if lang == "en":
			#text = nltk.word_tokenize(sentence)
			#return nltk.pos_tag(text)
			tree = self.parser.parse(sentence)
			preTerms = tree.preTerminalYield()
			terms = tree.yield_()
			return map(self.__concat, terms, preTerms)
		# tag a portuguese sentence, using aelius
		if lang == "po":
			sentence = sentence.decode("utf-8")
			toks = tok.tokenize(sentence)
			return anota_sentencas([toks],self._mxpost,"mxpost",separacao_contracoes=False)[0]
