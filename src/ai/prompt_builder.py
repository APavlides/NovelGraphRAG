"""
Generic prompt builder for novel generation.
Constructs prompts from seed data and RAG context without hardcoding story-specific details.
"""

import os
from typing import Any, Dict, List, Optional

import yaml


class PromptBuilder:
    """
    Generic prompt builder that constructs LLM prompts from seed data and RAG context.
    Completely agnostic to specific novel content.
    """
    
    def __init__(self, structure_config_path: Optional[str] = None, prompt_templates: Optional[Dict[str, str]] = None):
        """
        Initialize with optional structure configuration and custom prompt templates.
        
        Args:
            structure_config_path: Path to structure.yaml configuration file
            prompt_templates: Dictionary of custom templates for different prompt sections
        """
        self.structure_config = self._load_structure_config(structure_config_path)
        self.templates = prompt_templates or self.structure_config.get('templates', self._get_default_templates())
    
    def _load_structure_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load structure configuration from YAML file."""
        if config_path is None:
            config_path = os.path.join("data", "seed", "structure.yaml")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Structure config not found at {config_path}, using defaults")
            return self._get_default_structure_config()
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing structure config: {e}, using defaults")
            return self._get_default_structure_config()
    
    def _get_default_structure_config(self) -> Dict[str, Any]:
        """Fallback structure configuration if file not found."""
        return {
            'chapter_requirements': {
                'first_chapter': {
                    'guidance': 'Write an engaging opening chapter that introduces the main characters and setting.',
                    'required_elements': [],
                    'character_requirements': {}
                },
                'subsequent_chapters': {
                    'guidance': 'Continue the story while maintaining consistency.',
                    'include_seed_reference_when': {
                        'rag_context_shorter_than': 500,
                        'rag_context_missing': True
                    }
                }
            },
            'validation': {
                'check_elements': [],
                'missing_element_severity': 'warning',
                'retry_on_missing': False
            },
            'templates': self._get_default_templates()
        }
    
    def _get_default_templates(self) -> Dict[str, str]:
        """Default templates for prompt sections."""
        return {
            "system": "You are a skilled novelist writing a compelling narrative.",
            "seed_intro": "Here is the foundational information for this story:",
            "rag_intro": "Here is what has happened in the story so far:",
            "task_intro": "Your task:",
            "formatting_guide": "Write engaging prose with vivid descriptions, authentic dialogue, and emotional depth."
        }
    
    def build_prompt(
        self,
        chapter_outline: str,
        seed_data: Optional[Dict[str, Any]] = None,
        rag_context: Optional[str] = None,
        is_first_chapter: bool = True,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Build a complete prompt for chapter generation.
        
        Args:
            chapter_outline: Brief description of what should happen in this chapter
            seed_data: Dictionary containing story foundations (overview, characters, etc.)
            rag_context: Retrieved context from previous chapters/scenes
            is_first_chapter: Whether this is the first chapter (affects prompt structure)
            additional_instructions: Any extra guidance for the LLM
            
        Returns:
            Dictionary with 'system' and 'user' messages for the LLM
        """
        user_prompt_parts = []
        
        # Add seed data section (for first chapter or as reference)
        if seed_data and (is_first_chapter or self._should_include_seed_reference(rag_context)):
            seed_section = self._format_seed_data(seed_data)
            if seed_section.strip():
                user_prompt_parts.append(f"{self.templates['seed_intro']}\n{seed_section}")
        
        # Add RAG context section (for subsequent chapters)
        if rag_context and not is_first_chapter:
            user_prompt_parts.append(f"{self.templates['rag_intro']}\n{rag_context}")
        
        # Add task section
        task_section = self._format_task(chapter_outline, is_first_chapter, additional_instructions)
        user_prompt_parts.append(f"{self.templates['task_intro']}\n{task_section}")
        
        # Add formatting guidance
        user_prompt_parts.append(self.templates['formatting_guide'])
        
        return {
            "system": self.templates['system'],
            "user": "\n\n".join(user_prompt_parts)
        }
    
    def _format_seed_data(self, seed_data: Dict[str, Any]) -> str:
        """
        Format seed data into readable prompt text.
        Handles various data structures generically.
        """
        sections = []
        
        # Define preferred order for common sections
        preferred_order = ['overview', 'characters', 'world', 'arcs', 'themes', 'tone']
        
        # Process sections in preferred order first
        for key in preferred_order:
            if key in seed_data:
                formatted_section = self._format_section(key, seed_data[key])
                if formatted_section:
                    sections.append(formatted_section)
        
        # Process any remaining sections
        for key, value in seed_data.items():
            if key not in preferred_order:
                formatted_section = self._format_section(key, value)
                if formatted_section:
                    sections.append(formatted_section)
        
        return "\n\n".join(sections)
    
    def _format_section(self, section_name: str, content: Any) -> str:
        """Enhanced section formatting using templates from structure config."""
        if not content:
            return ""
        
        # Get template configuration for this section
        templates = self.structure_config.get('seed_data_templates', {})
        section_template = templates.get(section_name, {})
        
        # Check if we should use raw content
        if section_template.get('use_raw_content', False):
            header = f"**{section_name.replace('_', ' ').title()}:**"
            return f"{header}\n{content}"
        
        # Use template-based formatting if available
        if section_template and 'format' in section_template:
            return self._format_with_template(section_name, content, section_template)
        
        # Fall back to existing generic formatting methods
        if section_name == 'characters':
            return self._format_characters(content)
        elif section_name == 'arcs':
            return self._format_arcs(content)
        elif isinstance(content, dict):
            return self._format_dict_generic(f"**{section_name.replace('_', ' ').title()}:**", content)
        elif isinstance(content, list):
            return self._format_list(f"**{section_name.replace('_', ' ').title()}:**", content)
        else:
            return f"**{section_name.replace('_', ' ').title()}:**\n{str(content)}"

    def _format_with_template(self, section_name: str, content: Any, template_config: Dict[str, Any]) -> str:
        """Format content using specified template configuration."""
        
        if section_name == 'characters':
            return self._format_characters_with_template(content, template_config)
        elif section_name == 'arcs':
            return self._format_arcs_with_template(content, template_config)
        elif section_name == 'world':
            return self._format_world_with_template(content, template_config)
        else:
            return self._format_generic_with_template(section_name, content, template_config)

    def _format_arcs_with_template(self, arcs_data: Dict[str, Any], template_config: Dict[str, Any]) -> str:
        """Format arcs using template configuration."""
        arcs = arcs_data.get('arcs', []) if 'arcs' in arcs_data else arcs_data
        
        if not isinstance(arcs, list):
            return "**Story Arcs:** (Invalid format)"
        
        format_template = template_config.get('format', '')
        field_formatting = template_config.get('field_formatting', {})
        
        arc_descriptions = []
        for arc in arcs:
            if isinstance(arc, dict):
                if format_template:
                    try:
                        # Prepare arc data for template
                        arc_data = {}
                        arc_data['name'] = arc.get('name', 'Unnamed Arc')
                        arc_data['description'] = arc.get('description', '')
                        
                        # Format other fields
                        for key, value in arc.items():
                            if key not in ['name', 'description'] and value:
                                if key in field_formatting:
                                    formatting = field_formatting[key]
                                    arc_data[key] = self._format_field_value(value, formatting)
                                else:
                                    arc_data[key] = str(value)
                        
                        formatted_arc = format_template.format(**arc_data)
                        arc_descriptions.append(formatted_arc)
                    except KeyError:
                        # Fall back to basic formatting
                        arc_descriptions.append(self._format_arc_basic(arc))
                else:
                    arc_descriptions.append(self._format_arc_basic(arc))
        
        return "**Story Arcs:**\n\n" + "\n\n".join(arc_descriptions)

    def _format_world_with_template(self, world_data: Dict[str, Any], template_config: Dict[str, Any]) -> str:
        """Format world data using template configuration."""
        format_template = template_config.get('format', '')
        field_formatting = template_config.get('field_formatting', {})
        
        if format_template:
            try:
                # Prepare world data for template
                formatted_data = {}
                for key, value in world_data.items():
                    if key in field_formatting:
                        formatting = field_formatting[key]
                        formatted_data[key] = self._format_field_value(value, formatting)
                    else:
                        formatted_data[key] = str(value) if value else ''
                
                return format_template.format(**formatted_data)
            except KeyError:
                # Fall back to basic formatting
                pass
        
        # Basic world formatting
        if isinstance(world_data, dict):
            return self._format_dict_generic("**World:**", world_data)
        else:
            return f"**World:**\n{str(world_data)}"

    def _format_generic_with_template(self, section_name: str, content: Any, template_config: Dict[str, Any]) -> str:
        """Generic template formatting for any content type."""
        format_template = template_config.get('format', '')
        
        if format_template and isinstance(content, dict):
            try:
                return format_template.format(**content)
            except KeyError:
                pass
        
        # Fall back to existing methods
        if isinstance(content, dict):
            return self._format_dict_generic(f"**{section_name.replace('_', ' ').title()}:**", content)
        elif isinstance(content, list):
            return self._format_list(f"**{section_name.replace('_', ' ').title()}:**", content)
        else:
            return f"**{section_name.replace('_', ' ').title()}:**\n{str(content)}"

    def _format_character_basic(self, char: Dict[str, Any]) -> str:
        """Basic character formatting fallback."""
        name = char.get('name', 'Unknown Character')
        role = char.get('role', '')
        desc = char.get('description', '')
        
        char_text = f"- **{name}**"
        if role:
            char_text += f" ({role})"
        if desc:
            char_text += f": {desc}"
        
        return char_text

    def _format_arc_basic(self, arc: Dict[str, Any]) -> str:
        """Basic arc formatting fallback."""
        name = arc.get('name', 'Unnamed Arc')
        desc = arc.get('description', '')
        
        arc_text = f"- **{name}**"
        if desc:
            arc_text += f": {desc}"
        
        return arc_text

    def _format_characters_with_template(self, characters_data: Dict[str, Any], template_config: Dict[str, Any]) -> str:
        """Format characters using template configuration."""
        chars = characters_data.get('characters', []) if 'characters' in characters_data else characters_data
        
        if not isinstance(chars, list):
            return "**Characters:** (Invalid format)"
        
        # Get formatting preferences
        first_chapter_fields = template_config.get('first_chapter_fields', [])
        skip_fields = template_config.get('skip_fields', [])
        field_formatting = template_config.get('field_formatting', {})
        format_template = template_config.get('format', '')
        
        char_descriptions = []
        for char in chars:
            if isinstance(char, dict):
                # Prepare character data for template
                char_data = self._prepare_character_data(char, first_chapter_fields, skip_fields, field_formatting)
                
                # Apply template if provided
                if format_template:
                    try:
                        formatted_char = format_template.format(**char_data)
                        char_descriptions.append(formatted_char)
                    except KeyError:
                        # Fall back to basic formatting if template fails
                        char_descriptions.append(self._format_character_basic(char))
                else:
                    char_descriptions.append(self._format_character_basic(char))
        
        return "**Characters:**\n\n" + "\n\n".join(char_descriptions)

    def _prepare_character_data(self, char: Dict[str, Any], first_chapter_fields: List[str], 
                          skip_fields: List[str], field_formatting: Dict[str, str]) -> Dict[str, str]:
        """Prepare character data for template formatting."""
        char_data = {}
        
        # Basic fields
        char_data['name'] = char.get('name', 'Unknown Character')
        char_data['role'] = char.get('role', '')
        char_data['description'] = char.get('description', '')
        
        # Format other fields based on configuration
        for key, value in char.items():
            if key in skip_fields or key in ['name', 'role', 'description']:
                continue
                
            # Only include fields that are in first_chapter_fields or all if empty
            if first_chapter_fields and key not in first_chapter_fields:
                continue
                
            if key in field_formatting:
                formatting = field_formatting[key]
                char_data[key] = self._format_field_value(value, formatting)
            else:
                char_data[key] = str(value) if value else ''
        
        # Add first chapter guidance if present
        first_chapter_guidance = ""
        if 'must_reference_in_first_chapter' in char:
            items = char['must_reference_in_first_chapter']
            if items:
                first_chapter_guidance = "First Chapter Must Include: " + ", ".join(items)
        elif 'first_chapter_hint' in char:
            first_chapter_guidance = f"First Chapter Hint: {char['first_chapter_hint']}"
        
        char_data['first_chapter_guidance'] = first_chapter_guidance
        
        return char_data

    def _format_field_value(self, value: Any, formatting: str) -> str:
        """Format a field value according to specified formatting type."""
        if not value:
            return ""
        
        if formatting == "comma_separated":
            if isinstance(value, list):
                return ", ".join(map(str, value))
            return str(value)
        
        elif formatting == "bulleted_list":
            if isinstance(value, list):
                return "\n  • " + "\n  • ".join(map(str, value))
            return f"  • {value}"
        
        elif formatting == "numbered_list":
            if isinstance(value, list):
                return "\n  " + "\n  ".join(f"{i+1}. {item}" for i, item in enumerate(value))
            return f"  1. {value}"
        
        elif formatting == "key_value_pairs":
            if isinstance(value, dict):
                return "; ".join(f"{k}: {v}" for k, v in value.items())
            return str(value)
        
        elif formatting == "bulleted_descriptions":
            if isinstance(value, list):
                formatted_items = []
                for item in value:
                    if isinstance(item, dict):
                        name = item.get('name', 'Location')
                        desc = item.get('description', '')
                        formatted_items.append(f"• **{name}**: {desc}")
                    else:
                        formatted_items.append(f"• {item}")
                return "\n  " + "\n  ".join(formatted_items)
            return str(value)
        
        else:
            return str(value)
    
    def _format_characters(self, characters_data: Dict[str, Any]) -> str:
        """Format character data specifically."""
        if 'characters' in characters_data:
            chars = characters_data['characters']
        else:
            chars = characters_data
        
        if not isinstance(chars, list):
            return self._format_dict_generic("**Characters:**", characters_data)
        
        char_descriptions = []
        for char in chars:
            if isinstance(char, dict):
                name = char.get('name', 'Unknown Character')
                role = char.get('role', '')
                desc = char.get('description', '')
                
                char_text = f"- **{name}**"
                if role:
                    char_text += f" ({role})"
                if desc:
                    char_text += f": {desc}"
                
                # Add additional character details
                for key, value in char.items():
                    if key not in ['name', 'role', 'description'] and value:
                        if isinstance(value, list):
                            char_text += f"\n  - {key.title()}: {', '.join(map(str, value))}"
                        elif isinstance(value, dict):
                            char_text += f"\n  - {key.title()}: {self._format_nested_dict(value)}"
                        else:
                            char_text += f"\n  - {key.title()}: {value}"
                
                char_descriptions.append(char_text)
        
        return "**Characters:**\n" + "\n\n".join(char_descriptions)
    
    def _format_arcs(self, arcs_data: Dict[str, Any]) -> str:
        """Format story arcs specifically."""
        if 'arcs' in arcs_data:
            arcs = arcs_data['arcs']
        else:
            arcs = arcs_data
        
        if not isinstance(arcs, list):
            return self._format_dict_generic("**Story Arcs:**", arcs_data)
        
        arc_descriptions = []
        for arc in arcs:
            if isinstance(arc, dict):
                name = arc.get('name', 'Unnamed Arc')
                desc = arc.get('description', '')
                
                arc_text = f"- **{name}**"
                if desc:
                    arc_text += f": {desc}"
                
                # Add arc details
                for key, value in arc.items():
                    if key not in ['name', 'description'] and value:
                        if isinstance(value, list):
                            arc_text += f"\n  - {key.title()}: {', '.join(map(str, value))}"
                        else:
                            arc_text += f"\n  - {key.title()}: {value}"
                
                arc_descriptions.append(arc_text)
        
        return "**Story Arcs:**\n" + "\n\n".join(arc_descriptions)
    
    def _format_dict_generic(self, header: str, data: Dict[str, Any]) -> str:
        """Generic dictionary formatting."""
        items = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                items.append(f"- {key.title()}: {self._format_nested_value(value)}")
            else:
                items.append(f"- {key.title()}: {value}")
        
        return f"{header}\n" + "\n".join(items)
    
    def _format_list(self, header: str, data: List[Any]) -> str:
        """Generic list formatting."""
        items = [f"- {item}" for item in data]
        return f"{header}\n" + "\n".join(items)
    
    def _format_nested_dict(self, data: Dict[str, Any]) -> str:
        """Format nested dictionary inline."""
        items = [f"{k}: {v}" for k, v in data.items()]
        return "; ".join(items)
    
    def _format_nested_value(self, value: Any) -> str:
        """Format nested values inline."""
        if isinstance(value, list):
            return ", ".join(map(str, value))
        elif isinstance(value, dict):
            return self._format_nested_dict(value)
        else:
            return str(value)
    
    def _format_task(self, chapter_outline: str, is_first_chapter: bool, additional_instructions: Optional[str]) -> str:
        """Format the task section of the prompt with guidance from structure config."""
        task_parts = []
        
        if is_first_chapter:
            task_parts.append(f"Write the first chapter of this story based on the following outline: {chapter_outline}")
            
            # Add guidance from configuration
            first_chapter_config = self.structure_config.get('chapter_requirements', {}).get('first_chapter', {})
            guidance = first_chapter_config.get('guidance', '')
            if guidance:
                task_parts.append(guidance)
        else:
            task_parts.append(f"Continue the story by writing the next chapter based on this outline: {chapter_outline}")
            
            # Add guidance from configuration
            subsequent_config = self.structure_config.get('chapter_requirements', {}).get('subsequent_chapters', {})
            guidance = subsequent_config.get('guidance', '')
            if guidance:
                task_parts.append(guidance)
    
        if additional_instructions:
            task_parts.append(additional_instructions)
        
        return "\n".join(task_parts)
    
    def _should_include_seed_reference(self, rag_context: Optional[str]) -> bool:
        """
        Determine if seed data should be included as reference for subsequent chapters.
        Uses configuration from structure.yaml to make this decision.
        """
        subsequent_config = self.structure_config.get('chapter_requirements', {}).get('subsequent_chapters', {})
        include_config = subsequent_config.get('include_seed_reference_when', {})
        
        # Check if RAG context is missing
        if include_config.get('rag_context_missing', True) and not rag_context:
            return True
        
        # Check if RAG context is too short
        min_length = include_config.get('rag_context_shorter_than', 500)
        if rag_context and len(rag_context.strip()) < min_length:
            return True
        
        return False

    def _extract_key_details(self, seed_data: Dict[str, Any]) -> str:
        """Extract and highlight key details that should be included based on configuration."""
        key_details = []
        
        # Get required elements from configuration
        first_chapter_config = self.structure_config.get('chapter_requirements', {}).get('first_chapter', {})
        required_elements = first_chapter_config.get('required_elements', [])
        
        # Check for required elements in seed data
        if required_elements:
            for element in required_elements:
                # Look for this element in character descriptions
                if 'characters' in seed_data:
                    chars = seed_data['characters'].get('characters', [])
                    for char in chars:
                        name = char.get('name', '')
                        if 'description' in char:
                            desc = char['description']
                            if element.lower() in desc.lower():
                                key_details.append(f"- {name}'s connection to {element}")
                
                # Look for this element in arc events
                if 'arcs' in seed_data:
                    arcs = seed_data['arcs'].get('arcs', [])
                    for arc in arcs:
                        if 'key_events' in arc:
                            for event in arc['key_events']:
                                if element.lower() in event.lower():
                                    key_details.append(f"- Reference to {element} from story arc")
        
        # Extract important relationships based on character requirements
        char_requirements = first_chapter_config.get('character_requirements', {})
        if 'characters' in seed_data and char_requirements:
            chars = seed_data['characters'].get('characters', [])
            for char in chars:
                role = char.get('role', '').lower().replace(' ', '_')
                if 'relationships' in char and role in char_requirements:
                    for rel_name, rel_type in char['relationships'].items():
                        if rel_type.lower() in ['antagonist', 'family']:
                            key_details.append(f"- {char.get('name', 'Character')}'s relationship with {rel_name} ({rel_type})")
        
        if key_details:
            return "KEY ELEMENTS TO INCLUDE:\n" + "\n".join(key_details)
        return ""

    def _get_character_requirements(self, seed_data: Dict[str, Any]) -> str:
        """Generate requirements for character inclusion based on configuration."""
        if 'characters' not in seed_data:
            return ""
        
        # Get character requirements from configuration
        first_chapter_config = self.structure_config.get('chapter_requirements', {}).get('first_chapter', {})
        char_requirements = first_chapter_config.get('character_requirements', {})
        
        chars = seed_data['characters'].get('characters', [])
        requirements = []
        
        for char in chars:
            name = char.get('name', '')
            role = char.get('role', '').lower().replace(' ', '_')
            
            # Use configured requirement or fall back to default
            if role in char_requirements:
                requirement = char_requirements[role]
                requirements.append(f"- {name} {requirement}")
            else:
                # Default fallback
                requirements.append(f"- Consider including or referencing {name}")
        
        if requirements:
            return "CHARACTER REQUIREMENTS:\n" + "\n".join(requirements)
        return ""


    def extract_key_details(self, seed_data: Dict[str, Any]) -> str:
        """Public method to extract key details."""
        return self._extract_key_details(seed_data)
def build_prompt(chapter_outline: str, seed_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, str]:
    """
    Convenience function to build a prompt without instantiating the class.
    """
    builder = PromptBuilder()
    
    # Extract parameters from kwargs
    rag_context = kwargs.get('rag_context')
    is_first_chapter = kwargs.get('is_first_chapter', True)
    additional_instructions = kwargs.get('additional_instructions')
    
    # Add key details extraction for first chapter
    if seed_data and is_first_chapter:
        key_details = builder.extract_key_details(seed_data)
        if key_details:
            if additional_instructions:
                additional_instructions += f"\n\n{key_details}"
            else:
                additional_instructions = key_details
    
    return builder.build_prompt(
        chapter_outline=chapter_outline,
        seed_data=seed_data,
        rag_context=rag_context,
        is_first_chapter=is_first_chapter,
        additional_instructions=additional_instructions,
        **{k: v for k, v in kwargs.items() if k not in ['rag_context', 'is_first_chapter', 'additional_instructions']}
    )
