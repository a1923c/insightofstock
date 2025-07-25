## Agent OS Documentation

### Product Context
- **Mission & Vision**: @.agent-os/product/mission.md
- **Technical Architecture**: @.agent-os/product/tech-stack.md
- **Development Roadmap**: @.agent-os/product/roadmap.md
- **Decision History**: @.agent-os/product/decisions.md

### Development Standards
- **Code Style**: Follow PEP 8 standards for Python, consistent with existing codebase
- **Best Practices**: Test-driven development, clear variable naming, comprehensive error handling
- **Database**: SQLite with SQLAlchemy ORM, follow existing schema patterns

### Project Management
- **Active Specs**: @.agent-os/specs/
- **Spec Planning**: Use `@~/.agent-os/instructions/create-spec.md`
- **Tasks Execution**: Use `@~/.agent-os/instructions/execute-tasks.md`

## Workflow Instructions

When asked to work on this codebase:

1. **First**, check @.agent-os/product/roadmap.md for current priorities
2. **Then**, follow the appropriate instruction file:
   - For new features: @~/.agent-os/instructions/create-spec.md
   - For tasks execution: @~/.agent-os/instructions/execute-tasks.md
3. **Always**, adhere to the standards in the files listed above

## Important Notes

- Product-specific files in `.agent-os/product/` override any global standards
- This is a financial analytics platform focused on Chinese stock market private shareholders
- Data source is Tushare API with daily automated updates
- Core functionality includes shareholder analysis, ticker details, and individual holder tracking
- Database contains ~54k records of top 10 holders across 5,400+ tickers