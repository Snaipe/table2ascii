from table2ascii import table2ascii

TABLE = {
    'node': 'table',
    'colspec': [24, 12, 10, 10],
    'rowspec': [2, 1, 1, 1, 1],
    'children': [
      {
        'node': 'head',
        'children': [
            {
              'node': 'row',
              'children': [
                {'node': 'cell', 'data': 'Header row, column 1\n(header rows optional)'},
                {'node': 'cell', 'data': 'Header 2'},
                {'node': 'cell', 'data': 'Header 3'},
                {'node': 'cell', 'data': 'Header 4'},
              ]
            }
          ]
      },
      {
        'node': 'body',
        'children': [
          {
            'node': 'row',
            'children': [
              {'node': 'cell', 'data': 'body row 1, column 1'},
              {'node': 'cell', 'data': 'column 2'},
              {'node': 'cell', 'data': 'column 3'},
              {'node': 'cell', 'data': 'column 4'},
            ]
          },
          {
            'node': 'row',
            'children': [
              {'node': 'cell', 'data': 'body row 2'},
              {'node': 'cell', 'data': 'Cells may span columns.', 'morecols': 2},
            ],
          },
          {
            'node': 'row',
            'children': [
              {'node': 'cell', 'data': 'body row 3'},
              {'node': 'cell', 'data': 'Cells may span rows.', 'morerows': 1},
              {'node': 'cell', 'data': 'Cells may span both rows and columns.', 'morerows': 1, 'morecols': 1},
            ],
          },
          {
            'node': 'row',
            'children': [
              {'node': 'cell', 'data': 'body row 4'},
            ],
          }
        ]
      }
    ]
  }

print(table2ascii(TABLE))
