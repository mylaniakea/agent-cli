# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: matthew@mylaniakea.com

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Best Practices

### API Key Management

**Never commit API keys to version control:**

```bash
# Add these to .gitignore
.env
.env.local
.agent.yml
claude.md
gemini.md
gpt.md
*.md  # If you store keys in project markdown files
```

**Use environment variables:**

```bash
# Recommended: Store in .env file (not committed)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

**Or use keyring (optional):**

```bash
# Securely store keys in system keyring
agent config set --keyring openai sk-...
```

### Project Configuration Files

If using project-specific configuration files (`claude.md`, `.agent.yml`):

1. **Do not include API keys in these files**
2. **Add them to `.gitignore` if they contain sensitive data**
3. **Use environment variables for API keys instead**

Example safe configuration:

```yaml
# .agent.yml - Safe to commit
provider: anthropic
model: claude-3-5-sonnet-20241022
temperature: 0.7

# API key loaded from environment variable
# ANTHROPIC_API_KEY=sk-ant-... (in .env, not committed)
```

### Conversation Logs

Agent CLI may log conversations to `~/.agent-cli/logs/` for debugging and history.

**To disable logging:**

```yaml
# .agent.yml
logging:
  enabled: false
```

**To enable privacy mode:**

```bash
# Prevents logging sensitive data
agent config set privacy_mode true
```

### Network Security

- Agent CLI makes HTTPS requests to API providers (OpenAI, Anthropic, Google)
- Local Ollama connections use HTTP (localhost only by default)
- No telemetry or analytics data is collected

### Dependencies

We regularly update dependencies to patch security vulnerabilities. Run:

```bash
# Update agent-cli
pip install --upgrade agent-cli

# Or with uv
uv pip install --upgrade agent-cli
```

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find any similar problems
3. Prepare fixes for all supported versions
4. Release patched versions as soon as possible

## Comments on this Policy

If you have suggestions on how this process could be improved, please submit a pull request or open an issue.

## Additional Resources

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OpenAI API Key Best Practices](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [Anthropic Security Documentation](https://docs.anthropic.com/claude/docs/security)

---

Last updated: December 2024
