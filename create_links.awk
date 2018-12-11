#!/usr/bin/gawk -E

{
	if ($2 != "") {
		printf "ln -s %s %s\n",$1, $2
		system("rm -f \"" $2 "\"")
		system("ln -s \"" $1 "\" \"" $2 "\"")
	}
}
