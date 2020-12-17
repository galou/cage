#!/usr/bin/gawk -E
# Take as input a list of space separated tuples "real_file link" and create a symlink.

{
	if ($2 != "") {
		printf "ln -s %s %s\n",$1, $2
		system("rm -f \"" $2 "\"")
		system("ln -s \"" $1 "\" \"" $2 "\"")
	}
}
