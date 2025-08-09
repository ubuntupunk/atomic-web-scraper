# Atomic Scraper Tool

Next-generation intelligent web scraping tool built with the Atomic Agents framework. This AI-powered tool provides advanced natural language processing, dynamic strategy generation, and ethical data extraction capabilities with unprecedented intelligence and ease of use.

## Features

- 🤖 **AI-Powered Planning**: Natural language scraping requests with intelligent strategy generation
- 🔍 **Dynamic Analysis**: Automatic website structure analysis and schema recipe generation
- 📊 **Quality Scoring**: Built-in data quality assessment and validation
- 🛡️ **Ethical Compliance**: Robots.txt respect, rate limiting, and privacy compliance
- 🧪 **Comprehensive Testing**: Mock website generation and integration testing
- 📈 **Performance Monitoring**: Built-in metrics and performance tracking

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from atomic_scraper_tool.main import AtomicScraperApp

# Initialize the application
app = AtomicScraperApp()

# Start interactive chat interface
app.run()
```

### Programmatic Usage

```python
from atomic_scraper_tool.tools.atomic_scraper_tool import AtomicScraperTool
from atomic_scraper_tool.models.schema_models import SchemaRecipe

# Create scraper tool
scraper = AtomicScraperTool()

# Define scraping parameters
scraping_params = {
    'target_url': 'https://example.com/products',
    'strategy': {
        'scrape_type': 'list',
        'pagination_enabled': True,
        'max_pages': 5
    },
    'schema_recipe': {
        'fields': {
            'title': {'selector': 'h2.product-title', 'type': 'text'},
            'price': {'selector': '.price', 'type': 'text'},
            'rating': {'selector': '.rating', 'type': 'text'},
            'description': {'selector': '.description', 'type': 'text'}
        }
    },
    'max_results': 100
}

# Execute scraping
result = scraper.run(scraping_params)

# Access results
print(f"Scraped {result.results['total_scraped']} items")
for item in result.results['items']:
    print(f"Title: {item['title']}, Price: {item['price']}")
```

## Architecture

The Atomic Scraper Tool is built with a modular, next-generation architecture:

```
atomic_scraper_tool/
├── agents/                 # AI agents for planning and coordination
├── analysis/              # Website analysis and strategy generation
├── compliance/            # Ethical scraping compliance features
├── config/                # Configuration management
├── core/                  # Core interfaces and error handling
├── extraction/            # Content extraction and quality analysis
├── models/                # Data models and schemas
├── testing/               # Mock websites and test scenarios
├── tools/                 # Main scraper tool implementation
└── main.py               # Application entry point
```

## Core Components

### 1. Scraper Planning Agent

The `AtomicScraperPlanningAgent` interprets natural language requests and generates scraping strategies:

```python
from atomic_scraper_tool.agents.scraper_planning_agent import AtomicScraperPlanningAgent

agent = AtomicScraperPlanningAgent()

request = {
    'url': 'https://example.com',
    'description': 'Extract product information including names, prices, and ratings'
}

strategy = agent.run(request)
print(strategy['reasoning'])
```

### 2. Website Analyzer

Automatically analyzes website structure and identifies content patterns:

```python
from atomic_scraper_tool.analysis.website_analyzer import WebsiteAnalyzer

analyzer = WebsiteAnalyzer()
analysis = analyzer.analyze_website('https://example.com')

print(f"Detected content type: {analysis.content_type}")
print(f"Pagination detected: {analysis.has_pagination}")
```

### 3. Schema Recipe Generator

Generates dynamic extraction schemas based on website analysis:

```python
from atomic_scraper_tool.analysis.schema_recipe_generator import SchemaRecipeGenerator

generator = SchemaRecipeGenerator()
schema = generator.generate_schema_recipe(analysis_result)

print(f"Generated {len(schema.fields)} extraction fields")
```

### 4. Content Extractor

Extracts structured data using CSS selectors and XPath:

```python
from atomic_scraper_tool.extraction.content_extractor import ContentExtractor

extractor = ContentExtractor()
extracted_data = extractor.extract_content(html, extraction_rules)

