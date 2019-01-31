#!/bin/sh

set -e

die() {
	echo >&2 "$0: $*"
	exit 1
}

if [ "$1" = "-k" ]; then
	cache=yes
	shift
else
	cache=no
fi

# product name
product=chrome
# name
name=google-$product
# this package
specfile=$name.spec
# arch to check package. irrelevant for actual arch
arch=x86_64
# branch: stable, beta, unstable. default: stable
branch=${1:-stable}

case "${branch}" in
	stable|beta|unstable)
		;;
	*)
		die "Unknown branch: $branch. Supported branches: stable, beta, unstable."
		;;
esac

sourceurl=https://dl.google.com/linux/$product/rpm/stable/$arch

fetch_version() {
	echo -n "Fetching latest version for $branch... "

	# poldek is buggy, see https://bugs.launchpad.net/poldek/+bug/1026762
	#poldek -q --st=metadata --source "$sourceurl/" --update
	#poldek -q --skip-installed --st=metadata --source "$sourceurl/" --cmd "ls google-chrome-$branch" > $t

	set -- $(
		python3 <<-EOF
			import repomd
			repo = repomd.load('$sourceurl')
			package = repo.find('google-$product-$branch')
			print("{0} {1}".format(package.version, package.release))
		EOF
	)

	ver=$1
	rel=$2
}

if [ -n "$2" ];  then
	ver=$2
	rel=1
else
	fetch_version
fi

if [ -z "$ver" -o -z "$rel" ]; then
	die "Error: xml file is missing data for ${branch} type"
fi

# check google-chrome ver only
oldver=$(awk '/^Version:[ \t]+/{print $NF; exit}' $specfile)
oldrel=$(awk '/^Release:[ \t]+/{print $NF; exit}' $specfile)
if [ "$oldrel" = "$rel" -a "$oldver" = "$ver" ]; then
	echo "Already up to date (google-chrome/$ver-$rel)"
	exit 0
fi

# check google-chrome
if [ "$oldrel" = "$rel" -a "$oldver" = "$ver" ]; then
	echo "Already up to date (google-chrome/$ver-$rel)"
	exit 0
fi

echo "Updating $specfile for google-chrome/$oldver-$oldrel -> $ver-$rel"
sed -i -e "
	s/^\(%define[ \t]\+state[ \t]\+\)[a-z]\+\$/\1$branch/
	s/^\(Version:[ \t]\+\)[.0-9]\+\$/\1$ver/
	s/^\(Release:[ \t]\+\)[.0-9]\+\$/\1$rel/
" $specfile
../builder -ncs -nd -n5 -g $specfile || :
../builder -ncs -nd -5 $specfile
