#!/bin/sh
cd "$(dirname "$0")" # Make sure we are in the current dir
mkdir -p html # Create html folder if necessary
ln -s ../img html/img
for f in ./*.md # For all .md file here, create a html file in the html folder
do
  python -m markdown -x markdown.extensions.tables "$f" > "html/${f%.*}.html"
done