print(f"Extracted {len(extracted_data)} items")
```

### 5. Quality Analyzer

Assesses data quality and completeness:

```python
from atomic_scraper_tool.extraction.quality_analyzer import QualityAnalyzer

analyzer = QualityAnalyzer()
quality_score = analyzer.calculate_quality_score(extracted_data, schema_recipe)

print(f"Data quality score: {quality_score:.2f}")
```

## Compliance Features

### Robots.txt Compliance

```python
from atomic_scraper_tool.compliance.robots_parser import RobotsParser

parser = RobotsParser(user_agent="MyBot/1.0")

# Check if URL can be fetched
if parser.can_fetch('https://example.com/products'):
    print("URL is allowed by robots.txt")

# Get crawl delay
delay = parser.get_crawl_delay('https://example.com')
print(f"Recommended crawl delay: {delay} seconds")
```

### Rate Limiting

```python
from atomic_scraper_tool.compliance.rate_limiter import RateLimiter, RateLimitConfig

config = RateLimitConfig(
    default_delay=1.0,
    max_concurrent_requests=3,
    adaptive_delay_enabled=True
)

limiter = RateLimiter(config)

# Apply rate limiting
delay = limiter.wait_for_request('https://example.com/page1')
print(f"Applied delay: {delay} seconds")
```

### Privacy Compliance

```python
from atomic_scraper_tool.compliance.privacy_compliance import PrivacyComplianceChecker

checker = PrivacyComplianceChecker()

# Validate data collection
scraped_data = {'name': 'Product Name', 'price': '$19.99'}
is_compliant = checker.validate_data_collection('https://example.com', scraped_data)

if is_compliant:
    print("Data collection is compliant")
```

## Configuration

### Basic Configuration

```python
from atomic_scraper_tool.config.scraper_config import AtomicScraperConfig

config = AtomicScraperConfig(
    base_url="https://example.com",
    max_concurrent_requests=5,
    request_delay=1.0,
    timeout=30,
    user_agent="AtomicScraperTool/1.0"
)
```

### Advanced Configuration

```python
config = AtomicScraperConfig(
    # Request settings
    max_concurrent_requests=3,
    request_delay=2.0,
    timeout=60,
    max_retries=3,
    
    # Quality settings
    min_quality_score=0.7,
    enable_quality_filtering=True,
    
    # Compliance settings
    respect_robots_txt=True,
    enable_rate_limiting=True,
    privacy_compliance_enabled=True,
    
    # Output settings
    output_format="json",
    include_metadata=True,
    enable_data_validation=True
)
```

## Testing

### Mock Website Generation

```python
from atomic_scraper_tool.testing.mock_website import MockWebsiteGenerator

# Create mock e-commerce site
mock_site = MockWebsiteGenerator.create_ecommerce_site(num_products=50)

# Generate test pages
homepage = mock_site.generate_page("/")
product_page = mock_site.generate_page("/product/1")

# Get all available URLs
urls = mock_site.get_all_urls()
```

### Test Scenarios

```python
from atomic_scraper_tool.testing.test_scenarios import ScenarioGenerator, ScenarioType

generator = ScenarioGenerator()

# Generate test scenario
scenario = generator.generate_scenario(ScenarioType.BASIC_SCRAPING)

# Test with scenario
for url in scenario.test_urls:
    html = scenario.mock_website.generate_page(url)
    # Run validation rules
    for rule in scenario.validation_rules:
        assert rule(html)
```

## Error Handling

The tool provides comprehensive error handling:

```python
from atomic_scraper_tool.core.exceptions import ScrapingError

try:
    result = scraper.run(scraping_params)
except ScrapingError as e:
    print(f"Scraping error: {e.message}")
    print(f"Error type: {e.error_type}")
    print(f"URL: {e.url}")
    
    # Handle specific error types
    if e.error_type == "network_error":
        # Retry with different settings
        pass
    elif e.error_type == "parsing_error":
        # Adjust extraction rules
        pass
```

## Performance Optimization

### Concurrent Scraping

```python
import asyncio
from atomic_scraper_tool.tools.atomic_scraper_tool import AtomicScraperTool

