# Contributors

This project exists thanks to all the people who contribute.

## Core Team

### Elyo
- **Role**: Project Lead, Architect
- **Contributions**:
  - Clean Architecture migration (v1.0.0)
  - Domain Layer design (Entities, Repositories)
  - Plugin System architecture
  - Test Suite expansion (120+ tests)
  - Literal types implementation
  - Documentation & project organization

## Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute

1. **Code Contributions**
   - Bug fixes
   - Feature implementations
   - Performance improvements
   - Test coverage

2. **Documentation**
   - Improve existing docs
   - Add examples
   - Fix typos
   - Translate to other languages

3. **Testing**
   - Report bugs
   - Suggest improvements
   - Write test cases

4. **Design**
   - UI/UX improvements
   - Architecture proposals
   - API design

### How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/fdk-mcp.git
   cd fdk-mcp
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding style (see DEVELOPMENT.md)
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   uv run pytest
   uv run ruff check src/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add your feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub.

### Coding Standards

- **Python Style**: Follow PEP 8, enforced by ruff
- **Type Hints**: All code must have type hints
- **Tests**: All features must have tests
- **Documentation**: Public APIs must be documented

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Build/tooling changes

**Examples:**
```
feat(models): Add Literal types for sort fields
fix(cache): Handle empty cache directory
docs(readme): Update installation instructions
test(domain): Add edge case tests for CatalogObject
```

### Code Review Process

1. All contributions require review
2. At least one approval from core team
3. All tests must pass
4. No merge conflicts

### Recognition

Contributors are recognized in:
- This CONTRIBUTORS.md file
- GitHub contributors page
- Release notes (for significant contributions)

## Community

- **Issues**: [GitHub Issues](https://github.com/elyo/fdk-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/elyo/fdk-mcp/discussions)

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you to all contributors!** 🎉
