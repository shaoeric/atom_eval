import os
import re
from typing import Any, Dict

from evalscope.api.benchmark import BenchmarkMeta, DefaultDataAdapter
from evalscope.api.dataset import DatasetDict, LocalDataLoader, Sample
from evalscope.api.evaluator import TaskState
from evalscope.api.metric import Score
from evalscope.api.registry import register_benchmark
from evalscope.constants import Tags
from evalscope.utils.logger import get_logger

logger = get_logger()

# TEMPLATE_0SHOT_EN = """Please read the following text and answer the question below.

# <text>
# {context}
# </text>

# {question}

# Format your response as follows: "Therefore, the answer is (insert answer here)"."""

TEMPLATE_0SHOT_ZH = """请阅读以下文本并回答问题。

<text>
{context}
</text>

{question}

请按以下格式回答："因此，答案是（在此处插入答案，不需要括号、单位等）"。"""


@register_benchmark(
    BenchmarkMeta(
        name='FRAMES',
        pretty_name='FRAMES',
        tags=[Tags.REASONING, Tags.LONG_CONTEXT],
        description=
        'FRAMES is a comprehensive evaluation dataset designed to test the capabilities of Retrieval-Augmented Generation (RAG) systems across factuality, retrieval accuracy, and reasoning.',  # noqa: E501
        dataset_id='frames_dataset',
        subset_list=['frames_en', 'frames_zh'],
        metric_list=['acc'],
        prompt_template=TEMPLATE_0SHOT_ZH,
    )
)
class FramesAdapter(DefaultDataAdapter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Check if LLM judge should be enabled
        # When judge_strategy is AUTO, use_llm_judge property returns self._use_llm_judge
        # task_config is passed via kwargs and stored in self._task_config by LLMJudgeMixin
        
        self._use_llm_judge = False
        
        if 'model' in self._task_config.judge_model_args or \
            'model_id' in self._task_config.judge_model_args:
            self._use_llm_judge = True
            logger.info("LLM judge is enabled for FRAMES evaluation")
        
    def load(self):
        """
        Load the FRAMES dataset from local JSONL files.
        
        This method overrides the default loading behavior to use LocalDataLoader
        directly, which properly handles JSONL files in a directory.
        """
        # Get the dataset path from dataset_id (which may be overridden by dataset_args)
        dataset_path = self.dataset_id
        
        # If the path exists locally, use LocalDataLoader
        if os.path.exists(dataset_path):
            logger.info(f'Loading FRAMES dataset from local path: {dataset_path}')
            
            # Load each subset using LocalDataLoader
            subset_dict = {}
            for subset in self.subset_list:
                # LocalDataLoader will automatically find JSONL files in the directory
                # It will try: {subset}_{split}.jsonl, {subset}.jsonl, or any .jsonl file
                dataset = LocalDataLoader(
                    data_id_or_path=dataset_path,
                    split=self.eval_split,
                    subset=subset,
                    sample_fields=self.record_to_sample,
                    filter_func=self.sample_filter,
                    limit=self.limit,
                    repeats=self.repeats,
                    shuffle=self.shuffle,
                ).load()
                
                subset_dict[subset] = dataset
            
            test_dataset = DatasetDict(subset_dict)
            return test_dataset, None
        else:
            raise ValueError(f'Local path {dataset_path} does not exist')

    def record_to_sample(self, record: Dict[str, Any]) -> Sample:
        """
        Convert a data record to a Sample object.

        Args:
            record (Dict[str, Any]): Input data record.

        Returns:
            Sample: Sample object with input, target, and metadata.
        """
        context = '\n'.join([f"{i['title']}\n{i['text']}" for i in record['wiki_items']])
        question = record['Prompt']

        return Sample(
            input=question, target=record['Answer'], metadata={
                'context': context,
                # 'wiki_items': record['wiki_items']
            }
        )

    def format_prompt_template(self, sample):
        context = sample.metadata['context']
        question = sample.input
        # Determine if using Chinese or English template based on subset
        # Check if question contains Chinese characters
        # has_chinese = True # bool(re.search(r'[\u4e00-\u9fff]', question))
        # template = TEMPLATE_0SHOT_ZH if has_chinese else TEMPLATE_0SHOT_EN
        return TEMPLATE_0SHOT_ZH.format(context=context, question=question)

    def extract_answer(self, prediction: str, task_state: TaskState):
        """
        Extract the answer from the model prediction.
        Supports both English and Chinese formats.
        """
        response = prediction.replace('*', '')

        # # Try English format first
        # if 'the answer is' in response.lower():
        #     ans = response.rsplit('the answer is', 1)[-1].strip().strip('.').strip()
        #     if ans:
        #         return ans
        
        # Try Chinese format
        if '答案是' in response:
            ans = response.rsplit('答案是', 1)[-1].strip().strip('。').strip().strip('.').strip()
            if ans:
                return ans
        
        # If no pattern found, return empty string
        return ''

    def match_score(
        self,
        original_prediction: str,
        filtered_prediction: str,
        reference: str,
        task_state: TaskState,
    ) -> Score:
        """
        Calculate accuracy score by matching prediction with reference.
        """
        raise ValueError('match_score is not expected')
        from evalscope.metrics import exact_match
        from .utils import normalize_answer

        score = Score(
            extracted_prediction=filtered_prediction,
            prediction=original_prediction,
        )

        gold = normalize_answer(reference)
        pred = normalize_answer(filtered_prediction)
        accuracy = exact_match(gold=gold, pred=pred)

        score.value = {'acc': accuracy}
        score.main_score_name = 'acc'

        return score

    def llm_match_score(
        self,
        original_prediction: str,
        filtered_prediction: str,
        reference: str,
        task_state: TaskState,
    ) -> Score:
        """
        Use LLM judge to evaluate the prediction against the reference.
        """
        from .utils import GENERAL_ORM_PROMPT, ORM_USER_TEMPLATE

        score = Score(
            extracted_prediction=filtered_prediction,
            prediction=original_prediction,
        )

        question = task_state.input_text

        # Get grading response
        prompt = ORM_USER_TEMPLATE.format(problem=question, answer_1=reference, answer_2=filtered_prediction)
        orm_response = self.llm_judge.judge(prompt, system_prompt=GENERAL_ORM_PROMPT)

        # Parse grading response
        if 'YES' in orm_response:
            accuracy = 1.0
        else:
            accuracy = 0.0

        score.value = {'acc': accuracy}
        score.explanation = f'LLM judge: {orm_response}'
        score.metadata = {
            'source': 'llm_judge',
            'judge_strategy': self.judge_strategy,
            'model': self.llm_judge.model_id
        }
        score.main_score_name = 'acc'
        return score
