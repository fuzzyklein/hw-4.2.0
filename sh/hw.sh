#! /bin/bash

export program_name=${0##*/} ## Get the name of the script without its path
export program_path=$0
printf "Running %s.\n" $program_name

printf "Enter your name: "
read name

printf -v output_string "Hello, $name!\n"
export output_string
printf "$output_string"

accept=f:vhdi:o:e:V

printf "Command Line Arguments:\n\n"
printf "%s\n" "$@"

while getopts $accept option
do
  case $option in
    f) export filename=$OPTARG ;;
    v) export verbose=1 ;;
    h) export help=1 ;;
    d) export debug=1 ;;
    i) export input=$OPTARG ;;
    o) export output=$OPTARG ;;
    e) export errors=$OPTARG ;;
    V) export version=1 ;;
    *) ;;
  esac
done

shift "$(( $OPTIND - 1 ))"

# perl perl/hw.pl
