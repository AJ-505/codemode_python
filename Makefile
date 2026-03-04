.PHONY: help install setup clean test run benchmark test-regular test-codemode test-sandbox lint format check

PYTHON ?= python3

# Default target
help:
	@echo "Code Mode Benchmark - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install Python dependencies"
	@echo "  make setup            Complete setup (venv + deps + .env)"
	@echo "  make venv             Create virtual environment"
	@echo "  make env              Create .env file from example"
	@echo ""
	@echo "Running:"
	@echo "  make run              Run full benchmark with Claude"
	@echo "  make run-quick        Run quick benchmark with Claude"
	@echo "  make run-gemini       Run full benchmark with Gemini"
	@echo "  make run-gemini-quick Run quick benchmark with Gemini"
	@echo "  make run-opus         Run benchmark with Claude Opus 4.6"
	@echo "  make run-gpt51        Run benchmark with GPT-5.1"
	@echo "  make run-gpt          Run benchmark with GPT-5.2"
	@echo "  make run-glm          Run benchmark with GLM-5"
	@echo "  make run-minimax      Run benchmark with MiniMax M2.5"
	@echo "  make run-kimi         Run benchmark with Kimi 2.5"
	@echo "  make run-gemini3      Run benchmark with Gemini 3 Pro"
	@echo "  make run-latest       Run latest-model suite (default: no Opus 4.6)"
	@echo "  make run-latest-opus  Run latest-model suite including Opus 4.6"
	@echo "  make run-scenario     Run specific scenario (SCENARIO=<id>)"
	@echo "  make benchmark        Alias for 'make run'"
	@echo ""
	@echo "Testing:"
	@echo "  make test-regular     Test regular agent only"
	@echo "  make test-codemode    Test code mode agent only"
	@echo "  make test-sandbox     Test sandbox executor"
	@echo "  make test             Run all tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean            Remove cache and generated files"
	@echo "  make clean-all        Remove cache, venv, and results"
	@echo "  make format           Format code with black"
	@echo "  make lint             Lint code with flake8"
	@echo "  make check            Run format + lint"
	@echo ""
	@echo "Info:"
	@echo "  make show-results     Display last benchmark results"
	@echo "  make show-structure   Show project structure"

# Installation targets
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "✓ Virtual environment created"
	@echo ""
	@echo "To activate the virtual environment:"
	@echo "  source venv/bin/activate"

env:
	@if [ -f .env ]; then \
		echo ".env file already exists"; \
	else \
		cp .env.example .env; \
		echo "✓ Created .env file from .env.example"; \
		echo ""; \
		echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"; \
	fi

setup: venv env
	@echo ""
	@echo "Installing dependencies in virtual environment..."
	./venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate the virtual environment: source venv/bin/activate"
	@echo "  2. Edit .env and add your ANTHROPIC_API_KEY"
	@echo "  3. Run the benchmark: make run"

# Running targets
run: check-env
	@echo "Running full benchmark..."
	$(PYTHON) benchmark.py

benchmark: run

run-quick: check-env
	@echo "Running quick benchmark (first 2 scenarios)..."
	$(PYTHON) benchmark.py --limit 2

run-gemini: check-env
	@echo "Running benchmark with Gemini..."
	$(PYTHON) benchmark.py --model gemini

run-gemini-quick: check-env
	@echo "Running quick benchmark with Gemini..."
	$(PYTHON) benchmark.py --model gemini --limit 2

run-opus: check-env
	@echo "Running benchmark with Claude Opus 4.6..."
	$(PYTHON) benchmark.py --model opus_4_6

run-gpt51: check-env
	@echo "Running benchmark with GPT-5.1..."
	$(PYTHON) benchmark.py --model gpt_5_1

run-gpt: check-env
	@echo "Running benchmark with GPT-5.2..."
	$(PYTHON) benchmark.py --model gpt_5_2

run-glm: check-env
	@echo "Running benchmark with GLM-5..."
	$(PYTHON) benchmark.py --model glm_5

run-minimax: check-env
	@echo "Running benchmark with MiniMax M2.5..."
	$(PYTHON) benchmark.py --model minimax_m2_5

run-kimi: check-env
	@echo "Running benchmark with Kimi 2.5..."
	$(PYTHON) benchmark.py --model kimi_2_5

