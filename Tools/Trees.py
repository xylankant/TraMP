# coding: utf-8
import jpype
import re
from Config import *

class TreeFactory ():
	""" Class doc """
	
	def __init__ (self):
		""" Class initialiser """
		self.package_tree = jpype.JPackage("edu.stanford.nlp.trees")
		self.package = jpype.JPackage("edu.stanford.nlp")
		

	def fromString (self, string):
		""" Function doc """
		return self.package_tree.Tree.valueOf(string)


class TreeMatcher():
	
	def __init__ (self):
		self._pathFinder = PathFinder()
	
	def _equals (self, orgTree, parseTree):
		orgTreeString = re.sub(r":[0-9]+\s_", "", str(orgTree))
		parseTreeString = re.sub(r":[0-9]+\s_", "", str(parseTree))
		orgTreeString = re.sub(r":[0-9]+", "", orgTreeString)
		parseTreeString = re.sub(r":[0-9]+", "", parseTreeString)
		return orgTreeString == parseTreeString
		
	def _getPreTermTree (self, tree):
		t = tree.deepCopy()
		if t.isPreTerminal():
			t.removeChild(0);
		else:
			for i in range(len(t.children())):
				child = t.removeChild(i)
				t.addChild(i, self._getPreTermTree(child))
			
		return t;
	
	def matches (self, orgTree, parseTree):
		print("Trees matches called for\n\t" + str(orgTree) + "\n\t" + str(parseTree))
		if self._equals(orgTree, parseTree):
			print("\tTrees match!")
			oTreeCopy = orgTree.deepCopy()
			for path in self._pathFinder.getVarPaths(oTreeCopy):
				oVar = self._pathFinder.getTreeAtPath(oTreeCopy, path)
				v = str(oVar.label().value()).find(":")
				oVar.label().setValue(str(oVar.label().value())[:v])
			return (oTreeCopy, 1.0)
		orgPreTermTree = self._getPreTermTree(orgTree)
		parsePreTermTree = self._getPreTermTree(parseTree)
		if self._equals(orgPreTermTree, parsePreTermTree):
			print("\tpreTermTrees match")
			orgTreeCopy = orgTree.deepCopy()
			score = 1.0
			paths = self._pathFinder.getVarPaths(orgTreeCopy)
			for path in paths:
				oVar = self._pathFinder.getTreeAtPath(orgTreeCopy, path)
				oVarWord = oVar.children()[0]
				pVarWord = self._pathFinder.getTreeAtPath(parseTree, path).children()[0]
				if not str(oVarWord) == str(pVarWord):
					oVar.removeChild(0)
					score -= 1.0/len(paths)
				else:
					v = str(oVar.label().value()).find(":")
					oVar.label().setValue(str(oVar.label().value())[:v])
			return (orgTreeCopy, score)
		print("\tno matches!")
		return False

class PathFinder():
	def __init__ (self):
		pass
	
	def getVarPaths (self, tree, path="."):
		paths = []
		if ":" in str(tree.label().value()):
			paths.append(path)
		else:
			for i in range(len(tree.children())):
				paths.extend(self.getVarPaths(tree.children()[i], path + str(i)))
		return paths
	
	def getTreeAtPath(self, tree, path):
		if not path or path == ".":
			return tree
		if len(path) > 1:
			path = path[1:]
		child = None
		if "." in path:
			child = int(path[0:path.find(".")])
			path = path[path.find("."):]
		else:
			child = int(path)
			path = ""
			
		return self.getTreeAtPath(tree.children()[child], path)
	
	def getPathToVar(self, tree, var):
		for path in self.getVarPaths(tree):
			st = self.getTreeAtPath(tree, path)
			if int(st.label().value().split(":")[1]) == var:
				return path 
