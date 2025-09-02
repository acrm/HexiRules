# ASCII-UI Mini-Framework (Pre-development Design)

## Goals
- Deterministic symbolic UI (81×51 for now) for headless tests and retro aesthetic.
- Host-agnostic: CLI or Tk host forward keys; ASCII layer handles command buffer.

## Contracts
- Render: `(lines: List[str], tags: List[List[(start, end, tag)]])`.
- Inputs: controller (WorldService), ui_state (focus, command_buffer, selected_cell), theme.
- Deterministic output; never crash; errors tagged in-text.

## Layout & Rendering
- GridLayoutSpec (fixed now): header; two columns (Worlds/Rules, History/Logs); Selected; Footer.
- Border-join via bitmask grid (N/E/S/W) across all frames ensures shared lines.
- Titles/hotkeys are in-border; body text clipped to rect.
- Tags: border, border_sel, title, normal, command_prompt (host maps to colors).

## Widgets
- Frame(title, hotkey, body)
- TextBlock (clipped)
- ListView (Worlds/History)
- LogView (Logs)
- StatusBar (Selected)
- CommandBar (prompt + input buffer; Enter to submit)

## Theme
- Unicode (box-drawing) and ASCII fallback (+-|).

## Events & Focus
- Focus: top or a frame (W/R/H/L); Esc to top; Ctrl+Q quit (host handles).
- Typing feeds CommandBar buffer; Enter submits; UI re-renders.

## Testing
- Snapshot tests of (lines, tags) for widgets and whole surface.
- Property tests for border joins and clipping.
- Event tests feed key sequences and assert UI states.

## Integration
- CLI host: print lines, read stdin, feed keys.
- Tk host: Text widget draws lines + tag spans; keys bound globally (no Entry).

## Roadmap (incremental)
1) Theme + CommandBar extraction (replace ad-hoc prompt overlay)
2) Worlds as ListView; Logs as LogView; Selected as StatusBar
3) Optional resizing and proportional rows/cols (later)
