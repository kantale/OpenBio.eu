
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

window.nodeAnimation('hello__1', 'running')


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

<div class="faster" id="userDataDiv" style="display: none;">
	<ul id="userDataAccordion" class="collapsible expandable popout faster">
	    <!-- --------------------------------------------------------------------------------------- -->
	    <!-- ------------------------------------ General ------------------------------------------ -->
	    <!-- --------------------------------------------------------------------------------------- -->
		<li id="usersDataGeneral">
	        <div class="collapsible-header">
	            <i class="material-icons arrow">keyboard_arrow_right</i>
	            <i class="material-icons">info</i>
	            General
	        </div>
	        <div class="collapsible-body">
	            <form class="col s12">
	                <div class="row">
	                    <div class="input-field col s12 m4 grid-s12-m4-l4">
	                        <input id="generalName" type="text" class="validate">
	                        <label for="generalName">Name</label>
	                    </div>
	                </div>
	            </form>
	        </div>
	    </li>
	</ul>
</div>



<div class="faster" id="QARightPanel" style="display: none;">
    <div class="left-align" style="margin-left: 10px; margin-right: 15px;">
        <ul id="QARightPanelAccordion" class="collapsible expandable popout faster">
            <!-- --------------------------------------------------------------------------------------- -->
            <!-- ------------------------------------ General ------------------------------------------ -->
            <!-- --------------------------------------------------------------------------------------- -->
            <li id="QAGeneral">
                <div class="collapsible-header">
                    <i class="material-icons arrow">keyboard_arrow_right</i>
                    <i class="material-icons">info</i>
                    General
                </div>
                <div class="collapsible-body">
                    <div class="row">
                        <form class="col s12">
                            <div class="input-field">
                                <input id="qwerty" type="text" class="validate">
                            </div>
                        </form>
                    </div>
                </div>
            </li>
        </ul>
    </div>
</div>


<div class="faster" id="referencesRightPanel" style="display: none;">
    <div class="left-align" style="margin-left: 10px; margin-right: 15px;">
        <div ng-show="!references_info_editable">
            <h5>
                <span ng-bind="references_name"></span>
            </h5>
            <small class="form-text text-muted">
                <!-- <span ng-bind="tool_info_username"></span>
                    <span ng-show="!tools_info_editable">, created at <span
                            ng-bind="tool_info_created_at"></span></span>
                    <span ng-show="tools_info_forked_from">, forked from <a href
                            ng-click="tools_search_show_item(tools_info_forked_from)"><span
                                ng-bind="tools_info_forked_from | tool_label"></span></a></span>
                    <span>USED IN 86 WFs</span> -->
                <span ng-bind="references_username"></span>
                <span>, created at <span ng-bind="references_created_at"></span></span>
                <span>USED IN 86 WFs</span>
            </small>
            <div class="card blue-grey darken-1">
                <div class="card-content white-text">
                    <p><span ng-bind-html="references_formatted"></span></p>
                </div>
            </div>
        </div>

workflows_search_name
workflows_search_edit
workflows_search_input_changed()

all_search_2() . VIEWS
workflows_search_2(). VIEWS

    ret = {
        'workflows_search_tools_number' : results.count(),
        'workflows_search_jstree' : workflows_search_jstree,
    }

553

<div class="row" ng-show="!references_info_editable">
    <div class="col s12">
        <div class="row left-align">
            <div class="col s3"><b>Name:</b></div>
            <div class="col s9"><span ng-bind="references_name"></span></div>
        </div>

workflows_search_create_new_pressed()
tools_search_raise_edit_are_you_sure_modal DELETE IT!

TODO: CHANGE WORKFLOW ROOT NODE ID !!!!!

