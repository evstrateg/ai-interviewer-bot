# AssemblyAI Integration Test Suite Documentation

This document provides comprehensive guidance for testing the AssemblyAI voice processing integration in the AI Interviewer Telegram Bot.

## Overview

The test suite covers all aspects of the voice processing system:
- **Unit Tests**: Fast, isolated tests with mocks (no external API calls)
- **Integration Tests**: Full workflow tests with mocked APIs
- **Performance Tests**: Concurrent processing and load testing
- **Real API Tests**: Optional tests using actual AssemblyAI API
- **Error Handling Tests**: Comprehensive failure scenario coverage

## Quick Start

### Running Basic Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all unit tests (fast, no API calls)
pytest test_assemblyai_integration.py -m "unit"

# Run all tests except real API tests
pytest test_assemblyai_integration.py -m "not real_api"

# Run with coverage
pytest test_assemblyai_integration.py --cov=voice_handler --cov-report=html
```

### Running Specific Test Categories

```bash
# Unit tests only (fastest)
pytest test_assemblyai_integration.py -m "not integration and not performance and not real_api"

# Integration tests with mocks
pytest test_assemblyai_integration.py -m "integration and not real_api"

# Performance tests
pytest test_assemblyai_integration.py -m "performance"

# All tests with detailed output
pytest test_assemblyai_integration.py -v --tb=long
```

## Test Structure

### 1. Configuration Tests (`TestVoiceProcessingConfig`)

**Purpose**: Validate configuration initialization and validation

**Test Cases**:
- ✅ Minimal configuration with required parameters only
- ✅ Full configuration with all features enabled
- ✅ Default value assignment in `__post_init__`
- ✅ Custom language and PII policy settings
- ❌ Missing API key validation
- ❌ Invalid parameter ranges

**Example**:
```python
def test_config_initialization_full(self, test_config):
    config = test_config
    assert config.assemblyai_api_key == TEST_API_KEY
    assert config.enable_speaker_labels is True
    assert config.enable_pii_redaction is True
    assert "person_name" in config.pii_redaction_policies
```

### 2. Audio Processing Tests (`TestAudioProcessor`)

**Purpose**: Test audio file download, conversion, and optimization

**Test Cases**:
- ✅ Voice message download from Telegram
- ✅ Audio format conversion (OGG → WAV)
- ✅ Audio optimization (mono, 16kHz, normalization)
- ✅ Temporary file cleanup
- ❌ Download failures and network errors
- ❌ Unsupported audio format handling
- ❌ File corruption scenarios

**Example**:
```python
@pytest.mark.asyncio
async def test_convert_and_optimize_success(self, mock_audio_segment, sample_audio_file):
    # Mock AudioSegment behavior
    mock_audio = Mock()
    mock_audio.channels = 2
    mock_audio.frame_rate = 44100
    
    result_path, metadata = await self.processor.convert_and_optimize(sample_audio_file)
    
    assert result_path.suffix == ".wav"
    assert metadata["duration"] == 5.0
    mock_audio.set_channels.assert_called_with(1)  # Convert to mono
```

### 3. AssemblyAI Client Tests (`TestAssemblyAIClient`)

**Purpose**: Test AssemblyAI SDK integration with comprehensive mocking

**Test Cases**:
- ✅ Client initialization and API key validation
- ✅ Rate limiting and concurrent request handling
- ✅ Audio file validation (size, duration, format)
- ✅ Transcript configuration building with all features
- ✅ Retry logic with exponential backoff
- ✅ Transcription quality determination
- ❌ API authentication failures
- ❌ Network timeout handling
- ❌ Invalid file format errors
- ❌ Service unavailability scenarios

**Example**:
```python
@pytest.mark.asyncio
async def test_transcribe_with_retries_eventual_success(self, sample_audio_file, mock_successful_transcript):
    with patch.object(self.client, 'transcriber') as mock_transcriber:
        # Fail twice, then succeed
        mock_transcriber.transcribe.side_effect = [
            Exception("Network error"),
            Exception("Temporary failure"),
            mock_successful_transcript
        ]
        
        result = await self.client._transcribe_with_retries(sample_audio_file, config)
        assert result == mock_successful_transcript
        assert mock_transcriber.transcribe.call_count == 3
