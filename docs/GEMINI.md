# Using Gemini with the Benchmark

This guide explains how to use Google's Gemini model with the Code Mode benchmark.

## Setup

### 1. Get a Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Configure the API Key

Add your Gemini API key to `.env`:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

You can have both Claude and Gemini keys in the same `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
GOOGLE_API_KEY=your_google_api_key_here
```

## Running with Gemini

### Command Line

```bash
# Run full benchmark with Gemini
python benchmark.py --model gemini

# Run quick test (2 scenarios) with Gemini
python benchmark.py --model gemini --limit 2

# Run specific scenario with Gemini
python benchmark.py --model gemini --scenario 3
```

### Makefile

```bash
# Run full benchmark with Gemini
make run-gemini

# Run quick test with Gemini
make run-gemini-quick
```

## Comparing Models

You can run the benchmark with both models to compare:

```bash
# Run with Claude (default)
python benchmark.py --limit 2
# Results saved to: benchmark_results_claude.json

# Run with Gemini
python benchmark.py --model gemini --limit 2
# Results saved to: benchmark_results_gemini.json

# Compare the JSON files
```

## Implementation Details

### Gemini Regular Agent

Uses Gemini's native function calling:
- Converts Anthropic tool schemas to Gemini format
- Uses `genai.GenerativeModel` with tools parameter
- Handles function calls via `function_call` parts
- Returns function responses using `FunctionResponse` proto

Location: `agents/gemini_regular_agent.py`

### Gemini Code Mode Agent

Uses Gemini to generate Python code:
- Same system prompt as Claude version
- Generates code in ```python blocks
- Executes in the same sandbox (RestrictedPython)
- Uses the same tools API

Location: `agents/gemini_codemode_agent.py`

## Testing Individual Agents

```bash
# Test Gemini Regular Agent
cd codemode_benchmark
source venv/bin/activate
python agents/gemini_regular_agent.py

# Test Gemini Code Mode Agent
python agents/gemini_codemode_agent.py

# Test agent factory with both models
python agents/agent_factory.py
```

## Differences from Claude

### API Differences
- **Schema format**: Gemini uses different parameter schema format
- **Function calling**: Gemini uses proto-based function responses
- **Token counting**: Different token counting mechanisms
- **Context window**: Different limits

### Expected Behavior
Both models should:
- Complete all scenarios successfully
- Pass validation checks
- Generate correct final state

Performance may differ:
- Token usage
- Execution time
- Number of iterations
- Code quality (for Code Mode)

## Troubleshooting

### "GOOGLE_API_KEY not configured"
- Check `.env` file exists
- Verify the key is correct
- Make sure there are no extra spaces or quotes

### "Gemini API quota exceeded"
- Gemini has free tier rate limits
- Wait a minute between runs
- Or upgrade to paid tier

### "Model not found" error
- The code uses `gemini-1.5-pro-latest`
- Ensure your API key has access to this model
- You can change the model name in the agent files if needed

### Schema conversion issues
- If a tool doesn't work, check schema conversion in `_convert_schemas_to_gemini`
- Gemini may have stricter requirements for some parameter types

## Model Configuration

To change the Gemini model version, edit:

**For Regular Agent** (`agents/gemini_regular_agent.py`):
```python
self.model_name = "gemini-1.5-pro-latest"  # Change here
```

**For Code Mode Agent** (`agents/gemini_codemode_agent.py`):
```python
self.model_name = "gemini-1.5-pro-latest"  # Change here
```

Available models:
- `gemini-1.5-pro-latest`
- `gemini-1.5-flash-latest`
- `gemini-1.0-pro-latest`

## Notes

- Gemini's function calling API is different from Claude's
- Schema conversion happens automatically
- Code Mode uses the same sandbox for both models
- Results are saved to separate files by model name

## Adding More Models

To add support for other models (e.g., GPT-4), follow this pattern:

1. Create `agents/yourmodel_regular_agent.py`
2. Create `agents/yourmodel_codemode_agent.py`
3. Add to `agents/agent_factory.py`:
   ```python
   "yourmodel": {
       "name": "Your Model Name",
       "api_key_env": "YOUR_API_KEY",
       "regular": YourModelRegularAgent,
       "codemode": YourModelCodeModeAgent,
   }
   ```
4. Update `benchmark.py` to handle the new API key
5. Update documentation

The agent factory makes it easy to support multiple LLM providers!
