# OpenAI Configuration for LLM Testing

## Description
Add OpenAI configuration management for LLM testing capabilities. This PR introduces:

- `OpenAIConfig` class for managing API settings using Pydantic
- Environment variable support for configuration
- Validation of API key and model parameters
- Example configuration file (.env.example)

## Changes
- Add `src/smart_hive/configs/openai_config.py`
- Add `tests/smart_hive/configs/test_openai_config.py`
- Add `.env.example` with OpenAI variables

## Testing
- Unit tests added for configuration management
- Tests cover default values, environment loading, and validation
- All tests passing locally

## Related Issues
Part of the LLM testing implementation. Required for DeepEval integration.

## Checklist
- [x] Code follows project style guidelines
- [x] Tests added for new functionality
- [x] Documentation added (.env.example)
- [x] All tests passing
- [x] Example configuration provided
