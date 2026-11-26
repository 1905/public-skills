#!/usr/bin/env python3
"""Install public-skills by symlinking skill dirs into every agent skills folder found.

Dry run by default. Pass --apply to make changes.

Targets it detects:
  - Claude Code:       $CLAUDE_CONFIG_DIR/skills, else ~/.claude/skills
  - T3 Code (Claude):  <config dir>/skills for every enabled Claude provider instance
                       with its own config dir (settings: homePath or CLAUDE_CONFIG_DIR)
  - Codex / OpenCode / other Agent Skills hosts: ~/.agents/skills
  - Antigravity:       ~/.gemini/config/skills (only if ~/.gemini exists)

It never replaces a real directory or a symlink that points somewhere else.
It reads only paths from T3 settings; it never prints other settings values.
"""
import argparse
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
SKILLS_DIR = REPO / "skills"
HOME = Path.home()
T3_SETTINGS = HOME / ".t3" / "userdata" / "settings.json"


def all_skills():
    return sorted(p.name for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file())


def t3_claude_config_dirs():
    """Config dirs of enabled T3 Code Claude provider instances (only custom ones)."""
    if not T3_SETTINGS.is_file():
        return []
    try:
        data = json.loads(T3_SETTINGS.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠ could not read {T3_SETTINGS}: {e}", file=sys.stderr)
        return []
    dirs = []
    for inst_id, inst in (data.get("providerInstances") or {}).items():
        if inst.get("driver") != "claudeAgent" or inst.get("enabled") is False:
            continue
        path = (inst.get("config") or {}).get("homePath")
        env = inst.get("environment") or []
        if isinstance(env, list):
            for var in env:
                if isinstance(var, dict) and var.get("name") == "CLAUDE_CONFIG_DIR" and var.get("value"):
                    path = var["value"]
        if path:
            dirs.append((f"T3 Code Claude instance '{inst_id}'", Path(os.path.expanduser(path))))
    return dirs


def find_targets():
    """Return (label, config_dir_or_None, skills_dir)."""
    targets = []
    claude_dir = HOME / ".claude"
    targets.append(("Claude Code (~/.claude)", claude_dir, claude_dir / "skills"))
    env_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    if env_dir:
        cfg = Path(env_dir).expanduser()
        targets.append(("Claude Code ($CLAUDE_CONFIG_DIR)", cfg, cfg / "skills"))
    for label, cfg in t3_claude_config_dirs():
        targets.append((label, cfg, cfg / "skills"))
    if any((HOME / d).exists() for d in (".agents", ".codex", ".config/opencode")):
        targets.append(("Codex / OpenCode / Agent Skills hosts", None, HOME / ".agents" / "skills"))
    if (HOME / ".gemini").exists():
        targets.append(("Antigravity", None, HOME / ".gemini" / "config" / "skills"))
    # Several config dirs can share one skills dir (symlinked). Merge them, keep every label.
    merged = {}
    for label, cfg, sk in targets:
        key = sk.resolve() if sk.exists() else sk.absolute()
        if key in merged:
            merged[key][0].append(label)
            merged[key][1].append(cfg)
        else:
            merged[key] = ([label], [cfg], sk)
    return [(" + ".join(labels), cfgs, sk) for labels, cfgs, sk in merged.values()]


def has_official_frontend_design(cfgs):
    """True only if every config dir that loads this skills dir has the official plugin."""
    cfgs = [c for c in cfgs if c is not None]
    if not cfgs:
        return False
    return all((c / "plugins" / "cache").is_dir() and any((c / "plugins" / "cache").glob("*/frontend-design"))
               for c in cfgs)


def plan_links(skills_dir, cfgs, skills):
    actions = []
    for name in skills:
        src = SKILLS_DIR / name
        dst = skills_dir / name
        if name == "frontend-design" and has_official_frontend_design(cfgs):
            actions.append(("skip", dst, "official frontend-design plugin already installed"))
        elif dst.is_symlink():
            if dst.resolve() == src.resolve():
                actions.append(("ok", dst, "already linked"))
            else:
                actions.append(("conflict", dst, f"symlink to {os.readlink(dst)}"))
        elif dst.exists():
            actions.append(("conflict", dst, "real directory or file exists"))
        else:
            actions.append(("link", dst, f"-> {src}"))
    return actions


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="make the changes (default: dry run)")
    ap.add_argument("--skills", nargs="+", help="install only these skills")
    ap.add_argument("--target", action="append", type=Path,
                    help="extra skills dir to install into (repeatable)")
    args = ap.parse_args()

    skills = args.skills or all_skills()
    unknown = set(skills) - set(all_skills())
    if unknown:
        sys.exit(f"unknown skills: {', '.join(sorted(unknown))}")

    targets = find_targets() + [("--target", [None], t.expanduser()) for t in (args.target or [])]
    mode = "APPLY" if args.apply else "DRY RUN (pass --apply to install)"
    print(f"{mode}\nrepo: {REPO}\nskills: {', '.join(skills)}\n")

    conflicts = 0
    instruction_files = []
    for label, cfgs, skills_dir in targets:
        print(f"== {label}: {skills_dir}")
        for action, dst, note in plan_links(skills_dir, cfgs, skills):
            mark = {"link": "+", "ok": "✓", "skip": "•", "conflict": "✗"}[action]
            print(f"  {mark} {dst.name:16} {note}")
            if action == "conflict":
                conflicts += 1
            if action == "link" and args.apply:
                skills_dir.mkdir(parents=True, exist_ok=True)
                dst.symlink_to(SKILLS_DIR / dst.name, target_is_directory=True)
        instruction_files += [c / "CLAUDE.md" for c in cfgs if c is not None]
    if any("Codex" in t[0] for t in targets):
        instruction_files.append(HOME / ".codex" / "AGENTS.md")

    print("\nInstruction files for the rules in CLAUDE.snippet.md (ask the user before editing):")
    seen = set()
    for f in instruction_files:
        key = f.resolve()
        if key in seen:
            continue
        seen.add(key)
        print(f"  {f}{'' if f.exists() else '  (does not exist yet)'}")
    if conflicts:
        print(f"\n⚠ {conflicts} conflict(s) left untouched. Ask the user: move the existing item, or skip it.")
    print("\nRestart agent sessions so they load the new skills.")
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
