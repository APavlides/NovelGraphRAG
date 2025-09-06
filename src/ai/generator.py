
import os
from typing import Any, Dict, List

import openai
from dotenv import load_dotenv

from src.ai.prompt_builder import PromptBuilder
from src.ai.seed_prompt_loader import load_seed_data


class ChapterGenerator:
    def __init__(self, graph):
        self.graph = graph
        self.use_placeholder = (
            os.environ.get("USE_PLACEHOLDER_LLM", "false").lower() == "true"
        )
        self.seed_data = load_seed_data()
        self.first_chapter_generated = False
        self.prompt_builder = PromptBuilder()

    def _validate_chapter_content(self, content: str, seed_data: Dict[str, Any]) -> List[str]:
        """Check if generated content includes key elements."""
        missing_elements = []
        
        # Check for key character mentions
        if 'characters' in seed_data:
            chars = seed_data['characters'].get('characters', [])
            for char in chars:
                name = char.get('name', '')
                if name.lower() not in content.lower() and char.get('role', '') in ['Protagonist', 'Deuteragonist']:
                    missing_elements.append(f"Main character {name} not prominently featured")
        
        # Check for key backstory elements
        key_terms = ['fire', 'firefighter', 'grandmother', 'diary', 'lighthouse']
        for term in key_terms:
            if term not in content.lower():
                missing_elements.append(f"Key element '{term}' not referenced")
        
        return missing_elements



    def generate_chapter(self, chapter_outline):
        # Build prompt using generic prompt builder
        if not self.first_chapter_generated:
            # First chapter: use only seed data
            prompt_dict = self.prompt_builder.build_prompt(
                chapter_outline=chapter_outline,
                seed_data=self.seed_data,
                is_first_chapter=True
            )
            self.first_chapter_generated = True
        else:
            # Subsequent chapters: use RAG context
            rag_context = self.graph.get_relevant_context(chapter_outline)
            prompt_dict = self.prompt_builder.build_prompt(
                chapter_outline=chapter_outline,
                seed_data=self.seed_data,
                rag_context=rag_context,
                is_first_chapter=False
            )

        if self.use_placeholder:
            print(f"[PLACEHOLDER] Generating chapter for outline: {chapter_outline}")
            generated_content = f"Placeholder content for: {chapter_outline}\n\nPrompt used:\n{prompt_dict['user']}"
        else:
            print(f"[OPENAI] Generating chapter for outline: {chapter_outline}")
            openai.api_key = os.environ["OPENAI_API_KEY"]
            response = openai.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": prompt_dict["system"]},
                    {"role": "user", "content": prompt_dict["user"]},
                ],
                max_tokens=1500,  # Adjust as needed
                temperature=0.8,
            )
            generated_content = response.choices[0].message.content.strip()

        filename = os.path.join("data", "novel", f"chapter_{chapter_outline.replace(' ', '_').lower()}.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(generated_content)

        self.graph.add_node("scene", chapter_outline, generated_content)