# 🚀 Enterprise AI Development

> **Learn professional software development by building real AI applications**

[![Tests](https://img.shields.io/badge/tests-185%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-99.56%25-brightgreen)]()
[![TDD](https://img.shields.io/badge/methodology-TDD-orange)]()
[![Live Demo](https://img.shields.io/badge/demo-live-blue)](https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app)

---

## 🌐 Live Demo

**🎵 [Try the Spotify Mood2Music App →](https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app)**

Experience mood-based music recommendations powered by AI! Select a mood and get instant Spotify recommendations tailored to your emotional state.

---

## 📁 Two Production-Quality Applications

This repository demonstrates professional AI development through **two complete applications**:

### 1️⃣ **OpenAI Web Search** (`src/`)
- Production-quality web search using OpenAI's search API
- **100% test coverage** with 69 comprehensive tests
- Clean architecture: models, client, parser, service, main
- Enterprise logging with rotation and structured output
- Command-line interface for quick searches

### 2️⃣ **Spotify Mood Recommender** (`spotify/`) - **[LIVE DEMO](https://enterpriseaidemo1websearch-bguldwgonwx8mtucjwymbq.streamlit.app)** 🎵
- Mood-based music recommendations using Spotify API
- **100% test coverage** with 116 comprehensive tests  
- Interactive Streamlit web interface
- OAuth authentication with user library analysis
- Audio feature analysis for intelligent mood matching
- Deployed on Streamlit Community Cloud

**Total: 185 tests, 99.56% coverage across 681 statements**

---

## What You'll Learn in 2 Weeks

Build creative AI applications using **OpenAI** and **Spotify APIs** while mastering:

**Test-Driven Development** • **Clean Architecture** • **Enterprise Logging** • **Professional Git** • **CI/CD**

**The Twist:** This codebase is designed as a **living textbook**. Every file teaches you concepts through narrative comments and real examples.

---

## 🎯 Three Ways to Start

<table>
<tr>
<td width="33%" align="center">
<h3>🏃‍♂️ Just Get It Running</h3>
<p><strong>5-minute setup</strong></p>
<a href="docs/GETTING_STARTED.md">Quick Start Guide →</a>
<br><br>
<em>Setup, run tests, see it work</em>
</td>
<td width="33%" align="center">
<h3>📚 Teach Me Properly</h3>
<p><strong>Full learning path</strong></p>
<a href="docs/LEARNING_PATH.md">Learning Path Map →</a>
<br><br>
<em>Follow the guided journey</em>
</td>
<td width="33%" align="center">
<h3>🎯 I Know What I'm Doing</h3>
<p><strong>Jump to the code</strong></p>
<a href="src/">Browse Source →</a>
<br><br>
<em>See patterns, apply them</em>
</td>
</tr>
</table>

---

## 📖 Your Learning Resources

### 🎓 Course Materials
- **[Learning Path Map](docs/LEARNING_PATH.md)** - Master roadmap
- **[Getting Started](docs/GETTING_STARTED.md)** - Setup and first steps
- **[Course Structure](docs/COURSE_STRUCTURE.md)** - 2-week session plan
- **[Code as Textbook](docs/CODE_AS_TEXTBOOK.md)** - How to read this code
- **[Student Guide](docs/STUDENT_GUIDE.md)** - Day-by-day checklist
- **[Grading Rubric](docs/GRADING.md)** - What you'll be evaluated on

### 🛠️ Development Guides
- **[TDD Workflow](docs/TDD_WORKFLOW.md)** - Write tests first (15 min read)
- **[AI Collaboration](docs/AI_COLLABORATION.md)** - Work with Claude (10 min read)
- **[Git Workflow](docs/GIT_WORKFLOW.md)** - Professional commits (10 min read)
- **[Logging Guide](docs/LOGGING.md)** - Enterprise logging (5 min read)
- **[Labs (Guided Practice)](docs/LEARNING_PATH.md#2-narrative-reading-days-12)** - Hands-on exercises per chapter

### 💡 Project Resources
- **[Project Launch Kit](docs/PROJECT_LAUNCH_KIT.md)** - Scope and planning template
- **[Project Ideas](docs/PROJECT_IDEAS.md)** - 60+ ideas with difficulty ratings
- **[OpenAI APIs](docs/openai_tools_research_oct2025.md)** - Complete API reference (1,300 lines)
- **[Demo Playbook](docs/DEMO_PLAYBOOK.md)** - Prepare your final presentation

### 📚 Reference Library
- **[Architecture Overview](docs/architecture.md)** - System diagrams and design decisions
- **[OpenAI Web Search Notes](docs/web_search_openai.md)** - Tool behavior, payloads, and examples

---

## 🏗️ What This Repository Demonstrates

**Two production-quality applications demonstrating clean architecture:**

### Application 1: OpenAI Web Search (`src/`)
```
📂 Architecture                      What You'll Learn
├── src/models.py                   → Dataclasses, type hints, exceptions
├── src/client.py                   → API clients, error handling, secrets
├── src/parser.py                   → Data transformation, defensive parsing
├── src/search_service.py           → Service layer, validation, orchestration
├── src/main.py                     → CLI design, user experience
└── src/logging_config.py           → Enterprise logging, rotation

📂 Tests (69 tests, 100% coverage)   How You'll Prove It Works
├── tests/test_models.py            → Unit testing patterns
├── tests/test_client.py            → Mocking external APIs
├── tests/test_parser.py            → Data validation testing
├── tests/test_search_service.py    → Integration testing
└── tests/test_main.py              → System testing
```

### Application 2: Spotify Mood Recommender (`spotify/`)
```
📂 Architecture                      What You'll Learn
├── spotify/models.py               → 6 dataclasses with validation
├── spotify/client.py               → OAuth, pagination, batch operations
├── spotify/service.py              → Recommendation algorithms, fallback strategies
└── app.py                          → Streamlit UI (to be refactored)

📂 Tests (70 tests, 88% coverage)    Comprehensive Testing
├── tests/test_spotify_models.py    → 31 tests for data structures
├── tests/test_spotify_client.py    → 22 tests with API mocking
└── tests/test_spotify_service.py   → 17 tests for business logic
```

**Key Pattern:** Consistent architecture across both apps. Learn once, apply everywhere.

---

## 🎯 Your Mission (Choose One API or Combination)

**Available Tools:**
- Chat Completion (conversations)
- Vision (image analysis)
- DALL-E 3 (image generation)
- Whisper (speech-to-text)
- TTS (text-to-speech)
- Embeddings (semantic search)
- Assistants (persistent agents)
- Sora 2 (video generation)
- GPT-5 Pro (advanced reasoning)

**Examples:**
- 📸 Recipe from food photo (Vision + Chat)
- 🎙️ Meeting transcriber (Whisper + Summarization)
- 🎨 AI art studio (DALL-E 3 + Chat)
- 📚 Document Q&A (Embeddings + Chat)
- 🎬 Story to video (Chat + Sora 2)

**[Browse 10 detailed project ideas →](docs/PROJECT_IDEAS.md)**

---

## ⚡ Quick Start (5 Minutes)

**Prerequisites:** Python 3.11 or higher ([Download](https://python.org))

```bash
# Clone and setup
git clone https://github.com/kaw393939/enterprise_ai_demo1_websearch.git
cd enterprise_ai_demo1_websearch
python -m venv venv
source venv/bin/activate  # Mac/Linux (Windows: venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here

# Verify it works
pytest
python -m src.main "latest AI developments"
```

✅ **Working?** Great! Next: **[Read Course Structure →](docs/COURSE_STRUCTURE.md)**

❌ **Issues?** Check **[Getting Started Guide →](docs/GETTING_STARTED.md)**

---

## 💡 What Makes This Course Unique

### 1. **Code IS the Textbook**
Every file has narrative comments explaining concepts, design decisions, and alternatives.

**Traditional code:**
```python
@dataclass
class SearchOptions:
    model: str = "gpt-4o-mini"
```

**Our teaching code:**
```python
@dataclass
class SearchOptions:
    """
    📚 CONCEPT: Dataclasses auto-generate __init__, __repr__, __eq__
    
    📝 DESIGN: We default to "gpt-4o-mini" (fastest, cheapest for learning)
    
    EXAMPLE:
    >>> options = SearchOptions()  # Uses defaults
    >>> options = SearchOptions(model="gpt-4o")  # Override for production
    """
    model: str = "gpt-4o-mini"
```

### 2. **TDD is Non-Negotiable**
You'll write tests FIRST, then code. This is how professionals prevent bugs.

### 3. **Production Standards**
Not tutorial code—real patterns you'll use in your career.

### 4. **AI as Learning Partner**
Learn to use Claude effectively while maintaining quality and understanding.

---

## 📊 Grading at a Glance

| Category | Points | Key Requirements |
|----------|--------|------------------|
| **Works & Uses APIs** | 30 | No crashes, correct API usage |
| **Tests & TDD** | 30 | 80%+ coverage, tests written first |
| **Code Quality** | 25 | Clean architecture, logging, errors |
| **Documentation & Demo** | 15 | Clear README, 5-min presentation |

**[View full rubric →](docs/GRADING.md)**

---

## 🆘 Getting Help

**During class:** Ask instructor, pair with classmates, use Claude

**Outside class:**
1. Read the relevant guide in `docs/`
2. Check example code in `src/` and `tests/`
3. Search the [OpenAI API reference](docs/openai_tools_research_oct2025.md)
4. Ask Claude with specific context (see [AI Collaboration guide](docs/AI_COLLABORATION.md))

**Common issues:**
```bash
pytest -v                                          # See test details
source venv/bin/activate                           # Activate environment
pytest --cov=src --cov-report=term-missing         # Check coverage
git status && git log --oneline                    # Git status
```

---

## 🎓 Learning Outcomes

After completing this course, you will confidently:

✅ Build robust API clients with error handling  
✅ Write comprehensive tests using TDD methodology  
✅ Structure applications with clean architecture  
✅ Implement enterprise-grade logging and monitoring  
✅ Use professional git workflows and CI/CD  
✅ Collaborate effectively with AI tools  
✅ Present technical work clearly  

**Most importantly:** You'll shift from writing "scripts that work" to building "systems that last."

---

## 🚀 Ready to Start?

### Option 1: Dive Right In
**[Getting Started Guide →](docs/GETTING_STARTED.md)** - Get running in 5 minutes

### Option 2: Learn the Concepts First
**[Code as Textbook →](docs/CODE_AS_TEXTBOOK.md)** - Understand the philosophy

### Option 3: See the Full Plan
**[Course Structure →](docs/COURSE_STRUCTURE.md)** - 2-week breakdown

---

<div align="center">

**Questions?** Check the [Getting Started Guide](docs/GETTING_STARTED.md) or ask your instructor.

*Built with ❤️ for students who want to understand, not just copy-paste*

**Let's build something amazing! 🚀**

</div>
