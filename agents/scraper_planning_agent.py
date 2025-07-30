"""
Scraper Planning Agent for the website scraper tool.

Main conversational agent that interprets user requests and coordinates scraping operations.
"""

from typing import Dict, Any, Optional
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig
from atomic_agents.lib.base.base_io_schema import BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator, SystemPromptContextProviderBase
from pydantic import Field

from ..models.base_models import ScrapingStrategy
from ..models.schema_models import SchemaRecipe


class ScraperAgentInputSchema(BaseIOSchema):
    """Input schema for the scraper planning agent."""
    
    request: str = Field(..., description="Natural language scraping request")
    target_url: str = Field(..., description="Website URL to scrape")
    max_results: int = Field(10, ge=1, le=1000, description="Maximum items to return")
    quality_threshold: float = Field(50.0, ge=0.0, le=100.0, description="Minimum quality score")


class ScraperAgentOutputSchema(BaseIOSchema):
    """Output schema for the scraper planning agent."""
    
    scraping_plan: str = Field(..., description="Human-readable scraping plan")
    strategy: Dict[str, Any] = Field(..., description="Generated scraping strategy")
    schema_recipe: Dict[str, Any] = Field(..., description="Dynamic JSON schema recipe")
    reasoning: str = Field(..., description="Agent's reasoning process")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the plan")


class ScrapingContextProvider(SystemPromptContextProviderBase):
    """Context provider for scraping strategy planning."""
    
    def __init__(self):
        """Initialize the scraping context provider."""
        super().__init__(title="Website Scraping Capabilities")
    
    def get_info(self) -> str:
        """Provide context about scraping capabilities and strategies."""
        return """You are an expert website scraping planning agent. Your role is to analyze user requests and target websites to generate optimal scraping strategies.

### Scraping Types Available:
- **list**: Extract multiple items from list pages (e.g., product listings, article lists)
- **detail**: Extract detailed information from individual pages
- **search**: Extract results from search pages
- **sitemap**: Extract URLs and metadata from sitemaps

### Strategy Components:
- **target_selectors**: CSS selectors to identify content containers
- **extraction_rules**: Field-specific extraction rules with CSS selectors
- **pagination_strategy**: How to handle multiple pages (next_link, page_numbers, infinite_scroll, load_more)
- **content_filters**: Rules to filter out unwanted content
- **quality_thresholds**: Minimum quality scores for extracted data

### Schema Recipe Generation:
- Analyze website structure to identify data patterns
- Generate appropriate field definitions with extraction selectors
- Set quality weights based on field importance
- Create validation rules for data integrity

### Best Practices:
- Always respect robots.txt and rate limiting
- Prefer specific CSS selectors over generic ones
- Include fallback selectors for robustness
- Set appropriate quality thresholds based on data criticality
- Consider pagination and dynamic content loading"""


