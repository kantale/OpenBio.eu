
### Resources
* https://devhints.io/bash

### Caveats

* Difference between single and double quotes  
```bash
VAR="hello"
echo "$VAR"
```

```bash
V="hello"
echo '$VAR'
```

* Avoid grave-accent:
```bash
echo "I am: `whoami`"
echo "I am: $(whoami)"

current_month=`date +%m`
current_month=$(date +%m) # Better 
```

* ALWAYS WRAP BASH VARIABLES WITH CURLY BRACKETS ```{}```

```bash
OLD_FILENAME="file"
NEW_FILENAME=$OLD_FILENAME_NEW
echo "$NEW_FILENAME"
```

```bash
OLD_FILENAME="file"
NEW_FILENAME=${OLD_FILENAME}_NEW
echo "$NEW_FILENAME"
```

```bash
OLD_FILENAME="file"
NEW_FILENAME=${OLD_FILENAME}_NEW
echo "${NEW_FILENAME}"
```

* Use "" for multi-line variables 
```bash
A=$(cal)
echo $A
```

```bash
A=$(cal)
echo "$A"
```

```bash
A="this
is a multi-line
string
"

echo $A

ehoc "${A}"
```

* Get the output exit code of command

```bash
cal
echo "${?}"
```

```bash
cal
echo "${?}"
```

```bash
cal hello
echo "${?}"
```

* Create chain of commands. One runs if the previous runs 
```bash
touch test_file && cat test_file && echo "ok" 
```

```bash
touch test_file && cat test_file_2 && echo "ok" 
```

Hint: $? Still returns the exit code of the last command

```bash
ls
if [[ $? == 0 ]] ; then
  echo "ok"
fi
```

* Use parenthesis to run in a different shell

```bash
(mkdir -p test && cd test)
pwd
```

```bash
mkdir -p test && cd test
pwd
```

* 0 is True !  (man test to confirm)
```bash
true ; echo $?
false ; echo $? 

* Comparing strings / nuberss
[ "HELLO" = "HELL0" ] ; echo $?
[ "HELLO" = "HELLO" ] ; echo $?
[ "HELLO" != "HELL0" ] ; echo $?

[ "2" > "250" ];  echo $?    ## ALWAYS STRING COMPARISON
[ "2" -gt "250" ];  echo $?  ## Explicit declare numeric values
[[ "2" > "250" ]];  echo $?

[[ "2" < "250" ]];  echo $?  ## STRING COMPARISON !!
[[ "5" < "250" ]];  echo $?  ## STRING COMPARISON !!!

[ "2" -gt "250" ];  echo $?
[ -z "" ];  echo $?
[ -z "Hello" ];  echo $?

[ "" = "" ] ; echo $?


```

* NEVER - EVER use single ```[]``` in if. ```[]``` is an alias to test command! (man test)
```bash
[ "a" > "b" ];  echo $?  # "a" comes AFTER "b"  ???? 
[ "a" \> "b" ];  echo $? # ok-ish
[[ "a" > "b" ]];  echo $?  # OK

a=""
[ $a = "" ] ; echo $?  #OOPS 
[[ $a = "" ]];  echo $?   # OK !

[ "45.2" -gt "45.1" ]; echo $? # OOPS
[[ "45.2" > "45.1" ]]; echo $? # OK
```

* Semantics of ```export```
* Functions 
```bash
func () {
	local X=1
	echo ${Y}
	Z=1
	return 3
}

Y=2
func
echo $?
echo ${Z}

```

* Common patterns
```bash
for i in * ; do echo ${i}; done
for i in aa bb cc ; do echo ${i}; done

# CREATE A FILE
A=3
cat > foo1 << EOF 

this is file ${A}

EOF

A=3
cat > foo2 << 'EOF' 

this is file ${A}

EOF

```

1. Use [shellcheck](https://www.shellcheck.net/).
2. Try not to use sudo, or any other way of accessing root. Assume the user does not have the privileges. 
3. At the beginning check if tool is already installed / downloaded
4. When downloading with wget, curl always check the md5 checksum. 
