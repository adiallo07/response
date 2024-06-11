import csv, os, json, time, random
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv
import anthropic
import argparse
from random import shuffle, sample


	
load_dotenv()

def fix_seed(seed):
	# random
	random.seed(seed)

fix_seed(123)


def extract_explanation(text):
	#print ('raw -------->', text)
	lines = text.splitlines()
	if len(lines) >= 2 and lines[-1].startswith("Explanation: "):
		return lines[0], lines[-1][len("Explanation: "):]
	else:
		return text, ""

def decoder_for_claude(input, max_length=512, k=1):
	key = os.getenv("ANTHROPIC_API_KEY")
 
	client = anthropic.Anthropic(api_key=key)
	while True:
		try:

			message = client.messages.create(
			    model="claude-3-opus-20240229",
			    max_tokens=512,
			    temperature=0.0,
			    system="You are a helpful assistant that responds to questions. Imagine you're a human in the situation described by the context. You need to be autonomous in reacting.",
			    messages=[
			        {"role": "user", "content": input}
			    ]
			)

			return extract_explanation(message.content[0].text)
		except Exception as e:
			print(e)
			time.sleep(3)

def decoder_for_gpt4(input, max_length=512, k=1):
	key = os.getenv("OPENAI_API_KEY")
	client = OpenAI(api_key= key) #put your api here

	cnt = 0
	while True:
		try:
			response = client.chat.completions.create(
			model="gpt-4-turbo" ,
			messages=[
				{"role": "system", "content": "You are a helpful assistant that responds to questions. Imagine you're a human in the situation described by the context. You need to be autonomous in reacting."},
				{"role": "user", "content": input}],
			temperature=0.0,
			max_tokens=max_length,
			top_p=1,
			frequency_penalty=0.0,
			presence_penalty=0.0,
			stop=None)
			return extract_explanation(response.choices[0].message.content) 

		except Exception as e:
			print (e)
			time.sleep(3)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--model', help='which model to run')

	args = parser.parse_args()
	model = args.model

	files = ['data/all_questions_v1.json']
	immediate_gpt, immediate_claude = [], []
	week_gpt, week_claude = [], []
	month_gpt, month_claude = [], []
	results_immediate = []
	results_week = []
	results_month = []

	for _f in files:
		with open(_f, 'r') as f:
			data_ = json.load(f)

			for j, data in enumerate(data_):
				sol = [data['solution1'], data['solution2'], data['solution3']]
				exp = [data['explanation1'], data['explanation2'], data['explanation3']]
				context = data['context']

				scenarios = data['scenarios']
				if len(scenarios) >= 3:
					scene = random.sample(scenarios, 3)
				else:
					scene = data['scenarios']
				for s, scenario in enumerate(scene):
					q1 = scenario['question1']
					q2 = scenario['question2']
					q3 = scenario['question3']
					for i, question in enumerate([q1, q2, q3]):
						prompt = "Context: " + context + "\nQuestion: " + question + """ Respond in maximum 10 words with what you think is the most critical remedial action.\nThen, explain your answer in maximum 15 words starting with 'Explanation: '""" #+ "Answer: " 
						
						if 'gpt4' in model:
							answer_gpt, explanation_gpt = decoder_for_gpt4(prompt)
							if i == 0: 
								timeframe = 'immediate'
								results_immediate.append({'id':data['id'], 'timeframe': timeframe, 'question': question, 'explanation_gpt':explanation_gpt ,'explanation_gt':exp[i],'context': context, 'ground_truth': sol[i], 'gpt4': answer_gpt})

							if i == 1: 
								timeframe = 'week'
								results_week.append({'id':data['id'], 'timeframe': timeframe, 'question': question, 'explanation_gpt':explanation_gpt, 'explanation_gt':exp[i], 'context': context, 'ground_truth': sol[i], 'gpt4': answer_gpt})

							if i == 2: 
								timeframe = 'month'
								results_month.append({'id':data['id'], 'timeframe': timeframe, 'question': question, 'explanation_gpt':explanation_gpt, 'explanation_gt':exp[i], 'context': context, 'ground_truth': sol[i], 'gpt4': answer_gpt})

							print (i+1, 'gpt: ', answer_gpt)

						elif 'claude' in model:
							answer_claude, explanation_claude = decoder_for_claude(prompt)
							if i == 0: 
								timeframe = 'immediate'
								results_immediate.append({'id':data['id'], 'timeframe': timeframe, 'question': question, 'explanation_claude': explanation_claude,'explanation_gt':exp[i],'context': context, 'ground_truth': sol[i], 'claude': answer_claude})

							if i == 1: 
								timeframe = 'week'
								results_week.append({'id':data['id'], 'timeframe': timeframe, 'question': question, 'explanation_claude': explanation_claude, 'explanation_gt':exp[i], 'context': context, 'ground_truth': sol[i], 'claude': answer_claude})

							if i == 2: 
								timeframe = 'month'
								results_month.append({'id':data['id'], 'timeframe': timeframe, 'question': question, 'explanation_claude': explanation_claude, 'explanation_gt':exp[i], 'context': context, 'ground_truth': sol[i], 'claude': answer_claude})


							print (i+1, 'claude: ', answer_claude)
						print (i+1, 'ground truth: ', sol[i], '\n\n')







