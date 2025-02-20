# 定义清理目标
.PHONY: clean count start_test
clean:
	@echo "Clearing terminal..."
	@clear || cls || echo -e \\033c  # 兼容不同操作系统的清屏命令
	@echo "Cleaning __pycache__ directories..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "Cleaning .pyc files..."
	@find . -type f -name "*.pyc" -delete
	@echo "Cleaning complete."

# 统计Python文件数量和代码行数
count:
	@echo "Counting Python files and lines of code..."
	@echo "Python files count:" && find . -type f -name "*.py" | wc -l
	@echo "Total lines in Python files:" && find . -type f -name "*.py" -exec cat {} \; | wc -l

start:
	@echo "Starting main program..."
	python -m prompt_language.main_chronicle




# 测试工具
test_duckduckgo:
	@echo "Starting test_duckduckgo..."
	python -m prompt_language.utils.tool_factory.websearch.duckduckgo
test_wikipedia:
	@echo "Starting test_wikipedia..."
	python -m prompt_language.utils.tool_factory.websearch.wikipedia
test_google:
	@echo "Starting test_google..."
	python -m prompt_language.utils.tool_factory.websearch.google
test_bing:
	@echo "Starting test_bing..."
	python -m prompt_language.utils.tool_factory.websearch.bing
test_websearch:
	@echo "Starting test_websearch..."
	python -m prompt_language.utils.tool_factory.websearch.websearch
test_save2local:
	@echo "Starting test_save2local..."
	python -m prompt_language.utils.tool_factory.default.save2local
test_read_local:
	@echo "Starting test_read_local..."
	python -m prompt_language.utils.tool_factory.default.read_local
test_deduplicated:
	@echo "Starting test_deduplicated..."
	python -m prompt_language.utils.tool_factory.default.deduplicated
test_arxiv_search:
	@echo "Starting test_arxiv_search..."
	python -m prompt_language.utils.tool_factory.custom.arxiv_search
test_paper_with_code:
	@echo "Starting test_paper_with_code..."
	python -m prompt_language.utils.tool_factory.custom.paper_with_code
test_compute_calendar:
	@echo "Starting test_compute_calendar..."
	python -m prompt_language.utils.tool_factory.default.compute_calendar


# 测试工作流
test_chronicle:
	@echo "Starting test_chronicle..."
	python -m examples.chronicle.main_chronicle
test_scific:
	@echo "Starting test_scific..."
	python -m examples.scific_read.main_scific
test_paper:
	@echo "Starting test_paper..."
	python -m examples.paper.main_paper



# 测试逻辑块
test_function_block:
	@echo "Starting test_function_block..."
	python -m prompt_language.blocks.function_block




# 测试模型工厂的模型
test_glm:
	@echo "Starting test_glm_4..."
	python -m prompt_language.utils.model_factory.glm_model
test_gemini:
	@echo "Starting test_gemini..."
	python -m prompt_language.utils.model_factory.gemini_model
test_r1:
	@echo "Starting test_r1..."
	python -m prompt_language.utils.model_factory.deepseek_r1
test_r1_model:
	@echo "Starting test_r1_model..."
	python -m prompt_language.utils.tool_factory.default.r1_model
	



# 其他测试
test_g1:
	@echo "Starting test_g1..."
	python -m prompt_language.utils.agent_factory.g1
test_meta_prompt:
	@echo "Starting test_meta_prompt..."
	python -m docs.openai-cookbook.meta-prompt
test_meta_prompt_gemini:
	@echo "Starting test_meta_prompt_gemini..."
	python -m examples.conclusion_gemini.meta_prompt


test_conclusion_gemini:
	@echo "Starting test_conclusion_gemini..."
	python -m examples.conclusion_gemini.gemini_conclusion



# test promptor project
test_benchmark:
	@echo "Starting test_benchmark..."
	python -m prompt_language.utils.tool_factory.auto_promptor.benchmark

test_badcase_analyzer:
	@echo "Starting test_badcase_analyzer..."
	python -m prompt_language.utils.tool_factory.auto_promptor.badcase_analyzer
test_prompt_optimizer:
	@echo "Starting test_prompt_optimizer..."
	python -m prompt_language.utils.tool_factory.auto_promptor.prompt_optimizer
test_log2excelpic:
	@echo "Starting test_log2excelpic..."
	python -m prompt_language.utils.tool_factory.auto_promptor.log2excelpic

test_auto_prompter:
	@echo "Starting test_auto_prompter..."
	python -m examples.auto_prompter.promptor


test_core_logic:
	@echo "Starting test_core_logic..."
	python -m prompt_language.utils.tool_factory.auto_promptor.core_logic
test_prompt_optimizer:
	@echo "Starting test_prompt_optimizer..."
	python -m prompt_language.utils.tool_factory.auto_promptor.prompt_optimizer
test_log2excelpic:
	@echo "Starting test_log2excelpic..."
	python -m prompt_language.utils.tool_factory.auto_promptor.log2excelpic
	


# tmp
test_agent:
	@echo "Starting test_agent..."
	python -m examples.explore_demo_cases.agent
test_deepqa:
	@echo "Starting test_deepqa..."
	python -m examples.deepqa.main_deepqa
test_bambo:
	@echo "Starting test_bambo..."
	python -m examples.agent_demo_cases.agent

test_codetool:
	@echo "Starting test_codetool..."
	python -m prompt_language.utils.tool_factory.default.codetool



