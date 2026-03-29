# Mac Hardening Guide: Zero-Trust EEF Deployment

This guide configures a dedicated macOS environment for the Active EEF system
with defense-in-depth security. The goal: Claude can interact with your Mac
(Calendar, Reminders, screen) but cannot exfiltrate data or access unauthorized
directories.

## 1. Restricted macOS User Account

Create a standard (non-admin) user account dedicated to the EEF agent.

```bash
# Create the account (run from your admin account)
sudo sysadminctl -addUser Agent_Workspace -fullName "EEF Agent" -password - -home /Users/Agent_Workspace

# Verify it's NOT an administrator
dscl . -read /Groups/admin GroupMembership | grep -v Agent_Workspace && echo "GOOD: Not admin"
```

### Directory Scoping

The agent account only gets read/write access to its working directory:

```bash
# Create the EEF workspace
sudo mkdir -p /Users/Agent_Workspace/Documents/Second_Brain
sudo chown -R Agent_Workspace:staff /Users/Agent_Workspace/Documents/Second_Brain

# Lock down: agent cannot read your primary user's home directory
sudo chmod 700 /Users/$(whoami)
```

### Computer Use Boundary

When Claude uses screen reading/clicking capabilities, it can only see
applications open within the Agent_Workspace session. Your primary desktop
is physically isolated.

To switch: System Settings > Users & Groups > Login Options > Fast User Switching.

## 2. Network Egress Filtering

Default-deny firewall for the `claude` process and any Dispatch server.

### Option A: LuLu (Free, Open-Source)

1. Install: `brew install --cask lulu`
2. Open LuLu preferences
3. Set default rule to **Block** for all new connections
4. Add whitelist rules:

| Process | Destination | Port | Action |
|---------|------------|------|--------|
| `claude` | `api.anthropic.com` | 443 | Allow |
| `node` (MCP servers) | `localhost` | * | Allow |
| `python3` (Canvas API) | Your Canvas instance URL | 443 | Allow |
| Everything else | * | * | Block |

### Option B: Little Snitch (Paid, More Granular)

Same whitelist rules as above. Little Snitch provides per-connection
approval dialogs which are useful during initial setup.

### Verification

After configuring, test that unauthorized connections are blocked:

```bash
# This should FAIL (blocked by firewall)
curl -s https://httpbin.org/ip && echo "FAIL: Egress not blocked" || echo "PASS: Egress blocked"

# This should SUCCEED (whitelisted)
curl -s https://api.anthropic.com/v1/messages -H "x-api-key: test" && echo "API reachable"
```

## 3. DLP Middleware

The `canvas-agent-grader/dlp.py` script automatically scrubs PII from text
before it reaches any external API. It runs inline (not as a separate service)
and adds < 100ms of latency.

### What It Catches

| Pattern | Example | Redacted As |
|---------|---------|-------------|
| SSN | 123-45-6789 | [REDACTED:SSN] |
| Student IDs | 12345678 | [REDACTED:STUDENT_ID] |
| Email | student@school.edu | [REDACTED:EMAIL] |
| Phone | (555) 123-4567 | [REDACTED:PHONE] |
| API keys | sk-abc123... | [REDACTED:API_KEY] |
| Medications | 50 mg levothyroxine | [REDACTED:MEDICATION] |
| Lab values | TSH = 4.5 mIU/L | [REDACTED:LAB_VALUE] |
| Financials | $1,500.00 | [REDACTED:FINANCIAL] |

### Integration

DLP is already wired into `agents.py` (Gemini API calls). No manual
configuration needed. To test:

```bash
cd canvas-agent-grader
python dlp.py  # Runs self-test
```

## 4. Student Data Anonymization

The `canvas-agent-grader/anonymizer.py` module replaces student names and IDs
with deterministic pseudonyms before data leaves the Mac.

### How It Works

1. Canvas API returns real student name: "Jane Doe"
2. Anonymizer generates pseudonym: "Student_7A3F"
3. All submission text containing "Jane Doe" is replaced with "Student_7A3F"
4. Gemini AI grades the anonymized submission
5. Rationale text is deanonymized before writing to the local CSV

Real names **never leave the Mac**. Gemini only sees pseudonyms.

### Testing

```bash
cd canvas-agent-grader
python anonymizer.py  # Runs self-test
```

## 5. Transition Alert Daemon

Enable the `at` daemon for timed alerts:

```bash
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist
```

Grant Accessibility permissions to Terminal/Claude:
System Settings > Privacy & Security > Accessibility > Add Terminal.app

## 6. Cron Jobs for Night Shift and Sunday Reset

```bash
# Schedule Night Shift (2:00 AM daily) and Sunday Reset (3:00 AM Sundays)
REPO="$HOME/Documents/Second_Brain"
(crontab -l 2>/dev/null; echo "0 2 * * * ${REPO}/.claude/scripts/daily_night_shift.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * 0 ${REPO}/.claude/scripts/sunday_reset.sh") | crontab -

# Verify
crontab -l
```

## 7. MCP Server Installation

```bash
# Ensure Node.js is installed
brew install node

# The MCP config template is at .claude/mcp-config-template.json
# Copy it to the Claude Desktop config location:
cp .claude/mcp-config-template.json "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Install mcp-ical (requires uv for Python)
brew install uv
mkdir -p /Users/Shared/mcp
cd /Users/Shared/mcp
git clone https://github.com/aaplabs/mcp-ical.git
```

## 8. Credential Setup

```bash
# Copy the template and fill in your credentials
cp .env.example .env

# Edit with your values:
# CANVAS_API_URL=https://your-school.instructure.com
# CANVAS_API_TOKEN=<from Canvas Settings > Approved Integrations>
# GEMINI_API_KEY=<from Google AI Studio>
```

## 9. Verification Checklist

- [ ] Agent_Workspace account exists and is NOT admin
- [ ] LuLu/Little Snitch installed with default-deny rules
- [ ] `curl https://httpbin.org/ip` fails from Agent_Workspace
- [ ] `python dlp.py` self-test passes
- [ ] `python anonymizer.py` self-test passes
- [ ] `at` daemon is loaded
- [ ] Cron jobs are registered (`crontab -l` shows 2 entries)
- [ ] MCP config is in place
- [ ] `.env` has all three credentials filled
- [ ] Accessibility permissions granted to Terminal
