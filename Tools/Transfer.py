# coding: utf-8
from copy import deepcopy
from re import *
from Trees import *
from Parsing import *
from Config import *
from Translation import DictionaryTranslator

class Transferer (object):
	""" Class doc """

	def __init__ (self, dictionaryTranslator, transReg, transTrees):
		""" Class initialiser """
		self._regexpTrans = RegexTransferer(transReg, dictionaryTranslator)
		self._treeTrans = TreeTransferer(transTrees, dictionaryTranslator)
		self._parser = Parser(en_gram)
		
	def transfer (self, item):
		print("Transferer transfer called for\n\t" + str(item))
		rItem = self._regexpTrans.transfer(item[1:])
		print("Transferer received regex-transfered item\n\t" + str(rItem))
		if rItem:
			return rItem
		else:
			string = ""
			for tup in item[1:]:
				string += tup[0]
				string += " "
			tItem = self._treeTrans.transfer(self._parser.parse(string.strip()))
			print("Transferer received tree-transfered item\n\t" + str(tItem))
			if tItem:
				return tItem

class RegexTransferer() :
	""" Class doc """
	
	def __init__ (self, regFile, dictionaryTranslator):
		""" Class initialiser """
		self._translator = dictionaryTranslator
		self._patterns = []
		with open(regFile) as f:
			for line in f.readlines():
				line = line.strip()
				if not line or line.startswith("#"):
					continue
				patternList = []
				poOrder = []
				en,po = line.split("=>")
				enChunks = en.strip().split(" ")
				poChunks = po.strip().split(" ")
				for chunk in enChunks:
					words, pos = chunk.split("/")
					pattern = ""
					if words == "*":
						pattern = ".*"
					else:
						for word in words.replace("(","").replace(")","").split("|"):
							pattern += "\\A" + word.strip() + "\\b|"
						pattern = pattern[:len(pattern)-1]
					patternList.append((pattern,pos))
				for chunk in poChunks:
					word, pos = chunk.split("/")
					poOrder.append((word,pos))
				self._patterns.append((patternList,poOrder))
	
	def _match(self, pattern, token):
		pWord, pPos = pattern
		tWord, tPos = token
		if not "_" in pPos and not pPos == tPos:
			return False
		if "_" in pPos and not pPos.split("_")[0] == tPos:
			return False
		
		if re.match(pWord, tWord):
			return True
		return False
	
	def _transfer(self, pattern, english):
		en,po = pattern
		po = deepcopy(po)
		transfered = []
		for poChunk in po:
			if not "_" in poChunk[1]:
				transfered.append(poChunk)
				continue
			poTag, poInt = poChunk[1].split("_")
			for i in range(len(en)):
				enChunk = en[i]
				if not "_" in enChunk[1]:
					continue
				enTag, enInt = enChunk[1].split("_")
				if not poInt == enInt:
					continue
				else:
					enWord, enTag = english[i]
					translation = self._translator.translate(enWord, enTag, poTag)
					if translation:
						transfered.append((translation, poTag))					
		return transfered
	
	def transfer(self, tokens):
		print("RegexTransferer transfer called for\n\t" + str(tokens))
		for pattern in self._patterns:
			print("pattern\n\t" + str(pattern))
			if not len(pattern[0]) == len(tokens):
				continue
			match = map(self._match, pattern[0], tokens)
			print("match returned\n\t" + str(match))
			if not False in match:
				transfered = self._transfer(pattern, tokens)
				return transfered
				
		return False

class TreeTransferer():
	""" Class doc """
	
	def __init__ (self, transferTreeFile, dictionaryTranslator):
		""" Class initialiser """
		self._matcher = TreeMatcher()
		self._treeFile = transferTreeFile
		self._trees = dict()
		self._treeFac = TreeFactory()
		self._pathFinder = PathFinder()
		self._translator = dictionaryTranslator
		with open(transferTreeFile) as f:
			for line in f.readlines():
				line = line.strip()
				if line and not line.startswith("#"):
					en, po = line.split("=>")
					self._trees[self._treeFac.fromString(en)] = self._treeFac.fromString(po)

	def _transfer (self, orgTree, transTree, enTree, substitute=False):
		if substitute:
			orgTreeCopy = orgTree.deepCopy()
			for varPath in self._pathFinder.getVarPaths(orgTreeCopy):
				varTree = self._pathFinder.getTreeAtPath(orgTreeCopy, varPath)
				enWord = self._pathFinder.getTreeAtPath(enTree, varPath)
				varTree.removeChild(0)
				varTree.addChild(enWord.children()[0].deepCopy())
			return orgTreeCopy
		
		poTree = self._trees[orgTree].deepCopy()
		if not ":" in str(transTree):
			return poTree
		transVarPaths = self._pathFinder.getVarPaths(transTree)
		for path in transVarPaths:
			transSubTree = self._pathFinder.getTreeAtPath(transTree, path)
			var = int(str(transSubTree.label().value()).split(":")[1])
			enSubTree = self._pathFinder.getTreeAtPath(enTree, path)
			enPos = str(enSubTree.label().value())
			enWord = str(enSubTree.children()[0])
			poPath = self._pathFinder.getPathToVar(poTree, var)
			poSubTree = self._pathFinder.getTreeAtPath(poTree, poPath)
			poTag = str(poSubTree.label().value()).split(":")[0]
			translation = self._translator.translate(enWord, enPos, poTag)
			if translation:
				poSubTree.removeChild(0)
				poSubTree.addChild(self._treeFac.fromString("(" + translation + ")"))
		return poTree

	def transfer (self, enTree):
		print("TreeTransferer transfer called for\n\t" + str(enTree))
		bestMatch = (None, -1.0)
		matchTree = None
		for tree in self._trees:
			match = self._matcher.matches(tree, enTree)
			if match and match[1] > bestMatch[1]:
				print("TreeTransferer new best matching tree\n\t" + str(match[0]))
				print("\tscore: " + str(match[1]))
				bestMatch = match
				matchTree = tree
		print("TreeTransferer best matching tree is\n\t" + str(bestMatch[0]))
		print("\tscore: " + str(bestMatch[1]))
		if bestMatch[0]:
			translation = self._transfer(matchTree, bestMatch[0], enTree)
			if bestMatch[1] < 1.0:
				newKey = self._transfer(matchTree, matchTree, enTree, substitute=True)
				self._trees[newKey] = translation
				with open(self._treeFile, "a") as f:
					f.write(str(newKey) + " => " + str(translation) + "\n")
			return map(lambda x,y: (x.value(), y.value()), translation.yield_(), translation.preTerminalYield())
				
		return False
