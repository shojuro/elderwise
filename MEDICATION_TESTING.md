# ElderWise Medication Testing Guide

## Overview

This guide covers the comprehensive test suite for the ElderWise medication identification and management features. The tests ensure reliability, accuracy, and safety of medication-related functionality.

## Test Structure

### Backend Tests

#### 1. **Service Tests** (`tests/test_medication_services.py`)
Tests for core medication services:

- **VisionService Tests**
  - Image analysis with local processing
  - Google Vision API integration
  - Shape and color detection
  - Image validation and enhancement
  
- **MedicationDatabaseService Tests**
  - Medication identification by imprint
  - Detailed medication information retrieval
  - Drug interaction checking
  - Food interaction detection
  - Dosage validation
  - Mock and real API switching

- **RxNormClient Tests**
  - RxImage API search functionality
  - RxNorm medication details retrieval
  - FDA label information parsing
  - Color and shape normalization

- **GoogleVisionClient Tests**
  - Text extraction and filtering
  - Color detection and naming
  - Image enhancement for OCR

#### 2. **API Endpoint Tests** (`tests/test_medication_api.py`)
Tests for medication REST API endpoints:

- `/medications/identify` - Photo identification
- `/medications/{medication_id}` - Get details
- `/medications/search` - Search by name
- `/medications/user` - User medication management
- `/medications/interactions` - Drug interaction checking
- `/medications/validate-dosage` - Dosage validation

### Frontend Tests

#### Component Tests (`src/__tests__/MedicationScreen.test.tsx`)
- Medication screen rendering
- Camera integration and permissions
- Medication identification flow
- User medication management
- Drug interaction UI
- Accessibility compliance
- Error handling and edge cases

## Running Tests

### Quick Start
```bash
# Run all medication tests
python run_medication_tests.py

# Run specific test categories
pytest tests/test_medication_services.py -v
pytest tests/test_medication_api.py -v
cd frontend && npm test MedicationScreen.test.tsx
```

### Individual Test Suites

#### Backend Service Tests
```bash
# Run all service tests
pytest tests/test_medication_services.py

# Run specific test class
pytest tests/test_medication_services.py::TestVisionService -v

# Run specific test
pytest tests/test_medication_services.py::TestVisionService::test_analyze_medication_image_local -v
```

#### API Tests
```bash
# Run all API tests
pytest tests/test_medication_api.py

# Test specific endpoint
pytest tests/test_medication_api.py::TestMedicationAPI::test_identify_medication_by_photo -v
```

#### Frontend Tests
```bash
cd frontend

# Run all frontend tests
npm test

# Run medication screen tests
npm test MedicationScreen.test.tsx

# Run with coverage
npm test -- --coverage MedicationScreen.test.tsx
```

## Test Coverage

### Backend Coverage
```bash
# Generate coverage report
pytest tests/test_medication_*.py --cov=src.services --cov=src.api --cov-report=html

# View coverage
open htmlcov/index.html
```

### Frontend Coverage
```bash
cd frontend
npm test -- --coverage --watchAll=false
```

## Test Data

### Mock Medications
The test suite includes mock data for common medications:

1. **Acetaminophen (L484)**
   - Generic: acetaminophen
   - Brand: Tylenol
   - Shape: oval, Color: white

2. **Amoxicillin (TEVA 3109)**
   - Generic: amoxicillin
   - Brand: Amoxil
   - Shape: capsule, Color: pink

3. **Hydrocodone/Acetaminophen (M367)**
   - Generic: hydrocodone/acetaminophen
   - Brand: Norco, Vicodin
   - Shape: oblong, Color: white

### Test Images
Create test images using PIL:
```python
from PIL import Image
import base64
import io

# Create test pill image
img = Image.new('RGB', (200, 150), color='white')
buffer = io.BytesIO()
img.save(buffer, format='PNG')
image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
```

## Mocking External APIs

### Google Vision API
```python
with patch('src.services.vision.google_vision_client') as mock_client:
    mock_client.extract_text = AsyncMock(return_value=["L484"])
    mock_client.detect_colors = AsyncMock(return_value=[
        {"name": "white", "score": 0.9}
    ])
```

### RxNorm/RxImage APIs
```python
with patch('src.services.medication_db.rxnorm_client') as mock_client:
    mock_client.search_by_imprint = AsyncMock(return_value=[{
        "name": "Acetaminophen 500 mg",
        "rxcui": "198440",
        "shape": "OVAL",
        "color": ["WHITE"],
        "imprint": "L484"
    }])
```

