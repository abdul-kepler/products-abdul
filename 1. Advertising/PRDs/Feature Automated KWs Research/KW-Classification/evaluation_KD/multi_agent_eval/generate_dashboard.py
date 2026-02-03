#!/usr/bin/env python3
"""
Multi-Agent Evaluation Dashboard Generator

Generates an HTML dashboard from multi-agent evaluation results.

Usage:
    python generate_dashboard.py <results_json> [options]

Options:
    -o, --output FILE       Output HTML file (default: dashboards/<input>_dashboard.html)
    -c, --config FILE       Config YAML file for module-specific settings
    -m, --module MODULE     Module ID override (default: from data or 'M11')
    -t, --title TITLE       Dashboard title override
    --open                  Open dashboard in browser after generation

Examples:
    python generate_dashboard.py results/m11_multiagent_aggregated_latest.json
    python generate_dashboard.py results/m11_results.json -o dashboards/my_report.html --open
    python generate_dashboard.py results/m12_results.json -c config/m12_dashboard.yaml
"""

import json
import html as html_escape
import sys
import os
import argparse
from datetime import datetime

# Try to import yaml, but make it optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ============================================================================
# DEFAULT CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    # Module info
    "module_id": "M11",
    "module_name": "Hard Constraints Identification",
    "title": "Multi-Agent Evaluation Dashboard",
    "subtitle": "Adversarial Debate Evaluation System",

    # Critic categories with colors
    "critic_categories": {
        "FALSE_POSITIVE": {
            "color": "#cf222e",
            "bg": "rgba(207, 34, 46, 0.12)",
            "description": "Marked as constraint incorrectly"
        },
        "FALSE_NEGATIVE": {
            "color": "#bc4c00",
            "bg": "rgba(188, 76, 0, 0.12)",
            "description": "Missed genuine constraint"
        },
        "REASONING_ERROR": {
            "color": "#9a6700",
            "bg": "rgba(154, 103, 0, 0.12)",
            "description": "Flawed logic in analysis"
        },
        "CATEGORY_CONFUSION": {
            "color": "#8250df",
            "bg": "rgba(130, 80, 223, 0.12)",
            "description": "Mixed up MECHANISM/QUALITY"
        },
        "DISTRIBUTION_VIOLATION": {
            "color": "#0891b2",
            "bg": "rgba(8, 145, 178, 0.12)",
            "description": "Wrong constraint count"
        }
    },

    # Rubric dimensions
    "rubric_dimensions": [
        "accuracy",
        "relevance",
        "completeness",
        "clarity",
        "reasoning"
    ],

    # Severity levels (1-5)
    "severity_colors": {
        1: {"color": "#656d76", "bg": "rgba(101, 109, 118, 0.12)", "label": "Minor"},
        2: {"color": "#0969da", "bg": "rgba(9, 105, 218, 0.12)", "label": "Low"},
        3: {"color": "#9a6700", "bg": "rgba(154, 103, 0, 0.12)", "label": "Moderate"},
        4: {"color": "#bc4c00", "bg": "rgba(188, 76, 0, 0.12)", "label": "Major"},
        5: {"color": "#cf222e", "bg": "rgba(207, 34, 46, 0.12)", "label": "Critical"}
    },

    # Verdict colors
    "verdict_colors": {
        "valid": {"color": "#cf222e", "bg": "rgba(207, 34, 46, 0.12)"},
        "partially_valid": {"color": "#9a6700", "bg": "rgba(154, 103, 0, 0.12)"},
        "invalid": {"color": "#1a7f37", "bg": "rgba(26, 127, 55, 0.12)"}
    },

    # Agent prompts (paths relative to script)
    "prompts": {
        "critic": "prompts/critic_m11.md",
        "defender": "prompts/defender.md",
        "judge": "prompts/judge.md",
        "meta_judge": "prompts/meta_judge.md"
    },

    # Score thresholds
    "score_thresholds": {
        "high": 4.0,
        "medium": 3.0
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def escape_html(text):
    """Escape HTML special characters."""
    if text is None:
        return ''
    return html_escape.escape(str(text))


def format_json(obj, max_len=500):
    """Format JSON object as string, truncated if needed."""
    text = json.dumps(obj, indent=2)
    if len(text) > max_len:
        return text[:max_len] + '...'
    return text


def load_config(config_file):
    """Load configuration from YAML or JSON file."""
    if config_file is None:
        return DEFAULT_CONFIG.copy()

    if not os.path.exists(config_file):
        print(f"Warning: Config file not found: {config_file}, using defaults")
        return DEFAULT_CONFIG.copy()

    with open(config_file, 'r') as f:
        if config_file.endswith('.yaml') or config_file.endswith('.yml'):
            if not YAML_AVAILABLE:
                print("Warning: PyYAML not installed, cannot read YAML config")
                return DEFAULT_CONFIG.copy()
            user_config = yaml.safe_load(f)
        else:
            user_config = json.load(f)

    # Merge with defaults
    config = DEFAULT_CONFIG.copy()
    if user_config:
        for key, value in user_config.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                config[key].update(value)
            else:
                config[key] = value

    return config


def detect_categories(data):
    """Auto-detect categories from the results data."""
    categories = set()
    for result in data.get('results', []):
        debate = result.get('result', {}).get('debate', {})
        for w in debate.get('weaknesses', []):
            cat = w.get('category', '')
            if cat:
                categories.add(cat)
    return list(categories)


def count_categories(data, config):
    """Count occurrences of each category."""
    # Initialize with configured categories
    counts = {cat: 0 for cat in config.get('critic_categories', {}).keys()}

    for result in data.get('results', []):
        debate = result.get('result', {}).get('debate', {})
        for w in debate.get('weaknesses', []):
            cat = w.get('category', '')
            if cat:
                counts[cat] = counts.get(cat, 0) + 1

    return counts


# ============================================================================
# HTML GENERATION
# ============================================================================

def generate_css(config):
    """Generate CSS with configurable colors."""
    category_css = ""
    for cat_name, cat_config in config.get('critic_categories', {}).items():
        category_css += f'''
        .category-badge.{cat_name} {{ background: {cat_config['bg']}; color: {cat_config['color']}; }}'''

    severity_css = ""
    for sev, sev_config in config.get('severity_colors', {}).items():
        severity_css += f'''
        .severity-badge.sev-{sev} {{ background: {sev_config['bg']}; color: {sev_config['color']}; }}'''

    verdict_css = ""
    for verdict, verdict_config in config.get('verdict_colors', {}).items():
        verdict_css += f'''
        .verdict-badge.{verdict} {{ background: {verdict_config['bg']}; color: {verdict_config['color']}; }}'''

    return f'''
        :root {{
            --bg-primary: #ffffff; --bg-secondary: #f6f8fa; --bg-tertiary: #eef1f5;
            --text-primary: #1f2328; --text-secondary: #656d76; --border-color: #d0d7de;
            --accent-blue: #0969da; --accent-green: #1a7f37; --accent-red: #cf222e;
            --accent-yellow: #9a6700; --accent-purple: #8250df; --accent-orange: #bc4c00; --accent-cyan: #0891b2;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; background: var(--bg-primary); color: var(--text-primary); line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
        header {{ text-align: center; margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border-color); }}
        header h1 {{ font-size: 2rem; margin-bottom: 8px; background: linear-gradient(135deg, #0969da, #8250df); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .subtitle {{ color: var(--text-secondary); font-size: 1.1rem; }}
        .tab-nav {{ display: flex; gap: 4px; margin-bottom: 24px; border-bottom: 2px solid var(--border-color); }}
        .tab-btn {{ padding: 12px 24px; background: none; border: none; cursor: pointer; font-size: 1rem; font-weight: 500; color: var(--text-secondary); border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; }}
        .tab-btn:hover {{ color: var(--text-primary); background: var(--bg-secondary); }}
        .tab-btn.active {{ color: var(--accent-blue); border-bottom-color: var(--accent-blue); }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 32px; }}
        .stat-card {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; text-align: center; }}
        .stat-value {{ font-size: 2rem; font-weight: 700; margin-bottom: 4px; }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.85rem; }}
        .results-list {{ display: flex; flex-direction: column; gap: 24px; }}
        .result-card {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; }}
        .result-header {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: var(--bg-tertiary); border-bottom: 1px solid var(--border-color); }}
        .result-title {{ display: flex; align-items: center; gap: 12px; }}
        .result-id {{ font-weight: 600; font-size: 1.1rem; }}
        .score-badge {{ display: flex; align-items: center; justify-content: center; width: 56px; height: 56px; border-radius: 50%; font-size: 1.3rem; font-weight: 700; }}
        .score-badge.high {{ background: rgba(26, 127, 55, 0.12); color: var(--accent-green); border: 2px solid var(--accent-green); }}
        .score-badge.medium {{ background: rgba(154, 103, 0, 0.12); color: var(--accent-yellow); border: 2px solid var(--accent-yellow); }}
        .score-badge.low {{ background: rgba(207, 34, 46, 0.12); color: var(--accent-red); border: 2px solid var(--accent-red); }}
        .result-body {{ padding: 20px; }}
        .pipeline-steps {{ display: flex; flex-direction: column; gap: 16px; }}
        .pipeline-step {{ background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 12px; overflow: hidden; }}
        .step-header {{ display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--bg-tertiary); cursor: pointer; user-select: none; }}
        .step-header:hover {{ background: var(--border-color); }}
        .step-icon {{ width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; color: white; }}
        .step-icon.critic {{ background: linear-gradient(135deg, #cf222e, #f85149); }}
        .step-icon.defender {{ background: linear-gradient(135deg, #1a7f37, #3fb950); }}
        .step-icon.judge {{ background: linear-gradient(135deg, #0969da, #54aeff); }}
        .step-icon.meta {{ background: linear-gradient(135deg, #8250df, #a371f7); }}
        .step-title {{ flex: 1; font-weight: 600; }}
        .step-summary {{ color: var(--text-secondary); font-size: 0.9rem; }}
        .step-toggle {{ color: var(--text-secondary); transition: transform 0.2s; }}
        .pipeline-step.open .step-toggle {{ transform: rotate(180deg); }}
        .step-content {{ display: none; padding: 16px; border-top: 1px solid var(--border-color); }}
        .pipeline-step.open .step-content {{ display: block; }}
        .item-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .weakness-item, .strength-item {{ background: var(--bg-tertiary); border-radius: 8px; padding: 12px; }}
        .strength-item {{ background: rgba(26, 127, 55, 0.08); border-left: 3px solid var(--accent-green); }}
        .item-header {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }}
        .item-id {{ font-weight: 600; color: var(--accent-purple); }}
        .category-badge {{ padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
        {category_css}
        .severity-badge {{ padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
        {severity_css}
        .item-description {{ margin-bottom: 8px; }}
        .item-evidence {{ font-size: 0.9rem; color: var(--text-secondary); font-style: italic; padding-left: 12px; border-left: 2px solid var(--border-color); margin-top: 8px; }}
        .verdict-badge {{ padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }}
        {verdict_css}
        .scores-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin-top: 16px; }}
        .score-item {{ text-align: center; padding: 12px; background: var(--bg-tertiary); border-radius: 8px; }}
        .score-item-value {{ font-size: 1.5rem; font-weight: 700; }}
        .score-item-label {{ font-size: 0.75rem; color: var(--text-secondary); text-transform: capitalize; }}
        .summary-box {{ background: var(--bg-tertiary); border-radius: 8px; padding: 16px; margin-top: 16px; }}
        .summary-title {{ font-weight: 600; margin-bottom: 8px; }}
        .chain-of-thought {{ background: var(--bg-tertiary); border-radius: 8px; padding: 12px; margin-bottom: 12px; font-style: italic; color: var(--text-secondary); border-left: 3px solid var(--accent-purple); }}
        .chain-of-thought-label {{ font-weight: 600; color: var(--accent-purple); margin-bottom: 4px; font-style: normal; }}
        .section-title {{ font-weight: 600; margin: 16px 0 8px 0; color: var(--accent-blue); }}
        .confidence-badge {{ padding: 4px 12px; border-radius: 16px; font-size: 0.85rem; font-weight: 600; }}
        .confidence-badge.HIGH {{ background: rgba(26, 127, 55, 0.12); color: var(--accent-green); }}
        .confidence-badge.MEDIUM {{ background: rgba(154, 103, 0, 0.12); color: var(--accent-yellow); }}
        .confidence-badge.LOW {{ background: rgba(207, 34, 46, 0.12); color: var(--accent-red); }}
        .charts-section {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }}
        .chart-card {{ background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; }}
        .chart-title {{ font-weight: 600; margin-bottom: 16px; }}
        .io-content {{ background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 0.75rem; max-height: 250px; overflow-y: auto; white-space: pre-wrap; word-break: break-word; }}
        .io-section {{ margin-bottom: 16px; }}
        .io-label {{ font-weight: 600; font-size: 0.85rem; margin-bottom: 8px; color: var(--accent-blue); }}
        .io-label.input-label {{ color: var(--text-secondary); }}
        .agent-input-box {{ background: rgba(9, 105, 218, 0.05); border: 1px dashed var(--accent-blue); border-radius: 8px; padding: 12px; margin-bottom: 16px; }}
        .agent-input-title {{ font-weight: 600; color: var(--accent-blue); margin-bottom: 8px; font-size: 0.9rem; }}
        .agent-output-box {{ background: rgba(26, 127, 55, 0.05); border: 1px dashed var(--accent-green); border-radius: 8px; padding: 12px; margin-top: 16px; }}
        .agent-output-title {{ font-weight: 600; color: var(--accent-green); margin-bottom: 8px; font-size: 0.9rem; }}
        .stats-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 12px 0; padding: 12px; background: var(--bg-tertiary); border-radius: 8px; }}
        .stat-mini {{ text-align: center; padding: 8px 16px; background: var(--bg-primary); border-radius: 6px; }}
        .stat-mini-value {{ font-weight: 700; font-size: 1.1rem; }}
        .stat-mini-label {{ font-size: 0.7rem; color: var(--text-secondary); }}
        .justification-item {{ padding: 10px; background: var(--bg-tertiary); border-radius: 6px; margin-bottom: 8px; border-left: 3px solid var(--accent-blue); }}
        .justification-label {{ font-weight: 600; font-size: 0.85rem; color: var(--accent-blue); }}
        .justification-text {{ font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px; }}
        .assessment-box {{ background: var(--bg-tertiary); border-radius: 8px; padding: 12px; margin: 12px 0; border-left: 3px solid var(--accent-orange); }}
        .flow-container {{ padding: 20px; }}
        .flow-diagram {{ display: flex; flex-direction: column; max-width: 900px; margin: 0 auto; }}
        .flow-step {{ display: flex; align-items: stretch; gap: 20px; }}
        .flow-connector {{ width: 60px; display: flex; flex-direction: column; align-items: center; }}
        .flow-dot {{ width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; z-index: 1; }}
        .flow-dot.critic {{ background: var(--accent-red); box-shadow: 0 0 0 2px var(--accent-red); }}
        .flow-dot.defender {{ background: var(--accent-green); box-shadow: 0 0 0 2px var(--accent-green); }}
        .flow-dot.judge {{ background: var(--accent-blue); box-shadow: 0 0 0 2px var(--accent-blue); }}
        .flow-dot.meta {{ background: var(--accent-purple); box-shadow: 0 0 0 2px var(--accent-purple); }}
        .flow-dot.input {{ background: var(--text-secondary); box-shadow: 0 0 0 2px var(--text-secondary); }}
        .flow-line {{ flex: 1; width: 3px; background: var(--border-color); }}
        .flow-card {{ flex: 1; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 12px; padding: 20px; margin: 10px 0; }}
        .flow-card.critic {{ border-left: 4px solid var(--accent-red); }}
        .flow-card.defender {{ border-left: 4px solid var(--accent-green); }}
        .flow-card.judge {{ border-left: 4px solid var(--accent-blue); }}
        .flow-card.meta {{ border-left: 4px solid var(--accent-purple); }}
        .flow-card.input {{ border-left: 4px solid var(--text-secondary); }}
        .flow-card-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }}
        .flow-card-icon {{ width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: 700; color: white; }}
        .flow-card-icon.critic {{ background: linear-gradient(135deg, #cf222e, #f85149); }}
        .flow-card-icon.defender {{ background: linear-gradient(135deg, #1a7f37, #3fb950); }}
        .flow-card-icon.judge {{ background: linear-gradient(135deg, #0969da, #54aeff); }}
        .flow-card-icon.meta {{ background: linear-gradient(135deg, #8250df, #a371f7); }}
        .flow-card-icon.input {{ background: linear-gradient(135deg, #6e7781, #8b949e); }}
        .flow-card-title {{ font-size: 1.2rem; font-weight: 600; }}
        .flow-card-subtitle {{ font-size: 0.85rem; color: var(--text-secondary); }}
        .flow-section {{ margin-bottom: 16px; }}
        .flow-section-title {{ font-weight: 600; font-size: 0.9rem; margin-bottom: 8px; }}
        .flow-section-title.input {{ color: var(--accent-blue); }}
        .flow-section-title.output {{ color: var(--accent-green); }}
        .flow-list {{ background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 8px; padding: 12px; }}
        .flow-list-item {{ display: flex; align-items: flex-start; gap: 8px; padding: 6px 0; border-bottom: 1px solid var(--bg-tertiary); }}
        .flow-list-item:last-child {{ border-bottom: none; }}
        .flow-list-bullet {{ width: 6px; height: 6px; border-radius: 50%; background: var(--accent-blue); margin-top: 6px; flex-shrink: 0; }}
        .category-legend {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0; padding: 16px; background: var(--bg-secondary); border-radius: 8px; }}
        .category-legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.85rem; }}
        @media (max-width: 1200px) {{ .stats-grid {{ grid-template-columns: repeat(3, 1fr); }} }}
        @media (max-width: 768px) {{ .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} .charts-section {{ grid-template-columns: 1fr; }} }}
'''


def generate_dashboard(results_file, output_file=None, config=None, title_override=None, module_override=None):
    """Generate HTML dashboard from results JSON file."""

    # Load config
    if config is None:
        config = DEFAULT_CONFIG.copy()

    # Read results
    with open(results_file, 'r') as f:
        data = json.load(f)

    # Override module ID if specified
    module_id = module_override or data.get('module_id') or config.get('module_id', 'M11')
    config['module_id'] = module_id

    # Override title if specified
    if title_override:
        config['title'] = title_override

    # Auto-detect categories if not in config
    detected_cats = detect_categories(data)
    for cat in detected_cats:
        if cat not in config['critic_categories']:
            # Add with default purple color
            config['critic_categories'][cat] = {
                "color": "#8250df",
                "bg": "rgba(130, 80, 223, 0.12)",
                "description": cat
            }

    # Count categories
    category_counts = count_categories(data, config)

    # Determine output file
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(results_file))[0]
        output_dir = os.path.join(os.path.dirname(results_file), '..', 'dashboards')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{base_name}_dashboard.html")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Generate HTML
    html = generate_html(data, config, category_counts)

    # Write output
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"Dashboard generated: {output_file}")
    print(f"  - Module: {module_id}")
    print(f"  - Total samples: {data['summary']['total']}")
    print(f"  - Avg overall: {data['summary']['avg_overall']:.2f}")
    print(f"  - Timestamp: {data['timestamp']}")
    print(f"  - Categories: {list(category_counts.keys())}")

    return output_file


