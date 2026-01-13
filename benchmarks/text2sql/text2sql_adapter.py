from typing import Any, Dict
import os
import re
from evalscope.api.benchmark import BenchmarkMeta, DefaultDataAdapter
from evalscope.api.dataset import Sample, DatasetDict
from evalscope.api.dataset.loader import LocalDataLoader
from evalscope.api.evaluator import TaskState
from evalscope.api.messages.chat_message import ChatMessageUser
from evalscope.api.metric import Score
from evalscope.api.registry import register_benchmark
from evalscope.constants import Tags
from evalscope.utils import get_logger

logger = get_logger()


def extract_sql(text):
    code = '\n'.join([line for line in text.split('\n') if line.strip() != '']) + '\n'
    pattern_sql = r'^\s*(?:select|with\s[^\n]+as)[^;]*'
    matches = re.findall(pattern_sql, code, re.M | re.IGNORECASE)
    return matches

@register_benchmark(
    BenchmarkMeta(
        name='text2sql',
        dataset_id='text2sql_dataset',
        pretty_name='Text2SQL',
        tags=[Tags.CODING],
        metric_list=['sql_ast_sim'],
        aggregation='mean',
        prompt_template='Convert the following question into a SQL query based on the provided schema.\nSchema: {schema}\nQuestion: {question}\nSQL:',
    )
)
class Text2SQLAdapter(DefaultDataAdapter):
    """Adapter for Text2SQL benchmark with AST similarity evaluation."""

    def load(self):
        """
        Load the Text2SQL dataset from local file system.
        
        This method overrides the default loading behavior to use LocalDataLoader
        directly, which properly handles JSONL files in a directory.
        """
        # Get the dataset path from dataset_id (which may be overridden by dataset_args)
        dataset_path = self.dataset_id
        
        # If the path exists locally, use LocalDataLoader
        if os.path.exists(dataset_path):
            logger.info(f'Loading Text2SQL dataset from local path: {dataset_path}')
            
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
            # Fallback to default loading for remote datasets
            return super().load()

    def record_to_sample(self, record: Dict[str, Any]) -> Sample:
        """Convert a data record to a Sample object."""
        question = record['question']
        schema = record.get('schema', '')

        if isinstance(schema, list):
            schema = "\n".join(schema)
            
        full_prompt = self.prompt_template.format(schema=schema, question=question)
        
        # input: [ChatMessageUser(id='084b279f', content='Convert the following question into a SQL query based on the provided schema.\nSchema: CREATE TABLE employees (id INT, name TEXT, department TEXT, salary INT, hire_date DATE);\nQuestion: 查询所有工资超过 5000 的员工姓名和入职日期。\nSQL:', source=None, metadata=None, internal=None, role='user', tool_call_id=None)]
        # openai request: {'messages': [{'role': 'user', 'content': 'Convert the following question into a SQL query based on the provided schema.\nSchema: CREATE TABLE employees (id INT, name TEXT, department TEXT, salary INT, hire_date DATE);\nQuestion: 查询所有工资超过 5000 的员工姓名和入职日期。\nSQL:'}], 'tools': NOT_GIVEN, 'tool_choice': NOT_GIVEN, 'model': 'Qwen/Qwen3-Next-80B-A3B-Instruct-FP8', 'temperature': 0.0}
        return Sample(
            input=[{'role': 'user', 'content': full_prompt}],
            target=record['ground_truth']
        )

    def extract_answer(self, prediction: str, task_state: TaskState) -> str:
        """Extract SQL query from the model prediction."""
        sqls = extract_sql(prediction)
        if sqls:
            # Take the first matched SQL and remove trailing semicolon
            return sqls[0].strip().strip(';').replace('\n', ' ')
        
        # Fallback to simple cleaning if no fenced/heuristic block found
        return prediction.strip().strip(';').replace('\n', ' ')

    def match_score(self, original_prediction: str, filtered_prediction: str, reference: str, task_state: TaskState) -> Score:
        """Calculate the SQL AST similarity score."""
        # Modified to import from local sql_metrics
        from benchmarks.text2sql.sql_metrics import SQLASTSimilarity
        
        # Initialize and apply the custom SQL metric
        metric = SQLASTSimilarity()
        sim_scores = metric.apply([filtered_prediction], [reference])
        sim_score = sim_scores[0] if sim_scores else 0.0
        
        # Construct the Score object
        score = Score(
            extracted_prediction=filtered_prediction,
            prediction=original_prediction,
            value={'sql_ast_sim': sim_score},
            main_score_name='sql_ast_sim'
        )
        return score
