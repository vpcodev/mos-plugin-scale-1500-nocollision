#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import subprocess

DOMAINS = [
    "devops", "security", "data", "docs", "testing", "ui", "ai", "observability",
    "data-platform", "platform-engineering", "release-management", "content", "workflow",
    "code-review", "architecture", "search", "networking", "cloud", "storage", "analytics"
]
VERBS = ["atlas", "harbor", "signal", "orbit", "vector", "cinder", "nimbus", "sprout", "rivet", "relay"]
SUFFIXES = ["copilot", "ops", "insights", "studio", "agent", "lab", "fleet", "guide", "vault"]
EDGE_CASE_GROUPS = {
    "large-manifest": 18,
    "exactly-20-skills": 10,
    "too-many-skills": 12,
    "path-stress": 20,
    "content-stress": 16,
    "git-stress": 12,
    "duplicate-names": 10,
    "layout-conflicts": 12,
}


def slugify(value):
    value = value.lower().replace(" ", "-")
    value = ''.join(ch if ch.isalnum() or ch in '-_' else '-' for ch in value)
    value = value.strip('-_')
    return value or 'plugin'


def make_description(domain, idx):
    phrases = {
        "devops": "Helps teams automate CI/CD workflows, branch health checks, and release signoff in mixed environments.",
        "security": "Scans for insecure defaults, dependency drift, and policy gaps before a change lands.",
        "data": "Models data pipelines, schema drift, and warehouse checks with repeatable operational guardrails.",
        "docs": "Builds high-signal documentation plans, release notes, and reference summaries for product teams.",
        "testing": "Carries deterministic verification patterns for unit, integration, and end-to-end release checks.",
        "ui": "Provides design-system consistency checks and interface review patterns for product workflows.",
        "ai": "Coordinates prompt-scoping, model usage guardrails, and structured reasoning across multi-step tasks.",
        "observability": "Connects runtime signals, dashboards, and alert quality checks into a single operational loop.",
        "data-platform": "Applies data governance, lineage awareness, and cost signals to shared platform work.",
        "platform-engineering": "Standardizes templates, environment health, and service lifecycle checks across teams.",
        "release-management": "Tracks rollout readiness, validation criteria, and production promotion decisions.",
        "content": "Improves editorial consistency, change review, and source-quality checks for large content sets.",
        "workflow": "Maps team rituals into repeatable execution patterns, handoff steps, and decision checkpoints.",
        "code-review": "Authenticates code-review decisions via policy checks, change-risk heuristics, and author feedback summaries.",
        "architecture": "Captures architecture decisions, dependency boundaries, and system trade-offs in a reusable format.",
        "search": "Improves triage and knowledge discovery across code, docs, and operational artifacts.",
        "networking": "Tracks routing, connectivity, and service-to-service health across evolving environments.",
        "cloud": "Speeds up cloud operations, posture checks, and environment readiness analysis for teams.",
        "storage": "Optimizes object lifecycle, cleanup, and data-access policies for shared service backing stores.",
        "analytics": "Builds measurable reporting loops around launch readiness, adoption, and user-facing quality.",
    }
    base = phrases.get(domain, "Provides structured operational guidance for a modern technology workflow.")
    return f"{base} Plugin {idx:04d} centers the workflow around a reliable, repeatable operational habit."


def write_plugin(root: Path, plugin_name: str, description: str, skill_name: str, skill_text: str, extra_files=None, manifest_override=None, name_override=None, skill_count=1, json_bytes=None):
    plugin_dir = root / 'plugins' / plugin_name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    if manifest_override is not None:
        manifest_path = manifest_override
    else:
        manifest_path = plugin_dir / 'plugin.json'
    manifest = {
        'name': name_override or plugin_name,
        'description': description,
        'version': '1.0.0',
        'type': 'plugin',
        'skills': [
            {'name': skill_name, 'path': f'skills/{skill_name}/SKILL.md'}
        ],
    }
    if skill_count > 1:
        manifest['skills'] = []
        for idx in range(1, skill_count + 1):
            name = f'{skill_name}-{idx}' if idx > 1 else skill_name
            manifest['skills'].append({'name': name, 'path': f'skills/{name}/SKILL.md'})
    if json_bytes is not None:
        payload = b'{' + (b' ' * max(0, json_bytes - 2)) + b'}'
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(payload)
        return plugin_dir
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if extra_files:
        for rel, content in extra_files.items():
            p = plugin_dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                p.write_bytes(content)
            else:
                p.write_text(content, encoding='utf-8')
    if skill_count == 1:
        skill_path = plugin_dir / 'skills' / skill_name / 'SKILL.md'
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(skill_text, encoding='utf-8')
    else:
        for idx in range(1, skill_count + 1):
            s_name = f'{skill_name}-{idx}' if idx > 1 else skill_name
            skill_path = plugin_dir / 'skills' / s_name / 'SKILL.md'
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(skill_text.replace('{PLUGIN}', plugin_name).replace('{SKILL}', s_name), encoding='utf-8')
    return plugin_dir


