# HexiRules 🔬

A hexagonal cellular automaton simulator with an interactive GUI, implementing Conway's Game of Life rules on a hexagonal grid.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **Hexagonal Grid**: 6-neighbor cellular automaton (vs traditional 8-neighbor square grid)
- **Interactive GUI**: Click cells to toggle alive/dead states
- **Customizable Rules**: Support for Birth/Survival rules (e.g., `B3/S23`)
- **Real-time Simulation**: Start/stop evolution with visual feedback
- **Scalable Interface**: Auto-sizing grid that fits window dimensions
- **Clean Architecture**: Separated logic and GUI for easy testing

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- No external dependencies (uses only standard library)

### Installation & Running

```bash
# Clone the repository
git clone <repository-url>
cd HexiRules

# Run directly
python main.py

# Or create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

## 🎮 How to Use

1. **Toggle Cells**: Left-click hexagons to make them alive (black) or dead (white)
2. **Set Rules**: Enter rules in format `B3/S23` and click "Set Rule"
   - `B3` = Birth: dead cells become alive with exactly 3 neighbors
   - `S23` = Survival: alive cells survive with 2 or 3 neighbors
3. **Simulate**: Click "Start" to begin evolution, "Stop" to pause
4. **Clear**: Reset all cells to dead state

## 🧪 Development

### Running Tests
```bash
# Run all tests
python -m unittest discover -s tests -v

# Run specific test file
python tests/test_automaton.py
```

### VS Code Setup
The project includes VS Code configuration for:
- Debugging (`F5`)
- Test discovery and execution
- Python environment management

## 📐 Architecture

```
HexiRules/
├── main.py           # GUI and application entry point
├── automaton.py      # Core cellular automaton logic
├── tests/            # Unit tests
│   └── test_automaton.py
├── .vscode/          # VS Code configuration
└── README.md
```

## 🔬 Hexagonal vs Square Grids

Traditional cellular automata use square grids where each cell has 8 neighbors. Hexagonal grids offer:
- **6 neighbors per cell**: More natural and symmetric neighbor relationships
- **No diagonal bias**: All neighbors are equidistant
- **Biological relevance**: Many natural structures follow hexagonal patterns

## 🎯 Rule Examples

- `B3/S23`: Classic Conway's Game of Life adapted for hexagonal grid
- `B2/S34`: Different evolution patterns
- `B36/S23`: More aggressive birth conditions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
