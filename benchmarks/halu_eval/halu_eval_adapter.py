# flake8: noqa: E501

import os
from typing import Any, Dict, List

from evalscope.api.benchmark import BenchmarkMeta, DefaultDataAdapter
from evalscope.api.dataset import Sample, DatasetDict
from evalscope.api.dataset.loader import LocalDataLoader
from evalscope.api.messages import ChatMessageUser, Content, ContentText
from evalscope.api.metric.scorer import AggScore, SampleScore, Score
from evalscope.api.registry import register_benchmark
from evalscope.benchmarks.halu_eval.halu_eval_instructions import (
    DIALOGUE_INSTRUCTIONS,
    QA_INSTRUCTIONS,
    SUMMARIZATION_INSTRUCTIONS,
)
from evalscope.constants import Tags
from evalscope.utils.logger import get_logger

DESCRIPTION = (
    'HaluEval is a large collection of generated and human-annotated hallucinated samples for evaluating the performance of LLMs in recognizing hallucination.'
)

logger = get_logger()


@register_benchmark(
    BenchmarkMeta(
        name='halu_eval',
        pretty_name='HaluEval',
        tags=[Tags.KNOWLEDGE, Tags.HALLUCINATION, Tags.YES_NO],
        description=DESCRIPTION.strip(),
        dataset_id='halueval_dataset',
        subset_list=['dialogue_samples', 'qa_samples', 'summarization_samples'],
        default_subset='Full',
        metric_list=['accuracy', 'precision', 'recall', 'f1_score', 'yes_ratio'],
        few_shot_num=0,
        eval_split='data',
        prompt_template='{question}'
    )
)
class HaluEvalAdapter(DefaultDataAdapter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_overall_metric = False

    def load_from_disk(self, **kwargs):
        return super().load_from_disk(use_local_loader=True)

    def record_to_sample(self, record: Dict[str, Any]) -> Sample:
        if self.current_subset_name == 'dialogue_samples':
            knowledge = record['knowledge']
            dialogue_history = record['dialogue_history']
            response = record['response']
            hallucination = record['hallucination']
            inputs = f'{DIALOGUE_INSTRUCTIONS}\n\n#知识#: {knowledge}\n#对话历史#: {dialogue_history}\n#回复#: {response}\n#你的判断#:'
        elif self.current_subset_name == 'qa_samples':
            knowledge = record['knowledge']
            question = record['question']
            answer = record['answer']
            hallucination = record['hallucination']
            inputs = f'{QA_INSTRUCTIONS}\n\n#知识#: {knowledge}\n#问题#: {question}\n#答案#: {answer}\n#你的判断#:'
        elif self.current_subset_name == 'summarization_samples':
            document = record['document']
            summary = record['summary']
            hallucination = record['hallucination']
            inputs = f'{SUMMARIZATION_INSTRUCTIONS}\n\n#文档#: {document}\n#摘要#: {summary}\n#你的判断#:'
        else:
            raise ValueError(f'Invalid subset name: {self.current_subset_name}')

        input_text = self.prompt_template.format(question=inputs)
        content_list: List[Content] = [ContentText(text=input_text)]
        answer = str(hallucination).upper()  # 'YES' or 'NO'
        return Sample(
            input=[ChatMessageUser(content=content_list)], target=answer, metadata={
                'answer': hallucination,
            }
        )

    def match_score(self, original_prediction, filtered_prediction, reference, task_state) -> Score:
        score = Score(
            extracted_prediction=filtered_prediction,
            prediction=original_prediction,
        )
        # Check if the reference answer is in the filtered prediction
        result = 1 if reference in filtered_prediction.strip().upper() else 0
        score.value = {'acc': result}
        return score

    def aggregate_scores(self, sample_scores: List[SampleScore]) -> List[AggScore]:
        """
        Custom aggregation to compute accuracy, precision, recall, f1_score, and yes_ratio.
        """

        def compute_metrics(scores: List[SampleScore]):
            tp = fp = tn = fn = 0
            yes_count = 0
            total_count = len(scores)

            for ss in scores:
                gt = ss.sample_metadata['answer'].strip().upper()
                # Get prediction based on score
                pred = gt if ss.score.main_value == 1 else ('NO' if gt == 'YES' else 'YES')
                if pred == 'YES':
                    yes_count += 1
                if pred == 'YES' and gt == 'YES':
                    tp += 1
                elif pred == 'YES' and gt == 'NO':
                    fp += 1
                elif pred == 'NO' and gt == 'NO':
                    tn += 1
                elif pred == 'NO' and gt == 'YES':
                    fn += 1

            accuracy = (tp + tn) / total_count if total_count > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            yes_ratio = yes_count / total_count if total_count > 0 else 0.0

            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'yes_ratio': yes_ratio
            }

        overall_metrics = compute_metrics(sample_scores)
        agg_scores = []
        for metric_name, value in overall_metrics.items():
            agg_scores.append(AggScore(metric_name=metric_name, score=value, num=len(sample_scores), metadata={}))

        return agg_scores
