"""Template library for project initialization."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ProjectTemplate:
    """A project configuration template."""

    id: str
    name: str
    description: str
    category: str
    provider: str
    model: str
    temperature: float
    system_prompt: str
    context_files: List[str]
    exclude_patterns: List[str]
    tools: List[str]
    example_use_cases: List[str]


class TemplateLibrary:
    """Library of project templates for different use cases."""

    def __init__(self):
        """Initialize template library."""
        self.templates: Dict[str, ProjectTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        """Load all available templates."""
        # Python templates
        self.templates["python-fastapi"] = ProjectTemplate(
            id="python-fastapi",
            name="FastAPI Development",
            description="Modern async Python web API framework",
            category="Python",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.3,
            system_prompt="""# FastAPI Project Assistant

You are an expert FastAPI developer. When working on this project:

## Code Style
- Use async/await for all route handlers
- Type hints everywhere (Pydantic models)
- Follow PEP 8 conventions
- Descriptive variable names

## Architecture
- Follow clean architecture principles
- Separate concerns: routes, services, models
- Use dependency injection for services
- Keep routes thin, business logic in services

## Testing
- Write pytest tests for all endpoints
- Use TestClient from fastapi.testclient
- Mock external dependencies
- Aim for >80% coverage

## Security
- Validate all inputs with Pydantic
- Use proper authentication (OAuth2/JWT)
- Sanitize database queries (use ORM)
- CORS configuration for production

## Performance
- Use async database drivers
- Implement caching where appropriate
- Optimize database queries (N+1 problem)
- Use background tasks for slow operations

When generating code:
1. Always include type hints
2. Add docstrings for public functions
3. Include error handling
4. Write corresponding tests
5. Consider edge cases""",
            context_files=["**/*.py", "requirements.txt", "README.md"],
            exclude_patterns=["**/test_*.py", "**/__pycache__/**", "**/venv/**", "**/.venv/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["REST API development", "Async web services", "Microservices"]
        )

        self.templates["python-django"] = ProjectTemplate(
            id="python-django",
            name="Django Development",
            description="Full-featured Python web framework",
            category="Python",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.3,
            system_prompt="""# Django Project Assistant

You are an expert Django developer. When working on this project:

## Code Style
- Follow Django best practices
- Use Django ORM efficiently
- Keep views focused and simple
- Use class-based views when appropriate

## Architecture
- Follow MVT (Model-View-Template) pattern
- Use Django apps for modularity
- Keep business logic in models/managers
- Use forms for validation

## Testing
- Write tests using Django TestCase
- Test models, views, and forms
- Use fixtures for test data
- Integration tests for workflows

## Security
- Use Django's built-in security features
- CSRF protection enabled
- XSS protection with template escaping
- SQL injection prevention with ORM

## Best Practices
- Use migrations for all model changes
- Keep settings secure (environment variables)
- Use Django admin effectively
- Follow Django coding style

When generating code:
1. Follow Django conventions
2. Use Django's built-in features
3. Include proper error handling
4. Write tests for new functionality
5. Consider database performance""",
            context_files=["**/*.py", "requirements.txt", "README.md", "**/models.py", "**/views.py"],
            exclude_patterns=["**/test*.py", "**/__pycache__/**", "**/venv/**", "**/migrations/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["Full-stack web apps", "Admin interfaces", "Content management"]
        )

        self.templates["python-flask"] = ProjectTemplate(
            id="python-flask",
            name="Flask Development",
            description="Lightweight Python web framework",
            category="Python",
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            temperature=0.3,
            system_prompt="""# Flask Project Assistant

You are an expert Flask developer. When working on this project:

## Code Style
- Keep Flask app simple and modular
- Use blueprints for organization
- Follow PEP 8 conventions
- Use extensions wisely

## Architecture
- Use application factory pattern
- Organize with blueprints
- Keep business logic separate
- Use Flask extensions for common tasks

