"""Minimal OWID Chart Visualization Module for Educational Video Pipeline"""

import io
import os
import json
from typing import List
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from openai import OpenAI


MODERN_COLORS = [
    '#4CC9F0', '#F72585', '#7209B7', '#3A86FF', '#06FFA5',
    '#FB5607', '#FFBE0B', '#8338EC', '#FF006E', '#06D6A0',
]


def shorten_labels_with_llm(labels: List[str], max_length: int = 15) -> List[str]:
    """
    Use LLM to intelligently shorten long labels for graph legends.

    Args:
        labels: List of label strings (country names, column names, etc.)
        max_length: Target maximum length for shortened labels

    Returns:
        List of shortened labels maintaining clarity
    """
    # Skip if all labels are already short enough
    if all(len(label) <= max_length for label in labels):
        return labels

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""Shorten these labels to maximum {max_length} characters each while keeping them clear and recognizable.
Use standard abbreviations where appropriate (e.g., "USA" for "United States", "UK" for "United Kingdom").
Keep the meaning obvious.

Labels: {json.dumps(labels)}

Return ONLY a JSON array of shortened labels in the same order, nothing else.
Example: ["USA", "China", "Germany", "UK"]"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )

        # Parse the response
        response_text = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        shortened = json.loads(response_text)

        # Validate we got the same number of labels back
        if len(shortened) == len(labels):
            return shortened
        else:
            print(f"Warning: LLM returned {len(shortened)} labels but expected {len(labels)}, using originals")
            return labels

    except Exception as e:
        print(f"Warning: Could not shorten labels with LLM: {e}")
        # Fallback: simple truncation
        return [label[:max_length] + "..." if len(label) > max_length else label for label in labels]


