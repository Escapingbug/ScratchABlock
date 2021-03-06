// Graph props:
//  addr: 15
//  estimated_params: {$a2}
//  modifieds: {$a3, $save}
//  name: func
//  preserveds: {$a2}
//  reach_exit: {$a2, $a3, $save}
//  trailing_jumps: True

// Predecessors: []
// Node props:
//  live_gen: set()
//  live_in: {$a2_0}
//  live_kill: set()
//  live_out: {$a2_0}
//  reachdef_gen: {($a2, '.ENTRY')}
//  reachdef_in: {($a2, None), ($a3, None), ($save, None)}
//  reachdef_kill: {($a2, '15'), ($a2, '.ENTRY'), ($a2, None)}
//  reachdef_out: {($a2, '.ENTRY'), ($a3, None), ($save, None)}
// BBlock props:
//  state_out: {$a2=$a2_0}
.ENTRY:
// $a2 = $a2_0 (dead)
Exits: [(None, '15')]

// Predecessors: ['.ENTRY']
// Node props:
//  live_gen: {$a2_0}
//  live_in: {$a2_0}
//  live_kill: {$a3, $save}
//  live_out: {$a3, $save}
//  reachdef_gen: {($a2, '15'), ($a3, '15'), ($save, '15')}
//  reachdef_in: {($a2, '.ENTRY'), ($a3, None), ($save, None)}
//  reachdef_kill: {($a2, '15'), ($a2, '.ENTRY'), ($a2, None), ($a3, '15'), ($a3, None), ($save, '15'), ($save, None)}
//  reachdef_out: {($a2, '15'), ($a3, '15'), ($save, '15')}
// BBlock props:
//  state_in: {$a2=$a2_0}
//  state_out: {$a2=$a2_0, $a3=$a2_0 + 1, $save=$a2_0}
15:
$save = $a2_0
$a3 = $a2_0 + 1
// $a2 = 10 (dead)
// $a2 = $a2_0 (dead)
return
Exits: [(None, '_EXIT_')]

// Predecessors: ['15']
// Node props:
//  live_gen: set()
//  live_in: {$a3, $save}
//  live_kill: set()
//  live_out: {$a3, $save}
//  reachdef_gen: set()
//  reachdef_in: {($a2, '15'), ($a3, '15'), ($save, '15')}
//  reachdef_kill: set()
//  reachdef_out: {($a2, '15'), ($a3, '15'), ($save, '15')}
// BBlock props:
//  state_in: {$a2=$a2_0, $a3=$a2_0 + 1, $save=$a2_0}
//  state_out: {$a2=$a2_0, $a3=$a2_0 + 1, $save=$a2_0}
_EXIT_:
return
Exits: []
