import anthropic

from app.config import settings


def get_client() -> anthropic.Anthropic:
    """Get Anthropic client"""
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def get_idea_suggestions(board_name: str, existing_ideas: list[dict]) -> list[str]:
    """Generate idea suggestions for a board based on existing ideas"""
    client = get_client()

    existing_ideas_text = (
        "\n".join(
            [
                f"- {idea['title']}: {idea.get('description', 'No description')}"
                for idea in existing_ideas
            ]
        )
        if existing_ideas
        else "No ideas yet."
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""You are helping brainstorm ideas for a board called "{board_name}".

Here are the existing ideas on this board:
{existing_ideas_text}

Generate exactly 3 new, creative idea suggestions that complement the existing ideas. Each suggestion should be a concise title (max 50 characters).

Respond with just the 3 ideas, one per line, no numbering or bullets.""",
            }
        ],
    )

    # Parse response into list of suggestions
    response_text = message.content[0].text
    suggestions = [
        line.strip() for line in response_text.strip().split("\n") if line.strip()
    ]
    return suggestions[:3]


def summarize_board(board_name: str, ideas: list[dict]) -> dict:
    """Summarize a board's ideas, identifying themes and top priority"""
    client = get_client()

    if not ideas:
        return {
            "summary": "This board has no ideas yet.",
            "themes": [],
            "top_priority": None,
        }

    ideas_text = "\n".join(
        [
            f"- {idea['title']} (votes: {idea.get('votes', 0)}): {idea.get('description', 'No description')}"
            for idea in ideas
        ]
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""Analyze the ideas on this board called "{board_name}":

{ideas_text}

Provide:
1. A brief summary (2-3 sentences) of the board's focus
2. The main themes (list 2-4 themes, just keywords)
3. The highest priority idea based on votes and potential impact (just the title)

Format your response exactly like this:
SUMMARY: [your summary]
THEMES: [theme1], [theme2], [theme3]
TOP_PRIORITY: [idea title]""",
            }
        ],
    )

    response_text = message.content[0].text

    # Parse response
    summary = ""
    themes = []
    top_priority = None

    for line in response_text.strip().split("\n"):
        if line.startswith("SUMMARY:"):
            summary = line.replace("SUMMARY:", "").strip()
        elif line.startswith("THEMES:"):
            themes_text = line.replace("THEMES:", "").strip()
            themes = [t.strip() for t in themes_text.split(",")]
        elif line.startswith("TOP_PRIORITY:"):
            top_priority = line.replace("TOP_PRIORITY:", "").strip()

    return {"summary": summary, "themes": themes, "top_priority": top_priority}


def auto_categorize_idea(
    title: str, description: str | None, existing_tags: list[str]
) -> list[str]:
    """Suggest tags for an idea based on its content and existing tags"""
    client = get_client()

    existing_tags_text = ", ".join(existing_tags) if existing_tags else "None yet"

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": f"""Suggest tags for this idea:

Title: {title}
Description: {description or 'No description'}

Existing tags in the system: {existing_tags_text}

Suggest 1-3 tags that would help categorize this idea. Prefer existing tags if they fit. If suggesting new tags, keep them short (1-2 words).

Respond with just the tag names, comma-separated, nothing else.""",
            }
        ],
    )

    response_text = message.content[0].text
    suggestions = [
        tag.strip().lower() for tag in response_text.strip().split(",") if tag.strip()
    ]
    return suggestions[:3]
