#!/bin/sh

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
		echo "$0: Unknown branch: $branch. Supported branches: stable, beta, unstable." >&2
		exit 1
		;;
esac

sourceurl=http://dl.google.com/linux/$product/rpm/stable/$arch

set -e

echo -n "Fetching latest version... "
t=$(mktemp)

# poldek is buggy, see https://bugs.launchpad.net/poldek/+bug/1026762
#poldek -q --st=metadata --source "$sourceurl/" --update
#poldek -q --skip-installed --st=metadata --source "$sourceurl/" --cmd "ls google-chrome-$branch" > $t

repodata=primary-$branch-$(date +%Y%m%d).xml
[ "$cache" = "yes" ] || rm -f "$repodata"
test -e $repodata || {
	wget -c $sourceurl/repodata/primary.xml.gz -O $repodata.gz
	gzip -dc $repodata.gz > $repodata || test -s $repodata
}
perl -ne 'm{<name>google-'$product-$branch'</name>} and m{<version epoch="0" ver="([\d.]+)" rel="(\d+)"/>} and print "$1 $2"' > $t < $repodata

set -- $(sed -re "s,^.+-([^-]+)-([^-]+).$arch$,\1 \2," $t)

ver=$1
rel=$2

# check google-chrome ver only
oldver=$(awk '/^Version:[ \t]+/{print $NF; exit}' $specfile)
oldrel=$(awk '/^Release:[ \t]+/{print $NF; exit}' $specfile)
if [ "$oldrel" = "$rel" -a "$oldver" = "$ver" ]; then
	echo "Already up to date (google-chrome/$ver-$rel)"
	exit 0
fi

# extract flash version
rpm=$name-$branch-$ver-$rel.$arch.rpm
manifest=manifest-$ver.json
test -e $rpm || wget -c $sourceurl/$rpm
test -e $manifest || {
	echo ./opt/google/chrome*/PepperFlash/manifest.json > $t
	rpm2cpio $rpm | cpio -i -E $t --to-stdout > manifest-$ver.json
	if [ ! -s manifest-$ver.json ]; then
		echo "Failed to extract flash version."
		exit 1
	fi
}
flashv=$(awk -F'"' '/version/{print $4}' manifest-$ver.json)

rm -f "$t" "$manifest"

# check google-chrome and flash ver
oldflash=$(awk '/^%define[ 	]+flashv[ 	]+/{print $NF}' $specfile)
if [ "$oldrel" = "$rel" -a "$oldver" = "$ver" -a "$oldflash" = "$flashv" ]; then
	echo "Already up to date (google-chrome/$ver-$rel flash/$flashv)"
	exit 0
fi

echo "Updating $specfile for google-chrome/$oldver-$oldrel -> $ver-$rel, flash/$oldflash -> $flashv"
sed -i -e "
	s/^\(%define[ \t]\+state[ \t]\+\)[a-z]\+\$/\1$branch/
	s/^\(%define[ \t]\+flashv[ \t]\+\)[0-9.]\+\$/\1$flashv/
	s/^\(Version:[ \t]\+\)[.0-9]\+\$/\1$ver/
	s/^\(Release:[ \t]\+\)[.0-9]\+\$/\1$rel/
" $specfile
../builder -ncs -nd -n5 -g $specfile || :
../builder -ncs -nd -5 $specfile
