from evaluate import load
import json
import numpy as np
import argparse

def bertscore(prediction, reference):

	bertscore = load("bertscore")
	results = bertscore.compute(predictions=prediction, references=reference, model_type="microsoft/deberta-xlarge-mnli")
	P, R, F1 = results['precision'], results['recall'], results['f1']

	# Return the scores as a dictionary
	return {'precision': np.mean(P), 'recall': np.mean(R), 'f1': np.mean(F1)}


def bleurt_f(prediction, reference):
	bleurt = load("bleurt", module_type="metric", checkpoint="bleurt-base-128")
	results = bleurt.compute(predictions=prediction, references=reference)
	return results

def sacrebleu(prediction, reference):
	bleurt = load("sacrebleu")
	results = bleurt.compute(predictions=prediction, references=reference, lowercase=True)
	return results['score']


def evaluate(time, model, infile):
	generated, refs = [], []
	with open(infile, 'r') as infile:
		results = json.load(infile)
		for data in results:
			#gpt_ = data[model].lower()
			#gt = data['ground_truth'].lower()

			gpt_ = data['gpt_ans'].lower()
			gt = data['gt_ans'].lower()

			generated.append(gpt_)
			refs.append(gt)

		
	bleu = bleurt_f(generated, refs)
	bs = bertscore(generated, refs)
	sb = sacrebleu(generated, refs)

	print (f"BLEURT score:  {np.mean(bleu['scores']):.2f}")
	print (f"Sacrebleu score: {np.mean(sb):.2f}")
	print(f"BERTScore Precision: {bs['precision'].mean():.2f}, Recall: {bs['recall'].mean():.2f}, F1: {bs['f1'].mean():.2f}")


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--time', help='which timeframe to evaluate')
	parser.add_argument('--model', help='which model to evaluate')

	args = parser.parse_args()
	timef = args.time
	model = args.model

	infile = "results/res_immediate.json"

	evaluate(timef, model, infile)
