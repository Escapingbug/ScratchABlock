// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
10:
if ($a1 == 0) goto 20, ($a1 == 1) goto 30
Exits: [(COND(EXPR(==[$a1, 0])), '20'), (COND(EXPR(==[$a1, 1])), '30'), (None, '15')]

// Predecessors: ['10']
15:
nop()
Exits: [(None, '20')]

// Predecessors: ['10', '15']
20:
$a2 = 1
goto 99
Exits: [(None, '99')]

// Predecessors: ['10']
30:
$a2 = 2
goto 99
Exits: [(None, '99')]

// Predecessors: ['20', '30']
99:
return
Exits: []