## Environment Setup

### Test Environment Variables
Tests automatically set up required environment variables:
```python
# In conftest.py
@pytest.fixture(autouse=True)
def mock_medication_env_vars(monkeypatch):
    monkeypatch.setenv("RXIMAGE_BASE_URL", "http://rximage.nlm.nih.gov/api/rximage/1")
    monkeypatch.setenv("RXNORM_BASE_URL", "https://rxnav.nlm.nih.gov/REST")
    monkeypatch.setenv("FDA_API_BASE_URL", "https://api.fda.gov/drug")
```

### API Key Testing
- Tests run without API keys by default (using mocks)
- To test with real APIs, set environment variables:
  ```bash
  export GOOGLE_VISION_API_KEY=your_key_here
  pytest tests/test_medication_services.py -k "with_google_vision"
  ```

## Common Test Patterns

### Async Test Pattern
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### API Endpoint Testing
```python
def test_api_endpoint(client):
    response = client.post("/medications/identify", json={"image": image_data})
    assert response.status_code == 200
    assert "medications" in response.json()
```

### Component Testing
```typescript
it('displays medication details', async () => {
  renderComponent();
  
  await waitFor(() => {
    expect(screen.getByText('Acetaminophen 500 mg')).toBeInTheDocument();
  });
  
  const detailsButton = screen.getByRole('button', { name: /view details/i });
  await user.click(detailsButton);
  
  expect(screen.getByText('Medication Details')).toBeInTheDocument();
});
```

## Debugging Failed Tests

### Verbose Output
```bash
# Show detailed test output
pytest -vv tests/test_medication_services.py

# Show print statements
pytest -s tests/test_medication_services.py
```

### Debugging Specific Tests
```python
# Add breakpoint in test
import pdb; pdb.set_trace()

# Or use pytest debugging
pytest --pdb tests/test_medication_services.py
```

### Frontend Test Debugging
```typescript
// Add debug output
screen.debug();

// Find elements
screen.getByRole('button', { name: /take photo/i });
screen.getByText(/medication identified/i);
```

## Continuous Integration

### GitHub Actions Configuration
```yaml
name: Medication Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        cd frontend && npm install
    
    - name: Run medication tests
      run: python run_medication_tests.py
```

## Safety Testing

### Critical Safety Tests
1. **Drug Interaction Detection**
   - Contraindicated combinations
   - Severity levels
   - Clear warnings

2. **Dosage Validation**
   - Maximum daily limits
   - Single dose warnings
   - Elder-specific considerations

3. **Error Handling**
   - API failures
   - Invalid images
   - Network issues

### Elder-Friendly UI Tests
1. **Accessibility**
   - Large text
   - High contrast
   - Clear navigation

2. **Error Messages**
   - Simple language
   - Clear instructions
   - No technical jargon

## Performance Testing

### Load Testing
```python
@pytest.mark.performance
async def test_concurrent_identifications():
    tasks = []
    for _ in range(10):
        tasks.append(medication_db.identify_by_imprint("L484"))
    
    results = await asyncio.gather(*tasks)
    assert all(len(r) > 0 for r in results)
```

### Response Time Testing
```python
import time

async def test_identification_speed():
    start = time.time()
    await vision_service.analyze_medication_image(image_data)
    elapsed = time.time() - start
    
    assert elapsed < 2.0  # Should complete within 2 seconds
```

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on others
2. **Mock External Services**: Always mock external API calls in unit tests
3. **Test Edge Cases**: Include tests for error conditions and edge cases
4. **Descriptive Names**: Use clear, descriptive test names
5. **Arrange-Act-Assert**: Follow the AAA pattern in tests
6. **Regular Updates**: Update tests when APIs or requirements change

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure project root is in Python path
   export PYTHONPATH=/path/to/ElderWise:$PYTHONPATH
   ```

2. **Async Test Failures**
   ```python
   # Use pytest-asyncio
   pip install pytest-asyncio
   ```

3. **Frontend Test Failures**
   ```bash
   # Clear cache and reinstall
   cd frontend
   rm -rf node_modules
   npm install
   ```

The medication testing suite ensures the safety and reliability of one of ElderWise's most critical features - helping elderly users safely identify and manage their medications.