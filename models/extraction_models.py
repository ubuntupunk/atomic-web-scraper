"""
Extraction-related data models for the website scraper tool.

Contains models for content extraction and processing.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator


class ExtractionRule(BaseModel):
    """Rule for extracting specific content from HTML."""
    
    field_name: str = Field(..., description="Name of the field this rule extracts")
    selector: str = Field(..., description="CSS selector or XPath for extraction")
    extraction_type: str = Field(..., description="Type of extraction: 'text', 'attribute', 'html'")
    attribute_name: Optional[str] = Field(None, description="Attribute name for 'attribute' extraction type")
    post_processing: List[str] = Field(default_factory=list, description="Post-processing steps to apply")
    fallback_selectors: List[str] = Field(default_factory=list, description="Fallback selectors if primary fails")
    quality_indicators: List[str] = Field(default_factory=list, description="Indicators of high-quality content")
    
    @validator('extraction_type')
    def validate_extraction_type(cls, v):
        """Validate extraction type is supported."""
        valid_types = ['text', 'attribute', 'html', 'href', 'src']
        if v not in valid_types:
            raise ValueError(f'extraction_type must be one of: {valid_types}')
        return v
    
    @validator('attribute_name')
    def validate_attribute_name_required(cls, v, values):
        """Ensure attribute_name is provided for attribute extraction."""
        if values.get('extraction_type') == 'attribute' and not v:
            raise ValueError('attribute_name is required for attribute extraction type')
        return v


class ExtractedContent(BaseModel):
    """Content extracted from a single HTML element or page section."""
    
    data: Dict[str, Any] = Field(..., description="Extracted data fields")
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Quality score for this content")
    extraction_issues: List[str] = Field(default_factory=list, description="Issues encountered during extraction")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in extraction accuracy")
    source_url: str = Field(..., description="URL where content was extracted from")
    element_selector: Optional[str] = Field(None, description="Selector that matched this content")
    extraction_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional extraction metadata")
    
    def add_issue(self, issue: str) -> None:
        """Add an extraction issue to the list."""
        if issue not in self.extraction_issues:
            self.extraction_issues.append(issue)
    
    def has_required_fields(self, required_fields: List[str]) -> bool:
        """Check if all required fields are present and non-empty."""
        for field in required_fields:
            if field not in self.data or not self.data[field]:
                return False
        return True
    
    def get_field_completeness(self) -> float:
        """Calculate field completeness as percentage of non-empty fields."""
        if not self.data:
            return 0.0
        
        non_empty_fields = sum(1 for value in self.data.values() if value is not None and str(value).strip())
        return (non_empty_fields / len(self.data)) * 100.0


class ContentQualityMetrics(BaseModel):
    """Metrics for assessing content quality."""
    
    completeness_score: float = Field(..., ge=0.0, le=100.0, description="Percentage of fields with data")
    accuracy_score: float = Field(..., ge=0.0, le=100.0, description="Estimated accuracy of extracted data")
    consistency_score: float = Field(..., ge=0.0, le=100.0, description="Consistency with expected patterns")
    relevance_score: float = Field(..., ge=0.0, le=100.0, description="Relevance to extraction criteria")
    
    def calculate_overall_score(self, weights: Dict[str, float]) -> float:
        """Calculate weighted overall quality score."""
        score = 0.0
        score += self.completeness_score * weights.get('completeness', 0.25)
        score += self.accuracy_score * weights.get('accuracy', 0.25)
        score += self.consistency_score * weights.get('consistency', 0.25)
        score += self.relevance_score * weights.get('relevance', 0.25)
        return min(100.0, max(0.0, score))