## Testing
- Use pytest with Flask test client
- Test routes and business logic
- Mock external dependencies
- Integration tests for workflows

## Security
- Use Flask-WTF for CSRF protection
- Validate all inputs
- Use Flask-Login for auth
- Secure session configuration

## Best Practices
- Use environment variables for config
- Keep routes simple
- Use Jinja2 templates effectively
- Handle errors gracefully

When generating code:
1. Follow Flask conventions
2. Keep it simple and explicit
3. Include error handling
4. Write tests
5. Use appropriate extensions""",
            context_files=["**/*.py", "requirements.txt", "README.md", "app.py"],
            exclude_patterns=["**/test_*.py", "**/__pycache__/**", "**/venv/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["API development", "Small web apps", "Prototypes"]
        )

        self.templates["python-general"] = ProjectTemplate(
            id="python-general",
            name="Python Development",
            description="General Python development",
            category="Python",
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            temperature=0.3,
            system_prompt="""# Python Development Assistant

You are an expert Python developer. When working on this project:

## Code Style
- Follow PEP 8 conventions
- Use type hints
- Write clear docstrings
- Descriptive variable names

## Best Practices
- Write modular, reusable code
- Use virtual environments
- Keep dependencies minimal
- Use standard library when possible

## Testing
- Write tests with pytest
- Use fixtures for test data
- Mock external dependencies
- Aim for good coverage

## Quality
- Handle errors gracefully
- Use logging for debugging
- Follow SOLID principles
- Keep functions focused

When generating code:
1. Write clean, readable code
2. Include type hints
3. Add docstrings
4. Include error handling
5. Write tests""",
            context_files=["**/*.py", "requirements.txt", "README.md"],
            exclude_patterns=["**/test_*.py", "**/__pycache__/**", "**/venv/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["Scripts", "CLI tools", "Libraries"]
        )

        # Web development templates
        self.templates["web-react"] = ProjectTemplate(
            id="web-react",
            name="React Development",
            description="React frontend development",
            category="Web",
            provider="openai",
            model="gpt-4o",
            temperature=0.4,
            system_prompt="""# React Development Assistant

You are an expert React developer. When working on this project:

## Code Style
- Use functional components with hooks
- Follow React best practices
- Use TypeScript when available
- Keep components small and focused

## Architecture
- Component-based architecture
- Use proper state management
- Keep business logic separate
- Use custom hooks for reusability

## Best Practices
- Use React.memo for optimization
- Proper key usage in lists
- Handle loading and error states
- Accessibility (a11y) compliance

## Testing
- Write tests with React Testing Library
- Test user interactions
- Test edge cases
- Snapshot tests for UI

When generating code:
1. Use modern React patterns
2. Include TypeScript types
3. Handle edge cases
4. Write tests
5. Consider performance""",
            context_files=["src/**/*.{js,jsx,ts,tsx}", "package.json", "README.md"],
            exclude_patterns=["**/node_modules/**", "**/build/**", "**/dist/**", "**/*.test.*"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["SPAs", "Web apps", "UI components"]
        )

        self.templates["web-nextjs"] = ProjectTemplate(
            id="web-nextjs",
            name="Next.js Development",
            description="Next.js React framework",
            category="Web",
            provider="openai",
            model="gpt-4o",
            temperature=0.4,
            system_prompt="""# Next.js Development Assistant

You are an expert Next.js developer. When working on this project:

## Code Style
- Use App Router (Next.js 13+)
- Server Components by default
- Client Components when needed
- Follow Next.js conventions

## Architecture
- Use file-based routing
- Server vs Client Components
- API routes for backend
- Proper data fetching patterns

## Performance
- Use Next.js Image optimization
- Implement proper caching
- Static generation when possible
- Streaming and Suspense

## Best Practices
- SEO optimization
- Use Metadata API
- Error and loading states
- Progressive enhancement

