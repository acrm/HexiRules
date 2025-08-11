# CLI How-To

The HexiRules command-line interface lets you configure and run worlds
without the GUI.

## Starting the shell

```
python src/cli.py --rule B3/S23 --radius 3
```

Use `--rule` to choose the starting rule and `--radius` for grid size.

## Core commands

- `rule [RULE]` – set or show the current rule
- `rules` – list all rules
- `set Q R STATE` – set a cell state (1 alive, 0 dead)
- `toggle Q R` – toggle a cell
- `query Q R` – print cell state
- `summary` – show alive cell count
- `cells` – list alive cell coordinates
- `grid [RADIUS]` – print grid in ASCII
- `step [N]` – advance N generations
- `clear` – clear all cells
- `exit` – leave the shell

## HexiDirect rules

HexiDirect notation is also supported. Example:

```
python src/cli.py --rule "a=>_"
```

The same commands apply. Active cells default to state `a` with
direction `1` when using `set` or `toggle`.