def create_visualization(df: pd.DataFrame, title: str, chart_slug: str, max_lines: int = 10) -> bytes:
    """
    Create a visualization at 720p resolution (1280x720) for consistent video stitching.

    Args:
        df: DataFrame with OWID data
        title: Chart title
        chart_slug: Chart identifier
        max_lines: Maximum number of lines/entities to show (default: 10)

    Returns:
        PNG image bytes at 1280x720 resolution
    """
    plt.style.use('dark_background')
    # Calculate figsize for 720p (1280x720) at 120 DPI
    # figsize = (width_px / dpi, height_px / dpi) = (1280/120, 720/120)
    fig, ax = plt.subplots(figsize=(10.67, 6), facecolor='#0D1117', dpi=120)
    ax.set_facecolor('#161B22')

    # Clean data - remove NaN and inf values
    df = df.replace([float('inf'), float('-inf')], float('nan'))
    df = df.dropna(how='all', axis=1)  # Drop columns that are all NaN

    non_data_cols = ['Entity', 'Code', 'Year', 'Day', 'time']
    # Get data columns and filter out columns with only NaN values or non-numeric types
    data_cols = []
    for col in df.columns:
        if col not in non_data_cols:
            # Check if column has any non-NaN values and is numeric
            if pd.api.types.is_numeric_dtype(df[col]) and df[col].notna().any():
                data_cols.append(col)

    if not data_cols:
        ax.text(0.5, 0.5, 'No data columns found to visualize',
                ha='center', va='center', fontsize=16, color='#C9D1D9',
                fontfamily='sans-serif')
        ax.axis('off')
    else:
        time_col = 'Year' if 'Year' in df.columns else ('Day' if 'Day' in df.columns else None)

        if time_col and 'Entity' in df.columns:
            entities = df['Entity'].unique()

            # Limit to max_lines entities for readability
            if len(entities) > max_lines:
                latest_data = df.sort_values(time_col).groupby('Entity').last()
                top_entities = latest_data.nlargest(max_lines, data_cols[0]).index.tolist()
                df = df[df['Entity'].isin(top_entities)]
                entities = top_entities
                print(f"Limited to top {max_lines} entities for clarity")

            # Shorten entity names for legend using LLM
            entity_list = entities.tolist()
            shortened_entities = shorten_labels_with_llm(entity_list, max_length=15)
            entity_map = dict(zip(entity_list, shortened_entities))

            # Also shorten data column names if needed
            shortened_cols = shorten_labels_with_llm(data_cols, max_length=20) if len(data_cols) > 1 else data_cols
            col_map = dict(zip(data_cols, shortened_cols))

            for idx, entity in enumerate(entities):
                entity_data = df[df['Entity'] == entity].sort_values(time_col)
                color = MODERN_COLORS[idx % len(MODERN_COLORS)]

                short_entity = entity_map.get(entity, entity)

                for col in data_cols:
                    if entity_data[col].notna().any():
                        short_col = col_map.get(col, col)
                        ax.plot(entity_data[time_col], entity_data[col],
                                marker='o', markersize=5, linewidth=2.5,
                                label=f'{short_entity}' if len(data_cols) == 1 else f'{short_entity} - {short_col}',
                                alpha=0.95, color=color, markeredgewidth=0.8,
                                markeredgecolor='#0D1117', zorder=3)

            ax.set_xlabel(time_col, fontsize=14, fontweight='600', color='#C9D1D9', labelpad=10)
            ax.set_ylabel(data_cols[0] if len(data_cols) == 1 else 'Value',
                         fontsize=14, fontweight='600', color='#C9D1D9', labelpad=10)

            legend = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
                             fontsize=10, frameon=True, shadow=False,
                             fancybox=True, framealpha=0.9, edgecolor='#30363D')
            legend.get_frame().set_facecolor('#0D1117')

            ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.8, color='#30363D', zorder=0)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#30363D')
            ax.spines['bottom'].set_color('#30363D')

        elif time_col:
            # Shorten column names for legend
            shortened_cols = shorten_labels_with_llm(data_cols, max_length=20)
            col_map = dict(zip(data_cols, shortened_cols))

            df_sorted = df.sort_values(time_col)
            for idx, col in enumerate(data_cols):
                if df_sorted[col].notna().any():
                    color = MODERN_COLORS[idx % len(MODERN_COLORS)]
                    short_col = col_map.get(col, col)
                    ax.plot(df_sorted[time_col], df_sorted[col],
                           marker='o', markersize=6, linewidth=2.5,
                           label=short_col, alpha=0.95, color=color,
                           markeredgewidth=0.8, markeredgecolor='#0D1117', zorder=3)

            ax.set_xlabel(time_col, fontsize=14, fontweight='600', color='#C9D1D9', labelpad=10)
            ax.set_ylabel('Value', fontsize=14, fontweight='600', color='#C9D1D9', labelpad=10)

            legend = ax.legend(fontsize=11, frameon=True, shadow=False,
                             fancybox=True, framealpha=0.9, edgecolor='#30363D')
            legend.get_frame().set_facecolor('#0D1117')

            ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.8, color='#30363D', zorder=0)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#30363D')
            ax.spines['bottom'].set_color('#30363D')
        else:
            colors = [MODERN_COLORS[i % len(MODERN_COLORS)] for i in range(len(df))]
            ax.bar(range(len(df)), df[data_cols[0]], color=colors,
                   alpha=0.9, edgecolor='#0D1117', linewidth=1.5, zorder=3)

            # Shorten y-axis label (column name) if needed
            shortened_col = shorten_labels_with_llm([data_cols[0]], max_length=25)[0]
            ax.set_ylabel(shortened_col, fontsize=14, fontweight='600', color='#C9D1D9', labelpad=10)

            ax.set_xticks(range(len(df)))
            # Ensure labels are strings and shorten them
            if 'Entity' in df.columns:
                labels = [str(x) for x in df['Entity'].tolist()]
            else:
                labels = [str(i) for i in range(len(df))]

            # Shorten x-axis labels
            shortened_labels = shorten_labels_with_llm(labels, max_length=12)
            ax.set_xticklabels(shortened_labels, rotation=45, ha='right', fontsize=10)

            ax.grid(True, alpha=0.15, axis='y', linestyle='-', linewidth=0.8, color='#30363D', zorder=0)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#30363D')
            ax.spines['bottom'].set_color('#30363D')

    ax.set_title(title, fontsize=18, fontweight='700', color='#E6EDF3',
                pad=25, fontfamily='sans-serif')

    ax.tick_params(colors='#8B949E', labelsize=10)

    plt.tight_layout()

    buf = io.BytesIO()
    try:
        # Save at 120 DPI to produce exactly 1280x720 pixels (720p)
        # This ensures consistent dimensions for video stitching
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='#0D1117', edgecolor='none')
    finally:
        plt.close(fig)

    buf.seek(0)
    return buf.read()
