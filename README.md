# NovelGraphRAG

**A Python-based framework for writing novels using Graph-based Retrieval-Augmented Generation (RAG).**

This project provides a structured workflow to leverage AI for writing a full-length novel while maintaining **long-term consistency**, **complex character arcs**, and **nonlinear narrative structure**. It uses a **graph-based RAG approach with cluster summaries** to organize story elements and context hierarchically.

---

## Project Concept

Writing a novel with AI over multiple chapters can easily lead to **loss of continuity**, inconsistent character behavior, and missed thematic threads. This project solves that problem by:

1. **Graph-Based Story Representation**

   - Each element of the novel (scenes, chapters, characters, events, themes) is represented as a **node**.
   - Relationships like “follows,” “character appears in,” or “part of arc” are represented as **edges**.
   - Allows the story to maintain **nonlinear connections**, flashbacks, and parallel arcs.

2. **Cluster Summaries**

   - Nodes can be grouped into **semantic clusters** (e.g., all scenes relating to a character arc, theme, or plotline).
   - Cluster summaries provide a **hierarchical context** that can be retrieved efficiently for AI generation.

3. **Recursive RAG Workflow**

   - For each chapter:
     1. Retrieve relevant nodes and cluster summaries connected to the chapter’s outline.
     2. Generate scenes or chapters using AI with the retrieved context.
     3. Summarize new scenes and update the graph (nodes, edges, clusters).
   - Ensures that **new content is consistent with prior events, character arcs, and thematic elements**.

4. **Context Management**
   - Scene-level nodes: fine-grained details (objects, locations, dialogue, internal thoughts)
   - Chapter-level clusters: summarize sequences of events and character progression
   - Arc-level clusters: summarize long-term storylines and thematic threads

---

## Features

- Maintain long-term continuity across multiple chapters.
- Support nonlinear story structures, flashbacks, and parallel arcs.
- Track character evolution, relationships, and psychological states.
- Retrieve context dynamically to feed AI for chapter generation.
- Hierarchical summaries allow scaling to novels with dozens of chapters or more.

---

## Suggested Project Structure

```

NovelGraphRAG/
│
├── graph/
│   ├── node.py
│   ├── graph_manager.py
│   └── cluster.py
│
├── ai/
│   ├── generator.py
│   └── context_builder.py
│
├── scripts/
│   └── generate_chapter.py
│
├── data/
│   └── (optional storage for scenes, summaries, embeddings)
│
├── requirements.txt
└── README.md
```

---

## Getting Started

1. Clone the repo:

```bash
git clone https://github.com/yourusername/NovelGraphRAG.git
cd NovelGraphRAG
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialize your story graph and start adding nodes (scenes, chapters, characters):

```python
from graph.graph_manager import StoryGraph
graph = StoryGraph()
graph.add_scene(scene_name="David's first ghost encounter", content="...")
```

Generate chapters using AI:

```python
from ai.generator import ChapterGenerator
generator = ChapterGenerator(graph)
generator.generate_chapter(chapter_outline="David explores the crumbling cliffs")
```

### Future Enhancements

Advanced semantic search over nodes using embeddings.

Automatic cluster summary updates for multi-chapter arcs.

Visualization of the story graph and character arcs.

Integration with version control for AI-generated drafts.

Support for multi-perspective storytelling.

License

MIT License. Feel free to adapt, extend, and use for personal or collaborative novel projects.

```

```