def normal_plugin(root: Path, idx: int, name_prefix: str):
    domain = DOMAINS[idx % len(DOMAINS)]
    plugin_name = slugify(f'{name_prefix}-{domain}-{idx:04d}')
    skill_name = slugify(f'{domain}-playbook-{idx % 13 + 1}')
    description = make_description(domain, idx)
    skill_text = f"""---
name: {skill_name}
description: {description}
---

# {skill_name}

Use this plugin for {domain} workflows and operational review loops.

## Goals
- Validate the release checklist for {plugin_name}.
- Capture the current state and summarize the most important actions.
- Keep the workflow repeatable and evidence-based.

## Steps
1. Review the plugin context.
2. Identify the likely risk area.
3. Recommend a safe next action with clear evidence.
4. Record the result for downstream review or handoff.
"""
    write_plugin(root, plugin_name, description, skill_name, skill_text)


def add_edge_group(root: Path, group_name: str, count: int):
    for i in range(1, count + 1):
        base = f'edge-{group_name}-{i:03d}'
        plugin_name = slugify(base)
        description = f"{group_name.replace('-', ' ').title()} stress plugin for repository scanning. This is intentionally noisy to expose boundary behavior in GraphQL and manifest readers."
        skill_name = f'{group_name}-check'
        if group_name == 'large-manifest':
            write_plugin(root, plugin_name, description, skill_name, f'# Large payload {i}\n\nThis skill exercises bounded manifest and blob reads.\n')
            plugin_dir = root / 'plugins' / plugin_name
            manifest_path = plugin_dir / 'plugin.json'
            target_size = [240 * 1024, 520 * 1024, 1100 * 1024][(i - 1) % 3]
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['benchmarkPadding'] = ''
            encoded_manifest = json.dumps(manifest, ensure_ascii=False, indent=2)
            padding_length = target_size - len(encoded_manifest.encode('utf-8')) - 1
            manifest['benchmarkPadding'] = 'A' * max(0, padding_length)
            manifest_path.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
            skill_sizes = [240 * 1024, 520 * 1024, 1100 * 1024]
            skill_path = plugin_dir / 'skills' / skill_name / 'SKILL.md'
            skill_path.write_text(
                f'---\nname: {skill_name}\ndescription: large content test\n---\n\n# Large skill {i}\n\n'
                + ('A' * skill_sizes[(i - 1) % 3])
                + '\n',
                encoding='utf-8',
            )
        elif group_name == 'exactly-20-skills':
            skill_text = f"---\nname: {skill_name}\ndescription: exactly twenty declared skills\n---\n\n# {skill_name}\n\nThis plugin declares exactly twenty skills to test the accepted boundary.\n"
            write_plugin(root, plugin_name, description, skill_name, skill_text, skill_count=20)
        elif group_name == 'too-many-skills':
            skill_count = 21
            skill_text = "---\nname: skill\ndescription: content\n---\n\n# skill\n\nFocus on the review and artifact handoff.\n"
            write_plugin(root, plugin_name, description, skill_name, skill_text, skill_count=skill_count)
        elif group_name == 'path-stress':
            path_parts = ['very', 'deep', 'nested', 'emoji-🚀', 'space name', 'hash#tag', 'at@name', 'a' * (240 if i == 1 else 50)]
            deep_dir = Path('skills').joinpath(*path_parts)
            skill_path = (deep_dir / 'SKILL.md').as_posix()
            skill_text = f"---\nname: {skill_name}\ndescription: verifies path escaping and deep nesting\n---\n\n# Path stress\n\nThis plugin exercises a deeply nested Unicode and punctuation path.\n"
            write_plugin(root, plugin_name, description, skill_name, skill_text)
            plugin_dir = root / 'plugins' / plugin_name
            manifest_path = plugin_dir / 'plugin.json'
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['skills'][0]['path'] = skill_path
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            old_skill = plugin_dir / 'skills' / skill_name / 'SKILL.md'
            new_skill = plugin_dir / skill_path
            new_skill.parent.mkdir(parents=True, exist_ok=True)
            old_skill.replace(new_skill)
            if i == 1:
                new_skill.unlink()
                parent = new_skill.parent
                while parent != plugin_dir:
                    try:
                        parent.rmdir()
                    except OSError:
                        break
                    parent = parent.parent
        elif group_name == 'content-stress':
            if i % 6 == 0:
                write_plugin(root, plugin_name, description, skill_name, f'# Empty content case\n')
                empty_content = root / 'plugins' / plugin_name / 'content' / 'empty.md'
                empty_content.parent.mkdir(parents=True, exist_ok=True)
                empty_content.write_bytes(b'')
            elif i % 6 == 1:
                manifest_dir = root / 'plugins' / plugin_name
                manifest_dir.mkdir(parents=True, exist_ok=True)
                bad = '{"name": "dup", "version": "1.0.0", "description": "duplicate key", "description": "second duplicate" }'
                (manifest_dir / 'plugin.json').write_text(bad, encoding='utf-8')
                sx = manifest_dir / 'skills' / skill_name / 'SKILL.md'
                sx.parent.mkdir(parents=True, exist_ok=True)
                sx.write_text('---\nname: content-stress\ndescription: duplicate JSON key test\n---\n\n# content stress\n\nThis plugin intentionally uses malformed content.\n', encoding='utf-8')
                (manifest_dir / 'content').mkdir(parents=True, exist_ok=True)
                (manifest_dir / 'content' / 'note.bin').write_bytes(b'\x00\x01\x02\x03\xFF\xFE\xFD')
            elif i % 6 == 2:
                manifest_dir = root / 'plugins' / plugin_name
                manifest_dir.mkdir(parents=True, exist_ok=True)
                payload_utf8 = json.dumps({'name': plugin_name, 'description': description, 'version': '1.0.0', 'skills': [{'name': skill_name, 'path': f'skills/{skill_name}/SKILL.md'}]}, ensure_ascii=False)
                (manifest_dir / 'plugin.json').write_bytes(b'\xef\xbb\xbf' + payload_utf8.encode('utf-8'))
                f = manifest_dir / 'skills' / skill_name / 'SKILL.md'
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(b'---\r\nname: bom\r\ndescription: CRLF file\r\n---\r\n\r\n# bom\r\n\r\nThis file uses CRLF line endings.\r\n')
            elif i % 6 == 3:
                manifest_dir = root / 'plugins' / plugin_name
                manifest_dir.mkdir(parents=True, exist_ok=True)
                (manifest_dir / 'plugin.json').write_bytes(b'{"name":"invalid-\xff"}')
                f = manifest_dir / 'skills' / skill_name / 'SKILL.md'
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(f'---\nname: {skill_name}\ndescription: non-UTF-8 manifest test\n---\n\n# {skill_name}\n\nThe manifest contains an invalid UTF-8 byte.\n', encoding='utf-8')
            elif i % 6 == 4:
                write_plugin(root, plugin_name, description, skill_name, f'---\nname: {skill_name}\ndescription: invalid JSON test\n---\n\n# {skill_name}\n\nThe plugin manifest is intentionally malformed JSON.\n')
                (root / 'plugins' / plugin_name / 'plugin.json').write_text('{"name": "broken", "skills": [}', encoding='utf-8')
            else:
                manifest_dir = root / 'plugins' / plugin_name
                manifest_dir.mkdir(parents=True, exist_ok=True)
                manifest = {'name': plugin_name, 'description': description, 'version': '1.0.0', 'skills': [{'name': skill_name, 'path': f'skills/{skill_name}/SKILL.md'}]}
                (manifest_dir / 'plugin.json').write_text(json.dumps(manifest), encoding='utf-8')
                (manifest_dir / 'skills' / skill_name / 'SKILL.md').parent.mkdir(parents=True, exist_ok=True)
                (manifest_dir / 'skills' / skill_name / 'SKILL.md').write_text('---\nname: empty\ndescription: empty content\n---\n\n# empty\n', encoding='utf-8')
                (manifest_dir / 'skills' / skill_name / 'empty.md').write_text('', encoding='utf-8')
        elif group_name == 'git-stress':
            plugin_dir = root / 'plugins' / plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            (plugin_dir / 'plugin.json').write_text(json.dumps({'name': plugin_name, 'description': description, 'version': '1.0.0', 'skills': [{'name': 'git-stress', 'path': 'skills/git-stress/SKILL.md'}]}, ensure_ascii=False, indent=2) + '\n')
            skill_dir = plugin_dir / 'skills' / 'git-stress'
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / 'SKILL.md').write_text('---\nname: git-stress\ndescription: tests git object edge cases\n---\n\n# git-stress\n\nThis plugin is intentionally noisy for Git object and symlink handling.\n', encoding='utf-8')
            if i % 3 == 0:
                src = plugin_dir / 'docs' / 'source.md'
                src.parent.mkdir(parents=True, exist_ok=True)
                src.write_text('# docs\n\nThis is a symlink target.\n', encoding='utf-8')
                link = plugin_dir / 'docs-link'
                if not link.is_symlink():
                    os.symlink('docs/source.md', link)
            if i % 3 == 1:
                nested_gitmodules = plugin_dir / '.gitmodules'
                if nested_gitmodules.exists():
                    nested_gitmodules.unlink()
                (root / '.gitmodules').write_text(
                    '[submodule "vendor/module"]\n'
                    '\tpath = plugins/edge-git-stress-001/vendor/module\n'
                    '\turl = https://github.com/vpcodev/mos-plugin-scale-1500.git\n',
                    encoding='utf-8',
                )
            if i % 3 == 2:
                (plugin_dir / 'lfs-pointer.txt').write_text('version https://git-lfs.github.com/spec/v1\noid sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef\nsize 1048576\n', encoding='utf-8')
        elif group_name == 'duplicate-names':
            write_plugin(root, plugin_name, description, skill_name, f'---\nname: {skill_name}\ndescription: duplicate name for comparison\n---\n\n# duplicate\n\nThis plugin carries the same display name as a sibling.\n', name_override='shared-duplicate-plugin-name')
        elif group_name == 'layout-conflicts':
            plugin_dir = root / 'plugins' / plugin_name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            alt_dir = plugin_dir / '.github' / 'plugin'
            alt_dir.mkdir(parents=True, exist_ok=True)
            alt_manifest = {'name': f'{plugin_name}-alt', 'description': description, 'version': '1.0.0', 'skills': [{'name': f'{skill_name}-alt', 'path': 'skills/alt/SKILL.md'}]}
            (plugin_dir / 'plugin.json').write_text(json.dumps({'name': f'{plugin_name}-root', 'description': description, 'version': '1.0.0', 'skills': [{'name': skill_name, 'path': 'skills/root/SKILL.md'}]}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            (alt_dir / 'plugin.json').write_text(json.dumps(alt_manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            root_skill = plugin_dir / 'skills' / skill_name
            root_skill.mkdir(parents=True, exist_ok=True)
            (root_skill / 'SKILL.md').write_text('---\nname: root-skill\ndescription: root layout\n---\n\n# root\n\nThis plugin intentionally has a root manifest and alternative manifest.\n', encoding='utf-8')
            alt_skill = plugin_dir / '.github' / 'skills' / 'alt'
            alt_skill.mkdir(parents=True, exist_ok=True)
            (alt_skill / 'SKILL.md').write_text('---\nname: alt-skill\ndescription: alternative layout\n---\n\n# alt\n\nThis conflicts with the root plugin manifest.\n', encoding='utf-8')


def build_main(root: Path):
    # normal valid plugins
    for idx in range(1, 1451):
        normal_plugin(root, idx, 'plugin')
    # edge-case minority
    for group, count in EDGE_CASE_GROUPS.items():
        add_edge_group(root, group, count)


def build_over_limits(root: Path):
    for idx in range(1, 1501):
        normal_plugin(root, idx + 5000, 'overflow')
    extra = root / 'plugins' / 'over-limit-giant'
    extra.mkdir(parents=True, exist_ok=True)
    (extra / 'plugin.json').write_text('{"name": "over-limit-giant", "description": "branch that exceeds repo limits", "version": "1.0.0", "skills": [{"name": "overflow-skill", "path": "skills/overflow-skill/SKILL.md"}]}\n', encoding='utf-8')
    skill_dir = extra / 'skills' / 'overflow-skill'
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / 'SKILL.md').write_text('---\nname: overflow-skill\ndescription: large branch for failure tests\n---\n\n# overflow\n\nThis branch intentionally exceeds the repo size cap.\n', encoding='utf-8')
    for i in range(1, 500):
        placeholder = extra / 'bulk' / f'file-{i:04d}.md'
        placeholder.parent.mkdir(parents=True, exist_ok=True)
        placeholder.write_text('# ' + ('x' * 2000) + '\n', encoding='utf-8')


def write_git_object(root: Path, content: bytes) -> str:
    result = subprocess.run(
        ['git', 'hash-object', '-w', '--stdin'],
        cwd=root,
        input=content,
        capture_output=True,
        check=True,
    )
    return result.stdout.decode('ascii').strip()


def add_index_entry(root: Path, mode: str, sha: str, path: str):
    record = f'{mode} {sha}\t{path}\0'.encode('utf-8')
    subprocess.run(
        ['git', '-c', 'core.protectNTFS=false', '-c', 'core.ignorecase=false', 'update-index', '-z', '--index-info'],
        cwd=root,
        input=record,
        check=True,
    )


def add_over_limit_tree_entries(root: Path):
    long_directory = '/'.join(['p' * 250] * 10)
    blob_sha = write_git_object(root, b'# Long path tree-size fixture.\n')
    records = bytearray()
    for i in range(1, 3001):
        path = f'plugins/over-limit-giant/tree-metadata/{long_directory}/file-{i:04d}.md'
        if len(path.encode('utf-8')) > 4096:
            raise ValueError("The over-limit tree path exceeds GitHub's path-length limit.")
        records.extend(f'100644 {blob_sha}\t{path}\0'.encode('utf-8'))

    subprocess.run(
        ['git', '-c', 'core.protectNTFS=false', '-c', 'core.ignorecase=false', 'update-index', '-z', '--index-info'],
        cwd=root,
        input=bytes(records),
        check=True,
    )


def add_git_object_edge_cases(root: Path):
    repository = root
    submodule_commit = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subprocess.run(
        ['git', 'update-index', '--force-remove', 'plugins/edge-git-stress-002/vendor/module'],
        cwd=root,
        check=True,
    )
    add_index_entry(root, '160000', submodule_commit, 'plugins/edge-git-stress-001/vendor/module')

    crlf_path = 'plugins/edge-content-stress-002/skills/content-stress-check/SKILL.md'
    crlf_skill = (
        b'---\r\nname: bom\r\ndescription: CRLF file\r\n---\r\n\r\n'
        b'# bom\r\n\r\nThis file uses CRLF line endings.\r\n'
    )
    add_index_entry(root, '100644', write_git_object(root, crlf_skill), crlf_path)

    long_path = (
        'plugins/edge-path-stress-001/skills/very/deep/nested/emoji-🚀/space name/hash#tag/at@name/'
        + ('a' * 240)
        + '/SKILL.md'
    )
    long_skill = (
        '---\nname: path-stress-check\ndescription: verifies path escaping and deep nesting\n---\n\n'
        '# Path stress\n\nThis plugin exercises a deeply nested Unicode and punctuation path.\n'
    ).encode('utf-8')
    add_index_entry(root, '100644', write_git_object(root, long_skill), long_path)

    plugin_path = 'plugins/edge-graphql-expression/quote"backslash\\colon:hash#at@'
    skill_name = 'quote"backslash\\colon:hash#at@'
    manifest = json.dumps({
        'name': 'graphql-expression-path',
        'description': 'GraphQL expression path escaping test.',
        'version': '1.0.0',
        'skills': [{'name': skill_name, 'path': f'skills/{skill_name}/SKILL.md'}],
    }, ensure_ascii=False, indent=2).encode('utf-8') + b'\n'
    skill = (
        f'---\nname: graphql-expression-path\ndescription: path escaping test\n---\n\n'
        '# GraphQL path escaping\n\nThis file path contains a quote, backslash, colon, hash, and at-sign.\n'
    ).encode('utf-8')
    add_index_entry(root, '100644', write_git_object(root, manifest), f'{plugin_path}/plugin.json')
    add_index_entry(root, '100644', write_git_object(root, skill), f'{plugin_path}/skills/{skill_name}/SKILL.md')

    if (root / 'plugins' / 'over-limit-giant' / 'plugin.json').exists():
        add_over_limit_tree_entries(root)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['main', 'over-limits', 'index-edges'], default='main')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.mode == 'main':
        build_main(root)
    elif args.mode == 'over-limits':
        build_over_limits(root)
    add_git_object_edge_cases(root)

if __name__ == '__main__':
    main()
