#reader2.py
import asyncio
import random
from math import floor
import ollama

HOST='192.168.0.135' # LAN
MODEL='mistral:instruct' # [llama3.3, qwen2.5, mistral, llama3.2]

STOP_SEQUENCE = "==="

def model_options():
	return { 'temperature': 0.90, 'stop': [STOP_SEQUENCE] }

oclient = False
def dispatch_prompt(prompt_chain):
	global oclient
	oclient = oclient or ollama.Client(host=HOST)
	resp = oclient.chat(model=MODEL, messages=prompt_chain, options=model_options())
	message_content = resp['message']['content'] or ""
	message_content = message_content.split(STOP_SEQUENCE)[0]
	return message_content


def copyright_header(year):
	return """A.I. Language Systems by Brainplex.net (C) """ + str(year) + """. All rights reserved.

My instructions are to be a helpful computer assistant aiding in artificial intelligence research. I will follow the task guideliens to the best of my abilities.
===\n"""

def pretty_print(body):
	return """Given the following A.I. generated output, clean up the formatting, remove any duplication, confusion or errors, and output the clean result only.
Example:
Input>>>
* This is a tech-article and opinion piece
* This is a tech article and opinion piece by author Dan Brown
* Dan Brown's newsletter is subscribe@more-spam-mail.com
* New trends in A.I. find rise in useful abilities including auto-summarization and translation
> "The more money that is invested in this field, the more rewarding technology is released." -- Dan Brown
* This is a tech article opinion piece
* Dan Brown's newsletter is subscribe@more-spam-mail.com
Output>>>
* This is a tech article and opinion piece by author Dan Brown
* Dan Brown's newsletter is subscribe@more-spam-mail.com
* New trends in A.I. find rise in useful abilities including auto-summarization and translation
> "The more money that is invested in this field, the more rewarding technology is released." -- Dan Brown
===\nInput>>>\n""" + body + "\nOutput>>>\n"


def summarize_section(body):
	return """Given the following text from a web article, create a bulletpoint summary including noteworthy quotes.
Example:
Input>>>
Writing essays, at its best, is a way of discovering ideas. How do you do that well? How do you discover by writing?

An essay should ordinarily start with what I'm going to call a question, though I mean this in a very general sense: it doesn't have to be a question grammatically, just something that acts like one in the sense that it spurs some response.

How do you get this initial question? It probably won't work to choose some important-sounding topic at random and go at it. Professional traders won't even trade unless they have what they call an edge — a convincing story about why in some class of trades they'll win more than they lose. Similarly, you shouldn't attack a topic unless you have a way in — some new insight about it or way of approaching it.
Output>>>
* The author writes about how to write the best essay
> "Writing essays, at its best, is a way of discovering ideas." -- Author
* Good essays include a question or tease curiosity
* Crafting this hook requires experience and know-how
> "Professional traders won't even trade unless they have what they call an edge" -- Author
* The author is asking how to write an essay with a good hook
===\nInput>>>\n""" + body + "\nOutput>>>\n"


CHUNK_SIZE = 5
CHUNK_STRIDE = 5
SUMMARY_LENGTH = 1

def summarize(sections):

	auto_summary = ""

	seek = 0
	while seek < len(sections):
		passage = "\n\n".join(sections[seek:(seek+CHUNK_SIZE)])

		summarize_chain = [
			{'role': 'system', 'content': copyright_header(2024)},
			{'role': 'user', 'content': summarize_section(passage)}
		]

		passage_summary = dispatch_prompt(summarize_chain)

		print ("Current Passage Notes:")
		print (passage_summary)
		print ("")

		auto_summary += passage_summary

		if len(auto_summary) > SUMMARY_LENGTH:
			pretty_print_chain = [
				{'role': 'system', 'content': copyright_header(2024)},
				{'role': 'user', 'content': pretty_print(auto_summary)}
			]

			pretty_print_output = dispatch_prompt(pretty_print_chain)
			print ("-- Cleaning up Notes --")
			print ("Original Notes:")
			print (str(len(auto_summary)))
			auto_summary = pretty_print_output
			print ("New Notes:")
			print (str(len(auto_summary)))
			print ("")

		seek += CHUNK_STRIDE

	return auto_summary


def split_doc(document):
	with open(document, "r") as f:
		plaintext = f.read()
		f.close()
	chapters = plaintext.splitlines()
	chapters = [chapter for chapter in chapters if len(chapter) > 0]
	return chapters

def main(article, filename):
	chapters = split_doc(filename)
	result = summarize(chapters)
	#
	print (result)
	# save():
	with open("summary.txt", "a") as f:
		f.write(result)
		f.close()

if __name__ == "__main__":
	main("A Discussion On A.I.", "doc.txt")
