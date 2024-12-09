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

start_test:
	@echo "Starting main program..."
	python -m prompt_language.main
