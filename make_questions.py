import csv, os, json, time, re
from spellchecker import SpellChecker
from openai import OpenAI
from dotenv import load_dotenv
	
load_dotenv()

example_dictionary = {"problem":"getting myself to safety","resource":"ensuring i call 911 and stay far away from the fire","solution1":"move as fast as possible away from the fire","solution2":"get fire fighters to evaluate and stop the fire","solution3":"the fire should be out within 1 month, put preventive measures in place","explanation1":"Life is important, staying away from life reduces the risk to getting injured in the fire","explanation2":"stopping the fire is important","explanation3":"Preventive measures will ensure the fire does not come back", "incident":"wildfire, on fire", "place":"coast, mountain, forest"}
example_response = {
  "problem": "getting myself to safety",
  "missing resource": "ensuring I call 911 and stay far away from the fire",
  "scenarios": [
	{
	  "incident": "wildfire",
	  "place": "forest",
	  "question1": "If you encounter a wildfire in a forest, what's the most critical action to take immediately to ensure your safety?",
	  "question2": "After escaping a wildfire in a forest, what's the most important step to take after a week to ensure the fire is contained?",
	  "question3": "A month after a wildfire devastated a forest, what preventative measures can you take to minimize the risk of future fires?"
	},
	{
	  "incident": "on fire",
	  "place": "mountain",
	  "question1": "What's the essential first step to take if you find yourself caught on fire while hiking on a mountain?",
	  "question2": "After escaping a fire situation on a mountain, what's the crucial action to take after a week to ensure the fire is extinguished?",
	  "question3": "One month after a fire ravaged a mountain region, what preventative measures can be implemented to minimize the risk of future fires?"
	},
	{
	  "incident": "wildfire",
	  "place": "coast",
	  "question1": "If you encounter a wildfire near the coast, what immediate action should you take to prioritize your safety?",
	  "question2": "After evacuating from a wildfire on the coast, what's the most important step a week later to ensure the fire is under control?",
	  "question3": "A month after a wildfire swept through a coastal area, what preventative measures can be established to minimize the risk of future wildfires?"
	}
  ]
}

example = 'JSON: ' + str(example_dictionary) + '\n\nAnswer: ' + str(example_response)

def get_results(csv_file):
	PATH = csv_file
	with open(PATH, "r") as f:
		extracted_data = json.load(f)

	return (extracted_data)


def decoder_for_gpt4(input):
	key = os.getenv("OPENAI_API_KEY")
	client = OpenAI(api_key= key) #put your api here

	while True:
		try:
			response = client.chat.completions.create(
			model="gpt-4-turbo" ,
			messages=[
				{"role": "system", "content": "You are a helpful assistant that generates questions."},
				{"role": "user", "content": input}],
			temperature=0.8,
			max_tokens=2048,
			top_p=1,
			frequency_penalty=0.0,
			presence_penalty=0.0,
			stop=None)
			return response.choices[0].message.content 

		except Exception as e:
			time.sleep(3)


def make_questions(infile, outfile):
	all_questions = []
	annotations = get_results(infile)#[0]]

	print(len(annotations))

	all_questions = []
	not_done = []
	_prompt = 'Example: \n' + str(example) + '\n\n' + """You are given a JSON. 1, 2, and 3 correspond to these timeframes: immediately,  after 1 week, after 1 month. Use the example given for guidance."""
	_prompt = _prompt + '\n' + """First, create all the combinations of incident and place values. If place is an empty string, ommit it. Second, create natural, creative and realistic questions concerning the problem, one for each timeframe for which the missing resource is the answer. The question has to ask about remedial actions and responses. Then, paraphrase some of the generated questions (not all of them) (in particular the place if available and timeframes (for example, one month can be transformed in few weeks etc., a week into few days)) to improve the fluidity and the diversity of the questions. Do not mention or hint at the solutions nor the explanations in the generated question. Pay attention to follow the instructions and generate one question per timeframe. Answer in a plain JSON format without any Markdown or code block formatting."""
	
	for i, annotation in enumerate(annotations):
		prompt = _prompt + '\n\n' + 'JSON: \n' + str(annotation) + '\n'

		question = (decoder_for_gpt4(prompt))
		try:
			question = eval(question)
			question['id'] = annotation['id']
			if 'solution1' in annotation:
				question['solution1'] = annotation['solution1']
			if 'solution2' in annotation:
				question['solution2'] = annotation['solution2']
			if 'solution3' in annotation:
				question['solution3'] = annotation['solution3']

			if 'explanation1' in annotation:
				question['explanation1'] = annotation['explanation1']
			if 'explanation2' in annotation:
				question['explanation2'] = annotation['explanation2']
			if 'explanation3' in annotation:
				question['explanation3'] = annotation['explanation3']

			all_questions.append(question)
		except SyntaxError:
			continue 

	with open(outfile, 'w+', encoding='utf-8') as f:
		print ('Number of questions: ', len(all_questions))
		json.dump(all_questions, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
	infile = "raw/all_annotations_v1.json"
	outfile = "data/all_questions_v1.json"
	make_questions(infile, outfile)


