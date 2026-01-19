from evalscope.api.registry import BENCHMARK_REGISTRY

if 'FRAMES' not in BENCHMARK_REGISTRY:
    import benchmarks.frames.frames_adapter
if 'text2sql' not in BENCHMARK_REGISTRY:
    import benchmarks.text2sql.text2sql_adapter
if 'halu_eval' not in BENCHMARK_REGISTRY:
    import benchmarks.halu_eval.halu_eval_adapter