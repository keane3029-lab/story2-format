# .story2 File Format Specification (v1)

## Overview
`.story2` is a minimal, plain ASCII interactive narrative format designed for version control (GitHub diffs) and hand-editing in VS Code.

## Quick Reference
- **Version Header**: `# story2 v1` (Line 1)
- **Metadata**: `@title: <text>`, `@author: <text>`
- **Preview Block**:
  ```story2
  @preview
  <Title> by <Author>
  <Teaser Line 1>
  <Teaser Line 2>
  <Teaser Line 3>
  @end
  ```
- **Scene Block**:
  ```story2
  @scene: <scene_id>
  <Narration text>
  -> choice: <label> | <target_scene>
  -> goto: <target_scene>
  ```

## Rules & Validation
1. File encoding must be plain ASCII.
2. Every file must include `@scene: intro` and at least one terminal ending scene.
3. Every choice and goto target must point to an existing scene ID.
4. Preview block teaser text is limited to a maximum of 3 lines.
