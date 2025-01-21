Conventions:

Code Style:
- Follow PEP 8 with some modern adaptations
- Use type hints consistently throughout the code
- Use CamelCase for variable names
- Be sure to statically type all code

Comments and Documentation:
- Function docstrings should be at the top of each function
- Format for function documentation:
```python
def processTransaction(amount: Decimal, category: str) -> Transaction:
    """
    Creates and validates a new transaction.
    
    Args:
        amount: Transaction amount (positive for income, negative for expenses)
        category: Transaction category name, must exist in database
        
    Returns:
        Transaction: Validated transaction object
        
    Raises:
        ValidationError: If category doesn't exist or amount is invalid
    """
```
- Add inline comments only for complex logic that isn't immediately clear
- Keep implementation details in the code, business logic explanation in comments

Git Conventions:
- Commit messages should follow this format:
  ```
  type(scope): description
  
  [optional body]
  ```
  Types:
  - feat: new feature
  - fix: bug fix
  - refactor: code change that neither fixes a bug nor adds a feature
  - docs: documentation only changes
  - style: formatting, missing semi colons, etc; no code change
  - test: adding missing tests
  - chore: updating build tasks, package manager configs, etc

  Examples:
  ```
  feat(transactions): add support for recurring transactions
  fix(cli): correct date parsing in add command
  docs(readme): update installation instructions
  ```

Error Handling:
- Use custom exceptions for business logic errors
- Document all possible exceptions in function docstrings
- Handle edge cases explicitly

Testing:
- Write tests alongside new code
- Test files should mirror the structure of the main code
- Each test should have a clear "Arrange, Act, Assert" structure