# NovelGraphRAG

**A configuration-driven Python framework for AI novel writing using Graph-based Retrieval-Augmented Generation (RAG).**

This project provides a complete workflow for generating full-length novels with AI while maintaining **long-term consistency**, **character development**, and **narrative coherence**. The key innovation is a **configuration system** that makes the framework completely **genre-agnostic** and **reusable** across different novel projects.

---

## Key Features

- 🎛️ **Configuration-Driven Prompts** - No hardcoded story elements, completely customizable
- 📚 **Two-Phase Generation** - Seed data for first chapter, RAG context for subsequent chapters
- 🎭 **Genre-Agnostic System** - Works for any novel type (literary fiction, mystery, romance, fantasy, etc.)
- 📋 **Template-Based Formatting** - Flexible presentation of story data to AI
- 🔍 **Quality Analysis Tools** - Automated chapter evaluation against your requirements
- 🏗️ **Modular Architecture** - Reusable prompt building and graph management systems

---

## Project Structure

```
NovelGraphRAG/
├── src/
│   ├── ai/
│   │   ├── generator.py           # Chapter generation engine
│   │   ├── prompt_builder.py      # Configuration-driven prompt construction
│   │   ├── seed_prompt_loader.py  # Seed data loading utilities
│   │   └── context_builder.py     # RAG context management
│   └── graph/
│       ├── graph_manager.py       # Story graph and node management
│       ├── node.py               # Graph node representations
│       └── cluster.py            # Semantic clustering (future)
├── scripts/
│   ├── generate_first_chapter.py    # Generate opening chapter
│   ├── generate_subsequent_chapters.py # Generate follow-up chapters
│   ├── index_novel_documents.py     # Build RAG index
│   ├── analyze_chapter.py          # Quality analysis
│   └── refresh_all.py              # Clean up generated content
├── data/
│   ├── seed/                      # Story configuration files
│   │   ├── overview.md           # Story summary and themes
│   │   ├── characters.yaml       # Character definitions
│   │   ├── arcs.yaml            # Story arc definitions
│   │   ├── world.yaml           # Locations and world-building
│   │   └── structure.yaml       # Writing process configuration
│   └── novel/                    # Generated chapter content
├── .env                          # Environment configuration
└── requirements.txt
```

---

## Configuration System

The heart of NovelGraphRAG is its **five-file configuration system** that defines both your story content and the AI writing process:

### **Story Data Files** (`data/seed/`)

#### `overview.md`

High-level story summary, themes, and narrative direction.

```markdown
# Novel Overview

This novel follows David, a former firefighter tormented by his past...
```

#### `characters.yaml`

Character definitions with roles, traits, relationships, and backstory details.

```yaml
characters:
  - name: "David"
    role: "Protagonist"
    description: "A former firefighter haunted by his past, seeking redemption."
    backstory_details:
      - "Lost lives in a specific fire incident"
      - "Carries guilt about those he couldn't save"
    traits: ["Brave", "Guilt-ridden", "Loyal"]
    must_reference_in_first_chapter:
      - "His past as a firefighter"
      - "The specific fire that haunts him"
```

#### `arcs.yaml`

Story arc definitions with key events and character involvement.

```yaml
arcs:
  - name: "David's Redemption"
    description: "David struggles with guilt over his past and seeks redemption."
    key_events:
      - "David saves a child from a burning building."
      - "David confesses his secret to Maria."
```

#### `world.yaml`

Locations and world-building elements.

```yaml
locations:
  - name: "Crumbling Cliffs"
    description: "A dramatic, windswept coastline rumored to be haunted."
  - name: "Old Lighthouse"
    description: "An abandoned lighthouse central to the ghost mystery."
```

### **Process Configuration** (`data/seed/structure.yaml`)

The **meta-configuration file** that defines how the AI should approach novel writing:

