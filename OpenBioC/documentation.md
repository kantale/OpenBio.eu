
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

$scope.tools_search_input_changed(); //Update search results


