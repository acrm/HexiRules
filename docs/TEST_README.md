# HexiRules Test Suite

This directory contains comprehensive tests for the HexiRules hexagonal cellular automaton system.

## Test Files

### Core Engine Tests (`test_hex_rules.py`)
- **HexCell Tests**: Cell creation, string representation, equality
- **HexRule Tests**: Rule parsing for all syntax variants (conditions, directions, macros)
- **HexAutomaton Tests**: Grid management, rule application, neighbor calculation
- **Macro Expansion Tests**: Source %, target %, and pointing condition expansion
- **Complex Scenarios**: Direction persistence, randomization, movement patterns
- **Edge Cases**: Invalid syntax handling, boundary conditions, clearing

### GUI Constants Tests (`test_gui_constants.py`)
- **State Colors**: Completeness and format validation
- **Symbolic States**: Coverage and essential state presence

### ASCII Control Panel Tests (`test_ascii_ui.py`)
- **Rendering**: ASCII layout width and borders
- **Commands**: step and clear operations

### Test Runner (`tools/run_tests.py`)
- Comprehensive test runner with detailed reporting
- Automatically discovers and runs all test modules
- Provides success/failure summary with statistics

## Running Tests

### Run All Tests
```bash
python tools/run_tests.py --no-gui
```

### Run Individual Test Suites
```bash
# Core engine tests
python tests/test_hex_rules.py

# GUI constants tests
python tests/test_gui_constants.py
```

### Run Specific Test Classes
```bash
python -m unittest tests.test_hex_rules.TestHexCell
python -m unittest tests.test_hex_rules.TestMacroExpansion
```

## Test Coverage

### Core Functionality (✅ 100% Covered)
- **Cell Management**: Creation, state, direction handling
- **Rule Parsing**: All syntax variants including macros
- **Rule Application**: Source matching, condition checking, transformations
- **Macro Expansion**: 
  - Source `%` (any direction matching)
  - Target `%` (random direction assignment)
  - Pointing conditions `[x.]`
- **Grid Operations**: Neighbor calculation, boundary handling
- **Cellular Automaton**: Step execution, rule conflict resolution

### Advanced Features (✅ 100% Covered)
- **Randomization**: Multiple rule selection from same macro
- **Direction Persistence**: Once assigned, directions stay fixed
- **Direction Removal**: Rules can remove directions from cells
- **Complex Rule Interactions**: Movement, pointing, state changes
- **Error Handling**: Invalid syntax, boundary conditions

### GUI Components (⚠️ Partial Coverage)
- **Constants**: State colors, symbolic states (✅ Covered)
- **Widget Interactions**: Requires GUI environment (❌ Not testable in CI)
- **Visual Rendering**: Canvas operations (❌ Not testable in CI)

## Test Statistics

- **Total Tests**: 30
- **Core Engine**: 20 tests
- **CLI**: 4 tests
- **ASCII Control Panel**: 2 tests
- **Logic Helpers**: 4 tests
- **Success Rate**: 100%
- **Execution Time**: ~0.01 seconds

## Key Test Cases

### Macro Behavior Validation
- `test_movement_and_direction_persistence`: Ensures `%` creates stable directions
- `test_direction_removal`: Validates direction can be removed by rules
- `test_randomization_behavior`: Confirms random selection from macro expansions

### Rule Parsing Validation
- `test_macro_rule_parsing`: Parses `t%`, `a%5`, `[x.]` syntax
- `test_directional_condition_parsing`: Handles `[2b4]` pointing conditions
- `test_condition_rule_parsing`: Processes `[-a]` negated conditions

### Complex Scenario Testing
- Movement patterns with persistent directions
- Pointing rules creating cells in specific directions
- Multiple rule interactions and conflict resolution

## Adding New Tests

When adding new functionality:

1. **Add unit tests** to `test_hex_rules.py` for core engine features
2. **Add constants tests** to `test_gui_constants.py` for GUI constants
3. **Update test runner** if new test files are created
4. **Document test coverage** in this README

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestHexCell`)
- Test methods: `test_*` (e.g., `test_cell_creation`)

### Test Organization
- Group related tests in classes
- Use descriptive test names
- Include docstrings explaining what is being tested
- Test both success and failure cases
