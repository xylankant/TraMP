# coding: utf-8
import jpype
from Config import *
from Singleton import *

class Parser ():
	""" Class doc """
	__metaclass__ = Singleton
	def __init__ (self, model=en_gram):
		""" Class initialiser """
		self.package_lexparser = jpype.JPackage("edu.stanford.nlp.parser.lexparser")
		self.package = jpype.JPackage("edu.stanford.nlp")
		self.parser = self.package_lexparser.LexicalizedParser.getParserFromSerializedFile(model)

	def parse (self, sentence):
		""" Function doc """
		print("Parser parse was called for\n\t" + sentence)
		parsed = self.parser.apply(sentence)
		print("parsed\n\t" + str(parsed))
		lbl = parsed.label().value()
		while lbl == "ROOT" or lbl == "FRAG":
			parsed = parsed.children()[0]
			lbl = parsed.label().value()
		return parsed
