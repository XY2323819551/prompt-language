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
test_save2local:
	@echo "Starting test_save2local..."
	python -m prompt_language.utils.tool_factory.default.save2local
test_read_local:
	@echo "Starting test_read_local..."
	python -m prompt_language.utils.tool_factory.default.read_local
test_deduplicated:
	@echo "Starting test_deduplicated..."
	python -m prompt_language.utils.tool_factory.default.deduplicated


