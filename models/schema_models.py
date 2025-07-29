"""
Schema-related data models for the website scraper tool.

Contains models for dynamic schema generation and field definitions.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class FieldDefinition(BaseModel):
    """Definition for a data field in a schema recipe."""
    
    field_type: str = Field(..., description="Data type: 'string', 'number', 'array', 'object', 'boolean'")
    description: str = Field(..., description="Human-readable field description")
    extraction_selector: str = Field(..., description="CSS selector or XPath for extraction")
    validation_pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    required: bool = Field(False, description="Whether field is required")
    quality_weight: float = Field(1.0, ge=0.0, description="Weight for quality scoring")
    post_processing: List[str] = Field(default_factory=list, description="Post-processing steps")
    
    @validator('field_type')
    def validate_field_type(cls, v):
        """Validate field type is supported."""
        valid_types = ['string', 'number', 'array', 'object', 'boolean']
        if v not in valid_types:
            raise ValueError(f'field_type must be one of: {valid_types}')
        return v
    
    @validator('post_processing')
    def validate_post_processing(cls, v):
        """Validate post-processing steps are supported."""
        valid_steps = ['clean', 'normalize', 'validate', 'trim', 'lowercase', 'uppercase']
        for step in v:
            if step not in valid_steps:
                raise ValueError(f'Invalid post-processing step: {step}. Valid steps: {valid_steps}')
        return v


class SchemaRecipe(BaseModel):
    """Recipe for generating dynamic schemas based on website content."""
    
    name: str = Field(..., description="Unique name for the schema recipe")
    description: str = Field(..., description="Human-readable description of the schema")
    fields: Dict[str, FieldDefinition] = Field(..., description="Field definitions")
    validation_rules: List[str] = Field(default_factory=list, description="Global validation rules")
    quality_weights: Dict[str, float] = Field(
        default_factory=lambda: {"completeness": 0.4, "accuracy": 0.4, "consistency": 0.2},
        description="Weights for quality scoring components"
    )
    version: str = Field("1.0", description="Schema version")
    
    @validator('fields')
    def validate_fields_not_empty(cls, v):
        """Ensure at least one field is defined."""
        if not v:
            raise ValueError('Schema recipe must have at least one field defined')
        return v
    
    @validator('quality_weights')
    def validate_quality_weights_sum(cls, v):
        """Ensure quality weights sum to 1.0."""
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:  # Allow small floating point errors
            raise ValueError(f'Quality weights must sum to 1.0, got {total}')
        return v
    
    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [name for name, field_def in self.fields.items() if field_def.required]
    
    def get_field_selectors(self) -> Dict[str, str]:
        """Get mapping of field names to their extraction selectors."""
        return {name: field_def.extraction_selector for name, field_def in self.fields.items()}
    
    def calculate_field_quality_weight(self, field_name: str) -> float:
        """Calculate the quality weight for a specific field."""
        if field_name not in self.fields:
            return 0.0
        return self.fields[field_name].quality_weight