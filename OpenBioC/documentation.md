
* Input and Output Worfklow Variables cannot have the same name 

wget http://zzz.bwh.harvard.edu/plink/dist/plink-1.07-x86_64.zip 
unzip plink-1.07-x86_64.zip

cd plink-1.07-x86_64
./plink --noweb --file test


####
cat > runme.sh << THEEND

echo "Welcome to tool HELLO WORLD!"
echo "\$1" > output.txt

THEEND
chmod +x runme.sh 

####

tool variable
exec_path="./runme.sh"

STEP1

#####
${hello__1__2__exec_path} ${input__input_par__hello__null}
output__output_par__hello__null="output.txt"

#####

input_par
output_par

```
angular.element($('#angular_div')).scope().$apply(function () {
	console.log(angular.element($('#angular_div')).scope().tools_info_editable);
});


angular.element($('#angular_div')).scope().$apply(function () {
    console.log(angular.element($('#angular_div')).scope().tool_os_choices);
});

angular.element($('#angular_div')).scope().$apply(function () {
    console.log(angular.element($('#angular_div')).scope().os_choices);
});


angular.element($('#angular_div')).scope().$apply(function () {
	angular.element($('#angular_div')).scope().tool_os_choices = { group: "Debian", name: "Debian 9 (Stretch)", value: "stretch", "$$hashKey": "object:10" };
});


angular.element($('#angular_div')).scope().$apply(function () {
	angular.element($('#angular_div')).scope().tool_os_choices = {"group": "Debian", "name": "Debian 10 (Buster)", "value": "buster"};
});

```




@article{purcell2007plink,
  title={PLINK: a tool set for whole-genome association and population-based linkage analyses},
  author={Purcell, Shaun and Neale, Benjamin and Todd-Brown, Kathe and Thomas, Lori and Ferreira, Manuel AR and Bender, David and Maller, Julian and Sklar, Pamela and De Bakker, Paul IW and Daly, Mark J and others},
  journal={The American journal of human genetics},
  volume={81},
  number={3},
  pages={559--575},
  year={2007},
  publisher={Elsevier}
}

