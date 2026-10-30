# story2-format

`.story2` is a minimal, plain ASCII format for interactive narrative stories. It's designed to diff cleanly on GitHub and to be hand-edited in any text editor, including VS Code.

## Example

```story2
# story2 v1
@title: The Forgotten Crypt
@author: Alex Mercer

@preview
The Forgotten Crypt by Alex Mercer
A dark doorway beckons in the misty forest.
Will you step inside or turn back?
Choose wisely to survive the night.
@end

@scene: intro
You stand before an ancient stone door covered in glowing moss.
Cold wind blows from a crack in the frame.
-> choice: a.) Open the stone door | search
-> choice: b.) Walk away into the forest | walk_away

@scene: search
Inside, a spiral staircase leads down into darkness.
Torchlight flickers ahead, casting strange shadows on the wall.
-> goto: ending

@scene: walk_away
You turn back toward the safety of your village.
The secrets of the crypt remain buried forever.
-> goto: ending

@scene: ending
Your story comes to an end.
```

## Syntax

| Element | Form |
|---|---|
| Version header | `# story2 v1` on the first non-empty line |
| Title / author | `@title: <text>`, `@author: <text>` |
| Preview block | `@preview` ... `@end`. First line is the title line, followed by up to 3 teaser lines |
| Scene | `@scene: <scene_id>` followed by narration text |
| Choice | `-> choice: <label> \| <target_scene>` |
| Goto | `-> goto: <target_scene>` |

## Rules

1. Files must be plain ASCII.
2. Every file must include a `@scene: intro` scene.
3. Every file must include at least one ending scene, either a scene with no outgoing choices or gotos, or one named `ending` or `end`.
4. Every choice and goto target must point to a scene ID that exists in the file.
5. Preview teaser text is limited to 3 lines.

See [SPEC.md](SPEC.md) for the full specification.

## Parser and validator

`story2_parser.py` parses a `.story2` file and checks it against the rules above. It uses only the Python standard library.

```bash
python story2_parser.py example.story2
```

The script prints the parsed metadata, the number of scenes, and any validation issues. It can also be imported:

```python
from story2_parser import parse_story2, validate_story2

with open("example.story2", encoding="utf-8") as f:
    story = parse_story2(f.read())

issues = validate_story2(story)
```

## License

MIT. See [LICENSE](LICENSE).