def generate_html(data, config, category_counts):
    """Generate the full HTML content."""

    module_id = config.get('module_id', 'M11')
    title = config.get('title', 'Multi-Agent Evaluation Dashboard')
    subtitle = config.get('subtitle', 'Adversarial Debate Evaluation System')
    rubric_dims = config.get('rubric_dimensions', ['accuracy', 'relevance', 'completeness', 'clarity', 'reasoning'])
    score_thresholds = config.get('score_thresholds', {'high': 4.0, 'medium': 3.0})

    # Build stats cards for each rubric dimension
    stats_html = f'''
            <div class="stats-grid">
                <div class="stat-card"><div class="stat-value" style="color: var(--accent-blue);">{data['summary']['total']}</div><div class="stat-label">Total Samples</div></div>
                <div class="stat-card"><div class="stat-value" style="color: var(--accent-purple);">{data['summary']['avg_overall']:.2f}</div><div class="stat-label">Avg Overall</div></div>
'''
    colors = ['var(--accent-orange)', 'var(--accent-green)', 'var(--accent-cyan)', 'var(--accent-yellow)', 'var(--accent-red)']
    for i, dim in enumerate(rubric_dims):
        color = colors[i % len(colors)]
        avg = data['summary']['avg_scores'].get(dim, 0)
        stats_html += f'<div class="stat-card"><div class="stat-value" style="color: {color};">{avg:.1f}</div><div class="stat-label">Avg {dim.title()}</div></div>'
    stats_html += '</div>'

    # Build category legend
    legend_html = '<div class="category-legend">'
    for cat_name, cat_config in config.get('critic_categories', {}).items():
        if category_counts.get(cat_name, 0) > 0:
            legend_html += f'<div class="category-legend-item"><span class="category-badge {cat_name}">{cat_name}</span><span>({category_counts[cat_name]})</span></div>'
    legend_html += '</div>'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{module_id} {title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>{generate_css(config)}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{module_id} {title}</h1>
            <p class="subtitle">{subtitle}</p>
            <p style="margin-top: 8px; color: var(--text-secondary); font-size: 0.9rem;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Data: {data['timestamp']}</p>
        </header>

        <div class="tab-nav">
            <button class="tab-btn active" onclick="showTab('results')">Evaluation Results</button>
            <button class="tab-btn" onclick="showTab('flow')">Agent Flow & Architecture</button>
        </div>

        <div id="tab-results" class="tab-content active">
            {stats_html}

            <div class="charts-section">
                <div class="chart-card"><div class="chart-title">Score Distribution by Sample</div><canvas id="scoresChart"></canvas></div>
                <div class="chart-card"><div class="chart-title">Critic Category Distribution</div><canvas id="categoryChart"></canvas></div>
            </div>

            {legend_html}

            <h2 style="margin-bottom: 16px;">Results by Sample</h2>
            <div class="results-list">
'''

    # Generate result cards
    for idx, result in enumerate(data.get('results', [])):
        html += generate_result_card(idx, result, config, rubric_dims, score_thresholds)

    # Build chart data
    cat_labels = list(category_counts.keys())
    cat_values = [category_counts[k] for k in cat_labels]
    cat_colors = [config['critic_categories'].get(k, {}).get('color', '#8250df') for k in cat_labels]

    html += f'''
            </div>
        </div>

        {generate_flow_tab(config)}
    </div>

    <script>
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        const scoresCtx = document.getElementById('scoresChart').getContext('2d');
        new Chart(scoresCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps([r['sample_id'][:12] for r in data.get('results', [])])},
                datasets: [{{
                    label: 'Overall Score',
                    data: {json.dumps([r.get('result', {}).get('overall', 0) for r in data.get('results', [])])},
                    backgroundColor: {json.dumps(['rgba(26, 127, 55, 0.7)' if r.get('result', {}).get('overall', 0) >= score_thresholds['medium'] else 'rgba(207, 34, 46, 0.7)' for r in data.get('results', [])])},
                    borderRadius: 4
                }}]
            }},
            options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true, max: 5 }} }}, plugins: {{ legend: {{ display: false }} }} }}
        }});

        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        new Chart(categoryCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(cat_labels)},
                datasets: [{{
                    data: {json.dumps(cat_values)},
                    backgroundColor: {json.dumps(cat_colors)}
                }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
        }});
    </script>