@inproceedings{Mislove2007, address = {New York, New York, USA}, author = {Mislove, Alan and Marcon, Massimiliano and Gummadi, Krishna P. and Druschel, Peter and Bhattacharjee, Bobby}, booktitle = {Proceedings of the 7th ACM SIGCOMM conference on Internet measurement - IMC '07}, doi = {10.1145/1298306.1298311}, file = {:Users/alexandroskanterakis/Library/Application Support/Mendeley Desktop/Downloaded/Mislove et al. - 2007 - Measurement and analysis of online social networks.pdf:pdf}, isbn = {9781595939081}, keywords = {analysis,measurement,social networks}, month = oct, pages = {29}, publisher = {ACM Press}, title = {{Measurement and analysis of online social networks}}, url = {http://dl.acm.org/citation.cfm?id=1298306.1298311}, year = {2007} }

md5 check osx
a=$(find -s HM3/ -type f -exec md5 {} \; | md5)

HapMap
wget https://mathgen.stats.ox.ac.uk/wtccc-software/HM3.tgz
tar zxvf HM3.tgz 


a=$(find -s HM3/ -type f -exec md5 {} \; | md5)
  
if [ "$a" == "35f3dc6a51f47ade371e932ce275cc23" ]; then
    echo "ok"
else
    echo "not ok"
fi

###############################
cat > md5checkdir.sh << ENDOFFILE

echo "Checking md5sum of \$1"
result=\$(find -s \$1 -type f -exec md5 {} \; | md5)
  
if [ "\$result" == "\$2" ]; then
    echo "checksum ok"
    exit 0
else
    echo "checksum check failed"
    exit 1
fi

ENDOFFILE
chmod +x md5checkdir.sh

###########################
if test -f "$FILE"; then
    exit 0
else
    exit 1
fi
########################
wget https://mathgen.stats.ox.ac.uk/wtccc-software/HM3.tgz
tar zxvf HM3.tgz

########################


v="md5checkdir.sh"

command="./$v HM3/ 35f3dc6a51f47ade371e932ce275cc23"
eval $command

if [ $? -eq 0 ] ; then
        exit 0
else
        exit 1
fi
################
```
# Insert the BASH commands for this step

# /hapgen2 -h HM3/CEU.chr6.hap -l HM3/hapmap3.r2.b36.chr6.legend -m HM3/genetic_map_chr6_combined_b36.txt -o chr6 -dl 16199621 1 3 6 -n 100 100 -int 15199621 17199621

${hapgen2__macosx_intel__1__exec} \
 -h ${hapmap2__1__2__install_path}/CEU.chr${input__chromosome__artificialsignal__1}.hap \
 -l ${hapmap2__1__2__install_path}/hapmap3.r2.b36.chr${input__chromosome__artificialsignal__1}.legend \
 -m ${hapmap2__1__2__install_path}/genetic_map_chr${input__chromosome__artificialsignal__1}_combined_b36.txt \
 -o chr${input__chromosome__artificialsignal__1} \
 -dl ${input__location__artificialsignal__1} ${input__odds_ratio_ref_ref__artificialsignal__1} ${input__odds_ratio_ref_alt__artificialsignal__1} ${input__odds_ratio_alt_alt__artificialsignal__1} \
 -n ${input__cases__artificialsignal__1} ${input__controls__artificialsignal__1} \
 -int ${input__location_from__artificialsignal__1} ${input__location_to__artificialsignal__1}
 
output__out__artificialsignal__4=chr${input__chromosome__artificialsignal__1} 
```

```
${hapgen2__macosx_intel__1__exec} \
-h ${hapmap2__1__2__install_path}/CEU.chr${input__chromosome__root__null}.hap \
-l ${hapmap2__1__2__install_path}/hapmap3.r2.b36.chr${input__chromosome__root__null}.legend \
-m ${hapmap2__1__2__install_path}/genetic_map_chr${input__chromosome__root__null}_combined_b36.txt \
-o chr${input__chromosome__root__null} \
-dl ${input__location__root__null} ${input__odds_ratio_ref_ref__root__null} ${input__odds_ratio_alt_ref__root__null} ${input__odds_ratio_alt_alt__root__null} \
-n ${input__cases__root__null} ${input__controls__root__null} \
-int ${input__location_from__root__null} ${input__location_to__root__null}

output__out__root__null=chr${input__chromosome__root__null}

```

##############################
```
wget http://www.well.ox.ac.uk/~gav/resources/snptest_v2.5.2_MacOSX_x86_64.tgz
tar zxvf snptest_v2.5.2_MacOSX_x86_64.tgz 
```

```
./snptest_v2.5.2_MacOSX_x86_64/snptest_v2.5.2 -help
```
```
./snptest_v2.5.2_MacOSX_x86_64/snptest_v2.5.2 -data chr6.cases.gen chr6.cases.sample chr6.controls.gen chr6.controls.sample -frequentist 1 -method score -pheno pheno -o res
```
```
../snptest_v2.5.2_MacOSX_x86_64/snptest_v2.5.2 -data chr6.cases.gen chr6.cases.sample chr6.controls.gen chr6.controls.sample -frequentist 1   -method score -pheno pheno -o res
```

#############################
```


# Insert the BASH commands for this step

input__chromosome__artificialsignal__8=${input__chromosome__root__null}
input__location__artificialsignal__8=${input__location__root__null}
input__location_from__artificialsignal__8=${input__location_from__root__null}
input__location_to__artificialsignal__8=${input__location_to__root__null}
input__cases__artificialsignal__8=${input__cases__root__null}
input__controls__artificialsignal__8=${input__controls__root__null}
input__odds_ratio_ref_ref__artificialsignal__8=${input__odds_ratio_ref_ref__root__null}
input__odds_ratio_alt_ref__artificialsignal__8=${input__odds_ratio_ref_alt__root__null}
input__odds_ratio_alt_alt__artificialsignal__8=${input__odds_ratio_alt_alt__root__null}

step__st1__artificialsignal__8

input__dataset__frequentistadditive__1=${output__out__artificialsignal__8}

step__main__frequentistadditive__3

output__result__root__null=${output__result__frequentistadditive__3}


#############################
```
