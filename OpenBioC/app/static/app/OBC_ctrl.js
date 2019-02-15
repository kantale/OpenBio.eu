
/*
inner_: functions / variables not connected with the UI
show_ : shows / hide divs
_error_message : Error messages
_pressed : Something was clicked 
*/

/*
angular.module('OBC_app').filter('ifEmpty', function() {
    return function(input, defaultValue) {
        if (angular.isUndefined(input) || input === null || input === '') {
            return defaultValue;
        }

        return input;
    }
});
*/

/*
* https://stackoverflow.com/a/30471421/5626738
*/
angular.module('OBC_app').filter('ifNull', function() {
    return function(input, defaultValue) {
        if (input === null) {
            return defaultValue;
        }

        return input;
    }
});

angular.module('OBC_app').filter('tool_label', function() {
    return function(tool) {
        if (tool === null) {
            return '';
        }

        return tool.name + '/' + tool.version +'/' + tool.edit;
    }
});


app.controller("OBC_ctrl", function($scope, $http, $filter, $timeout, $log) {
    /*
    * ok some things that are here perhaps could be placed elsewhere.. 
    * https://docs.angularjs.org/api/ng/directive/ngInit
    */
    $scope.init = function() {
        $scope.username = window.username; // Empty username means non-authenticated user.
        $scope.general_success_message = window.general_success_message;
        $scope.general_alert_message = window.general_alert_message;
        $scope.password_reset_token = window.password_reset_token;
        $scope.inner_hide_all_navbar();
        $scope.inner_hide_all_error_messages();
        
        $scope.tools_search_tools_number = null; // Number of tools found on search
        //$scope.tools_search_create_disabled = true; // Navbar --> Tools/Data --> Search navbar --> Create New disabled

        $scope.tools_name_regexp = /^\w+$/ ;
        $scope.tools_version_regexp = /^[\w\.]+$/ ;
        $scope.tools_edit_regexp = /^\d+$/; 
        $scope.tools_search_warning= "";
        $scope.workflows_search_warning = "";
        $scope.tools_info_editable = false; // Can we edit tools_info ?
        $scope.tools_info_forked_from = null; //From which tool is this tool forked from?
        $scope.tool_changes = ''; // Changes from forked
        $scope.tool_installation_init = '# Insert the BASH commands that install this tool\n# The following tools are available:\n#  apt-get, wget\n\n';
        $scope.tool_validation_init = '# Insert the BASH commands that confirm that this tool is correctly installed\n# In success, this script should return 0 exit code.\n# A non-zero exit code, means failure to validate installation.\n\nexit 1\n';
        $scope.tool_info_validation_message = '';

        $scope.tool_variables = [{name: '', value: '', description: ''}];
        $scope.tools_var_jstree_id_show = true;

        $scope.workflows_info_editable = false;

        $scope.get_init_data();


    };

    //TODO. BETTER NAME?
    $scope.itemArray = [
        {id: 1, name: 'Tools and Data'},
        {id: 2, name: 'Workflows'}
    ];

    $scope.selected = { value: $scope.itemArray[0] };

    /*
    * Helper function that perform ajax calls
    * success_view: what to do if data were correct and call was successful
    * fail_view: What to do if call was succesful but data where incorrect
    * fail_ajax: what to do if ajax call was incorrect / System error
    */
    $scope.ajax = function(url, data, success_view, fail_view, fail_ajax) {
        // URL should always end with '/'

        console.log('Before Ajax, data:');
        console.log(data);

        data.csrftoken = CSRF_TOKEN;

        $http({
            headers: {
                "Content-Type": 'application/json',
                "Access-Control-Allow-Origin": "*", // TODO : REMOVE THIS!
                //"X-CSRFToken" : getCookie('csrftoken'),
                "X-CSRFToken" : window.CSRF_TOKEN,
            },
            method : "POST",
            url : url,
            data : data
        }).then(function mySucces(response) {
            // $scope.myWelcome = response.data;
            // alert(JSON.stringify(response));
            if (response['data']['success']) {
                console.log('AJAX SUCCESS:');
                console.log(response['data']['success']);
                success_view(response['data']);
            }
            else {
                console.log('AJAX ERROR:');
                fail_view(response['data']);
            }
            
        }, function myError(response) {
            console.log('AJAX SYSTEM ERROR:');
            console.log(response.statusText);
            if (response.statusText) {
                fail_ajax(response.statusText);
            }
            else {
                fail_ajax('Internal Error. Server not responding');
            }
        });
    };

    /*
    * Hide everything 
    */
    $scope.inner_hide_all_navbar = function() {
    	$scope.show_login = false;
        $scope.show_signup = false;
        $scope.show_reset_password_email = false;
        $scope.show_password_reset = $scope.password_reset_token ? true : false;
        $scope.show_user_profile = false;
        $scope.show_tools = false;
        $scope.show_tools_info = false;
        $scope.show_workflows_info = false;

        $scope.show_workflows = false;
    };

    /*
    * Hide all error messages
    */
    $scope.inner_hide_all_error_messages = function() {
        $scope.signup_error_message = '';
        $scope.login_error_message = '';
        $scope.reset_password_email_error_message = '';
        $scope.user_profile_error_message = '';
        $scope.user_profile_success_message = '';
        $scope.tools_info_error_message = '';
        //$scope.workflows_info_error_message = '';
        $scope.tools_info_success_message = '';
    };

    /*
    * Hide all error messages including general success and alert messages
    */
    $scope.inner_hide_all_error_and_general_messages = function() {
        $scope.inner_hide_all_error_messages();
        $scope.show_password_reset = false;
        $scope.general_success_message = '';
        $scope.general_alert_message = '';
    };

    /*
    * navbar --> Login --> Pressed
    */
    $scope.navbar_login_pressed = function() {
    	$scope.inner_hide_all_navbar();
        $scope.inner_hide_all_error_and_general_messages();
    	
    	$scope.show_login = true;
    };

    /*
    * Navbar --> Signup --> pressed 
    */
    $scope.navbar_signup_pressed = function() {
    	// $scope.inner_hide_all_navbar(); // FROM OLD UI. NOT RELEVANT IN M
        //$scope.inner_hide_all_error_and_general_messages(); // FROM OLD UI. NOT RELEVANT IN M

        //$scope.show_signup = true; // FROM OLD UI. NOT RELEVANT IN M

        $scope.signup_error_message = '';
        $scope.login_error_message = '';
        //$("#signModal").modal('open');
        M.Modal.getInstance($("#signModal")).open();
    };

    /*
    * Navbar --> Signup --> Signup (button) --> Pressed
    */
    $scope.signup_signup_pressed = function() {

        $scope.ajax(
            'register/',
            {
                'signup_username' : $scope.signup_username,
                'signup_password' : $scope.signup_password,
                'signup_confirm_password': $scope.signup_confirm_password,
                'signup_email' : $scope.signup_email
            },
            function (data) {
                $scope.signup_error_message = '';
                $scope.show_signup = false;
                $scope.general_success_message = 'Thank you for registering to openbio.eu . A validation link has been sent to ' + $scope.signup_email;
                $scope.general_alert_message = '';

                // Sign up modal close + Sign in modal close.
                $("#signModal").modal('close');
            },
            function (data) {
                $scope.signup_error_message = data['error_message'];
                $scope.general_success_message = '';
            },
            function(statusText) {
                $scope.signup_error_message = statusText;
                $scope.general_success_message = '';
            }
        );

    };

    /*
    * Navbar --> login --> login (button) --> Pressed 
    */
    $scope.login_login_pressed = function() {
        $scope.ajax(
            'login/',
            {
                "login_username": $scope.login_username,
                "login_password": $scope.login_password,
            },
            function(data) {
                $scope.login_error_message = '';
                window.CSRF_TOKEN = data['csrf_token'];
                $scope.username = data['username'];
                $scope.show_login = false;

                //Close modal sign in 
                $("#signModal").modal('close');
            },
            function(data) {
                $scope.login_error_message = data['error_message'];
            },
            function(statusText) {
                $scope.login_error_message = statusText;
            }
        );
    };

    /*
    * Navbar -> username (pressed) -> "Update my profile" button pressed
    */
    $scope.user_profile_update_pressed = function() {
        $scope.ajax(
            'user_data_set/',
            {
                'user_first_name': $scope.user_first_name,
                'user_last_name': $scope.user_last_name,
                'user_email': $scope.user_email,
                'user_website': $scope.user_website,
                'user_public_info': $scope.user_public_info
            },
            function(data) {
                $scope.user_profile_success_message = 'User\'s profile updated';
            },
            function(data) {
                $scope.user_profile_error_message = data['error_message'];
            },
            function(statusText) {
                $scope.user_profile_error_message = statusText;
            }
        );
    };

    /*
    * Fetch user data
    */
    $scope.inner_fetch_user_data = function() {
        $scope.ajax(
            'user_data_get/',
            { // This is empty deliberately. Get the user data of the logged in user.
            },
            function(data) {
                $scope.user_first_name = $filter('ifNull')(data['user_first_name'], '');
                $scope.user_last_name = $filter('ifNull')(data['user_last_name'], '');
                $scope.user_email = data['user_email'];
                $scope.user_website = $filter('ifNull')(data['user_website'], '');
                $scope.user_public_info = $filter('ifNull')(data['user_public_info'], '');
            },
            function(data) {
                $scope.user_profile_error_message = data['error_message']; // Never executed
            },
            function(statusText) {
                $scope.user_profile_error_message = statusText;
            }
        );
    };

    /*
    * Navbar (after login) --> username --> pressed
    */
    $scope.navbar_username_pressed = function() {
        $scope.inner_hide_all_navbar();
        $scope.show_user_profile = true;
        $scope.user_profile_success_message = '';
        $scope.inner_fetch_user_data();
    };


    /*
    * Navbar -> Login -> password reset -> clicked
    */
    $scope.login_password_reset_pressed = function() {
        $scope.inner_hide_all_navbar();
        $scope.show_reset_password_email = true;
    };

    /*
    * Navbar --> Login -> password reset -> clicked -> Send -> clicked
    */
    $scope.login_password_reset_email_send_pressed = function() {
        // reset_password_email 
        $scope.ajax(
            'reset_password_email/',
            {
                'reset_password_email': $scope.reset_password_email
            },
            function(data) {
                $scope.show_reset_password_email = false;
                $scope.general_success_message = 'An email with instructions to reset your password was sent to ' + $scope.reset_password_email;
            },
            function(data) {
                $scope.reset_password_email_error_message = data['error_message'];
            },
            function(statusText) {
                $scope.reset_password_email_error_message = statusText;
            }
        );
    }

    /*
    * password reset --> Change (button) --> pressed
    */
    $scope.password_reset_change_pressed = function() {
        $scope.ajax(
            'password_reset/',
            {
                'password_reset_password': $scope.password_reset_password,
                'password_reset_confirm_password': $scope.password_reset_confirm_password,
                'password_reset_token': $scope.password_reset_token
            },
            function(data) {
                $scope.password_reset_token = '';
                $scope.show_password_reset = false;
                $scope.general_success_message = 'Your password has been reset';
            },
            function(data) {
                $scope.password_reset_error_message = data['error_message'];
            },
            function(statusText) {
                $scope.password_reset_error_message = statusText;
            }
        );
    };

    /// TOOLS 

    /*
    * Runs from init() at startup
    * Fetch init data from server. 
    */
    $scope.get_init_data = function() {
        $scope.inner_hide_all_navbar();
        $scope.show_tools = true;
        $scope.tools_search_1();
    };

    /*
    *   Get the number of all tools
    */
    $scope.tools_search_1 = function() {
        $scope.ajax(
            'tools_search_1/',
            {},
            function(data) {
                $scope.tools_search_tools_number = data['tools_search_tools_number'];
                $scope.workflows_search_tools_number = data['workflows_search_tools_number']; // TODO CHANGE NAMES
            },
            function(data) {

            },
            function(statusText) {

            }
        );
    };


    /*
    *  Search tools after search items changed
    */
    $scope.tools_search_2 = function() {
        $scope.ajax(
            'tools_search_2/',
            {
                'tools_search_name': $scope.tools_search_name,
                'tools_search_version': $scope.tools_search_version,
                'tools_search_edit': $scope.tools_search_edit
            },
            function(data) {
                $scope.tools_search_tools_number = data['tools_search_tools_number'];
                angular.copy(data['tools_search_jstree'], $scope.tools_search_jstree_model);

            },
            function(data) {

            },
            function(statusText) {

            }
        );
    };

    /*
    *  Search workflows after search items changed
    */
    $scope.workflows_search_2 = function() {
        $scope.ajax(
            'workflows_search_2/',
            {
                'workflows_search_name': $scope.workflows_search_name,
                'workflows_search_edit': $scope.workflows_search_edit
            },
            function(data) {
                $scope.workflows_search_tools_number = data['workflows_search_tools_number'];
                //angular.copy(data['tools_search_jstree'], $scope.tools_search_jstree_model);  // UNCOMMENT ME !!!!!

            },
            function(data) {

            },
            function(statusText) {

            }
        );
    };


    /*
    * Search SPECIFIC tool. Update UI
    */ 
    $scope.tools_search_3 = function(item) {
        $scope.ajax(
            'tools_search_3/',
            {
                "tool_name": item.name,
                "tool_version": item.version,
                "tool_edit": item.edit
            },
            function (data) {
                $scope.tool_info_username = data['username'];
                $scope.tool_website = data['website'];
                $scope.tool_description = data['description'];
                $scope.tool_changes = data['changes'];
                $scope.tool_info_created_at = data['created_at'];
                $scope.tools_info_forked_from = data['forked_from'];
                $scope.tools_info_name = item.name;
                $scope.tools_info_version = item.version;
                $scope.tools_info_edit = item.edit;
                $scope.tools_info_success_message = '';
                $scope.tools_info_error_message = '';

                angular.copy(data['dependencies_jstree'], $scope.tools_dep_jstree_model);
                angular.copy(data['variables_js_tree'], $scope.tools_var_jstree_model);

                $scope.tool_variables = data['variables'];

                tool_installation_editor.setValue(data['installation_commands'], -1);
                tool_validation_editor.setValue(data['validation_commands'], -1);
                tool_installation_editor.setReadOnly(true);
                tool_validation_editor.setReadOnly(true);
                $scope.tools_var_jstree_id_show = true; // Show variable/dependency tree
            },
            function (data) {

            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
            }
        );
    };

    /*
    *   navbar --> Tools --> Search sidebar --> Name or Version or Name Change
    */
    $scope.tools_search_input_changed = function() {

//        if ((!$scope.tools_search_name) && (!$scope.tools_search_version) && (!$scope.tools_search_edit)) {
//            $scope.tools_search_warning = '';
//            return;
//        }

        //if (!$scope.username) {
        //    $scope.tools_search_warning = 'Login to create new tools';
        //    return;
        //}

        //Check tool name
        if ($scope.tools_search_name) {
            if (!$scope.tools_name_regexp.test($scope.tools_search_name)) {
                $scope.tools_search_warning = 'Invalid Tool name';
                return;
            }
        }

        //Check tool version
        if ($scope.tools_search_version) {
            if (!$scope.tools_version_regexp.test($scope.tools_search_version)) {
                $scope.tools_search_warning = 'Invalid Version value';
                return;
            }
        }


        //Check edit version
        //if (!$scope.tools_edit_regexp.test($scope.tools_search_edit)) {
        //    $scope.tools_search_warning = 'Invalid Edit value';
        //    return;
        //};

        //Check edit version
        if ($scope.tools_search_edit) {
            if (!$scope.tools_edit_regexp.test($scope.tools_search_edit)) {
                $scope.tools_search_warning = 'Invalid Edit value';
                return;
            }
            $scope.tools_search_warning = 'Edit value should be empty to create new tools';
            $scope.tools_search_2();
            return; 
        }

        //Everything seems to be ok
        $scope.tools_search_warning = '';
        $scope.tools_search_2();
    };

    /*
    *   navbar --> Tools --> Search sidebar --> Combobox Workflows --> Name or Version or Name Change
    */
    $scope.workflows_search_input_changed = function() {
        //Check workflow name
        if ($scope.workflows_search_name) {
            if (!$scope.tools_name_regexp.test($scope.workflows_search_name)) {
                $scope.workflows_search_warning = 'Invalid Workflow name';
                return;
            }
        }

        //Check edit value
        if ($scope.workflows_search_edit) {
            if (!$scope.tools_edit_regexp.test($scope.workflows_search_edit)) {
                $scope.workflows_search_warning = 'Invalid Edit value';
                return;
            }
            $scope.workflows_search_warning = 'Edit value should be empty to create new Workflows';
            $scope.workflows_search_2(); // UNCOMMENT ME!!!!!!!!
            return; 
        }


        //Everything seems to be ok
        $scope.workflows_search_warning = '';
        $scope.workflows_search_2();


    };

    /*
    * Navbar -> Tools/Data --> Appropriate input --> "Create New" button --> Pressed
    */
    $scope.tools_search_create_new_pressed = function() {

        if (!$scope.username) {
            //$scope.tools_info_error_message = 'Login to create new tools';
            $scope.tools_search_warning = 'Login to create new tools';
            return;
        }

        //Check if tool search name and version are non empty 
        if (!($scope.tools_search_name && $scope.tools_search_version)) {
            $scope.tools_search_warning = 'Name and Version should not be empty';
            return;
        }

        //Edit SHOULD BE EMPTY!
        if ($scope.tools_search_edit) {
            $scope.tools_search_warning = 'An edit number will be assigned after you save your tool (leave it empty)';
            return;
        }


        $scope.tools_search_warning = '';

    
        window.createToolDataBtn_click();


        $scope.show_tools_info = true;
        //$scope.show_workflows_info = false; // TODO. THIS SHOULDN'T BE HERE

        $scope.tools_info_editable = true;
        $scope.tools_info_forked_from = null;
        $scope.tools_info_name = $scope.tools_search_name;
        $scope.tools_info_version = $scope.tools_search_version;
        $scope.tools_info_success_message = '';
        $scope.tools_info_error_message = '';
        $scope.tool_info_username = $scope.username;
        $scope.tool_website = '';
        $scope.tool_description = '';
        $scope.tool_changes = '';

        //Empty dependencies JSTREE 
        angular.copy([], $scope.tools_dep_jstree_model);

        //Empty variables JSTREE
        angular.copy([], $scope.tools_var_jstree_model);

        //Empty variables
        $scope.tool_variables = [{name: '', value: '', description: ''}];

        tool_installation_editor.setValue($scope.tool_installation_init, -1);
        tool_installation_editor.setReadOnly(false);
        tool_validation_editor.setValue($scope.tool_validation_init, -1);
        tool_validation_editor.setReadOnly(false);

        $scope.tools_var_jstree_id_show = true; // Show variable/dependency tree

    };

    /*
    * Navbar -> Tools/Data --> Search ComboBox Workflows --> Appropriate input --> "Create New" button --> Pressed
    */
    $scope.workflows_search_create_new_pressed = function() {
        if (!$scope.username) {
            $scope.workflows_search_warning = 'Login to create new Workflows';
            return;
        }

        //Check if worfklows search name are empty 
        if (!$scope.workflows_search_name) {
            $scope.workflows_search_warning = 'Name should not be empty';
            return;
        }

        //Edit SHOULD BE EMPTY!
        if ($scope.workflows_search_edit) {
            $scope.worfflows_search_warning = 'An edit number will be assigned after you save your workflow (leave it empty)';
            return;
        }



        //$scope.show_tools_info = false;
        //$scope.show_workflows_info = true;

        //Close tool accordion
        window.cancelToolDataBtn_click();

        //Open Workflows accordion
        window.createWorkflowBtn_click();

        $scope.workflows_info_name = $scope.workflows_search_name;
        $scope.workflows_info_username = $scope.username;
        $scope.workflows_info_editable = true;

        //$scope.workflows_info_error_message = '';


    };

    /*
    * Navbar --> Tools/data --> Appropriate input --> "Create New" button --> Pressed --> Filled input --> Save (button) --> Pressed
    */
    $scope.tool_create_save_pressed = function() {

        //Get the dependencies
        var tool_dependencies = [];
        for (var i=0; i<$scope.tools_dep_jstree_model.length; i++) {
            //Add only the roots of the tree
            if ($scope.tools_dep_jstree_model[i].parent === '#') {
                tool_dependencies.push($scope.tools_dep_jstree_model[i].data);
            }
        }

        $scope.ajax(
            'tools_add/',
            {
                'tools_search_name': $scope.tools_info_name,
                'tools_search_version': $scope.tools_info_version,
                'tool_website': $scope.tool_website,
                'tool_description': $scope.tool_description,
                'tool_forked_from': $scope.tools_info_forked_from,
                'tool_changes': $scope.tool_changes,

                'tool_dependencies': tool_dependencies,

                'tool_variables': $scope.tool_variables,

                'tool_installation_commands': tool_installation_editor.getValue(),
                'tool_validation_commands': tool_validation_editor.getValue()

            },
            function(data) {
                $scope.tools_info_success_message = 'Tool/Data successfully saved';
                generateToast($scope.tools_info_success_message, 'green lighten-2 black-text', 'stay on');
                $scope.tools_info_editable = false;
                $scope.tool_info_created_at = data['created_at'];
                $scope.tools_info_edit = data['edit'];
                $scope.tools_search_input_changed(); //Update search results
            },
            function(data) {
                $scope.tools_info_error_message = data['error_message'];
            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
            }
        );
    };

    /*
    * Navbar --> tools/data --> Appropriate Input --> List Item --> clicked
    */
    $scope.tools_search_show_item = function(item) {
        $scope.show_tools_info = true;
        $scope.show_workflows_info = false;
        $scope.tools_info_editable = false;
        $scope.tools_search_3(item);
        M.updateTextFields(); // The text inputs in Materialize needs to be updated after change.
    };

    /*
    * Navbar --> tools/data --> Appropriated Input (search) --> List Item --> clicked --> Fork --> pressed
    */
    $scope.tool_info_fork_pressed = function() {

        if (!$scope.username) {
            $scope.tools_info_error_message = 'Login to create new tools';
            return;
        }

        $scope.tools_info_editable = true;
        $scope.tools_info_error_message = '';
        $scope.tools_info_success_message = "Tool successfully forked. Press Save after completing your edits";
        generateToast($scope.tools_info_success_message, 'green lighten-2 black-text', 'stay on'); 

        $scope.tools_info_forked_from = {
            'name': $scope.tools_info_name, 
            'version': $scope.tools_info_version, 
            'edit' :$scope.tools_info_edit
        }
        $scope.tool_changes = '';


        //If the parent tool does not have variables, add empty:
        if ($scope.tool_variables.length == 0) {
            $scope.tool_variables = [{name: '', value: '', description: ''}];
        }

        tool_installation_editor.setReadOnly(false);
        tool_validation_editor.setReadOnly(false);
        $scope.tools_var_jstree_id_show = true; // Show variable/dependency tree
    };

    /*
    * Navbar --> tools/data --> Aprioprate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> Validate (pressed)
    */
    $scope.tool_info_validate_pressed = function() {
        $scope.tool_info_validation_message = 'Not yet implemented';
    };

    /*
    * Navbar --> tools/data --> Aprioprate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "-" (variables) (pressed)
    */
    $scope.tools_info_remove_variable = function(index) {
        $('.tooltipped').tooltip('close');
        $scope.tool_variables.splice(index, 1);
    };

    /*
    * Navbar --> tools/data --> Appropriate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "+" (variables) (pressed)
    */
    $scope.tools_info_add_variable = function() {
        $('.tooltipped').tooltip('close');
        $scope.tool_variables.push({name:'', value: '', description: ''});  
    };

    /*
    * Navbar --> tools/data --> Appropriate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> Show variables href link (clicked)
    */
    $scope.tools_var_jstree_id_show_clicked = function() {
        $scope.tools_var_jstree_id_show = !$scope.tools_var_jstree_id_show;
    };
    ////// JSTREES ////////

    /*
    * Remove a parent node from a jstree. Recursive
    * This acts on the model. Not on the jstree itself 
    * tests: 
    * t = [{id: 1, parent:'#'}, {id: 2, parent:'#'}, {id: 3, parent:'#'}]
    * n = {id:1, parent:'#'}
    *
    * t = [{id: 1, parent:'#'}, {id: 2, parent:'#'}, {id: 3, parent:2}]
    * n = {id:3, parent:2}     n = {id:2, parent:'#'}
    *
    * t = [{id: 1, parent:'#'}, {id: 2, parent:1}, {id: 3, parent:1}]
    * n =  {id:3, parent:1}    n = {id: 1, parent:'#'}
    */ 
    $scope.delete_parent_node_from_jstree = function(tree, node) {

        //Remove all children
        while (true) {
            var has_children = false;
            var this_index = -1;
            var child_index = -1;
            for (var i=0; i<tree.length; i++) {
                if (tree[i].parent == node.id) {
                    has_children = true;
                    child_index = i;
                }
                if (tree[i].id == node.id) {
                    this_index = i;
                }
            }

            if (has_children) {
                $scope.delete_parent_node_from_jstree(tree, tree[child_index]);
                //a(tree, tree[child_index]); # For testing. Create a function a: a = ...
            }
            else {
                //This node does not have children
                //Delete this node
                if (this_index == -1) {
                    console.log('This should never happen')
                }
                //Delete the node
                tree.splice(this_index, 1);
                break;
            }
        }
    };

    /*
    * Get the dependencies of this tool
    * This is called from OBC.js
    * what_to_do == 1: DRAG FROM SEARCH TREE TO DEPENDENCY TREE
    * what_to_do == 2: DRAG FROM SWARCH TREE TO WORKFLOW DIV
    */
    $scope.tool_get_dependencies = function(tool, what_to_do) {

        if (what_to_do == 1 && (!$scope.tools_info_editable)) {
            return;
        }

        $scope.ajax(
            'tool_get_dependencies/',
            {
                'tool_name': tool.name,
                'tool_version': tool.version,
                'tool_edit': tool.edit
            },
            function(data) {

                if (what_to_do == 1) { // DRAG FROM SEARCH TREE TO DEPENDENCY TREE
                    $scope.tools_info_error_message = '';

                    //Is this action valid?
                    //Find the parent
                    var inserted_parent_id = '';
                    for (var i=0; i<data['dependencies_jstree'].length; i++) {
                        if (data['dependencies_jstree'][i].parent == '#') {
                            //This is the parent
                            inserted_parent_id = data['dependencies_jstree'][i].id;
                            break;
                        }
                    }

                    //Check if this parent is already in the tree
                    for (var i=0; i<$scope.tools_dep_jstree_model.length; i++) {
                        if ($scope.tools_dep_jstree_model[i].id == inserted_parent_id) {
                            $scope.tools_info_error_message = 'This tool is already in the dependency tree';
                            return;
                        }
                    }

                    //We suppose there is no error
                    $scope.tools_info_error_message = '';

                    //Add all dependencies to the Dependencies jSTREE
                    for (var i=0; i<data['dependencies_jstree'].length; i++) {
                        $scope.tools_dep_jstree_model.push(data['dependencies_jstree'][i]);
                    }

                    //Add all dependencies to the Dependencies + Variables JSTREE
                    for (var i=0; i<data['variables_jstree'].length; i++) {
                        $scope.tools_var_jstree_model.push(data['variables_jstree'][i]);
                    }
                }
                else if (what_to_do == 2) { //DRAG FROM SEARCH TREE TO WORKFLOW DIV
                    window.buildTree(data['dependencies_jstree'])
                }
            },
            function(data) {

            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
            }
        );
    };

    //JSTREE tools_search
    $scope.tools_search_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                check_callback : function(operation, node, node_parent, node_position, more) { //https://stackoverflow.com/a/23486435/5626738

                    console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true
            },
//            types : {
//                default : {
//                    icon : 'fa fa-flash'
//                },
//                star : {
//                    icon : 'fa fa-star'
//                },
//                cloud : {
//                    icon : 'fa fa-cloud'
//                }
//            },
            version : 1,
            plugins : ['dnd', 'types'],
                        types : {
                default : {
                    icon : 'fa fa-cog'
                }
            },
            dnd: {
                is_draggable : function(node) {
                    return true;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []
        };

    /*
    * Should the changes on the model be reflected on the tree? 
    */
    $scope.tools_search_jstree_config_apply = function() {
        return true;
    };

    $scope.tools_search_jstree_model_init = [];

    $scope.tools_search_jstree_model = [];
    angular.copy($scope.tools_search_jstree_model_init, $scope.tools_search_jstree_model);


    /* 
    * Raise a modal "all your edits will be list. Are you aure?". Raised when:
    * 1. Click an item in the jstree tools
    * 2. Click Cancel in Tool Search
    */
    $scope.tools_search_raise_edit_are_you_sure_modal = function() {
        $scope.modal_data = null;
        M.Modal.getInstance($("#warningModal")).open();
    };

    /*
    * An item in tool tree on the search panel is selected
    */
    $scope.tools_search_jstree_select_node = function(e, data) {
        //console.log(data.node.data.name);

        //Check if the tool pane is editable. If we do not include this check. All edits will be lost!
        //If it editable show a modal (see function tools_search_jstree_modal_editable)

        //Save in a variable the data of the item that has been clicked
        $scope.modal_data = data;
        if ($scope.tools_info_editable) {
            $scope.tools_search_raise_edit_are_you_sure_modal();
        }
        else {
            // Pressed an item in tool search tree, but the tool_info is not editable
            // Simulate a YES response from warning modal
            $scope.tools_search_jstree_modal_editable(true);
        }

    };


    /*
    * Called by Yes/No on Modal "All tool edits will be lost!"
    * M.Modal.getInstance($("#warningModal")).open()
    * tools_search_jstree_modal_editable_response = True // YES IS PRESSED !
    * tools_search_jstree_modal_editable_response = False // NO IS PRESSED!
    */
    $scope.tools_search_jstree_modal_editable = function(yes_no) {
        $scope.tools_search_jstree_modal_editable_response = yes_no;

        //If modal is open, close it
        if (M.Modal.getInstance($("#warningModal")).isOpen) {
            M.Modal.getInstance($("#warningModal")).close();
        }

        if ($scope.tools_search_jstree_modal_editable_response) { // This means, she clicked YES AFTER clicking on tree
            if ($scope.modal_data) {
                $scope.tools_search_show_item($scope.modal_data.node.data);
                window.createToolDataBtn_click();
            }
            else {
                window.cancelToolDataBtn_click(); // She clicked YES after CANCEL button 
                $scope.tools_info_editable = false;

                // Konstantina
                // $scope.open_div_on_right_panel();
            }
        }

    };

    // Konstantina
    // get called when we want to open something to the right panel
    // $scope.open_div_on_right_panel = function() {
    //     var parent = document.getElementsByClassName('rightPanel')[0].getElementsByTagName('div')[0];
    //     var child = $(parent).find('div:visible');
    //     if(child.length > 0){
    //         // right panel has visible content
    //         // open warning modal 
    //     }
    //     else{
    //         // right panel is empty
    //     }
    // };

    //JSTREE END tools_search

    //JSTREE TOOLS DEPENDENCIES
    $scope.tools_dep_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                //check_callback: true,
                check_callback : function(operation, node, node_parent, node_position, more) {
                    console.log('Second Tree Operation:', operation);

                    if (operation == 'copy_node') {
                        //$scope.tools_dep_jstree_model.push({'id': 'eee', 'parent': '#', 'text': 'ddddd'});
                        return false;
                    }

                    return true;
                },
                worker : true
            },
//            types : {
//                default : {
//                    icon : 'fa fa-flash'
//                },
//                star : {
//                    icon : 'fa fa-star'
//                },
//                cloud : {
//                    icon : 'fa fa-cloud'
//                }
//            },
            version : 1,
            plugins : ['dnd', 'contextmenu', 'types'],
            types : {
                default : {
                    icon : 'fa fa-cog'
                }
            },
            contextmenu: {
                items: function(node) {

                    if (node.parent != '#') {
                        // This is not a parent node. We cannot delete them. Return an empty context menu
                        return {};
                    }

                    var items = {
                        deleteItem: {
                            label: "Remove",
                            action: function() {
                                $scope.delete_parent_node_from_jstree($scope.tools_dep_jstree_model, node);
                                $scope.delete_parent_node_from_jstree($scope.tools_var_jstree_model, node);
                            }
                        }
                    };

                    return items;
                }
            },
            dnd: {
                is_draggable : function(node) {
                    return false;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []

    };

    $scope.tools_dep_jstree_model_init = [];
    $scope.tools_dep_jstree_model = [];
    angular.copy($scope.tools_dep_jstree_model_init, $scope.tools_dep_jstree_model);

    //JSTREE TOOLS DEPENDENCIES END
    
    //JSTREE TOOL VARIABLES
    $scope.tools_var_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                //check_callback: true,
                check_callback : function(operation, node, node_parent, node_position, more) {
                    console.log('Third Tree Operation:', operation);

                    if (operation == 'copy_node') {
                        //$scope.tools_dep_jstree_model.push({'id': 'eee', 'parent': '#', 'text': 'ddddd'});
                        return false;
                    }
                    else if (operation == 'move_node') {
                        return false;
                    }

                    return true;
                },
                worker : true
            },
            types : {
                tool : {
                    icon : 'fa fa-cog'
                },
                variable : {
                    icon : 'fa fa-star' // other ideas: bullseye , dot-circle , star , circle  
                }
            },
            version : 1, // Remnant. DELETE IT
            plugins : ['dnd', 'types'],
            dnd: {
                is_draggable : function(node) {
                    if (node.length!=1) {
                        return false;
                    }
                    if (node[0].data.type === 'variable') {
                        return true;
                    }
                    return false;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []

    };

    $scope.tools_var_jstree_model_init = [
        //{'id': 'a', 'parent': '#', 'text': 'AAAAAAA'}
    ];
    $scope.tools_var_jstree_model = [];
    angular.copy($scope.tools_var_jstree_model_init, $scope.tools_var_jstree_model);

    //JSTREE TOOL VARIABLES END

    //JSTREE END

    // WORKFLOWS 
    /*
    * Navbar --> Tools/Data --> pressed
    */
    $scope.navbar_workflows_pressed = function() {
        $scope.inner_hide_all_navbar();
        $scope.show_workflows = true;
    };

    $scope.workflow_clear_button_pressed = function() {
        window.initTree();
    }

    // WORKFLOWS END 


}); 