</body>
</html>
'''

    return html


def generate_result_card(idx, result, config, rubric_dims, score_thresholds):
    """Generate HTML for a single result card."""
    sample_id = result['sample_id']
    input_data = result.get('input_data', {})
    output_data = result.get('output_data', {})
    expected_data = result.get('expected_data', {})
    res = result.get('result', {})
    overall = res.get('overall', 0)
    scores = res.get('scores', {})
    confidence = res.get('confidence', 'N/A')
    summary = res.get('summary', '')
    debate = res.get('debate', {})
    justifications = res.get('justifications', {})
    point_judgments = res.get('point_judgments', [])
    judge_summary = res.get('judge_debate_summary', {})
    meta = res.get('meta_judge', {})

    # Determine score class
    if overall >= score_thresholds.get('high', 4.0):
        score_class = 'high'
    elif overall >= score_thresholds.get('medium', 3.0):
        score_class = 'medium'
    else:
        score_class = 'low'

    weaknesses = debate.get('weaknesses', [])
    strengths = debate.get('strengths', [])
    defenses = debate.get('defenses', []) or debate.get('rebuttals', [])

    # Build scores grid
    scores_html = '<div class="scores-grid">'
    for dim in rubric_dims:
        scores_html += f'<div class="score-item"><div class="score-item-value">{scores.get(dim, 0)}</div><div class="score-item-label">{dim.title()}</div></div>'
    scores_html += '</div>'

    html = f'''
                <div class="result-card">
                    <div class="result-header">
                        <div class="result-title">
                            <span class="result-id">#{idx+1} - {sample_id}</span>
                            <span class="confidence-badge {confidence}">{confidence}</span>
                        </div>
                        <div class="result-meta"><div class="score-badge {score_class}">{overall:.1f}</div></div>
                    </div>
                    <div class="result-body">
                        <div class="summary-box"><div class="summary-title">Final Summary</div><p>{escape_html(summary)}</p></div>
                        {scores_html}

                        <div class="pipeline-steps">
