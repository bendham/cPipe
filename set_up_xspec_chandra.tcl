query yes

puts "Welcome to the XSPEC Spectral Chandra setup"

puts "Which model would you like? tbabs*(pow + bb) (1), tbabs*pow (2), or tbabs*wabs*zpow (3) (enter for nothing)"
gets stdin modelOpt

puts "Which stat would you like? chi (1) or cstat (2)"
gets stdin statOpt


if { $modelOpt == 2 } {
	model tbabs*pow
} elseif {$modelOpt == 1 } {
	model tbabs*(pow + bb)
} elseif {$modelOpt == 3 } {
	model tbabs*wabs*zpow
}

if { $statOpt == 2} {
	statistic cstat
} else {
	statistic chi
}

ignore bad

ignore **:**-0.3

ignore **:7.5-**

abund wilm

setplot energy

fit

setplot dev /xw
