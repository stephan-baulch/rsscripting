import logging

def debugLogs():
	logging.basicConfig(
        filename='log.txt', 
        filemode='w', 
        level=logging.DEBUG,
        format='%(asctime)s: %(message)s')

def debug(message):
	logging.debug(message)