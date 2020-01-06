# (c) Lauritz Holtmann, Jan 2020
#
# Crawl and search URLs recursively and check their response codes
# (aim to find hidden API endpoints in embedded scripts + unauthenticated access to sensitive data)

# ToDo: Implement blacklist for URLs (important when recursively searching for URLs) || eventually implement whitelist, too
# ToDo: Implement argparse CLI interface
# ToDo: Implement proper base URL handling on recursions >1

import requests
import re
import time
import numpy

# Regular Expressions
url_regex = r"http?[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
url_path_regex = r"/[A-Za-z\.0-9_/\-\+]?[A-Za-z\.0-9_/\-\+]+[^\">']"
closing_tag_regex = r"</?[A-Za-z0-9]{0,20}>"

# Todo (s.o.): Implement CLI interface for following variables using argparse
search_url = "https://security.lauritz-holtmann.de"
check_status = False
save_output = True
recursion_level = 1 # minimum 1: when choosing 1, only the currently submitted url is treated and crawled

def requestHandler(url):
	# ToDo: Implement blacklist
	try:
		# handle relative URLs
		# ToDo: On recursions >1 the base url may vary from our initial search URL - check!
		if url[0] == "/":
			url = search_url + url

		r = requests.get(url)
		return r
	except:
		print(" [+] Could not request {}".format(url))

def crawlUrl(url):
	r = requestHandler(url)
	return r.text

def checkUrl(url):
	r = requestHandler(url)
	return r.status_code

def findUrlsInString(string):
	global url_regex, url_path_regex, closing_tag_regex

	# strip closing html tags in order to prevent false positives
	stripped = re.sub(closing_tag_regex, '', string)

	# search urls and remove them from string in order to prevent duplicates
	found = re.findall(url_regex, stripped)
	stripped = re.sub(url_regex, '', stripped)

	# search url paths (relative urls)
	found += re.findall(url_path_regex, stripped)

	return found
	
def main():
	global search_url, search_url, recursion_level

	urls = (search_url,)

	# core crawling logic
	for i in range(0, recursion_level):
		for cur in urls:
			response = crawlUrl(cur)
			urls += tuple(findUrlsInString(response))
			urls = numpy.unique(urls)
		print(urls)

	# check status_code of found urls
	if(check_status):
		for cur in urls:
			status = checkUrl(cur)
			print("[*] Crawled {}, got {}".format(cur, status))

	# save found urls to file, add base URL if needed
	if(save_output):
		output = ""
		for cur in urls:
			# ToDo: Be careful if base url is not equal to initial url, may vary in recursions >1
			if cur[0] == "/":
				cur = search_url + cur
			output += cur + "\n"
		with open("{}.txt".format(int(time.time())), "w+") as f:
			f.write(output)

if __name__ == '__main__': 
	main()