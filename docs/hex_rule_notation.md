# Hexagonal Rule Notation Specification

This document defines the custom rule notation used to simulate state transitions in a hexagonal cellular automaton. It includes coordinate conventions, rule syntax, semantics, macro expansions, and constraints.

## 1. Hexagonal Grid Model

Each cell has 6 neighbors. Directions are numbered clockwise, starting from the upper right:

```
   6   1
 5   *   2
   4   3
```

Each cell has:

- A state (e.g., \_, a, wH)
- An optional direction (integer 1–6)

## 2. Rule Notation Overview

A rule has the form:

```
source => target
```

It describes how a cell changes state (and optionally direction) based on its own state and neighborhood.

### Examples

- `a => b` — Unconditional change from `a` to `b`
- `a[x] => b` — Change from `a` to `b` if any neighbor has state `x` 
- `a[1x] => b` — Change from `a` to `b` if the neighbor in the position 1 has state `x`
- `a[1x3] => b` — Change from `a` to `b` if the neighbor in the position 1 has state `x3` (x with direction 3)  
- `x% => y%` — Change from `x` to `y` in the same (random) direction
- `x% => y%5` — Change from `x` to `y`, rotate direction by 5 steps clockwise
- `x[1-a] => b` — Change from `x` to `b` if direction 1 does not contain state `a`
- `x[y.] => z` — Change from `x` to `z` if any neighbor in state `y` is pointing at the center
- `x[y.] => z.5` — Same as above, but `z` gains direction 5 clockwise from incoming neighbor

## 3. Formal Syntax (EBNF)

```
rule             = source "=>" target ;
source           = state [ direction ] [ condition_block ] ;
target           = state [ direction ]
                 | state "%" [ rotation ] ;

state            = identifier ;
direction        = integer ;           (* 1–6 *)
rotation         = integer ;           (* 0–5 *)

condition_block  = "[" condition "]" ;
condition        = [ direction_index ] [ "-" ] state [ orientation_marker ] ;
direction_index  = integer ;           (* 1–6 *)
orientation_marker = "." | integer | "%" ;  (* direction of neighbor: to center, exact, or random *)

identifier       = letter { letter | "_" } ;
integer          = digit { digit } ;
digit            = "0".."9" ;
letter           = "a".."z" ;
```

## 4. Semantics

- Rules are applied in parallel to all cells
- Only one rule is applied per cell, chosen randomly among valid matches
- States can have direction suffixes (e.g., `a3`, `wH1`)
- `%` implies random direction (macro-expanded)
- `.` in condition means neighbor points toward center
- `-` means absence of the state in specified direction

## 5. Macro Expansions

- `x%` expands to: `x1 x2 x3 x4 x5 x6`
- `x[y.]` expands to: `x[1y4] x[2y5] x[3y6] x[4y1] x[5y2] x[6y3]`
- `y%5` means rotate y's direction 5 steps clockwise from source direction
- `z.5` means `z` takes direction 5 steps clockwise from incoming direction

## 6. Constraints

- Only one condition allowed per rule (no `,` support)
- Digits are not allowed in state names
- Rules are string-based and must be expanded before matching
- All direction math is modulo 6 (1-based): `(d + n - 1) % 6 + 1`

To reverse direction (point to center), use: `(d + 3 - 1) % 6 + 1`

## 7. Example Rules

```
t[-a] => t%
_[t.] => a
t%[a] => t
```

## 8. Planned Extensions (Not Yet Implemented)

- JSON-like state properties
- State inheritance from neighbors
- Probabilistic transitions with weights
- Totalistic / semi-totalistic shorthand

