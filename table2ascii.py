from textwrap import wrap

class SkipChildren(Exception):
  pass

class Visitor(object):

  def visit(self, node):
    """
    Visit a generic node. Calls 'visit_' + node_name on the node,
    then visit its children, then calls 'depart_' + node_name.
    """
    def noop(node):
      pass

    try:
      visit_fn = getattr(self, 'visit_' + node['node'])
    except AttributeError:
      visit_fn = noop

    try:
      depart_fn = getattr(self, 'depart_' + node['node'])
    except AttributeError:
      depart_fn = noop

    try:
      visit_fn(node)
      for n in node.get('children', []):
        self.visit(n)
    except SkipChildren:
      return
    finally:
      depart_fn(node)

class BaseTableVisitor(Visitor):

  def __init__(self):
    Visitor.__init__(self)
    self.lines = ['']
    self.line = 0
    self.cursor = 0
    self.col = 0
    self.row = 0
    self.widths = []
    self.heights = []

  def _rewrite_in_line(self, line_index, from_index, repl):
    """
    Overwrites a part of the specified line,
    starting from the specified index, with another string.
    """

    line = self.lines[line_index]
    line = line[:from_index] + repl + line[from_index + len(repl):]
    self.lines[line_index] = line

  def visit_row(self, node):
    self.col = 0
    self.cursor = 0

  def depart_row(self, node):
    self.line += self.heights[self.row] + 1
    self.row += 1

  def _get_cols(self, node, col):
    """
    Returns the number of columns this cell spans,
    and its width in character columns.
    """
    cols = node.get('morecols', 0) + 1
    width = sum(self.widths[col:col + cols]) + (cols - 1)
    return cols, width

  def _get_rows(self, node, row):
    """
    Returns the number of rows this cell spans,
    and its height in lines.
    """
    rows = node.get('morerows', 0) + 1
    height = sum(self.heights[row:row + rows]) + (rows - 1)
    return rows, height

  def _get_cell_dimensions(self, node, col, row):
    """
    Returns the number of columns and rows this cell spans,
    and its width in character columns and height in lines.
    """
    cols, width = self._get_cols(node, col)
    rows, height = self._get_rows(node, row)

    return cols, rows, width, height

  def visit_cell(self, node):
    cols, width = self._get_cols(node, self.col)

    self.col += cols
    self.cursor += width + 1

    # Do not recurse
    raise SkipChildren

class TableOutliner(BaseTableVisitor):

  def __init__(self):
    BaseTableVisitor.__init__(self)
    self.nb_rows = 0
    self.local_row = 0

  def _draw_rule(self):
    total_width = sum(self.widths) + (len(self.widths) + 1)
    total_height = sum(self.heights) + (len(self.heights) + 1)

    self.lines[self.line] += '+' + '-' * (total_width - 1)
    self.lines.extend(['|' + ' ' * (total_width - 1)] * (total_height - 1))
    self.line += 1
    self.cursor = 0

  def visit_table(self, node):
    self.widths = node['colspec']
    self.heights = node['rowspec']
    self._draw_rule()

  def depart_row(self, node):
    BaseTableVisitor.depart_row(self, node)
    self.local_row += 1

  def visit_head(self, node):
    self.nb_rows = len(node['children'])
    self.local_row = 0

  visit_body = visit_head

  def visit_cell(self, node):
    cols, rows, width, height = self._get_cell_dimensions(node, self.col, self.row)

    # Draw the horizontal rule

    rule = '=' if self.local_row + rows - 1 == self.nb_rows - 1 else '-'

    self._rewrite_in_line(self.line + height, self.cursor, '+' + (width * rule) + '+')

    # Draw the vertical rule

    for i in range(height):
      self._rewrite_in_line(self.line + i, self.cursor + width + 1, '|')

    self._rewrite_in_line(self.line - 1, self.cursor + width + 1, '+')

    self.col += cols
    self.cursor += width + 1

    # Do not recurse
    raise SkipChildren

class TableWriter(BaseTableVisitor):

  def visit_table(self, node):
    outliner = TableOutliner()
    outliner.visit(node)
    self.lines = outliner.lines
    self.widths = outliner.widths
    self.heights = outliner.heights

  def visit_cell(self, node):
    cols, rows, width, height = self._get_cell_dimensions(node, self.col, self.row)

    # Write cell contents

    data = wrap(node['data'], width=width - 2)
    i = 1
    for l in data:
      self._rewrite_in_line(self.line + i, self.cursor + 2, l)
      i += 1

    BaseTableVisitor.visit_cell(self, node)

def table2ascii(table):
  v = TableWriter()
  v.visit(table)
  return '\n'.join(v.lines)