```

### 4. Voice Handler Tests (`TestVoiceMessageHandler`)

**Purpose**: Test main voice processing workflow and response formatting

**Test Cases**:
- ✅ Handler initialization with statistics
- ✅ Transcription response formatting for all quality levels
- ✅ Enhanced features display (language, speakers, summary)
- ✅ Word search functionality
- ✅ Error message formatting with specific guidance
- ✅ Statistics tracking and calculation

**Example**:
```python
def test_format_transcription_response_failed_auth_error(self):
    result = VoiceTranscriptionResult(
        text="",
        confidence=0.0,
        quality=VoiceQuality.FAILED,
        error="authentication: API key invalid"
    )
    
    response = self.handler.format_transcription_response(result)
    assert "🎤❌" in response
    assert "API authentication failed" in response
```

### 5. Integration Tests (`TestVoiceHandlerIntegration`)

**Purpose**: Test complete end-to-end workflows with mocked external dependencies

**Test Cases**:
- ✅ Full successful processing workflow
- ✅ Workflow failure at different stages
- ✅ Statistics update verification
- ✅ Telegram context interaction
- ✅ File cleanup after processing

**Example**:
```python
@pytest.mark.asyncio
async def test_full_workflow_success(self, sample_audio_file, mock_successful_transcript):
    # Setup comprehensive mocks for full workflow
    with patch('voice_handler.AssemblyAIClient') as mock_client_class:
        # ... mock setup ...
        
        handler = VoiceMessageHandler(self.config)
        result = await handler.process_voice_message(self.update, self.context)
        
        assert result.quality == VoiceQuality.HIGH
        stats = handler.get_statistics()
        assert stats['messages_processed'] == 1
```

### 6. Error Handling Tests (`TestErrorHandling`)

**Purpose**: Comprehensive error scenario coverage

**Test Cases**:
- ❌ Network timeout and connection failures
- ❌ Authentication and authorization errors
- ❌ File format and size validation errors
- ❌ AssemblyAI service errors
- ❌ Concurrent request limit handling
- ✅ Graceful error recovery and cleanup

### 7. Performance Tests (`TestPerformance`)

**Purpose**: Test system performance under load

**Test Cases**:
- ⚡ Concurrent message processing
- ⚡ Large file handling simulation
- ⚡ Memory usage optimization
- ⚡ Configuration performance settings

**Example**:
```python
@pytest.mark.asyncio
async def test_concurrent_processing(self):
    num_concurrent = 5
    tasks = []
    
    # Create concurrent processing tasks
    for i in range(num_concurrent):
        task = handler.process_voice_message(update, context)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert len([r for r in results if r.quality != VoiceQuality.FAILED]) == num_concurrent
```

## Test Configuration

### Environment Variables

```bash
# Required for basic tests
TELEGRAM_BOT_TOKEN=your_telegram_token
ANTHROPIC_API_KEY=your_anthropic_key

# Optional for real API tests
ASSEMBLYAI_API_KEY=your_assemblyai_key
ASSEMBLYAI_INTEGRATION_TESTS=true  # Enable real API tests

# Test behavior control
VOICE_PROCESSING_ENABLED=true
LOG_LEVEL=DEBUG
```

### Test Markers

Use pytest markers to run specific test categories:

- `unit` - Fast unit tests with mocks
- `integration` - Integration tests with mocked APIs
- `performance` - Performance and load tests
- `real_api` - Tests requiring real AssemblyAI API
- `slow` - Long-running tests
- `audio` - Audio processing specific tests
- `config` - Configuration related tests
- `error` - Error handling tests
- `concurrent` - Concurrency tests

### Test Data

The test suite includes comprehensive test data generation:

```python
# Audio file generation
wav_file = AudioFileGenerator.create_wav_silence(duration_seconds=5.0)
tone_file = AudioFileGenerator.create_wav_tone(frequency=440.0)
large_file = AudioFileGenerator.create_large_file(size_mb=30)

# Mock transcript generation  
success_transcript = MockTranscriptGenerator.create_successful_transcript()
failed_transcript = MockTranscriptGenerator.create_failed_transcript()
low_conf_transcript = MockTranscriptGenerator.create_low_confidence_transcript()

# Telegram mock objects
voice_msg = TelegramMockFactory.create_voice_message(duration=5.0)
update = TelegramMockFactory.create_update(user_id=12345)
context = TelegramMockFactory.create_context()
```

## Running Tests in CI/CD

### GitHub Actions

The project includes comprehensive GitHub Actions workflows:

```yaml
# .github/workflows/test.yml
- Unit tests on Python 3.9, 3.10, 3.11, 3.12
- Integration tests with mocked APIs
- Performance tests
- Optional real API tests (if secrets configured)
- Security scanning with bandit and safety
- Docker build testing
- Coverage reporting to Codecov
```

### Local CI Simulation

```bash
# Simulate CI environment
export CI=true
export GITHUB_ACTIONS=true