'''

    # Critic Agent
    html += generate_critic_section(input_data, output_data, expected_data, debate, weaknesses, strengths, config)

    # Defender Agent
    html += generate_defender_section(output_data, weaknesses, defenses, debate)

    # Judge Agent
    html += generate_judge_section(overall, confidence, summary, point_judgments, judge_summary, justifications, res)

    # Meta-Judge
    if meta:
        html += generate_meta_judge_section(meta, overall, confidence, summary, judge_summary)

    html += '''
                        </div>
                    </div>
                </div>
'''
    return html


def generate_critic_section(input_data, output_data, expected_data, debate, weaknesses, strengths, config):
    """Generate Critic Agent section."""
    cot = debate.get('chain_of_thought', '')
    initial_score = debate.get('initial_score', 'N/A')
    avg_severity = debate.get('avg_severity', 0)
    overall_assessment = debate.get('overall_assessment', '')

    html = f'''
                            <div class="pipeline-step">
                                <div class="step-header" onclick="this.parentElement.classList.toggle('open')">
                                    <div class="step-icon critic">C</div>
                                    <div class="step-title">Critic Agent</div>
                                    <div class="step-summary">{len(weaknesses)} weaknesses, {len(strengths)} strengths, initial: {initial_score}</div>
                                    <div class="step-toggle">▼</div>
                                </div>
                                <div class="step-content">
                                    <div class="agent-input-box">
                                        <div class="agent-input-title">INPUT to Critic</div>
                                        <div class="io-section"><div class="io-label input-label">Input Data</div><div class="io-content">{escape_html(format_json(input_data, 600))}</div></div>
                                        <div class="io-section"><div class="io-label input-label">Module Output</div><div class="io-content">{escape_html(format_json(output_data, 500))}</div></div>
                                        <div class="io-section"><div class="io-label input-label">Expected (Reference)</div><div class="io-content">{escape_html(format_json(expected_data, 400))}</div></div>
                                    </div>
                                    <div class="agent-output-box">
                                        <div class="agent-output-title">OUTPUT from Critic</div>