run-gemini3: check-env
	@echo "Running benchmark with Gemini 3 Pro..."
	$(PYTHON) benchmark.py --model gemini_3_pro

run-latest: check-env
	@echo "Running latest-model suite (without Opus 4.6)..."
	$(PYTHON) benchmark.py --run-latest

run-latest-opus: check-env
	@echo "Running latest-model suite including Opus 4.6..."
	$(PYTHON) benchmark.py --run-latest --include-opus

run-scenario: check-env
	@echo "Running specific scenario..."
	@if [ -z "$(SCENARIO)" ]; then \
		echo "Usage: make run-scenario SCENARIO=<id>"; \
		echo "Example: make run-scenario SCENARIO=1"; \
		exit 1; \
	fi
	$(PYTHON) benchmark.py --scenario $(SCENARIO)

# Testing targets
test-regular: check-env
	@echo "Testing Regular Agent..."
	$(PYTHON) agents/regular_agent.py

test-codemode: check-env
	@echo "Testing Code Mode Agent..."
	$(PYTHON) agents/codemode_agent.py

test-sandbox:
	@echo "Testing Sandbox Executor..."
	$(PYTHON) sandbox/executor.py

test: test-sandbox test-regular test-codemode
	@echo ""
	@echo "✓ All tests completed"

# Maintenance targets
clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

clean-all: clean
	@echo "Removing virtual environment and results..."
	rm -rf venv
	rm -f benchmark_results.json
	@echo "✓ Deep clean complete"

format:
	@echo "Formatting code with black..."
	@if command -v black >/dev/null 2>&1; then \
		black agents/ tools/ sandbox/ benchmark.py; \
		echo "✓ Code formatted"; \
	else \
		echo "⚠️  black not installed. Install with: pip install black"; \
	fi

lint:
	@echo "Linting code with flake8..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 agents/ tools/ sandbox/ benchmark.py --max-line-length=120 --ignore=E203,W503; \
		echo "✓ Linting passed"; \
	else \
		echo "⚠️  flake8 not installed. Install with: pip install flake8"; \
	fi

check: format lint
	@echo "✓ Code check complete"

# Info targets
show-results:
	@if [ -f benchmark_results.json ]; then \
		echo "Last Benchmark Results:"; \
		echo "======================"; \
		$(PYTHON) -m json.tool benchmark_results.json | head -100; \
	else \
		echo "No results found. Run 'make benchmark' first."; \
	fi

show-structure:
	@echo "Project Structure:"
	@echo "=================="
	@tree -I '__pycache__|*.pyc|venv|.git' -L 3 || find . -type f -name "*.py" | grep -v __pycache__ | sort

# Utility targets
check-env:
	@if [ ! -f .env ]; then \
		echo "⚠️  .env file not found"; \
		echo "Run 'make env' to create it"; \
		exit 1; \
	fi
	@if ! grep -qE "(ANTHROPIC_API_KEY=|GOOGLE_API_KEY=|OPENAI_API_KEY=|ZHIPU_API_KEY=|OPENROUTER_API_KEY=|MINIMAX_API_KEY=|MOONSHOT_API_KEY=)" .env 2>/dev/null; then \
		echo "⚠️  No API keys configured in .env"; \
		echo "Please edit .env and add at least one API key:"; \
		echo "  - ANTHROPIC_API_KEY for Claude / Opus"; \
		echo "  - OPENAI_API_KEY for GPT-5.2"; \
		echo "  - OPENROUTER_API_KEY for OpenRouter-routed models"; \
		echo "  - ZHIPU_API_KEY for GLM-5 direct"; \
		echo "  - MINIMAX_API_KEY for MiniMax direct"; \
		echo "  - MOONSHOT_API_KEY for Kimi direct"; \
		echo "  - GOOGLE_API_KEY for Gemini"; \
		exit 1; \
	fi

# Quick start - one command to set everything up
quick-start: setup
	@echo ""
	@echo "Quick start setup complete!"
	@echo ""
	@echo "⚠️  Don't forget to:"
	@echo "  1. Activate venv: source venv/bin/activate"
	@echo "  2. Add your API key to .env"
	@echo "  3. Run: make benchmark"
