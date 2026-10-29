# story2_parser.py - Parser and Validator for .story2 interactive story files

import re
from typing import Dict, List, Any, Tuple, Optional

class Story2ParseError(Exception):
    pass

def parse_story2(content: str) -> Dict[str, Any]:
    """
    Parses a .story2 format string and returns a structured story object.
    
    Returns:
        dict containing:
            - version: str
            - title: Optional[str]
            - author: Optional[str]
            - preview: dict with 'title_line' and 'teaser_lines'
            - scenes: dict mapping scene_id to scene data dict
            - errors: list of syntax/formatting errors found during parsing
    """
    lines = content.splitlines()
    
    result = {
        "version": None,
        "title": None,
        "author": None,
        "preview": {
            "title_line": None,
            "teaser_lines": []
        },
        "scenes": {},
        "errors": []
    }
    
    # Check ASCII constraint
    for idx, line in enumerate(lines, 1):
        if not line.isascii():
            result["errors"].append(f"Line {idx}: Non-ASCII character detected.")

    # Validate version header
    non_empty_lines = [(idx + 1, l.strip()) for idx, l in enumerate(lines) if l.strip()]
    if not non_empty_lines:
        result["errors"].append("File is empty.")
        return result
        
    first_line_num, first_line = non_empty_lines[0]
    if first_line.startswith("# story2 v"):
        result["version"] = first_line.replace("# story2 ", "").strip()
    else:
        result["errors"].append(f"Line {first_line_num}: Missing or invalid version header '# story2 v1'.")

    in_preview = False
    preview_lines = []
    current_scene_id = None
    
    for line_num, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        
        # Skip empty lines or general comments outside preview
        if not line or (line.startswith("#") and not in_preview):
            continue
            
        # Preview block handling
        if line == "@preview":
            if in_preview:
                result["errors"].append(f"Line {line_num}: Nested @preview block detected.")
            in_preview = True
            continue
        elif line == "@end":
            if not in_preview:
                result["errors"].append(f"Line {line_num}: @end without matching @preview.")
            in_preview = False
            
            # Process collected preview lines
            if preview_lines:
                result["preview"]["title_line"] = preview_lines[0]
                result["preview"]["teaser_lines"] = preview_lines[1:]
                if len(preview_lines[1:]) > 3:
                    result["errors"].append(f"Line {line_num}: Preview block has {len(preview_lines[1:])} teaser lines (max allowed is 3).")
            continue
            
        if in_preview:
            preview_lines.append(line)
            continue

        # Metadata tags
        if line.startswith("@title:"):
            result["title"] = line[7:].strip()
            continue
        elif line.startswith("@author:"):
            result["author"] = line[8:].strip()
            continue
            
        # Scene definition
        if line.startswith("@scene:"):
            current_scene_id = line[7:].strip()
            if not current_scene_id:
                result["errors"].append(f"Line {line_num}: Empty scene name.")
                continue
            if current_scene_id in result["scenes"]:
                result["errors"].append(f"Line {line_num}: Duplicate scene definition '@scene: {current_scene_id}'.")
            result["scenes"][current_scene_id] = {
                "id": current_scene_id,
                "narration": [],
                "choices": [],
                "gotos": []
            }
            continue

        # Inside scene processing
        if current_scene_id and current_scene_id in result["scenes"]:
            scene = result["scenes"][current_scene_id]
            
            if line.startswith("-> choice:"):
                choice_body = line[10:].strip()
                if "|" in choice_body:
                    parts = choice_body.split("|", 1)
                    label = parts[0].strip()
                    target = parts[1].strip()
                    scene["choices"].append({"label": label, "target": target})
                else:
                    result["errors"].append(f"Line {line_num}: Malformed choice syntax. Expected '-> choice: <label> | <target>'.")
            elif line.startswith("-> goto:"):
                target = line[8:].strip()
                scene["gotos"].append(target)
            else:
                # Plain narration line
                scene["narration"].append(raw_line)
        else:
            if not line.startswith("@"):
                result["errors"].append(f"Line {line_num}: Line content found outside of any scene context: '{line}'.")

    if in_preview:
        result["errors"].append("Unclosed @preview block (missing @end).")

    return result


def validate_story2(parsed_story: Dict[str, Any]) -> List[str]:
    """
    Validates scene references, required scenes (intro/ending), and structural consistency.
    
    Returns a list of validation error/warning messages.
    """
    issues = []
    
    # Include parser errors
    issues.extend(parsed_story.get("errors", []))
    
    scenes = parsed_story.get("scenes", {})
    defined_scene_ids = set(scenes.keys())
    
    # 1. Check required scenes
    if "intro" not in defined_scene_ids:
        issues.append("Missing required 'intro' scene (@scene: intro).")
        
    # Check for ending scenes (defined as scenes with no outgoing choices/gotos, or explicitly named 'ending')
    ending_scenes = []
    for scene_id, scene_data in scenes.items():
        if not scene_data["choices"] and not scene_data["gotos"]:
            ending_scenes.append(scene_id)
        elif scene_id.lower() in ("ending", "end"):
            ending_scenes.append(scene_id)
            
    if not ending_scenes:
        issues.append("Missing ending scene (no scene without outgoing choices/gotos, and no scene named 'ending').")

    # 2. Check choice and goto targets against defined scenes
    missing_targets = set()
    for scene_id, scene_data in scenes.items():
        for choice in scene_data["choices"]:
            target = choice["target"]
            if target not in defined_scene_ids:
                missing_targets.add(target)
                issues.append(f"Scene '{scene_id}' has choice '{choice['label']}' pointing to missing scene '{target}'.")
        for target in scene_data["gotos"]:
            if target not in defined_scene_ids:
                missing_targets.add(target)
                issues.append(f"Scene '{scene_id}' has goto pointing to missing scene '{target}'.")

    return issues


if __name__ == "__main__":
    import sys
    
    test_filepath = sys.argv[1] if len(sys.argv) > 1 else "artifacts/file_generation/ttl=63d/output/example.story2"
    with open(test_filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    parsed = parse_story2(content)
    validation_issues = validate_story2(parsed)
    
    print("--- PARSED STORY METADATA ---")
    print(f"Title: {parsed['title']}")
    print(f"Author: {parsed['author']}")
    print(f"Version: {parsed['version']}")
    print(f"Preview Title Line: {parsed['preview']['title_line']}")
    print(f"Preview Teaser Lines: {parsed['preview']['teaser_lines']}")
    print(f"Total Scenes: {len(parsed['scenes'])}")
    print("\n--- VALIDATION RESULTS ---")
    if validation_issues:
        for issue in validation_issues:
            print(f"- [ISSUE] {issue}")
    else:
        print("No validation errors found! Story is clean.")