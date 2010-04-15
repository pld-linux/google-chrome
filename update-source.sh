#!/bin/sh
set -e

echo -n "Fetching latest version... "
t=$(mktemp)
curl --silent http://dl.google.com/linux/direct/google-chrome-beta_current_x86_64.rpm -o $t
ver=$(rpm -qp --nodigest --nosignature --qf '%{V}' $t)
rev=$(rpm -qp --nodigest --nosignature --qf '%{R}' $t)
rm -f $t
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