When generating code:
1. Follow Next.js 13+ patterns
2. Use TypeScript
3. Optimize for performance
4. Consider SEO
5. Write tests""",
            context_files=["app/**/*.{js,jsx,ts,tsx}", "pages/**/*.{js,jsx,ts,tsx}", "package.json", "README.md"],
            exclude_patterns=["**/node_modules/**", "**/.next/**", "**/out/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["Full-stack apps", "Static sites", "SEO-critical sites"]
        )

        self.templates["nodejs-backend"] = ProjectTemplate(
            id="nodejs-backend",
            name="Node.js Backend",
            description="Node.js backend development",
            category="Web",
            provider="openai",
            model="gpt-4o-mini",
            temperature=0.3,
            system_prompt="""# Node.js Backend Assistant

You are an expert Node.js backend developer. When working on this project:

## Code Style
- Use async/await
- Follow JavaScript/TypeScript best practices
- Use ESM modules
- Proper error handling

## Architecture
- RESTful API design
- Proper middleware usage
- Separate routes/controllers
- Use services for business logic

## Security
- Input validation
- Authentication/authorization
- Rate limiting
- CORS configuration

## Best Practices
- Use environment variables
- Proper logging
- Error handling middleware
- Database connection pooling

When generating code:
1. Use modern JavaScript
2. Include error handling
3. Validate inputs
4. Write tests
5. Consider scalability""",
            context_files=["src/**/*.{js,ts}", "package.json", "README.md"],
            exclude_patterns=["**/node_modules/**", "**/dist/**", "**/*.test.*"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["REST APIs", "GraphQL servers", "Microservices"]
        )

        # Mobile templates
        self.templates["mobile-react-native"] = ProjectTemplate(
            id="mobile-react-native",
            name="React Native",
            description="Cross-platform mobile development",
            category="Mobile",
            provider="openai",
            model="gpt-4o",
            temperature=0.4,
            system_prompt="""# React Native Development Assistant

You are an expert React Native developer. When working on this project:

## Code Style
- Use functional components
- Follow React Native best practices
- Use TypeScript
- Platform-specific code when needed

## Architecture
- Component-based architecture
- Use React Navigation
- State management (Redux/Context)
- Proper async handling

## Performance
- Optimize re-renders
- Use FlatList for lists
- Image optimization
- Memory management

## Best Practices
- iOS and Android testing
- Handle permissions
- Offline functionality
- Accessibility

When generating code:
1. Cross-platform by default
2. Platform-specific when needed
3. Consider performance
4. Test on both platforms
5. Handle edge cases""",
            context_files=["src/**/*.{js,jsx,ts,tsx}", "package.json", "README.md"],
            exclude_patterns=["**/node_modules/**", "**/android/build/**", "**/ios/build/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["Mobile apps", "Cross-platform apps"]
        )

        # Data Science template
        self.templates["data-science"] = ProjectTemplate(
            id="data-science",
            name="Data Science",
            description="Data analysis and ML projects",
            category="Data Science",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.5,
            system_prompt="""# Data Science Assistant

You are an expert data scientist. When working on this project:

## Code Style
- Use pandas for data manipulation
- NumPy for numerical operations
- Clear variable names
- Document assumptions

## Analysis
- Exploratory data analysis
- Data visualization
- Statistical testing
- Feature engineering

## ML Best Practices
- Train/test/validation split
- Cross-validation
- Model evaluation metrics
- Hyperparameter tuning

## Documentation
- Document data sources
- Explain methodology
- Visualize results
- Reproducible analysis

When generating code:
1. Clear and reproducible
2. Include visualizations
3. Document assumptions
4. Explain methodology
5. Validate results""",
            context_files=["**/*.py", "**/*.ipynb", "requirements.txt", "README.md"],
            exclude_patterns=["**/data/**", "**/__pycache__/**", "**/.ipynb_checkpoints/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["Data analysis", "ML modeling", "Visualization"]
        )

        # Documentation template
        self.templates["documentation"] = ProjectTemplate(
            id="documentation",
            name="Documentation",
            description="Technical writing and documentation",
            category="Documentation",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            system_prompt="""# Documentation Assistant