class ScraperPlanningAgent(BaseAgent):
    """
    Main conversational agent for website scraping planning.
    
    This agent interprets natural language requests, analyzes target websites,
    and generates appropriate scraping strategies and schema recipes.
    """
    
    def __init__(self, config: BaseAgentConfig):
        """
        Initialize the scraper planning agent.
        
        Args:
            config: Agent configuration with client and model settings
        """
        # Set up system prompt generator with scraping context
        context_providers = {"scraping_context": ScrapingContextProvider()}
        system_prompt_generator = SystemPromptGenerator(
            background=[
                "You are an expert website scraping planning agent.",
                "Your role is to analyze user requests and target websites to generate optimal scraping strategies.",
                "You understand website structures and can create appropriate extraction strategies."
            ],
            steps=[
                "Analyze the user's natural language request to understand what data they want to extract",
                "Examine the target website structure and content patterns",
                "Determine the most appropriate scraping strategy (list, detail, search, sitemap)",
                "Generate CSS selectors and extraction rules for the identified data",
                "Create a dynamic schema recipe that matches the expected data structure",
                "Provide reasoning for your decisions and confidence in the strategy"
            ],
            output_instructions=[
                "Always provide a clear, human-readable scraping plan",
                "Include specific CSS selectors and extraction strategies",
                "Generate a complete schema recipe with field definitions",
                "Explain your reasoning process and decision-making",
                "Provide a confidence score between 0.0 and 1.0"
            ],
            context_providers=context_providers
        )
        
        # Update config with our schemas and system prompt generator
        config.input_schema = ScraperAgentInputSchema
        config.output_schema = ScraperAgentOutputSchema
        config.system_prompt_generator = system_prompt_generator
        
        super().__init__(config)
    
    def run(self, input_data: ScraperAgentInputSchema) -> ScraperAgentOutputSchema:
        """
        Process scraping request and generate plan.
        
        Args:
            input_data: User's scraping request and parameters
            
        Returns:
            Generated scraping plan with strategy and schema
        """
        try:
            # Parse the natural language request
            parsed_request = self._parse_natural_language_request(input_data.request)
            
            # Analyze the target website
            website_analysis = self._analyze_target_website(input_data.target_url)
            
            # Generate scraping strategy
            strategy = self._generate_scraping_strategy(
                website_analysis, 
                parsed_request, 
                input_data
            )
            
            # Generate schema recipe
            schema_recipe = self._generate_schema_recipe(
                website_analysis, 
                parsed_request, 
                input_data
            )
            
            # Generate human-readable plan
            scraping_plan = self._generate_scraping_plan(
                strategy, 
                schema_recipe, 
                parsed_request
            )
            
            # Generate reasoning explanation
            reasoning = self._generate_reasoning(
                website_analysis, 
                strategy, 
                schema_recipe, 
                parsed_request
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(
                website_analysis, 
                strategy, 
                schema_recipe
            )
            
            return ScraperAgentOutputSchema(
                scraping_plan=scraping_plan,
                strategy=strategy.model_dump(),
                schema_recipe=schema_recipe.model_dump(),
                reasoning=reasoning,
                confidence=confidence
            )
            
        except Exception as e:
            # Handle errors gracefully
            return self._handle_error(str(e), input_data)
    
    def _parse_natural_language_request(self, request: str) -> Dict[str, Any]:
        """Parse natural language request to extract key information."""
        request_lower = request.lower()
        
        parsed = {
            'content_type': 'list',  # Default
            'target_data': [],
            'filters': [],
            'keywords': [],
            'temporal_filters': [],
            'location_filters': []
        }
        
        # Determine content type
        if any(word in request_lower for word in ['list', 'items', 'multiple', 'all']):
            parsed['content_type'] = 'list'
        elif any(word in request_lower for word in ['detail', 'information', 'about', 'specific']):
            parsed['content_type'] = 'detail'
        elif any(word in request_lower for word in ['search', 'find', 'results']):
            parsed['content_type'] = 'search'
        
        # Extract target data types
        data_indicators = {
            'markets': ['market', 'marketplace', 'bazaar'],
            'events': ['event', 'happening', 'activity'],
            'products': ['product', 'item', 'goods'],
            'articles': ['article', 'post', 'blog', 'news'],
            'contacts': ['contact', 'phone', 'email', 'address'],
            'prices': ['price', 'cost', 'fee', 'rate'],
            'dates': ['date', 'time', 'when', 'schedule'],
            'locations': ['location', 'place', 'where', 'address']
        }
        
        for data_type, indicators in data_indicators.items():
            if any(indicator in request_lower for indicator in indicators):
                parsed['target_data'].append(data_type)
        
        # Extract temporal filters
        temporal_keywords = ['saturday', 'sunday', 'weekend', 'today', 'tomorrow', 'this week']
        for keyword in temporal_keywords:
            if keyword in request_lower:
                parsed['temporal_filters'].append(keyword)
        
        # Extract location filters
        location_keywords = ['cape town', 'johannesburg', 'durban', 'local', 'nearby']
        for keyword in location_keywords:
            if keyword in request_lower:
                parsed['location_filters'].append(keyword)
        
        # Extract general keywords
        import re
        words = re.findall(r'\b\w+\b', request_lower)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'scrape', 'get', 'find'}
        parsed['keywords'] = [word for word in words if word not in stop_words and len(word) > 2]
        
        return parsed
    
    def _analyze_target_website(self, url: str) -> 'WebsiteStructureAnalysis':
        """Analyze the target website structure."""
        from ..analysis.website_analyzer import WebsiteAnalyzer
        import requests
        from bs4 import BeautifulSoup
        
        try:
            # Fetch the website content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Analyze the website structure
            analyzer = WebsiteAnalyzer()
            analysis = analyzer.analyze_website(response.text, url)
            
            return analysis
            
        except Exception as e:
            # Create a minimal analysis if website fetch fails
            from ..analysis.website_analyzer import WebsiteStructureAnalysis
            return WebsiteStructureAnalysis(
                url=url,
                title="Unknown Website",
                content_patterns=[],
                metadata={'error': str(e)}
            )
    
    def _generate_scraping_strategy(
        self, 
        analysis: 'WebsiteStructureAnalysis', 
        parsed_request: Dict[str, Any], 
        input_data: ScraperAgentInputSchema
    ) -> ScrapingStrategy:
        """Generate optimal scraping strategy."""
        from ..analysis.strategy_generator import StrategyGenerator, StrategyContext
        
        # Create strategy context
        context = StrategyContext(
            user_criteria=input_data.request,
            target_content_type=parsed_request['content_type'],
            quality_threshold=input_data.quality_threshold,
            max_results=input_data.max_results,
            include_pagination=True,
            extraction_depth='medium'
        )
        
        # Generate strategy
        generator = StrategyGenerator()
        strategy = generator.generate_strategy(analysis, context)
        
        return strategy
    
    def _generate_schema_recipe(
        self, 
        analysis: 'WebsiteStructureAnalysis', 
        parsed_request: Dict[str, Any], 
        input_data: ScraperAgentInputSchema
    ) -> 'SchemaRecipe':
        """Generate dynamic schema recipe."""
        from ..analysis.schema_recipe_generator import SchemaRecipeGenerator, SchemaGenerationContext
        
        # Create schema generation context
        context = SchemaGenerationContext(
            user_criteria=input_data.request,
            target_content_type=parsed_request['content_type'],
            sample_html="",  # Would be populated with actual HTML in real implementation
            quality_requirements={
                "completeness": 0.4,
                "accuracy": 0.4,
                "consistency": 0.2
            },
            field_preferences=parsed_request['target_data']
        )
        
        # Generate schema recipe
        generator = SchemaRecipeGenerator()
        
        # For now, create a basic schema recipe since we don't have HTML content
        # In a real implementation, this would use the actual website HTML
        schema_recipe = self._create_basic_schema_recipe(parsed_request, input_data)
        
        return schema_recipe
    
    def _create_basic_schema_recipe(
        self, 
        parsed_request: Dict[str, Any], 
        input_data: ScraperAgentInputSchema
    ) -> 'SchemaRecipe':
        """Create a basic schema recipe based on parsed request."""
        from ..models.schema_models import SchemaRecipe, FieldDefinition
        
        # Determine fields based on target data
        fields = {}
        
        # Always include basic fields
        fields['title'] = FieldDefinition(
            field_type='string',
            description='Title or name of the item',
            extraction_selector='h1, h2, h3, .title, .name',
            required=True,
            quality_weight=0.9,
            post_processing=['trim', 'clean']
        )
        
        fields['description'] = FieldDefinition(
            field_type='string',
            description='Description or summary of the item',
            extraction_selector='p, .description, .summary, .content',
            required=False,
            quality_weight=0.7,
            post_processing=['trim', 'clean']
        )
        
        fields['url'] = FieldDefinition(
            field_type='string',
            description='Link to more information',
            extraction_selector='a[href]',
            required=False,
            quality_weight=0.5,
            post_processing=['trim']
        )
        
        # Add fields based on target data
        if 'markets' in parsed_request['target_data']:
            fields['location'] = FieldDefinition(
                field_type='string',
                description='Market location or address',
                extraction_selector='.location, .address, .venue',
                required=False,
                quality_weight=0.8,
                post_processing=['trim', 'clean']
            )
            
            fields['operating_hours'] = FieldDefinition(
                field_type='string',
                description='Market operating hours',
                extraction_selector='.hours, .time, .schedule',
                required=False,
                quality_weight=0.7,
                post_processing=['trim', 'clean']
            )
        
        if 'prices' in parsed_request['target_data']:
            fields['price'] = FieldDefinition(
                field_type='string',
                description='Price or cost information',
                extraction_selector='.price, .cost, .fee, .amount',
                required=False,
                quality_weight=0.8,
                post_processing=['trim', 'clean', 'extract_numbers']
            )
        
        if 'dates' in parsed_request['target_data']:
            fields['date'] = FieldDefinition(
                field_type='string',
                description='Date or time information',
                extraction_selector='.date, .time, time, .published',
                required=False,
                quality_weight=0.7,
                post_processing=['trim', 'clean']
            )
        
        if 'contacts' in parsed_request['target_data']:
            fields['contact'] = FieldDefinition(
                field_type='string',
                description='Contact information',
                extraction_selector='.contact, .phone, .email, .tel',
                required=False,
                quality_weight=0.8,
                post_processing=['trim', 'clean']
            )
        
        # Create schema name
        keywords = parsed_request['keywords'][:2] if parsed_request['keywords'] else ['data']
        schema_name = '_'.join(keywords) + '_schema'
        
        return SchemaRecipe(
            name=schema_name,
            description=f"Schema for extracting {parsed_request['content_type']} data based on: {input_data.request}",
            fields=fields,
            validation_rules=['normalize_whitespace', 'allow_partial_data'],
            quality_weights={
                "completeness": 0.4,
                "accuracy": 0.4,
                "consistency": 0.2
            },
            version="1.0"
        )
    
    def _generate_scraping_plan(
        self, 
        strategy: ScrapingStrategy, 
        schema_recipe: 'SchemaRecipe', 
        parsed_request: Dict[str, Any]
    ) -> str:
        """Generate human-readable scraping plan."""
        plan_parts = []
        
        # Introduction
        plan_parts.append(f"## Scraping Plan for {parsed_request['content_type'].title()} Data")
        plan_parts.append("")
        
        # Strategy overview
        plan_parts.append("### Strategy Overview")
        plan_parts.append(f"- **Scrape Type**: {strategy.scrape_type}")
        plan_parts.append(f"- **Target Selectors**: {', '.join(strategy.target_selectors[:3])}")
        if strategy.pagination_strategy:
            plan_parts.append(f"- **Pagination**: {strategy.pagination_strategy}")
        plan_parts.append(f"- **Max Pages**: {strategy.max_pages}")
        plan_parts.append(f"- **Request Delay**: {strategy.request_delay}s")
        plan_parts.append("")
        
        # Data fields
        plan_parts.append("### Data Fields to Extract")
        for field_name, field_def in schema_recipe.fields.items():
            required_text = " (Required)" if field_def.required else ""
            plan_parts.append(f"- **{field_name.title()}**{required_text}: {field_def.description}")
        plan_parts.append("")
        
        # Extraction approach
        plan_parts.append("### Extraction Approach")
        plan_parts.append(f"1. Navigate to the target website")
        plan_parts.append(f"2. Identify content using selectors: {', '.join(strategy.target_selectors[:2])}")
        plan_parts.append(f"3. Extract data fields using CSS selectors")
        if strategy.pagination_strategy:
            plan_parts.append(f"4. Handle pagination using {strategy.pagination_strategy} strategy")
        plan_parts.append(f"5. Apply quality filtering (minimum score: {strategy.extraction_rules.get('min_quality', 'N/A')})")
        plan_parts.append("")
        
        # Quality measures
        plan_parts.append("### Quality Measures")
        plan_parts.append("- Data validation and cleaning")
        plan_parts.append("- Duplicate removal")
        plan_parts.append("- Quality scoring based on completeness and accuracy")
        
        return "\n".join(plan_parts)
    
    def _generate_reasoning(
        self, 
        analysis: 'WebsiteStructureAnalysis', 
        strategy: ScrapingStrategy, 
        schema_recipe: 'SchemaRecipe', 
        parsed_request: Dict[str, Any]
    ) -> str:
        """Generate reasoning explanation for the decisions made."""
        reasoning_parts = []
        
        reasoning_parts.append("## Decision Reasoning")
        reasoning_parts.append("")
        
        # Strategy reasoning
        reasoning_parts.append("### Strategy Selection")
        reasoning_parts.append(f"Selected '{strategy.scrape_type}' strategy because:")
        
        if strategy.scrape_type == 'list':
            reasoning_parts.append("- The request indicates multiple items need to be extracted")
            reasoning_parts.append("- Website analysis suggests list-like content structure")
        elif strategy.scrape_type == 'detail':
            reasoning_parts.append("- The request focuses on detailed information")
            reasoning_parts.append("- Website appears to have rich content areas")
        
        reasoning_parts.append("")
        
        # Selector reasoning
        reasoning_parts.append("### Selector Selection")
        reasoning_parts.append("Target selectors chosen based on:")
        reasoning_parts.append("- Common HTML patterns for the content type")
        reasoning_parts.append("- Website structure analysis results")
        reasoning_parts.append("- Fallback options for robustness")
        reasoning_parts.append("")
        
        # Schema reasoning
        reasoning_parts.append("### Schema Design")
        reasoning_parts.append("Field selection based on:")
        reasoning_parts.append(f"- User criteria: '{' '.join(parsed_request['keywords'][:3])}'")
        reasoning_parts.append(f"- Target data types: {', '.join(parsed_request['target_data'])}")
        reasoning_parts.append("- Standard fields for the content type")
        reasoning_parts.append("")
        
        # Quality reasoning
        reasoning_parts.append("### Quality Considerations")
        reasoning_parts.append("- Required fields ensure minimum data completeness")
        reasoning_parts.append("- Quality weights prioritize important fields")
        reasoning_parts.append("- Post-processing steps clean and validate data")
        
        return "\n".join(reasoning_parts)
    
    def _calculate_confidence(
        self, 
        analysis: 'WebsiteStructureAnalysis', 
        strategy: ScrapingStrategy, 
        schema_recipe: 'SchemaRecipe'
    ) -> float:
        """Calculate confidence score for the generated plan."""
        confidence_factors = []
        
        # Website analysis confidence
        if 'error' not in analysis.metadata:
            confidence_factors.append(0.8)  # Successfully analyzed website
        else:
            confidence_factors.append(0.3)  # Failed to analyze website
        
        # Strategy confidence
        if strategy.target_selectors:
            confidence_factors.append(0.7)  # Has target selectors
        else:
            confidence_factors.append(0.4)  # No specific selectors
        
        # Schema confidence
        required_fields = sum(1 for field in schema_recipe.fields.values() if field.required)
        if required_fields > 0:
            confidence_factors.append(0.8)  # Has required fields
        else:
            confidence_factors.append(0.6)  # No required fields
        
        # Field coverage confidence
        field_count = len(schema_recipe.fields)
        if field_count >= 3:
            confidence_factors.append(0.9)  # Good field coverage
        elif field_count >= 2:
            confidence_factors.append(0.7)  # Adequate field coverage
        else:
            confidence_factors.append(0.5)  # Limited field coverage
        
        # Calculate weighted average
        return sum(confidence_factors) / len(confidence_factors)
    
    def _handle_error(self, error_message: str, input_data: ScraperAgentInputSchema) -> ScraperAgentOutputSchema:
        """Handle errors gracefully by returning a basic response."""
        return ScraperAgentOutputSchema(
            scraping_plan=f"Error occurred while generating scraping plan: {error_message}",
            strategy={
                "scrape_type": "list",
                "target_selectors": ["div", "article", "li"],
                "extraction_rules": {"title": "h1, h2, h3"},
                "max_pages": 1,
                "request_delay": 1.0
            },
            schema_recipe={
                "name": "error_schema",
                "description": "Basic schema due to error",
                "fields": {
                    "title": {
                        "field_type": "string",
                        "description": "Title of the item",
                        "extraction_selector": "h1, h2, h3",
                        "required": True
                    }
                }
            },
            reasoning=f"An error occurred during plan generation: {error_message}. Providing basic fallback strategy.",
            confidence=0.2
        )