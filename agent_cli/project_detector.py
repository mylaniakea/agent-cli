"""Project detection and analysis for intelligent initialization."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ProjectAnalysis:
    """Results of project detection and analysis."""

    # Basic info
    path: Path
    has_git: bool = False

    # Language detection
    primary_language: Optional[str] = None
    languages: Dict[str, int] = field(default_factory=dict)  # language -> file count

    # Framework detection
    frameworks: List[str] = field(default_factory=list)

    # Size metrics
    total_files: int = 0
    total_loc: int = 0
    complexity: str = "simple"  # simple, medium, complex

    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    dependency_files: List[str] = field(default_factory=list)

    # Project characteristics
    has_tests: bool = False
    has_docs: bool = False
    has_ci: bool = False

    # Recommendations
    recommended_provider: str = "anthropic"
    recommended_model: str = "claude-3-5-sonnet-20241022"
    recommended_temperature: float = 0.3
    recommended_template: Optional[str] = None

    def get_summary(self) -> str:
        """Get a human-readable summary of the analysis."""
        lines = []
        lines.append("🔍 Project Analysis:")
        lines.append("")

        if self.primary_language:
            lang_name = self.primary_language.title()
            lines.append(f"Primary Language: {lang_name}")

        if self.frameworks:
            frameworks_str = ", ".join(self.frameworks)
            lines.append(f"Frameworks: {frameworks_str}")

        lines.append(f"Project Size: {self.complexity.title()} (~{self.total_loc:,} LOC, {self.total_files} files)")

        if self.has_git:
            lines.append("Git Repository: Yes")

        if self.dependency_files:
            deps_str = ", ".join(self.dependency_files)
            lines.append(f"Dependencies: {deps_str}")

        lines.append("")
        lines.append("📊 Characteristics:")
        lines.append(f"  {'✓' if self.has_tests else '✗'} Tests")
        lines.append(f"  {'✓' if self.has_docs else '✗'} Documentation")
        lines.append(f"  {'✓' if self.has_ci else '✗'} CI/CD")

        lines.append("")
        lines.append("💡 Recommended Configuration:")
        lines.append(f"Provider: {self.recommended_provider}")
        lines.append(f"Model: {self.recommended_model}")
        lines.append(f"Temperature: {self.recommended_temperature}")
        if self.recommended_template:
            lines.append(f"Template: {self.recommended_template}")

        return "\n".join(lines)


class ProjectDetector:
    """Detects project characteristics for intelligent configuration."""

    # Language indicators (filename -> language)
    LANGUAGE_INDICATORS = {
        "requirements.txt": "python",
        "setup.py": "python",
        "pyproject.toml": "python",
        "Pipfile": "python",
        "package.json": "javascript",
        "yarn.lock": "javascript",
        "pnpm-lock.yaml": "javascript",
        "tsconfig.json": "typescript",
        "Cargo.toml": "rust",
        "go.mod": "go",
        "pom.xml": "java",
        "build.gradle": "java",
        "Gemfile": "ruby",
        "composer.json": "php",
    }

    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        # Python
        "fastapi": ["fastapi", "uvicorn"],
        "django": ["django", "manage.py"],
        "flask": ["flask"],
        "pytest": ["pytest", "test_", "_test.py"],

        # JavaScript/TypeScript
        "react": ["react", "jsx", "tsx"],
        "vue": ["vue", ".vue"],
        "next.js": ["next.config", "pages/", "app/"],
        "nuxt": ["nuxt.config"],
        "express": ["express"],
        "nest.js": ["@nestjs"],

        # Mobile
        "react-native": ["react-native"],
        "flutter": ["pubspec.yaml", "flutter"],

        # Other
        "docker": ["Dockerfile", "docker-compose"],
        "kubernetes": [".yaml", "k8s/"],
    }

    # File extensions for language detection
    EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".rb": "ruby",
        ".php": "php",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".swift": "swift",
        ".kt": "kotlin",
    }

    def __init__(self, path: Path):
        """Initialize detector for a project path."""
        self.path = Path(path).resolve()
        self.analysis = ProjectAnalysis(path=self.path)

    def analyze(self) -> ProjectAnalysis:
        """Perform complete project analysis."""
        self._detect_git()
        self._detect_languages()
        self._detect_frameworks()
        self._detect_dependencies()
        self._analyze_size()
        self._detect_project_characteristics()
        self._generate_recommendations()

        return self.analysis

    def _detect_git(self):
        """Detect if project is a git repository."""
        git_dir = self.path / ".git"
        self.analysis.has_git = git_dir.exists()

    def _detect_languages(self):
        """Detect programming languages used in the project."""
        language_counts: Dict[str, int] = {}

        # Check for language indicator files
        for filename, language in self.LANGUAGE_INDICATORS.items():
            if (self.path / filename).exists():
                language_counts[language] = language_counts.get(language, 0) + 10

        # Count files by extension
        for ext, language in self.EXTENSIONS.items():
            files = list(self.path.rglob(f"*{ext}"))
            # Filter out common ignore patterns
            files = [
                f for f in files
                if not any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.venv', 'target', 'build', 'dist']
                          for part in f.relative_to(self.path).parts)
            ]
            if files:
                language_counts[language] = language_counts.get(language, 0) + len(files)

        self.analysis.languages = language_counts

        # Determine primary language
        if language_counts:
            self.analysis.primary_language = max(language_counts.items(), key=lambda x: x[1])[0]

    def _detect_frameworks(self):
        """Detect frameworks used in the project."""
        frameworks = []

        for framework, indicators in self.FRAMEWORK_PATTERNS.items():
            for indicator in indicators:
                # Check if indicator is a file
                if '.' in indicator or indicator.endswith('.py'):
                    if list(self.path.rglob(indicator)):
                        frameworks.append(framework)
                        break
                # Check in dependency files or directory names
                else:
                    # Check requirements.txt
                    req_file = self.path / "requirements.txt"
                    if req_file.exists():
                        content = req_file.read_text()
                        if indicator.lower() in content.lower():
                            frameworks.append(framework)
                            break

                    # Check package.json
                    pkg_file = self.path / "package.json"
                    if pkg_file.exists():
                        content = pkg_file.read_text()
                        if indicator.lower() in content.lower():
                            frameworks.append(framework)
                            break

                    # Check for directories
                    if indicator.endswith('/'):
                        if (self.path / indicator.rstrip('/')).exists():
                            frameworks.append(framework)
                            break

        self.analysis.frameworks = list(set(frameworks))

    def _detect_dependencies(self):
        """Detect project dependencies."""
        dep_files = []
        dependencies = []

        # Python
        if (self.path / "requirements.txt").exists():
            dep_files.append("requirements.txt")
            content = (self.path / "requirements.txt").read_text()
            dependencies.extend([
                line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                for line in content.split('\n')
                if line.strip() and not line.startswith('#')
            ])

        if (self.path / "pyproject.toml").exists():
            dep_files.append("pyproject.toml")

        # JavaScript
        if (self.path / "package.json").exists():
            dep_files.append("package.json")
            try:
                import json
                content = json.loads((self.path / "package.json").read_text())
                dependencies.extend(content.get("dependencies", {}).keys())
                dependencies.extend(content.get("devDependencies", {}).keys())
            except:
                pass

        # Rust
        if (self.path / "Cargo.toml").exists():
            dep_files.append("Cargo.toml")

        # Go
        if (self.path / "go.mod").exists():
            dep_files.append("go.mod")

        self.analysis.dependency_files = dep_files
        self.analysis.dependencies = dependencies

    def _analyze_size(self):
        """Analyze project size and complexity."""
        # Count files
        source_files = []
        for ext in self.EXTENSIONS.keys():
            files = list(self.path.rglob(f"*{ext}"))
            # Filter out common ignore patterns
            files = [
                f for f in files
                if not any(part.startswith('.') or part in ['node_modules', '__pycache__', 'venv', '.venv', 'target', 'build', 'dist']
                          for part in f.relative_to(self.path).parts)
            ]
            source_files.extend(files)

        self.analysis.total_files = len(source_files)

        # Count lines of code
        total_loc = 0
        for file in source_files[:100]:  # Limit to first 100 files for performance
            try:
                content = file.read_text()
                total_loc += len([line for line in content.split('\n') if line.strip()])
            except:
                pass

        self.analysis.total_loc = total_loc

        # Determine complexity
        if total_loc < 1000 or self.analysis.total_files < 10:
            self.analysis.complexity = "simple"
        elif total_loc < 10000 or self.analysis.total_files < 50:
            self.analysis.complexity = "medium"
        else:
            self.analysis.complexity = "complex"

    def _detect_project_characteristics(self):
        """Detect project characteristics like tests, docs, CI."""
        # Check for tests
        test_indicators = ["test", "tests", "spec", "__tests__"]
        for indicator in test_indicators:
            if (self.path / indicator).exists():
                self.analysis.has_tests = True
                break

        # Check for test files
        if not self.analysis.has_tests:
            test_files = list(self.path.rglob("test_*.py")) + list(self.path.rglob("*_test.py")) + \
                        list(self.path.rglob("*.test.js")) + list(self.path.rglob("*.spec.js"))
            self.analysis.has_tests = len(test_files) > 0

        # Check for docs
        doc_indicators = ["docs", "doc", "documentation"]
        for indicator in doc_indicators:
            if (self.path / indicator).exists():
                self.analysis.has_docs = True
                break

        # Check for CI
        ci_indicators = [".github/workflows", ".gitlab-ci.yml", ".travis.yml", "Jenkinsfile"]
        for indicator in ci_indicators:
            if (self.path / indicator).exists():
                self.analysis.has_ci = True
                break

    def _generate_recommendations(self):
        """Generate recommendations based on project analysis."""
        # Provider recommendation
        if self.analysis.complexity == "complex":
            self.analysis.recommended_provider = "anthropic"
            self.analysis.recommended_model = "claude-3-5-sonnet-20241022"
        elif self.analysis.primary_language == "python":
            self.analysis.recommended_provider = "anthropic"
            self.analysis.recommended_model = "claude-3-5-haiku-20241022"
        else:
            self.analysis.recommended_provider = "openai"
            self.analysis.recommended_model = "gpt-4o-mini"

        # Temperature recommendation
        if self.analysis.has_tests or "test" in self.analysis.frameworks:
            self.analysis.recommended_temperature = 0.2
        elif self.analysis.has_docs:
            self.analysis.recommended_temperature = 0.7
        else:
            self.analysis.recommended_temperature = 0.3

        # Template recommendation
        self.analysis.recommended_template = self._determine_template()

    def _determine_template(self) -> Optional[str]:
        """Determine the best template for this project."""
        # Python templates
        if self.analysis.primary_language == "python":
            if "fastapi" in self.analysis.frameworks:
                return "python-fastapi"
            elif "django" in self.analysis.frameworks:
                return "python-django"
            elif "flask" in self.analysis.frameworks:
                return "python-flask"
            else:
                return "python-general"

        # JavaScript/TypeScript templates
        elif self.analysis.primary_language in ["javascript", "typescript"]:
            if "next.js" in self.analysis.frameworks:
                return "web-nextjs"
            elif "react" in self.analysis.frameworks:
                return "web-react"
            elif "vue" in self.analysis.frameworks:
                return "web-vue"
            elif "express" in self.analysis.frameworks:
                return "nodejs-backend"
            else:
                return "web-general"

        # Mobile templates
        elif "react-native" in self.analysis.frameworks:
            return "mobile-react-native"
        elif "flutter" in self.analysis.frameworks:
            return "mobile-flutter"

        # Rust
        elif self.analysis.primary_language == "rust":
            return "rust-general"

        # Go
        elif self.analysis.primary_language == "go":
            return "go-general"

        return "general"


def detect_project(path: Optional[Path] = None) -> ProjectAnalysis:
    """Convenience function to detect and analyze a project.

    Args:
        path: Path to analyze (default: current directory)

    Returns:
        ProjectAnalysis with detected characteristics
    """
    if path is None:
        path = Path.cwd()

    detector = ProjectDetector(path)
    return detector.analyze()