'''

    if cot:
        html += f'<div class="chain-of-thought"><div class="chain-of-thought-label">Chain of Thought</div>{escape_html(cot)}</div>'

    if weaknesses:
        html += '<div class="section-title">Weaknesses Found</div><div class="item-list">'
        for w in weaknesses:
            cat = w.get('category', 'UNKNOWN')
            sev = w.get('severity', 0)
            html += f'''<div class="weakness-item">
                <div class="item-header"><span class="item-id">{escape_html(w.get('id', ''))}</span><span class="category-badge {cat}">{escape_html(cat)}</span><span class="severity-badge sev-{sev}">Severity {sev}</span></div>
                <div class="item-description"><strong>Claim:</strong> {escape_html(w.get('claim', ''))}</div>
                <div class="item-evidence"><strong>Evidence:</strong> {escape_html(w.get('evidence', ''))}</div>
            </div>'''
        html += '</div>'

    if strengths:
        html += '<div class="section-title" style="color: var(--accent-green);">Strengths Found</div><div class="item-list">'
        for s in strengths:
            html += f'''<div class="strength-item">
                <div class="item-header"><span class="item-id">{escape_html(s.get('id', ''))}</span><span class="category-badge" style="background: rgba(26,127,55,0.12); color: var(--accent-green);">{escape_html(s.get('category', 'STRENGTH'))}</span></div>
                <div class="item-description"><strong>Claim:</strong> {escape_html(s.get('claim', ''))}</div>
                {f'<div class="item-evidence"><strong>Evidence:</strong> {escape_html(s.get("evidence", ""))}</div>' if s.get('evidence') else ''}
            </div>'''
        html += '</div>'

    html += f'''
                                        <div class="stats-row">
                                            <div class="stat-mini"><div class="stat-mini-value">{initial_score}</div><div class="stat-mini-label">Initial Score</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{len(weaknesses)}</div><div class="stat-mini-label">Weaknesses</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{len(strengths)}</div><div class="stat-mini-label">Strengths</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{avg_severity:.1f}</div><div class="stat-mini-label">Avg Severity</div></div>
                                        </div>