async def scrape_multiple_urls(urls):
    scraper = AtomicScraperTool()
    tasks = []
    
    for url in urls:
        task = asyncio.create_task(scraper.run_async({
            'target_url': url,
            'strategy': {'scrape_type': 'detail'},
            'schema_recipe': schema
        }))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

### Memory Management

```python
# Enable streaming for large datasets
config = AtomicScraperConfig(
    enable_streaming=True,
    batch_size=100,
    memory_limit_mb=500
)

scraper = AtomicScraperTool(config=config)
```

## Best Practices

### 1. Respectful Scraping

- Always check robots.txt before scraping
- Use appropriate delays between requests
- Limit concurrent requests per domain
- Respect rate limiting headers

### 2. Data Quality

- Validate extracted data against expected schemas
- Implement quality thresholds
- Handle missing or malformed data gracefully
- Use data cleaning and normalization

### 3. Error Handling

- Implement retry logic for transient failures
- Log errors for debugging and monitoring
- Provide fallback strategies for critical failures
- Monitor success rates and performance metrics

### 4. Performance

- Use caching for repeated requests
- Implement connection pooling
- Monitor memory usage for large datasets
- Use streaming for processing large amounts of data

## API Reference

### Core Classes

#### AtomicScraperTool

Main scraping tool class.

**Methods:**
- `run(input_data)`: Execute scraping operation
- `validate_inputs(input_data)`: Validate input parameters
- `get_supported_formats()`: Get supported output formats

#### AtomicScraperPlanningAgent

AI agent for scraping strategy planning.

**Methods:**
- `run(request)`: Generate scraping strategy from natural language
- `parse_request(description)`: Parse user request
- `generate_strategy(analysis)`: Generate scraping strategy

#### WebsiteAnalyzer

Website structure analysis.

**Methods:**
- `analyze_website(url)`: Analyze website structure
- `detect_content_type(html)`: Detect content type
- `find_pagination(html)`: Detect pagination patterns

### Data Models

#### ScrapingStrategy

Defines scraping approach and parameters.

**Fields:**
- `scrape_type`: Type of scraping (list, detail, search, sitemap)
- `pagination_enabled`: Enable pagination handling
- `max_pages`: Maximum pages to scrape
- `selectors`: CSS selectors for content extraction

#### SchemaRecipe

Defines data extraction schema.

**Fields:**
- `fields`: Dictionary of field definitions
- `quality_weights`: Quality weights for fields
- `validation_rules`: Data validation rules

#### ScrapingResult

Contains scraping results and metadata.

**Fields:**
- `items`: Extracted data items
- `total_found`: Total items found
- `total_scraped`: Total items scraped
- `quality_score`: Overall quality score
- `execution_time`: Scraping execution time

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Problem Solving

### Common Issues and Solutions

#### 1. Missing pyproject.toml File

**Problem**: The project was missing its main `pyproject.toml` configuration file, only having a backup file (`pyproject.toml.bak`).

**Solution**: 
```bash
# Restore from backup
cp pyproject.toml.bak pyproject.toml
```

**Root Cause**: The main configuration file was accidentally moved to backup during development.

#### 2. TOML Parsing Errors

**Problem**: Invalid TOML syntax error: "Unexpected character: '[' at line 1 col 1"

**Solution**: 
- Check for stray characters at the beginning of the file
- Ensure proper TOML section header format: `[tool.poetry]` not `t[tool.poetry]`

**Prevention**: Use a TOML validator or IDE with TOML syntax highlighting.

#### 3. Module Import Errors with Poetry

**Problem**: `ModuleNotFoundError: No module named 'atomic_scraper_tool'` when running with Poetry.

**Solutions**:

**Option A - Run from parent directory with PYTHONPATH:**
```bash
PYTHONPATH=. poetry -C atomic_scraper_tool run python -m atomic_scraper_tool.main --help
```

**Option B - Run main.py directly (for development):**
```bash
cd atomic_scraper_tool
poetry run python main.py --help
```