You are an expert technical writer. When working on this project:

## Writing Style
- Clear and concise
- Active voice
- User-focused
- Proper formatting

## Structure
- Logical organization
- Table of contents
- Code examples
- Screenshots/diagrams

## Best Practices
- Keep it up to date
- Include examples
- Link to resources
- Version information

## Documentation Types
- README files
- API documentation
- Tutorials
- User guides

When generating documentation:
1. Write clearly
2. Include examples
3. Use proper formatting
4. Keep it updated
5. Consider the audience""",
            context_files=["**/*.md", "docs/**/*", "README.md"],
            exclude_patterns=["**/node_modules/**", "**/venv/**"],
            tools=["code_search", "file_edit"],
            example_use_cases=["Technical docs", "User guides", "API docs"]
        )

        # General template
        self.templates["general"] = ProjectTemplate(
            id="general",
            name="General Development",
            description="Generic project template",
            category="General",
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
            temperature=0.5,
            system_prompt="""# Development Assistant

You are an expert software developer. When working on this project:

## Code Style
- Follow language conventions
- Write clean, readable code
- Use meaningful names
- Add comments when needed

## Best Practices
- Keep code modular
- Handle errors gracefully
- Write tests
- Use version control

## Quality
- Code reviews
- Testing
- Documentation
- Continuous improvement

When generating code:
1. Write clean code
2. Include error handling
3. Add tests
4. Document complex logic
5. Follow best practices""",
            context_files=["**/*"],
            exclude_patterns=["**/node_modules/**", "**/__pycache__/**", "**/venv/**", "**/.git/**"],
            tools=["code_search", "file_edit", "terminal"],
            example_use_cases=["Any project type"]
        )

    def get_template(self, template_id: str) -> Optional[ProjectTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def list_templates(self, category: Optional[str] = None) -> List[ProjectTemplate]:
        """List all templates, optionally filtered by category."""
        templates = list(self.templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return sorted(templates, key=lambda t: (t.category, t.name))

    def get_categories(self) -> List[str]:
        """Get list of template categories."""
        categories = set(t.category for t in self.templates.values())
        return sorted(categories)

    def find_best_template(self, primary_language: Optional[str], frameworks: List[str]) -> Optional[ProjectTemplate]:
        """Find the best matching template for given characteristics.

        Args:
            primary_language: Primary programming language
            frameworks: List of detected frameworks

        Returns:
            Best matching template or None
        """
        # Special mappings for frameworks that don't match template IDs directly
        framework_mappings = {
            "express": "nodejs-backend",
            "nest.js": "nodejs-backend",
            "nestjs": "nodejs-backend",
            "next.js": "web-nextjs",
            "nextjs": "web-nextjs",
            "react-native": "mobile-react-native",
        }

        # Check for framework-specific templates with mappings
        for framework in frameworks:
            framework_lower = framework.lower().replace('.', '').replace('-', '')

            # Check direct mapping
            if framework_lower in framework_mappings:
                mapped_id = framework_mappings[framework_lower]
                if mapped_id in self.templates:
                    return self.templates[mapped_id]

            # Check template ID matching
            for template_id, template in self.templates.items():
                template_id_clean = template_id.lower().replace('.', '').replace('-', '')
                if framework_lower in template_id_clean:
                    return template

        # Check for language-specific templates
        if primary_language:
            lang_lower = primary_language.lower()
            for template_id, template in self.templates.items():
                if template_id.startswith(f"{lang_lower}-general"):
                    return template

        # Return general template as fallback
        return self.templates.get("general")


# Singleton instance
_library: Optional[TemplateLibrary] = None


def get_template_library() -> TemplateLibrary:
    """Get the global template library instance."""
    global _library
    if _library is None:
        _library = TemplateLibrary()
    return _library