'''

    if overall_assessment:
        html += f'<div class="assessment-box"><strong>Overall Assessment:</strong> {escape_html(overall_assessment)}</div>'

    html += '</div></div></div>'
    return html


def generate_defender_section(output_data, weaknesses, defenses, debate):
    """Generate Defender Agent section."""
    overall_argument = debate.get('overall_argument', '')
    w_found = debate.get('weaknesses_found', len(weaknesses))
    w_accepted = debate.get('weaknesses_accepted', 0)
    w_partial = debate.get('weaknesses_partially_accepted', 0)
    w_rejected = debate.get('weaknesses_rejected', 0)
    w_valid = debate.get('weaknesses_valid', 0)

    html = f'''
                            <div class="pipeline-step">
                                <div class="step-header" onclick="this.parentElement.classList.toggle('open')">
                                    <div class="step-icon defender">D</div>
                                    <div class="step-title">Defender Agent</div>
                                    <div class="step-summary">{len(defenses)} rebuttals | Valid: {w_valid}, Partial: {w_partial}, Rejected: {w_rejected}</div>
                                    <div class="step-toggle">▼</div>
                                </div>
                                <div class="step-content">
                                    <div class="agent-input-box">
                                        <div class="agent-input-title">INPUT to Defender</div>
                                        <div class="io-section"><div class="io-label input-label">Module Output (to defend)</div><div class="io-content">{escape_html(format_json(output_data, 500))}</div></div>
                                        <div class="io-section"><div class="io-label input-label">Critic Weaknesses (to address)</div><div class="io-content">{escape_html(format_json([{"id": w.get("id"), "category": w.get("category"), "claim": w.get("claim"), "severity": w.get("severity")} for w in weaknesses], 700))}</div></div>
                                    </div>
                                    <div class="agent-output-box">
                                        <div class="agent-output-title">OUTPUT from Defender</div>
                                        <div class="item-list">
'''

    for d in defenses:
        verdict = d.get('verdict', 'unknown')
        html += f'''<div class="weakness-item">
            <div class="item-header"><span class="item-id">Re: {escape_html(d.get('weakness_id', ''))}</span><span class="verdict-badge {verdict}">{escape_html(verdict)}</span></div>
            <div class="item-description"><strong>Rebuttal:</strong> {escape_html(d.get('rebuttal', ''))}</div>
            {f'<div class="item-evidence"><strong>Evidence:</strong> {escape_html(d.get("evidence", ""))}</div>' if d.get('evidence') else ''}
            {f'<div class="item-evidence" style="border-left-color: var(--accent-yellow);"><strong>Concession:</strong> {escape_html(d.get("concession", ""))}</div>' if d.get('concession') else ''}
        </div>'''

    html += f'''</div>
                                        <div class="stats-row">
                                            <div class="stat-mini"><div class="stat-mini-value">{w_found}</div><div class="stat-mini-label">Found</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value" style="color: var(--accent-red);">{w_accepted}</div><div class="stat-mini-label">Accepted</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value" style="color: var(--accent-yellow);">{w_partial}</div><div class="stat-mini-label">Partial</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value" style="color: var(--accent-green);">{w_rejected}</div><div class="stat-mini-label">Rejected</div></div>
                                        </div>
'''

    if overall_argument:
        html += f'<div class="assessment-box" style="border-left-color: var(--accent-green);"><strong>Overall Argument:</strong> {escape_html(overall_argument)}</div>'

    html += '</div></div></div>'
    return html


def generate_judge_section(overall, confidence, summary, point_judgments, judge_summary, justifications, res):
    """Generate Judge Agent section."""
    critic_wins = judge_summary.get('critic_wins', 0)
    defender_wins = judge_summary.get('defender_wins', 0)
    ties = judge_summary.get('ties', 0)
    overall_winner = judge_summary.get('overall_winner', 'N/A')
    dim_avg = res.get('dimension_average', overall)
    debate_adj = res.get('debate_adjustment', 0)

    html = f'''
                            <div class="pipeline-step">
                                <div class="step-header" onclick="this.parentElement.classList.toggle('open')">
                                    <div class="step-icon judge">J</div>
                                    <div class="step-title">Judge Agent</div>
                                    <div class="step-summary">Final: {overall:.1f} | Critic: {critic_wins}, Defender: {defender_wins}, Ties: {ties}</div>
                                    <div class="step-toggle">▼</div>
                                </div>
                                <div class="step-content">
                                    <div class="agent-output-box">
                                        <div class="agent-output-title">OUTPUT from Judge</div>

                                        <div class="section-title">Point Judgments</div>
                                        <div class="item-list">
