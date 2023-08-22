import re
from typing import Optional, Dict

import pandas as pd

from data_to_paper.latex.clean_latex import replace_special_latex_chars, process_non_math_parts
from data_to_paper.utils.dataframe import extract_df_headers_and_values

THREEPARTTABLE = r"""\begin{table}[htbp]
\centering
\begin{threeparttable}
<caption>
<label>
<tabular>
\begin{tablenotes}
<note_and_legend>
\end{tablenotes}
\end{threeparttable}
\end{table}
"""

THREEPARTTABLE_WIDE = r"""\begin{table}[h]
<caption>
<label>
\begin{threeparttable}
\renewcommand{\TPTminimum}{\linewidth}
\makebox[\linewidth]{%
<tabular>}
\begin{tablenotes}
\footnotesize
<note_and_legend>
\end{tablenotes}
\end{threeparttable}
\end{table}
"""


def to_latex_with_note(df: pd.DataFrame, filename: Optional[str], caption: str = None, label: str = None,
                       note: str = None,
                       legend: Dict[str, str] = None,
                       is_wide: bool = True,
                       **kwargs):
    """
    Create a latex table with a note.
    Same as df.to_latex, but with a note and legend.
    """
    regular_latex_table = df.to_latex(None, caption=None, label=None, **kwargs)
    index = kwargs.get('index', True)

    tabular_part = get_tabular_block(regular_latex_table)
    caption = r'\caption{' + process_non_math_parts(caption) + '}\n' if caption else ''
    label = r'\label{' + label + '}\n' if label else ''

    note_and_legend = []
    if note:
        note_and_legend.append(r'\item ' + replace_special_latex_chars(note))
    if legend:
        headers = extract_df_headers_and_values(df, index=index)
        for key, value in legend.items():
            if key in headers:
                note_and_legend.append(r'\item \textbf{' + replace_special_latex_chars(key) +
                                       '}: ' + replace_special_latex_chars(value))
            else:
                print('WARNING: legend key "{}" is not a headers in the dataframe'.format(key))
    if len(note_and_legend) == 0:
        note_and_legend.append(r'\item ')  # add an empty item to avoid an error

    template = THREEPARTTABLE if not is_wide else THREEPARTTABLE_WIDE
    latex = template.replace('<tabular>', tabular_part) \
        .replace('<caption>\n', caption) \
        .replace('<label>\n', label) \
        .replace('<note_and_legend>', '\n'.join(note_and_legend))

    if filename is not None:
        with open(filename, 'w') as f:
            f.write(latex)
    return latex


def get_tabular_block(latex_table: str) -> str:
    """
    Extract the tabular block of the table.
    """
    return re.search(pattern=r'\\begin{tabular}.*\n(.*)\\end{tabular}', string=latex_table, flags=re.DOTALL).group(0)
