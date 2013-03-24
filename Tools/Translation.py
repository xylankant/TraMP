# coding: utf-8
from subprocess import Popen, PIPE
from Config import *
from Tagging import *
from Singleton import *

class DictionaryTranslator() :
	__metaclass__ = Singleton
	def __init__(self, dictionary=trans_dict):
		self._dictFile = dictionary
		self._dict = dict()
		with open(self._dictFile) as f:
			for line in f.readlines():
				line = line.strip()
				if line and not line.startswith("#"):
					en,po = line.split("\t")
					enW, enT = en.split("/")
					poW, poT = po.split("/")
					try:
						self._dict[enT][enW][poT].add(poW)
					except KeyError:
						try:
							self._dict[enT][enW][poT] = set([poW])
						except KeyError:
							try:
								self._dict[enT][enW] = dict()
								self._dict[enT][enW][poT] = set([poW])
							except KeyError:
								self._dict[enT] = dict()
								self._dict[enT][enW] = dict()
								self._dict[enT][enW][poT] = set([poW])
	
	def _getNewWord(self, enWord, enPos, poTag):
		add = raw_input("\nATTENTION!\nTranslation missing in Dictionary for\n\t" + enWord + "/" +
			enPos +	"\nto a Portuguese word\n\t*/" + poTag + "\nWould you like to manually add a new dictionary entry? (y/n) ").strip()
		if add == "y":
			new = raw_input("Please enter a new Dictionary entry for " + str(enWord) + 
			": ").strip()
			return new
		return False
	
	def _addToDict(self, enWord, enTag, newWord, newTag):
		try:
			self._dict[enWord][enTag][newTag].add(newWord)
		except KeyError:
			try:
				self._dict[enWord][enTag][newTag] = set([newWord])
			except KeyError:
				try:
					self._dict[enWord][enTag] = dict()
					self._dict[enWord][enTag][newTag] = set([newWord])
				except KeyError:
					self._dict[enWord] = dict()
					self._dict[enWord][enTag] = dict()
					self._dict[enWord][enTag][newTag] = set([newWord])
		f = open(self._dictFile, "a")
		f.write(enWord + "/" + enTag + "\t" + newWord + "/" + newTag + "\n")
		f.close()
				
	def translate(self, enWord, enTag, poTag):
		try:
			return self._dict[enTag][enWord][poTag].__iter__().next()
		except KeyError:
			newWord = self._getNewWord(enWord, enTag, poTag)
			if newWord:
				self._addToDict(enWord, enTag, newWord, poTag)
				return newWord
		return ""
				

class GoogleTranslator() :
	""" This translator uses gtr to translate via google translate
	it is only used as a backup for now """
	
	def __init__ (self):
		""" Class initialiser """
		self._tagger = Tagger(en_gram)
	
	def _correctTranslation(self, trans):
		cor = str(raw_input("\nI have the following translation\n\t" + str(trans) +
		"\nWould you like to manually correct the translation? (y/n) ")).strip()
		if not cor == "y":
			return trans
		else:
			stri = ""
			i = 0
			for item in trans:
				stri += "\n\t" + str(i) + " " + str(item)
				i+=1
			i = int(str(raw_input("\nWhich part would you like to correct by giving the correct Portuguese translation" + stri + "\n? ")).strip())
			t = str(raw_input("\nPlease enter the correct Portuguese translation for each word, in the form word1:tag1, word2:tag2 [...] > ")).strip()
			t = t.replace(" ", "").strip().split(",")
			org = trans.pop(i)
			new = []
			for x in org[:len(org)-1]:
				new.append(x)
			corrected = []
			for wt in t:
				if wt:
					corrected.append(tuple(wt.split(":")))
			new.append(tuple(corrected))
			trans.insert(i, tuple(new))
			return self._correctTranslation(trans)

	def translate(self, chunks):
		print("Google translator called for\n\t" + str(chunks))
		print("gtr_home is " + gtr_home)
		ret = []
		# translate given chunks
		string = ""
		for item in chunks[1:]:
			try:
				(translation,error) = Popen(["ruby", gtr_home + "/gtr", "en", "pt", item[0]], stdout=PIPE).communicate()
				translation = translation.strip().lower()
				tagged = tuple(self._tagger.tag(translation, lang="po"))
				ret.append((item, tagged))
			except Exception:
				return None
			string += item[0]
			string += " "
		string = string.strip()
		print("translating '" + string + "'")
		try:
			(translation,error) = Popen(["gtr", "en", "pt", string], stdout=PIPE).communicate()
			translation = translation.strip().lower()
			tagged = tuple(self._tagger.tag(translation, lang="po"))
			ret.append((chunks, tagged))
		except Exception:
			return None
		ret = self._correctTranslation(ret)
		return ret

