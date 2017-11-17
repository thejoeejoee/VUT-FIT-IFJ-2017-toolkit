#!/usr/bin/env bash

# pouziti:   is_it_ok.sh xlogin01.zip testdir
#  
#   - POZOR: obsah adresare zadaneho druhym parametrem bude VYMAZAN!
#   - rozbali archiv studenta xlogin01.zip do adresare testdir a overi formalni pozadavky pro odevzdani projektu IFJ
#   - nasledne vyzkousi kompilaci
#   - detaily prubehu jsou logovany do souboru is_it_ok.log v adresari testdir

# Autor: Zbynek Krivka
# Verze: 1.2 (2012-11-23)

LOG="is_it_ok.log"

# implicit task indetifier from config.sh
if [[ $# -ne 2 ]]; then
  echo "ERROR: Missing arguments or too much arguments!"
  echo "Usage: $0  ARCHIVE  TESTDIR"
  echo "       This script checks formal requirements for archive with solution of IFJ project."
  echo "         ARCHIVE - the filename of archive to check"
  echo "         TESTDIR - temporary directory that can be deleted/removed during testing!"
  exit 2
fi

# extrakce archivu
function unpack_archive () {
	local ext=`echo $1 | cut -d . -f 2,3`
  echo -n "Archive extraction: "
  RETCODE=100  
	if [[ "$ext" = "zip" ]]; then
		unzip -o $1 >> $LOG 2>&1
    RETCODE=$?
	elif [[ "$ext" = "gz" || "$ext" = "tgz" || "$ext" = "tar.gz" ]]; then
		tar xfz $1 >> $LOG 2>&1
    RETCODE=$? 
	elif [[ "$ext" = "tbz2" || "$ext" = "tar.bz2" ]]; then
		tar xfj $1 >> $LOG 2>&1
    RETCODE=$?   
	fi
  if [[ $RETCODE -eq 0 ]]; then
    echo "OK"
  elif [[ $RETCODE -eq 100 ]]; then
    echo "ERROR (unsupported extension)"
    exit 1
  else
    echo "ERROR (code $RETCODE)"
    exit 1
  fi
} 

# prevod jmen souboru obsahujicich nepovolene znaky
function to_small () {
	local N=`echo $1 | tr "[:upper:]" "[:lower:]"`
	if [ "$N" != "$1" ]; then
	    mv "$1" "$N" 2>/dev/null
      echo "ERROR ($1 -> $N)"
      exit 1       
	fi
} 

# flattening aktualniho adresare + to_small
function flattening () {
        local FILE=""
        local NFILE=""
	local FILES=`find . -name '*' -type f`
	for FILE in $FILES; do
            NFILE=./${FILE##*/}            
            if [ "$FILE" != "$NFILE" ]; then
              mv "$FILE" ${NFILE} 2>/dev/null
              echo "ERROR ($FILE -> $NFILE)"
              exit 1              
            fi
            F=`basename $FILE`
            if [ "$F" != "Makefile" ]; then
              to_small ${NFILE}
            fi
	done     
  echo "OK"
}

# stare odstraneni DOSovskych radku (nyni mozno pouzit i utilitu dos2unix)
function remove_CR () {
	FILES=`ls $* 2>/dev/null`
	for FILE in $FILES; do
		mv -f "$FILE" "$FILE.tmp"
		tr -d "\015" < "$FILE.tmp" > "$FILE"
		rm -f "$FILE.tmp"
	done
}

#   0) Priprava testdir a overeni serveru
rm -rf $2 2>/dev/null
mkdir $2 2>/dev/null
cp $1 $2 2>/dev/null

echo -n "Testing on Merlin: "
HN=`hostname`
if [[ $HN = "merlin.fit.vutbr.cz" ]]; then
  echo "Yes"
else
  echo "No"
fi


#   1) Extrahovat do testdir
cd $2
touch $LOG
ARCHIVE=`basename $1`
NAME=`echo $ARCHIVE | cut -d . -f 1 | egrep "x[a-z]{5}[0-9][0-9a-z]"`
echo -n "Archive name ($ARCHIVE): "
if [[ -n $NAME ]]; then
  echo "OK"
else
  echo "ERROR (the name does not correspond to a login)"
fi

unpack_archive ${ARCHIVE}

#   2) Normalizace jmen na mala pismena
echo -n "Normalization of filenames: "
flattening

#   3) Dokumentace
echo -n "Searching for dokumentace.pdf: "
if [[ -f "dokumentace.pdf" ]]; then
  echo "OK"
else
  echo "ERROR (not found)"
fi  

#   4) Priprava kompilace
remove_CR *.mak *.c *.cpp *.cc *.h *.c++ *.hpp
chmod 644 *

echo -n "Project compilation: "
#   5) Kompilace
if [[ -f Makefile ]]; then
   ( make ) >> $LOG 2>&1
   RETCODE=$?
   if [[ -z $RETCODE ]]; then
     echo "ERROR (returns code $RETCODE)"
     exit 1
   fi
else
   echo "ERROR (missing Makefile)"
   exit 1 
fi
echo "OK"

#    6) Najdi prelozeny binarni soubor
echo -n "Searching for created binary file: "
EXE=`ls -F | grep "*" | tr -d "*" | grep "" -m 1`   # A naj?t bin?rku...
if [[ -f $EXE ]]; then
  echo "OK ($EXE)"
else
  echo "ERROR (not found)"
  exit 1
fi  

#    7) Kontrola, ze nebyl vytvoren podadresar
echo -n "Searching for new subdirectories: "
DIR_COUNT=`find -type d | grep -v "^\.$" | wc -l`
if [[ $DIR_COUNT -eq 0 ]]; then
  echo "OK (None)"
else
  echo "ERROR (found $DIR_COUNT subdirectory/ies)"
  exit 1
fi

#    8) Kontrola rozdeleni
echo -n "Presence of file rozdeleni: "
IFS="$IFS:"
if [[ -f rozdeleni ]]; then

  # zpracovani souboru rozdeleni
  unset LOGINS
  unset PERCENTS
  unset ARCHNAME
  declare -a LOGINS
  {
    i=0
    while read -a RADEK; do
      if [[ "${RADEK[0]}" != "" ]]; then
    		LOGINS[$i]=${RADEK[0]}
    		PERCENTS[$i]=`echo ${RADEK[1]} | tr -cd [:digit:]`
    		((TMP_PROC+=${PERCENTS[$i]:-0}))
    		((i++))
        if [[ "$NAME" = "${RADEK[0]}" ]]; then
          ARCHNAME=$NAME
        fi
      else
        echo "ERROR (empty line occured)"
        exit 1
      fi
    done
  } < rozdeleni
  
  # kontrola formatu rozdeleni a souctu procent
  if [[ -n $RADEK ]]; then
    echo "ERROR (the last line is not ended properly)"
  elif [[ $TMP_PROC -ne 100 ]]; then
    echo "ERROR (sum != 100%)"
  elif [[ -z $ARCHNAME ]]; then
    echo "ERROR (rozdeleni does not contain the leader's login $NAME)"
  else
    echo "OK"
  fi

else
  echo "ERROR (file not found)" 
fi

#   9) Kontrola rozsireni
echo -n "Presence of file rozsireni (optional): "
if [[ -f rozsireni ]]; then
  echo "Yes"
else
  echo "No"
fi 


        