'''

    for pj in point_judgments:
        winner = pj.get('winner', 'tie')
        winner_class = 'valid' if winner == 'critic' else ('invalid' if winner == 'defender' else 'partially_valid')
        c_score = pj.get('critic_score', 0)
        d_score = pj.get('defender_score', 0)
        reasoning = pj.get('reasoning', '')
        html += f'''<div class="weakness-item">
            <div class="item-header">
                <span class="item-id">{escape_html(pj.get('weakness_id', ''))}</span>
                <span class="verdict-badge {winner_class}">Winner: {escape_html(winner)}</span>
                <span style="font-size: 0.8rem; color: var(--text-secondary);">Critic: {c_score}/5 | Defender: {d_score}/5</span>
            </div>
            <div class="item-evidence"><strong>Reasoning:</strong> {escape_html(reasoning)}</div>
        </div>'''

    html += '</div>'

    if justifications:
        html += '<div class="section-title">Rubric Justifications</div>'
        for dim, just in justifications.items():
            html += f'<div class="justification-item"><div class="justification-label">{escape_html(dim)}</div><div class="justification-text">{escape_html(just)}</div></div>'

    html += f'''
                                        <div class="stats-row">
                                            <div class="stat-mini"><div class="stat-mini-value">{dim_avg:.2f}</div><div class="stat-mini-label">Dimension Avg</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{debate_adj:+.1f}</div><div class="stat-mini-label">Debate Adj</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value" style="color: var(--accent-blue);">{overall:.1f}</div><div class="stat-mini-label">Final Score</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{overall_winner}</div><div class="stat-mini-label">Debate Winner</div></div>
                                        </div>
                                        <div class="assessment-box" style="border-left-color: var(--accent-blue);"><strong>Summary:</strong> {escape_html(summary)}</div>
                                    </div>
                                </div>
                            </div>
'''
    return html


def generate_meta_judge_section(meta, overall, confidence, summary, judge_summary):
    """Generate Meta-Judge section."""
    is_syco = meta.get('is_sycophantic', False)
    jq = meta.get('judgment_quality', 'N/A')
    meta_conf = meta.get('confidence', 0)
    should_retry = meta.get('should_retry', False)
    rec = meta.get('recommendation', 'N/A')
    qc = meta.get('quick_check', {})
    full_skipped = meta.get('full_check_skipped', 'N/A')

    html = f'''
                            <div class="pipeline-step">
                                <div class="step-header" onclick="this.parentElement.classList.toggle('open')">
                                    <div class="step-icon meta">M</div>
                                    <div class="step-title">Meta-Judge</div>
                                    <div class="step-summary">Quality: {jq}/5 | Rec: {rec} | Sycophantic: {'Yes' if is_syco else 'No'}</div>
                                    <div class="step-toggle">▼</div>
                                </div>
                                <div class="step-content">
                                    <div class="agent-input-box">
                                        <div class="agent-input-title">INPUT to Meta-Judge</div>
                                        <div class="io-content">Judge Output Summary:
- Final Score: {overall:.1f}
- Confidence: {confidence}
- Debate Winner: {judge_summary.get('overall_winner', 'N/A')}
- Summary: {escape_html(summary[:300])}...</div>
                                    </div>
                                    <div class="agent-output-box">
                                        <div class="agent-output-title">OUTPUT from Meta-Judge</div>
                                        <div class="stats-row">
                                            <div class="stat-mini"><div class="stat-mini-value" style="color: {'var(--accent-red)' if is_syco else 'var(--accent-green)'};">{'Yes' if is_syco else 'No'}</div><div class="stat-mini-label">Sycophantic</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{jq}</div><div class="stat-mini-label">Quality (1-5)</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{meta_conf:.0%}</div><div class="stat-mini-label">Confidence</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value" style="color: {'var(--accent-red)' if should_retry else 'var(--accent-green)'};">{'Yes' if should_retry else 'No'}</div><div class="stat-mini-label">Should Retry</div></div>
                                            <div class="stat-mini"><div class="stat-mini-value">{rec}</div><div class="stat-mini-label">Recommendation</div></div>
                                        </div>
                                        <div class="section-title">Quick Check Details</div>
                                        <div class="io-content">Likely Sycophantic: {qc.get('likely_sycophantic', 'N/A')}
Triggers Found: {qc.get('triggers', [])}
Trigger Count: {qc.get('trigger_count', 0)}
Estimated Quality: {qc.get('estimated_quality', 'N/A')}
Estimated Confidence: {qc.get('estimated_confidence', 'N/A')}
Full Check Skipped: {full_skipped}</div>
                                    </div>
                                </div>
                            </div>
