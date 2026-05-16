"""
Seed DB with real AI apps.
Usage: cd backend && python -m scripts.seed
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))


from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.models.app import App, AppCategory

SEED_APPS = [
    # ── Original 5 ──
    {
        "name": "ChatGPT",
        "url": "https://chat.openai.com",
        "description": "OpenAI's general-purpose AI assistant",
        "category": AppCategory.productivity,
        "is_health": False,
        "company": "OpenAI",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Ada Health",
        "url": "https://ada.com",
        "description": "AI-powered symptom checker and health guide",
        "category": AppCategory.health,
        "is_health": True,
        "company": "Ada Health GmbH",
        "pricing": "free",
        "source": "manual",
    },
    {
        "name": "Babylon Health",
        "url": "https://www.babylonhealth.com",
        "description": "AI doctor consultation and triage",
        "category": AppCategory.health,
        "is_health": True,
        "company": "Babylon Health",
        "pricing": "paid",
        "source": "manual",
    },
    {
        "name": "Woebot",
        "url": "https://woebothealth.com",
        "description": "AI-based mental health support using CBT",
        "category": AppCategory.health,
        "is_health": True,
        "company": "Woebot Health",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "GitHub Copilot",
        "url": "https://github.com/features/copilot",
        "description": "AI pair programmer by GitHub and OpenAI",
        "category": AppCategory.coding,
        "is_health": False,
        "company": "GitHub",
        "pricing": "paid",
        "source": "manual",
    },
    # ── 10 New Apps ──
    {
        "name": "Google Gemini",
        "url": "https://gemini.google.com",
        "description": "Google's multimodal AI assistant for text, image, and code",
        "category": AppCategory.productivity,
        "is_health": False,
        "company": "Google DeepMind",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Claude",
        "url": "https://claude.ai",
        "description": "Anthropic's AI assistant focused on safety and helpfulness",
        "category": AppCategory.productivity,
        "is_health": False,
        "company": "Anthropic",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Midjourney",
        "url": "https://www.midjourney.com",
        "description": "AI image generation from text prompts",
        "category": AppCategory.creative,
        "is_health": False,
        "company": "Midjourney Inc",
        "pricing": "paid",
        "source": "manual",
    },
    {
        "name": "Khan Academy Khanmigo",
        "url": "https://www.khanacademy.org/khan-labs",
        "description": "AI tutor for personalized learning across subjects",
        "category": AppCategory.education,
        "is_health": False,
        "company": "Khan Academy",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Grammarly",
        "url": "https://www.grammarly.com",
        "description": "AI writing assistant for grammar, tone, and clarity",
        "category": AppCategory.productivity,
        "is_health": False,
        "company": "Grammarly Inc",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Perplexity AI",
        "url": "https://www.perplexity.ai",
        "description": "AI-powered search engine with cited answers",
        "category": AppCategory.productivity,
        "is_health": False,
        "company": "Perplexity AI",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Caktus AI",
        "url": "https://www.caktus.ai",
        "description": "AI study tools for students — essays, math, coding help",
        "category": AppCategory.education,
        "is_health": False,
        "company": "Caktus AI",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Lensa AI",
        "url": "https://prisma-ai.com/lensa",
        "description": "AI photo editor and avatar generator",
        "category": AppCategory.creative,
        "is_health": False,
        "company": "Prisma Labs",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Wysa",
        "url": "https://www.wysa.com",
        "description": "AI mental health chatbot with CBT and mindfulness exercises",
        "category": AppCategory.health,
        "is_health": True,
        "company": "Wysa Ltd",
        "pricing": "freemium",
        "source": "manual",
    },
    {
        "name": "Codeium",
        "url": "https://codeium.com",
        "description": "Free AI code completion and chat for developers",
        "category": AppCategory.coding,
        "is_health": False,
        "company": "Exafunction",
        "pricing": "free",
        "source": "manual",
    },
]


def seed():
    create_db_and_tables()
    added = 0
    with Session(engine) as session:
        for data in SEED_APPS:
            existing = session.exec(
                select(App).where(App.url == data["url"])
            ).first()
            if not existing:
                app = App(**data)
                session.add(app)
                print(f"  ✅ Added: {data['name']}")
                added += 1
            else:
                print(f"  ⏭️  Skip (exists): {data['name']}")
        session.commit()
    print(f"\nDone! Added {added} new apps ({len(SEED_APPS)} total in seed).")


if __name__ == "__main__":
    seed()