```yaml
chapter_requirements:
  first_chapter:
    guidance: |
      IMPORTANT: In this first chapter, you should:
      - Reference specific backstory details mentioned in character descriptions
      - Include at least hints of key relationships and conflicts from the arcs
      - Set up major story threads that will develop throughout the novel

    required_elements:
      - "fire" # David's traumatic incident
      - "firefighter" # His past profession
      - "lighthouse" # Important location

    character_requirements:
      protagonist: "should have significant presence in this chapter"
      supernatural_entity: "should be mentioned, hinted at, or make an appearance"

genre:
  type: "literary_fiction"
  conventions: ["character_driven", "atmospheric", "introspective"]
  tone_guidance: |
    Write engaging prose with vivid descriptions, authentic dialogue, and emotional depth.

# Template formatting for different content types
seed_data_templates:
  characters:
    format: |
      **{name}** ({role}): {description}
      Key Traits: {traits}
      Goals: {goals}
```

This configuration system makes the framework **completely reusable** - just replace the seed files with your own story data and the system adapts automatically.

---

## Getting Started

### 1. **Setup Environment**

```bash
git clone https://github.com/yourusername/NovelGraphRAG.git
cd NovelGraphRAG
pip install -r requirements.txt
```

Create `.env` file:

```bash
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
USE_PLACEHOLDER_LLM=false
```

### 2. **Configure Your Story**

Edit the files in `data/seed/` to define your novel:

- `overview.md` - Your story concept and themes
- `characters.yaml` - Your protagonists, antagonists, and supporting characters
- `arcs.yaml` - Your major story arcs and plot threads
- `world.yaml` - Your settings and locations
- `structure.yaml` - Your genre and writing approach preferences

### 3. **Generate Your Novel**

```bash
# Generate first chapter (uses seed data)
python -m scripts.generate_first_chapter

# Index generated content for RAG
python scripts/index_novel_documents.py

# Generate subsequent chapters (uses RAG context)
python -m scripts.generate_subsequent_chapters

# Analyze chapter quality against your requirements
python scripts/analyze_chapter.py

# Clean up to start fresh (optional)
python scripts/refresh_all.py
```

### 4. **Workflow**

**Phase 1: Foundation** - The first chapter is generated using only your seed data to establish characters, setting, and initial plot threads.

**Phase 2: Development** - Subsequent chapters use RAG (Retrieval-Augmented Generation) to maintain consistency with previous content while advancing the story.

**Quality Control** - The analysis script checks generated chapters against your configured requirements and provides feedback.

---

## Customization Examples

### **For Different Genres**

**Mystery Novel:**

```yaml
# structure.yaml
chapter_requirements:
  first_chapter:
    required_elements: ["crime", "detective", "clue", "suspect"]
    guidance: "Establish the central mystery and introduce key suspects"

genre:
  type: "mystery"
  conventions: ["plot_driven", "suspenseful", "clue_based"]
```

**Romance Novel:**

```yaml
# structure.yaml
chapter_requirements:
  first_chapter:
    required_elements: ["meet_cute", "conflict", "attraction"]
    guidance: "Establish romantic tension and character chemistry"

genre:
  type: "romance"
  conventions: ["relationship_focused", "emotional", "character_chemistry"]
```

### **For Different Story Approaches**

**Literary Fiction:**

```yaml
seed_data_templates:
  characters:
    format: |
      **{name}**: {description}

      Internal Conflicts: {internal_conflicts}
      Psychological State: {psychological_state}
```

**Fantasy Adventure:**

```yaml
seed_data_templates:
  characters:
    format: |
      **{name}** the {role}: {description}

      Powers: {magical_abilities}
      Quest: {goals}
      Companions: {relationships}
```

---

## Dependencies

- `llama-index` - Document indexing and RAG functionality
- `openai` - AI text generation
- `python-dotenv` - Environment configuration
- `pyyaml` - Configuration file parsing

---

## Troubleshooting

**Q: Generated chapters don't include required elements**
A: Check your `structure.yaml` configuration and ensure required elements are properly defined in your seed data files.

**Q: RAG context seems inconsistent**  
A: Run `python scripts/index_novel_documents.py` after generating each chapter to update the knowledge base.

**Q: Characters feel inconsistent across chapters**
A: Review your `characters.yaml` file and ensure key traits and relationships are well-defined.

**Q: Placeholder content instead of AI-generated text**
A: Set `USE_PLACEHOLDER_LLM=false` in your `.env` file and ensure your OpenAI API key is valid.

---

## License

MIT License. Feel free to adapt and extend for your own novel writing projects.
