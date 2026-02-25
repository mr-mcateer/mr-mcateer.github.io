# Project: Prompt AI Solutions
# Owner: Andrew McAteer
# Domain: promptaisolutions.com

## About
AI consulting and scaled communication campaigns. AI as an invisible tool
that amplifies your reach -- not a gimmick.

## Security Rules
- NEVER hardcode API keys in scripts, commands, or chat output.
- ALL secrets live in `.env` and are loaded via env_loader (see education repo).

## Code Style
- No em-dashes in any generated content.
- Pure static HTML/CSS/JS -- no build system, no framework.
- Dark mode support via `data-theme="dark"` attribute.

## Project Structure
```
CNAME                           # promptaisolutions.com
index.html                      # Solutions landing page
yard-game/                      # Frisbeam GTM pitch
img/                            # Site images
.claude/                        # Claude Code config
.gitignore                      # Prevents .env from being committed
```

## Related Repos
- Education site: github.com/mr-mcateer/prompt-ai-education (promptaieducation.com)
