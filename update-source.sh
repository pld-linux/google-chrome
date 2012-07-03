#!/bin/sh
arch=x86_64
branch=${1:-stable}
sourceurl=http://dl.google.com/linux/chrome/rpm/stable/$arch/

set -e

echo -n "Fetching latest version... "
t=$(mktemp)

poldek -q --st=metadata --source "$sourceurl" --update
poldek -q --skip-installed --st=metadata --source "$sourceurl" --cmd "ls google-chrome-$branch" > $t

set -- $(sed -re "s,^.+-([^-]+)-([^-]+).$arch$,\1 \2," $t)

rm -f $t

ver=$1
rev=$2

echo "$ver-$rev"

specfile=google-chrome.spec
oldrev=$(awk '/^%define[ 	]+svnrev[ 	]+/{print $NF}' $specfile)
if [ "$oldrev" != "$rev" ]; then
	echo "Updating $specfile for $ver r$rev"
	sed -i -e "
		s/^\(%define[ \t]\+svnrev[ \t]\+\)[0-9]\+\$/\1$rev/
		s/^\(Version:[ \t]\+\)[.0-9]\+\$/\1$ver/
	" $specfile
	../builder -ncs -5 $specfile
else
	echo "Already up to date"
fi
