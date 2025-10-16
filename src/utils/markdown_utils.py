
import os
import glob
import re

def extract_breaking_changes_and_guides(angular_version: str):
    """
    Given an angular version string (e.g. ^8.0.0),
    return a list of breaking changes and upgrade instructions from the knowledge base.
    """
    base_dir = os.path.dirname(__file__)
    breaking_dir = os.path.abspath(os.path.join(base_dir, '../knowledge/angular/breaking-changes'))
    guide_dir = os.path.abspath(os.path.join(base_dir, '../knowledge/angular/upgrade-guides'))
    version_num = re.sub(r'[^0-9]', '', angular_version.split('.')[0])
    breaking_changes = []
    upgrade_instructions = []
    # Find all breaking changes for this version
    for md_file in glob.glob(os.path.join(breaking_dir, '*.md')):
        if f'v{version_num}' in md_file:
            with open(md_file, 'r') as f:
                breaking_changes.append(f.read())
    # Find all upgrade guides for this version
    for md_file in glob.glob(os.path.join(guide_dir, '*.md')):
        if f'v{version_num}' in md_file:
            with open(md_file, 'r') as f:
                upgrade_instructions.append(f.read())
    return breaking_changes, upgrade_instructions