# Run full test suite like CI
pytest test_assemblyai_integration.py \
  -v \
  --cov=voice_handler \
  --cov-report=xml \
  --cov-report=term-missing \
  --timeout=300
```

## Test Coverage Goals

- **Unit Tests**: >90% line coverage
- **Integration Tests**: >80% workflow coverage  
- **Error Handling**: 100% error path coverage
- **Performance**: All concurrent scenarios tested

### Checking Coverage

```bash
# Generate HTML coverage report
pytest test_assemblyai_integration.py --cov=voice_handler --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Debugging Tests

### Verbose Output

```bash
# Maximum verbosity
pytest test_assemblyai_integration.py -vvv --tb=long

# Show print statements
pytest test_assemblyai_integration.py -s

# Run single test with debugging
pytest test_assemblyai_integration.py::TestVoiceProcessingConfig::test_config_initialization_full -vvv
```

### Capturing Logs

```python
def test_with_logs(self, capture_logs):
    # Test code that generates logs
    result = voice_handler.process_message()
    
    # Check logs
    logs = capture_logs.getvalue()
    assert "Processing voice message" in logs
```

### Performance Profiling

```python
def test_with_performance_tracking(self):
    with PerformanceTracker() as tracker:
        # Code to profile
        result = expensive_operation()
        
        # Check performance
        assert tracker.elapsed_time() < 5.0
        
    metrics = tracker.get_metrics()
    print(f"Operation took {metrics['elapsed_time']:.2f}s")
```

## Best Practices

### Writing New Tests

1. **Use descriptive names**: `test_transcription_succeeds_with_high_confidence`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test one thing**: Each test should verify one specific behavior
4. **Use appropriate markers**: Tag tests with relevant markers
5. **Mock external dependencies**: Don't make real API calls in unit tests
6. **Clean up resources**: Use fixtures and context managers
7. **Test error cases**: Include both happy and sad paths

### Test Organization

```python
class TestFeatureName:
    """Test specific feature with clear organization"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup common to all tests in this class"""
        pass
    
    def test_success_case(self):
        """Test the happy path"""
        pass
    
    def test_error_case(self):
        """Test error handling"""
        pass
    
    @pytest.mark.performance
    def test_performance_case(self):
        """Test performance aspects"""
        pass
```

### Mock Strategy

1. **Mock at boundaries**: Mock external services, not internal logic
2. **Use realistic data**: Mock responses should match real API responses
3. **Test mock setup**: Verify mocks are called correctly
4. **Fail fast**: Make tests fail quickly if setup is wrong

### Async Testing

```python
@pytest.mark.asyncio
async def test_async_operation(self):
    """Test async operations properly"""
    result = await async_function()
    assert result is not None
    
    # Test timeouts
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1.0)
```

## Troubleshooting

### Common Issues

1. **Import errors**: Check that all dependencies are installed
2. **Fixture not found**: Make sure conftest.py is in the right location
3. **Async warnings**: Use `pytest-asyncio` and proper async fixtures
4. **Mock not working**: Verify patch target path is correct
5. **Tests hang**: Check for infinite loops or missing timeouts

### Test Failures

```bash
# Run failed tests only
pytest --lf

# Run tests that failed last time
pytest --ff

# Stop on first failure
pytest -x

# Run specific test with pdb debugger
pytest --pdb test_assemblyai_integration.py::TestClass::test_method
```

## Contributing

When adding new features to the voice processing system:

1. **Write tests first**: Follow TDD approach
2. **Update test documentation**: Add new test cases to this document
3. **Run full test suite**: Ensure all tests pass
4. **Check coverage**: Maintain high coverage levels
5. **Update CI**: Modify GitHub Actions if needed

### Test Review Checklist

- [ ] Tests cover both success and failure cases
- [ ] Appropriate use of mocks and fixtures
- [ ] Tests are fast and deterministic
- [ ] Error messages are helpful
- [ ] Performance implications considered
- [ ] Documentation updated
- [ ] CI pipeline passes

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [AssemblyAI Python SDK Documentation](https://www.assemblyai.com/docs/)

## Conclusion

This comprehensive test suite ensures the reliability, performance, and maintainability of the AssemblyAI voice processing integration. By following the testing patterns and practices outlined in this documentation, developers can confidently add new features and modifications while maintaining system quality.

The test suite is designed to:
- **Run fast** for quick development feedback
- **Provide comprehensive coverage** of all system components
- **Support CI/CD pipelines** with appropriate test categorization
- **Enable safe refactoring** through thorough regression testing
- **Document expected behavior** through clear test cases

Regular execution of this test suite ensures the voice processing system continues to function reliably as the codebase evolves.