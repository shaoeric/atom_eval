from evalscope.api.benchmark import BenchmarkMeta, DefaultDataAdapter
from evalscope.api.dataset import Sample
from evalscope.api.evaluator import TaskState
from evalscope.api.messages.chat_message import ChatMessageUser
from evalscope.api.metric import Score
from evalscope.api.registry import register_benchmark
from evalscope.constants import Tags
from evalscope.utils.code_utils import extract_sql
from typing import Any, Dict

@register_benchmark(
    BenchmarkMeta(
        name='text2sql',
        pretty_name='Text2SQL',
        tags=[Tags.CODING],
        metric_list=['sql_ast_sim'],
        aggregation='mean',
        prompt_template='Convert the following question into a SQL query based on the provided schema.\nSchema: {schema}\nQuestion: {question}\nSQL:',
    )
)
class Text2SQLAdapter(DefaultDataAdapter):
    """Adapter for Text2SQL benchmark with AST similarity evaluation."""

    def record_to_sample(self, record: Dict[str, Any]) -> Sample:
        """Convert a data record to a Sample object."""
        question = record['question']
        # Support both 'schema' and 'contexts' as schema input
        schema = record.get('schema', '')
        if isinstance(schema, list):
            schema = "\n".join(schema)
            
        full_prompt = self.prompt_template.format(schema=schema, question=question)
        
        return Sample(
            input=[ChatMessageUser(content=full_prompt)],
            target=record['ground_truth']
        )

    def extract_answer(self, prediction: str, task_state: TaskState) -> str:
        """Extract SQL query from the model prediction."""
        # Use evalscope's built-in SQL extraction utility
        sqls = extract_sql(prediction)
        if sqls:
            # Take the first matched SQL and remove trailing semicolon
            return sqls[0].code.strip().strip(';')
        
        # Fallback to simple cleaning if no fenced/heuristic block found
        return prediction.strip().strip(';')

    def match_score(self, original_prediction: str, filtered_prediction: str, reference: str, task_state: TaskState) -> Score:
        """Calculate the SQL AST similarity score."""
        # Modified to import from local sql_metrics
        try:
            from .sql_metrics import SQLASTSimilarity
        except ImportError:
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
