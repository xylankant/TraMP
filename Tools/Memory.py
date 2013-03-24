# coding: utf-8
from Config import *
import shelve

class ShelveMemory ():
	""" this is a persistent memory using a shelve object """
	def __init__ (self, mempath):
		""" mempath: path to a shelve file on disk """
		self._memory = shelve.open(mempath)
	
	def query(self, q):
		# return a translation if the english sequence has been seen before, None otherwise
		print("ShelveMemory query was called for\n\t" + str(q))
		try:
			ret = self._memory[str(q)]
			return ret
		except KeyError:
			return None
	
	def memorize(self, key, val):
		print("ShelveMemory memorize\n\t" + str(key) + "\n\t" + str(val))
		# add a new translation to memory
		if not None in val:
			self._memory[str(key)] = val
		i = 0
		for j in range(len(key)):
			if key[j][0]:
				if val[i]:
					foo = [False for x in val[i] if x[0] == "_"]
					if not False in foo:
						self._memory[str(key[j])] = val[i]
				i += 1
		print("shelve looks like this\n\t" + str(self._memory))