**Option C - Install in development mode:**
```bash
cd atomic_scraper_tool
poetry install
# Then run as module from parent directory
```

**Root Cause**: Poetry doesn't automatically add the current directory to Python path when running modules.

#### 4. Syntax Errors in main.py

**Problem**: Various syntax errors including:
- Unterminated string literals
- Unmatched parentheses  
- Incorrect class references (`WebsiteScraperApp` vs `AtomicScraperApp`)

**Solution**: 
- Restore from git: `git restore main.py`
- Fix class name references to match actual class definition
- Ensure proper string termination and parentheses matching

**Prevention**: Use proper IDE with syntax checking and run syntax validation before commits.

#### 5. Script Entry Points

**Problem**: No script entry points defined in `pyproject.toml` for easy CLI access.

**Solution**: Add script entry points to `pyproject.toml`:
```toml
[tool.poetry.scripts]
atomic-scraper = "atomic_scraper_tool.main:main"
```

Then install and run:
```bash
poetry install
poetry run atomic-scraper --help
```

#### 6. Relative Import Issues

**Problem**: `ImportError: attempted relative import with no known parent package` when running main.py directly.

**Solution**: 
- Run as module: `python -m atomic_scraper_tool.main`
- Or run from parent directory with proper PYTHONPATH
- Avoid running files with relative imports directly as scripts

**Root Cause**: Python treats files run directly as `__main__` module, breaking relative imports.

### Development Workflow

For smooth development, follow this workflow:

1. **Setup Environment**:
   ```bash
   cd atomic_scraper_tool
   poetry install
   ```

2. **Run Application**:
   ```bash
   # From parent directory
   PYTHONPATH=. poetry -C atomic_scraper_tool run python -m atomic_scraper_tool.main
   
   # Or with script entry point (after poetry install)
   poetry run atomic-scraper
   ```

3. **Development Testing**:
   ```bash
   # Quick syntax check
   poetry run python -m py_compile main.py
   
   # Run help to verify
   poetry run atomic-scraper --help
   ```

4. **Troubleshooting Checklist**:
   - [ ] `pyproject.toml` exists and is valid TOML
   - [ ] Poetry environment is activated
   - [ ] No syntax errors in Python files
   - [ ] Class names match between definition and usage
   - [ ] Running from correct directory with proper PYTHONPATH

## Orchestration Integration

The Atomic Scraper Tool supports integration with orchestrators like `atomic-cli` and `intelligent-web-scraper` through model provider injection.

### Standalone Mode

When run independently, the tool uses its own model provider configuration:

```bash
# Uses environment variables like OPENAI_API_KEY
atomic-scraper

# Or with explicit config
atomic-scraper --config my_config.json
```

### Orchestrated Mode

When called by orchestrators, the model provider is injected:

```python
import instructor
import openai
from atomic_scraper_tool.main import create_orchestrated_app

# Create shared client
client = instructor.from_openai(openai.OpenAI())

# Create orchestrated app with injected client
app = create_orchestrated_app(
    config={
        "scraper": {
            "max_results": 50,
            "quality_threshold": 70.0
        }
    },
    client=client  # Injected model provider
)

# Use the app programmatically
# app.run() or call specific methods
```

### Integration Metadata

For ecosystem discovery and integration:

```python
from atomic_scraper_tool.main import get_orchestration_metadata

metadata = get_orchestration_metadata()
print(f"Tool: {metadata['name']}")
print(f"Supports client injection: {metadata['supports_client_injection']}")
print(f"Factory function: {metadata['factory_function']}")
```

### Execution Modes

1. **Standalone Mode**: 
   - Uses own API keys from environment
   - Full interactive CLI interface
   - Independent operation

2. **Orchestrated Mode**:
   - Receives model provider from orchestrator
   - Shared client configuration
   - Coordinated with other agents

This pattern ensures:
- **Consistency**: Same model provider across all agents
- **Efficiency**: Shared client connections and configuration
- **Flexibility**: Works both standalone and orchestrated
- **Scalability**: Proper resource management in multi-agent scenarios

## Support

For questions, issues, or contributions, please visit our GitHub repository or contact the development team.