# this is a TraMP configuration file, to set several parameters for TraMP
# all configurations should look like
# option = value

# use an absolute path here for now
tramp_home = "/home/philip/Dropbox/RuPa-Project/TraMP/"

# tag-set that is used for chunking in TraMP. if empty, a standard set of
# ["NN", "NNS", "PRP", "DT", "POS"] is used
tagset = ["NNP", "NNS", "NN", "IN", "DT", "POS", "VBG"]

# paths to several external tools
mxpost_home = tramp_home + "/resources/jmx/"
mxpost_jar = "mxpost.jar"
stanford_home = tramp_home + "/resources/stanfordParser/"
en_gram = tramp_home + "/resources/grammars/englishPCFG.ser.gz"
gtr_home = tramp_home + "/resources/gtr"

# do not use this. for now, this is configured inside aelius itself
#aelius_data = "./resources/aelius_data"

# paths to TraMP's own needed data files
memory = tramp_home + "/resources/memory/memory.shelve"
trans_dict = tramp_home + "/resources/transfer/transferDict"
trans_regex = tramp_home + "/resources/transfer/transferRegex"
trans_trees = tramp_home + "/resources/transfer/transferTrees"
