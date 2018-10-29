#export PATH=/usr/local/anaconda3/bin:$PATH

#!/bin/sh
BASEDIR=$(dirname "$0")
Pwd
cd $BASEDIR
pushd .
if [ -d ./LogFile ] 
then
	cd LogFile
	find . -mtime +7  -delete
	popd
	pushd .
	python getLogFromServer.py
	cd LogFile/`date +%Y%m%d`
	mkdir InLot
	for f in *.zip; do unzip -p "$f" > "${f%.zip}.log"; done
	rm *.zip
	rm \*.log
	popd
	python analysisLog.py
	python analysisInlot.py	
else
    echo "Error: Directory path does not exists."
fi