'''
    return html


def generate_flow_tab(config):
    """Generate the Agent Flow tab content."""
    module_id = config.get('module_id', 'M11')
    prompts = config.get('prompts', {})
    categories = config.get('critic_categories', {})

    # Build category badges HTML
    cat_badges = ''
    for cat_name in categories.keys():
        cat_badges += f'<span class="category-badge {cat_name}">{cat_name}</span> '

    return f'''
        <div id="tab-flow" class="tab-content">
            <div class="flow-container">
                <h2 style="text-align: center; margin-bottom: 32px;">Adversarial Debate Evaluation Pipeline</h2>
                <div class="flow-diagram">
                    <div class="flow-step">
                        <div class="flow-connector"><div class="flow-dot input"></div><div class="flow-line"></div></div>
                        <div class="flow-card input">
                            <div class="flow-card-header"><div class="flow-card-icon input">0</div><div><div class="flow-card-title">Input Data</div><div class="flow-card-subtitle">Sample to evaluate</div></div></div>
                            <div class="flow-section"><div class="flow-section-title">Data Components:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>input_data:</strong> Product/item information</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>output_data:</strong> {module_id} module's response</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>expected_data:</strong> Reference/ground truth</div></div>
                            </div></div>
                        </div>
                    </div>
                    <div class="flow-step">
                        <div class="flow-connector"><div class="flow-dot critic"></div><div class="flow-line"></div></div>
                        <div class="flow-card critic">
                            <div class="flow-card-header"><div class="flow-card-icon critic">C</div><div><div class="flow-card-title">Step 1: Critic Agent</div><div class="flow-card-subtitle">{prompts.get('critic', 'prompts/critic.md')}</div></div></div>
                            <div class="flow-section"><div class="flow-section-title input">INPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div>module_id, context, input_data, output_data, expected_data</div></div>
                            </div></div>
                            <div class="flow-section"><div class="flow-section-title output">OUTPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>chain_of_thought</strong> - Reasoning process</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>weaknesses</strong> - [{{id, category, claim, evidence, severity}}]</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>strengths</strong> - [{{id, category, claim, evidence}}]</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>initial_score</strong> - Critic's assessment</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>overall_assessment</strong> - Summary</div></div>
                            </div></div>
                            <div class="flow-section"><div class="flow-section-title">Categories:</div><div style="margin-top: 8px;">{cat_badges}</div></div>
                        </div>
                    </div>
                    <div class="flow-step">
                        <div class="flow-connector"><div class="flow-dot defender"></div><div class="flow-line"></div></div>
                        <div class="flow-card defender">
                            <div class="flow-card-header"><div class="flow-card-icon defender">D</div><div><div class="flow-card-title">Step 2: Defender Agent</div><div class="flow-card-subtitle">{prompts.get('defender', 'prompts/defender.md')}</div></div></div>
                            <div class="flow-section"><div class="flow-section-title input">INPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet" style="background:var(--accent-red);"></div><div>All above + <strong>Critic's weaknesses</strong> (from Step 1)</div></div>
                            </div></div>
                            <div class="flow-section"><div class="flow-section-title output">OUTPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>defenses</strong> - [{{weakness_id, verdict, rebuttal, evidence, concession}}]</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>overall_argument</strong> - Defense summary</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div>Stats: weaknesses_accepted, partially_accepted, rejected</div></div>
                            </div></div>
                            <div class="flow-section"><div class="flow-section-title">Verdicts:</div><div style="margin-top: 8px;"><span class="verdict-badge valid">valid</span> <span class="verdict-badge partially_valid">partially_valid</span> <span class="verdict-badge invalid">invalid</span></div></div>
                        </div>
                    </div>
                    <div class="flow-step">
                        <div class="flow-connector"><div class="flow-dot judge"></div><div class="flow-line"></div></div>
                        <div class="flow-card judge">
                            <div class="flow-card-header"><div class="flow-card-icon judge">J</div><div><div class="flow-card-title">Step 3: Judge Agent</div><div class="flow-card-subtitle">{prompts.get('judge', 'prompts/judge.md')}</div></div></div>
                            <div class="flow-section"><div class="flow-section-title input">INPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet" style="background:var(--accent-red);"></div><div>All above + <strong>Debate transcript</strong> (weaknesses + defenses)</div></div>
                            </div></div>
                            <div class="flow-section"><div class="flow-section-title output">OUTPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>point_judgments</strong> - [{{weakness_id, critic_score, defender_score, winner, reasoning}}]</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>judge_debate_summary</strong> - {{critic_wins, defender_wins, ties, overall_winner}}</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>rubric_scores</strong> - Per-dimension scores</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>justifications</strong> - Per-dimension explanations</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>final_score</strong> = dimension_average + debate_adjustment</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>summary</strong> - Overall assessment</div></div>
                            </div></div>
                        </div>
                    </div>
                    <div class="flow-step">
                        <div class="flow-connector"><div class="flow-dot meta"></div></div>
                        <div class="flow-card meta">
                            <div class="flow-card-header"><div class="flow-card-icon meta">M</div><div><div class="flow-card-title">Step 4: Meta-Judge</div><div class="flow-card-subtitle">{prompts.get('meta_judge', 'prompts/meta_judge.md')}</div></div></div>
                            <div class="flow-section"><div class="flow-section-title input">INPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet" style="background:var(--accent-blue);"></div><div><strong>Judge's complete output</strong> (from Step 3)</div></div>
                            </div></div>
                            <div class="flow-section"><div class="flow-section-title output">OUTPUT:</div><div class="flow-list">
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>is_sycophantic</strong> - Boolean</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>judgment_quality</strong> - 1-5 score</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>confidence</strong> - 0-1</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>should_retry</strong> - Boolean</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>recommendation</strong> - "accept" | "retry" | "flag"</div></div>
                                <div class="flow-list-item"><div class="flow-list-bullet"></div><div><strong>quick_check</strong> - {{triggers, trigger_count, estimated_quality}}</div></div>
                            </div></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
'''


def main():
    parser = argparse.ArgumentParser(
        description='Generate HTML dashboard from multi-agent evaluation results.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python generate_dashboard.py results/m11_results.json
    python generate_dashboard.py results/m11_results.json -o my_report.html --open
    python generate_dashboard.py results/m12_results.json -c config/m12_dashboard.yaml
    python generate_dashboard.py results/m11_results.json -m M11 -t "My Custom Title"
        '''
    )

    parser.add_argument('results_file', help='Input JSON results file')
    parser.add_argument('-o', '--output', help='Output HTML file')
    parser.add_argument('-c', '--config', help='Config YAML/JSON file for module-specific settings')
    parser.add_argument('-m', '--module', help='Module ID override (e.g., M11, M12)')
    parser.add_argument('-t', '--title', help='Dashboard title override')
    parser.add_argument('--open', action='store_true', help='Open dashboard in browser after generation')

    args = parser.parse_args()

    if not os.path.exists(args.results_file):
        print(f"Error: Results file not found: {args.results_file}")
        sys.exit(1)

    # Load config
    config = load_config(args.config)

    # Generate dashboard
    output_file = generate_dashboard(
        args.results_file,
        output_file=args.output,
        config=config,
        title_override=args.title,
        module_override=args.module
    )

    # Open in browser if requested
    if args.open:
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(output_file))


if __name__ == '__main__':
    main()
