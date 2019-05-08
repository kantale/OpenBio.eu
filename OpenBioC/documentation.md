
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
tar zxvf https://mathgen.stats.ox.ac.uk/wtccc-software/HM3.tgz

########################





