// Graph props:
//  name: None
//  trailing_jumps: True

// Predecessors: []
05:
$a4 = 1
$a2 = 1
Exits: [(None, '05.if')]

// Predecessors: ['05']
05.if:
if ($a1 == 5) {
  $a2 = 2
}
Exits: [(None, '20')]

// Predecessors: ['05.if']
20:
$a3 = 3
Exits: []
