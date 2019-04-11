
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

        return tool.name + '/' + tool.version + '/' + tool.edit;
    }
});

angular.module('OBC_app').filter('workflow_label', function() {
    return function(workflow) {
        if (workflow === null) {
            return '';
        }

        return workflow.name + '/' + workflow.edit;
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

        $scope.main_container_show = true;
        $scope.profile_container_show = false;

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
        $scope.workflow_website = '';
        $scope.workflow_description = '';
        $scope.workflow_changes = '';
        $scope.workflow_info_forked_from = null; // From which workflow was this workflow forked from?
        $scope.workflows_info_error_message = '';
        $scope.workflows_step_name = '';
        $scope.workflows_step_description = '';
        $scope.worfklows_step_ace_init = '# Insert the BASH commands for this step\n\n';
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
        $scope.workflow_step_error_message = '';

        //The input and output variables of the workflow
        $scope.workflow_input_outputs = [{name: '', description: '', out:true}]; // {name: 'aa', description: 'bb', out:true}, {name: 'cc', description: 'dd', out:false}


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
    *
    */
    $scope.toast = function(message, type) {
        if (type == 'error') {
            generateToast(message, 'red lighten-2 black-text', 'stay on');
        }
        else if (type == 'success') {
            generateToast(message, 'green lighten-2 black-text', 'stay on');
        }
        else {
            console.warn('Error: 8133 Unknown toast type:' + type);
        }
    };

    /*
    * Navbar --> Home --> clicked 
    */
    $scope.navbar_home_clicked = function() {
        $scope.profile_container_show = false;
        $scope.main_container_show = true;
    };

    $scope.navbar_profile_clicked = function() {
        $scope.main_container_show = false;
        $scope.profile_container_show = true;
    };

    $scope.profile_save_pressed = function() {
        $scope.main_container_show = true;
        $scope.profile_container_show = false;
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
                angular.copy(data['workflows_search_jstree'], $scope.workflows_search_jstree_model);  

            },
            function(data) {

            },
            function(statusText) {

            }
        );
    };


    /*
    * Search SPECIFIC tool. Update UI
    * See also workflows_search_3
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

                $scope.tool_info_validation_status = data.validation_status;
                $scope.tool_info_validation_created_at = data.validation_created_at;
                $scope.tool_info_validation_message = data.validation_status; // REMOVE THIS !
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
            $scope.workflows_search_2(); 
            return; 
        }


        //Everything seems to be ok
        $scope.workflows_search_warning = '';
        $scope.workflows_search_2();


    };


    /*
    * Create new tool button pressed.
    * All checks are ok.
    */
    $scope.tools_search_create_new_pressed_ok = function() {
        $scope.tools_search_warning = '';

        //Close Workflow right panel
        window.cancelWorkflowBtn_click();

        //Triggers animation to open right window
        window.createToolDataBtn_click();


        $scope.show_tools_info = true;
        //$scope.show_workflows_info = false; // TODO. THIS SHOULDN'T BE HERE

        $scope.tools_info_editable = true;
        $scope.tool_info_created_at = null;
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

        //Empty validation status
        $scope.tool_info_validation_status = 'Unvalidated';
        $scope.tool_info_validation_created_at = null;

        $scope.tool_info_validation_message = 'Unvalidated';
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

        //If workflows are editable then raise a modal to ask user if she want to lose all edits.
        if ($scope.workflows_info_editable) {
            $scope.tools_search_raise_edit_are_you_sure_modal('TOOLS_CREATE_BUTTON');
            return;
        }

        // Everything seems ok.
        $scope.tools_search_create_new_pressed_ok();


    };

    /*
    * Create new workflow. All checks are ok. 
    */
    $scope.workflows_search_create_new_pressed_ok = function() {
        //Close tool accordion
        $scope.tools_info_editable = false;
        window.cancelToolDataBtn_click();

        //Open Workflows accordion
        window.createWorkflowBtn_click();

        $scope.workflow_info_name = $scope.workflows_search_name;
        $scope.workflows_info_username = $scope.username;
        $scope.workflows_info_editable = true;
        $scope.workflow_info_created_at = null;
        $scope.workflow_info_forked_from = null;
        $scope.workflow_website = '';
        $scope.workflow_description = '';

        //Clear graph
        $scope.workflow_info_clear_pressed();

        //Clear STEP
        $scope.workflows_step_name = '';
        $scope.workflows_step_description = '';
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
        workflow_step_editor.setReadOnly(false); 

        //Clear input/output variables
        $scope.workflow_input_outputs = [{name: '', description: '', out:true}];

        //Update Step Editor Tab completion 
        $scope.workflow_update_tab_completion_info_to_step();

        //By default we Add a step.
        $scope.workflow_step_add_update_label = 'Add';
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

        //If tools are editable then raise a modal to ask user if she want to lose all edits.
        if ($scope.tools_info_editable) {
            $scope.tools_search_raise_edit_are_you_sure_modal('WORKFLOWS_CREATE_BUTTON');
            return;
        }

        $scope.workflows_search_create_new_pressed_ok();

        //Open a modal window. The Yes/No buttons of the window are binded to tools_search_jstree_modal_editable 
        //window.createToolDataBtn_click();


        //$scope.show_tools_info = false;
        //$scope.show_workflows_info = true;

        //$scope.workflows_info_error_message = '';


    };

    /*
    * Navbar --> Tools/data --> Appropriate input --> "Create New" button --> Pressed --> Filled input --> Save (button) --> Pressed
    * See also: workflows_create_save_pressed 
    */
    $scope.tool_create_save_pressed = function() {

        console.log("$scope.tools_dep_jstree_model:");
        console.log($scope.tools_dep_jstree_model);

        //Get the dependencies
        var tool_dependencies = [];
        for (var i=0; i<$scope.tools_dep_jstree_model.length; i++) {
            //Add only the roots of the tree
            if ($scope.tools_dep_jstree_model[i].parent === '#') {
                tool_dependencies.push($scope.tools_dep_jstree_model[i]); //Although we only need name, version, edit, we pass the complete object 
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
                $scope.toast($scope.tools_info_success_message, 'success');
                $scope.tools_info_editable = false;
                $scope.tool_info_created_at = data['created_at'];
                $scope.tools_info_edit = data['edit'];
                $scope.tools_search_input_changed(); //Update search results
            },
            function(data) {
                $scope.tools_info_error_message = data['error_message'];
                $scope.toast($scope.tools_info_error_message, 'error');
            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
                $scope.toast($scope.tools_info_error_message, 'error')
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
        $scope.toast($scope.tools_info_success_message, 'success');

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
    *  Create the bash script that we will submit to the controller for validation
    */
    $scope.create_bash_script_for_validation = function(installation_bash, validation_bash) {
        return installation_bash + '\n' + validation_bash;
    };

    /*
    * Called $scope.tool_info_validate_pressed upon receiving "queued" status
    * Backend updates the database
    */
    $scope.tool_info_validation_queued = function(this_id, tool) {
        $scope.ajax(
            'tool_info_validation_queued/',
            {
                payload: {
                    id: this_id,
                    status: "Queued",
                    tool: tool
                }
            },
            function(data) {
                $scope.toast('Succesfully submitted tool/data for validation', 'success');
                $scope.tool_info_validation_message = 'Queued';
                $scope.tool_info_validation_created_at = data['last_validation'];
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        );
    };

    /*
    * Navbar --> tools/data --> Aprioprate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> Validate (pressed)
    */
    $scope.tool_info_validate_pressed = function() {
        // var ossel = $scope.osSelection;
        var installation_bash = tool_installation_editor.getValue();
        var validation_bash = tool_validation_editor.getValue();
        //take the value from dropdown menu 
        var os_selected_value = $('#tools_os_combo').val(); // TODO: CHECK IF NOT CHOSEN 

        // console.log(os_selected_value);
        //console.log('INSTALLATION BASH:');
        //console.log(installation_bash);
        //console.log('VALIDATION BASH:');
        //console.log(validation_bash);
        var tool_to_be_validated = {
            name: $scope.tools_info_name,
            version: $scope.tools_info_version,
            edit: $scope.tools_info_edit
        };


        $scope.ajax(
            window.OBC_CONTROLLER_URL, // Sent from view: index
            {
                action: 'validate',
                bash: $scope.create_bash_script_for_validation(installation_bash, validation_bash),
                ostype: os_selected_value // user selected os
            },
            function (data) {
                var this_id = data['id'];
                var status = data['status']; // This should always be queued
                if (status != 'Queued') {
                     throw "ERROR: 4529"; // This should never happen
                }
                $scope.tool_info_validation_queued(this_id, tool_to_be_validated);
    
            },
            function (data) {
                $scope.toast(data['error_message'], 'error');
            },
            function (statusText) {
                $scope.toast('Server Error:' + statusText, 'error');
            }
        );
    };

    /*
    * Navbar --> tools/data --> Aprioprate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "-" (variables) (pressed)
    */
    $scope.tools_info_remove_variable = function(index) {
        // $('.tooltipped').tooltip('close');
        $scope.tool_variables.splice(index, 1);
    };

    /*
    * Navbar --> tools/data --> Appropriate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "+" (variables) (pressed)
    */
    $scope.tools_info_add_variable = function() {
        // $('.tooltipped').tooltip('close');

        //Check for double names
        var names = {};
        for (var i=0; i<$scope.tool_variables.length; i++) {
            if ($scope.tool_variables[i].name in names) {
                $scope.toast('There is alreay a variable with this name', 'error');
                return;
            }
            names[$scope.tool_variables[i].name] = null;
        }

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
                    console.log('UPDATE THE GRAPH WITH: dependencies_jstree');
                    console.log(data['dependencies_jstree']);
                    console.log('variables_jstree:');
                    console.log(data['variables_jstree']);

                    if (!$scope.workflows_info_editable) {
                        $scope.toast('You cannot edit this workflow. You can fork it, or create a new one.', 'error');
                        return;
                    }


                    //Add the variable information to the tool nodes. 
                    //By doing that we make sure that tool nodes have variable information
                    //This is by far not optimal neither nice!
                    data['variables_jstree'].forEach(function(variables_jstree_item) {
                        if (variables_jstree_item.type == 'variable') { // if (variables_jstree_item.data.type == 'variable') {
                            //We need to find the tool object of this variable
                            for (var i=0; i<data['dependencies_jstree'].length; i++) {
                                if (data['dependencies_jstree'][i].id == variables_jstree_item.parent) {
                                    if (typeof data['dependencies_jstree'][i].variables !== 'undefined') {
                                        data['dependencies_jstree'][i].variables.push(variables_jstree_item.data);
                                    }
                                    else {
                                        data['dependencies_jstree'][i].variables = [variables_jstree_item.data];
                                    }

                                }
                            }
                        }
                    });
                    //Make sure that all dependencies_jstree nodes have a variables field
                    //Also make sure that all ependencies_jstree nodes have a belongto fields
                    for (var i=0; i<data['dependencies_jstree'].length; i++) {
                        if (typeof data['dependencies_jstree'][i].variables !== 'undefined') {
                        }
                        else {
                            data['dependencies_jstree'][i].variables = [];
                        }
                        data['dependencies_jstree'][i].belongto = null;
                    }

                    window.buildTree(data['dependencies_jstree'], {name: $scope.workflow_info_name, edit: null}); //FIXME SEE A46016A6E393 
                    $scope.workflow_update_tab_completion_info_to_step(); 


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
    * the results are capture by function: tools_search_jstree_modal_editable(yes_no)
    */
    $scope.tools_search_raise_edit_are_you_sure_modal = function(who_called_me) {
        M.Modal.getInstance($("#warningModal")).open();
        $("#warningModal").data('who_called_me', who_called_me);

    };

    /*
    * An item in tool tree on the search panel is selected
    * Defined in: tree-events="select_node:tools_search_jstree_select_node" 
    * See also: workflows_search_jstree_select_node 
    */
    $scope.tools_search_jstree_select_node = function(e, data) {
        //console.log(data.node.data.name);

        //Check if the tool pane is editable. If we do not include this check. All edits will be lost!
        //If it editable show a modal (see function tools_search_jstree_modal_editable)

        //Save in a variable the data of the item that has been clicked
        $scope.modal_data = data;
        if ($scope.tools_info_editable || $scope.workflows_info_editable) {
            $scope.tools_search_raise_edit_are_you_sure_modal('TOOL_SEARCH_JSTREE');
        }
        else {
            // Pressed an item in tool search tree, but the tool_info is not editable
            // Simulate a YES response from warning modal
            $("#warningModal").data('who_called_me', 'TOOL_SEARCH_JSTREE');
            $scope.tools_search_jstree_modal_editable(true);
        }

    };


    /*
    * Called by Yes/No on Modal "All tool edits will be lost!"
    * M.Modal.getInstance($("#warningModal")).open()
    * tools_search_jstree_modal_editable_response = True // YES IS PRESSED !
    * tools_search_jstree_modal_editable_response = False // NO IS PRESSED!
    * Who called me value: 
    * TOOLS_CANCEL_BUTTON, WORKFLOWS_CANCEL_BUTTON, TOOL_SEARCH_JSTREE, WORKFLOWS_CREATE_BUTTON, TOOLS_CREATE_BUTTON
    */
    $scope.tools_search_jstree_modal_editable = function(yes_no) {
        $scope.tools_search_jstree_modal_editable_response = yes_no;

        //Who called me?
        var who_called_me = $("#warningModal").data('who_called_me');

        //If modal is open, close it
        if (M.Modal.getInstance($("#warningModal")).isOpen) {
            M.Modal.getInstance($("#warningModal")).close();
        }

        if ($scope.tools_search_jstree_modal_editable_response) { // She clicked YES
            console.log('CLICKED YES MODAL');
            console.log('MODAL DATA:');
            console.log($scope.modal_data);

            console.log('WHO CALLED MODAL:');
            console.log(who_called_me);

            if (who_called_me == 'TOOL_SEARCH_JSTREE') { // This means, she clicked YES AFTER clicking on tools js tree 
                console.log('MODAL WHO CALLED ME: TOOL_SEARCH_JSTREE');
                $scope.tools_search_show_item($scope.modal_data.node.data);
                window.createToolDataBtn_click();
                window.cancelWorkflowBtn_click();
                $scope.tools_info_editable = false;
                $scope.workflows_info_editable = false;
            }
            else if (who_called_me == 'TOOLS_CREATE_BUTTON') {
                $scope.tools_search_create_new_pressed_ok();
            }
            else if (who_called_me == 'TOOLS_CANCEL_BUTTON') {
                console.log('MODAL WHO CALLED ME: TOOLS_CANCEL_BUTTON');
                window.cancelToolDataBtn_click(); // Close Tool panel
                $scope.tools_info_editable = false;
            }
            else if (who_called_me == 'WORKFLOWS_CANCEL_BUTTON') {
                console.log('MODAL WHO CALLED ME: WORKFLOWS_CANCEL_BUTTON');
                $scope.workflows_info_editable = false;
                window.cancelWorkflowBtn_click(); // Close WORFKLOW accordion

            }
            else if (who_called_me == 'WORKFLOWS_CREATE_BUTTON') {
                $scope.workflows_search_create_new_pressed_ok();
            }
            else {
                throw "ERROR: 7847"; // This should never happen
            }

        }

    };

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

    //JSTREE workflows_search
    $scope.workflows_search_jstree_config = {
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
                    icon : 'fa fa-sitemap' //
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

    $scope.workflows_search_jstree_model_init = [];

    $scope.workflows_search_jstree_model = [];
    angular.copy($scope.workflows_search_jstree_model_init, $scope.workflows_search_jstree_model);

    /*
    * An item in workflow tree on the search panel is selected
    * Defined in: tree-events="select_node:workflows_search_jstree_select_node" 
    * See also: tools_search_jstree_select_node
    */
    $scope.workflows_search_jstree_select_node = function(e, data) {
        //console.log('Workflow search tree clicked node data:');
        //console.log(data);

        $scope.workflows_search_show_item(data.node.data);
    };


    /*
    * Show a WORKFLOW on UI
    * See also tools_search_show_item
    */
    $scope.workflows_search_show_item = function(item) {
        //$scope.show_tools_info = true;
        //$scope.show_workflows_info = false;
        //$scope.tools_info_editable = false;
        //$scope.tools_search_3(item);
        //M.updateTextFields(); // The text inputs in Materialize needs to be updated after change.

        //console.log('WORFKLOW ITEM IN workflows_search_show_item:');
        //console.log(item);

        //FIX: Do this according to tools_search_show_item
        window.cancelToolDataBtn_click();
        window.createWorkflowBtn_click();
        $scope.workflows_info_editable = false;
        $scope.workflows_search_3(item);
        M.updateTextFields();
    };

    /*
    * Get the details from the backend of a particular workflow and update the UI
    * See also: tools_search_3
    */ 
    $scope.workflows_search_3 = function(item) {
        $scope.ajax(
            'workflows_search_3/',
            {
                workflow_name: item.name,
                workflow_edit: item.edit,
            },
            function(data) {
                $scope.workflows_info_username = data['username'];
                $scope.workflow_info_name = item.name;
                $scope.workflow_info_edit = item.edit;
                $scope.workflow_info_created_at = data['created_at'];
                $scope.workflow_website = data['website'];
                $scope.workflow_description = data['description'];
                $scope.workflow_info_forked_from = data['forked_from'];

                //Load the graph. TODO: WHAT HAPPENS WHEN WE CLICK TO NODE? IT IS NOT REGISTERED
                cy.json(data['workflow']);
                cy.resize();
                window.cy_setup_events();

                //Make step editor readonly
                workflow_step_editor.setReadOnly(true);

                //Load the input/output variables
                // $scope.workflow_input_outputs . [{name: '', description: '', out:true}];
                $scope.workflow_input_outputs = [];
                if (cy.$('node[type="input"] , node[type="output"]').length) {
                    cy.$('node[type="input"] , node[type="output"]').forEach(function(variable){
                        var data = variable.data();
                        $scope.workflow_input_outputs.push({name: data.name, description: data.description, out: data.type === 'output'});
                    });
                }
                // $scope.workflow_input_outputs should never be empty. FIXME: Build an initializer function
                if (! $scope.workflow_input_outputs.length) {
                    $scope.workflow_input_outputs = [{name: '', description: '', out:true}];
                }
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            },
        );
    };

    /*
    * Navbar --> Tools/Data --> pressed
    */
    $scope.navbar_workflows_pressed = function() {
        $scope.inner_hide_all_navbar();
        $scope.show_workflows = true;
    };

    $scope.workflow_clear_button_pressed = function() {
        window.initTree();
    };

    /*
    * When a new tool is added (or removed from) to the workflow, we need to know what variables are available
    * We use this info to update the tab completion to the step bash editor ace.  
    */ 
    $scope.workflow_update_tab_completion_info_to_step = function() {

        // Remove all tab completion
        // https://stackoverflow.com/questions/28920998/custom-autocompleter-and-periods
        lang.setCompleters();

        var completion_info = [];

        cy.$('node').forEach(function(node) {
            var this_data = node.data();

            //If this_data.belongto is null then this is the root workflow. Not a tool/step/input/output.
            if (!this_data.belongto) {
                return;
            }

            var this_node_belong_to_show_edit = this_data.belongto.edit ? this_data.belongto.edit : 'root'; //The workflow edit to show on tab completion
            var this_node_belong_to_value_edit = this_data.belongto.edit ? this_data.belongto.edit : 'null'; // The workflow edit as a variable on tab completion

            if (this_data.type=='tool') {
                this_data.variables.forEach(function(variable) {
                    completion_info.push({
                        caption: 'tool/' + this_data.name + '/' + this_data.version + '/' + this_data.edit + '/' +  variable.name,
                        value: '$(' + this_data.name + '__' + this_data.version + '__' + this_data.edit + '__' + variable.name + ')',
                        meta: variable.description
                    });
                });
            }
            else if (this_data.type=='step') {

                completion_info.push({
                    caption: 'call(' + this_data.label + '/' + this_data.belongto.name + '/' + this_node_belong_to_show_edit + ')',
                    value: 'call(' + this_data.label + '__' + this_data.belongto.name + '__' + this_node_belong_to_value_edit + ')',
                    meta: 'STEP'
                });
            }
            else if (this_data.type=='input' || this_data.type=='output') {
                completion_info.push({
                    caption: this_data.type + '/' + this_data.name + '/' + this_data.belongto.name + '/' + this_node_belong_to_show_edit,
                    value: '$(' + this_data.type + '__' + this_data.name + '__' + this_data.belongto.name + '__' + this_node_belong_to_value_edit + ')',
                    meta: this_data.description
                });
            }

        });

        //Create a new tab completion  object
        var compl = {
          identifierRegexps: [/[a-zA-Z_0-9\.\$\-\u00A2-\uFFFF]/],
          getCompletions: function (editor, session, pos, prefix, callback) {
            //alert(prefix);

            callback(null, 
//                [
//                    {
//                        caption: 'tool.mitsos',
//                        value: '$(tool_mitsos)',
//                        meta: 'TOOL'
//                    },
//                    {
//                        caption: 'KLM',
//                        value: 'NOP',
//                        meta: 'STEP'
//                    }
//                ]

            completion_info

            );
            //return;
          }
        }

        //Load new completion info
        lang.addCompleter(compl);

    };

    /*
    * Workflow --> Info --> Button: Add Step --> Clicked 
    */
    $scope.workflow_info_add_step_clicked = function() {

        $scope.workflow_step_add_update_label = 'Add'; 

        //Update tab completion info to step ace editor
        $scope.workflow_update_tab_completion_info_to_step();

        //Open accordion
        window.openEditWorkflowBtn_click();

        $scope.workflows_step_name = ''; //Clear STEP name
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1); //Add default content
    };

    /*
    * workflows --> Step --> Button: Add/Update --> Clicked
    * We either ADD the step or UPDATE the step 
    */
    $scope.workflow_step_add = function() {

        if (!$scope.tools_name_regexp.test($scope.workflows_step_name)) {
            $scope.workflow_step_error_message = 'Invalid step name';
            return;
        }

        //Is this an UPDATE or an ADD?
        if ($scope.workflow_step_add_update_label == 'Update') {
            // If this is an update then delete the previous node
            cy.$('node[id="' +  $scope.workflow_step_previous_step.id + '"]').remove();
        }
        else if ($scope.workflow_step_add_update_label == 'Add') {
            // If this is an add then check if we are adding a step with a name that already exists.
            var this_step_id = window.create_step_id({name: $scope.workflows_step_name}, {name: $scope.workflow_info_name, edit: null});
            if (cy.$('node[id="' +  this_step_id + '"]').length) {
                $scope.toast('There is already a step with this name', 'error');
                return;
            }
        }

        $scope.workflow_step_error_message = '';

        var bash_commands = workflow_step_editor.getValue(); //BASH Commands
        var steps = window.OBCUI.get_steps_from_bash_script(bash_commands); //STEPS
        var tools = window.OBCUI.get_tools_from_bash_script(bash_commands); //TOOLS
        var input_output = window.OBCUI.get_input_outputs_from_bash_script(bash_commands); // INPUT/OUTPUTS
        //console.log('STEPS:');
        //console.log(steps);

        //console.log('TOOLS:');
        //console.log(tools);

        //The object to pass to buildTree has to be a list of node objects
        var step_node = [{
            name: $scope.workflows_step_name,
            type: 'step',
            bash: bash_commands,
            steps: steps,
            tools: tools,
            inputs: input_output.inputs,
            outputs: input_output.outputs,
            belongto: null
        }];

        //Always when updating the graph, update also tab completion data for step editor! FIXME!! (bundle these things together!) A46016A6E393
        window.buildTree(step_node, {name: $scope.workflow_info_name, edit: null});
        $scope.workflow_update_tab_completion_info_to_step();

        //Empty STEP fields
        $scope.workflows_step_name = '';
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);

    };

    /*
    * workflows -> Step -> Delete step clicked.
    */ 
    $scope.workflow_step_delete = function() {
        //console.log('DELETE STEP');
        var this_step_id = window.create_step_id($scope.workflow_step_previous_step, $scope.workflow_step_previous_step.belongto);

        //console.log('STEP ID TO DELETE:')
        //console.log(this_step_id);
        
        //We do not have to check if this node exists. cytoscape is ok with this.
        cy.$('node[id="' + this_step_id + '"]').remove();

        //Empty the step editor
        $scope.workflows_step_name = '';
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
        $scope.workflow_step_add_update_label = 'Add';
    
    };

    /*
    * Called from UI.js . Right Click a node in cytoscape --> delete
    */
    $scope.workflow_cytoscape_delete_node = function(node_id) {

        //Cannot edit a saved worfklow
        if (!$scope.workflows_info_editable) {
            $scope.toast('Cannot edit a saved workflow. Fork it to make edits.', 'error');
            return;
        }

        /* Remove the successors of a node */
        function remove_successors(node) {
            node.successors().targets().forEach(function (element) {
                cy.remove(element);                  
            });

        }

        var node = cy.$('node[id="' + node_id + '"]');
        var data = node.data();
        if (data.type == 'step'){
            node.remove();
        }
        else if (data.type=='tool') {

            //Is there any tool that is dependent from this tool?
            if (node.incomers('node[type="tool"]').length) {
                $scope.toast('Cannot remove this tool. Other tools are dependent on this.', 'error');
            }
            else {
                //Remove successors as well 
                remove_successors(node);
                node.remove();
            }
        }
        else if (data.type=='input' || data.type=='output') {
            //Check if this is belongs to root WF
            if (window.is_workflow_root_from_SIO_id(node.id())) {
                
                //Locate the index 
                var index = -1;
                for (var i=0; i<$scope.workflow_input_outputs.length; i++) {
                    if ($scope.workflow_input_outputs[i].name == data.name && $scope.workflow_input_outputs[i].out == (data.type=='output')) {
                        index = i;
                        break;
                    }
                }
                //Remove it
                if (index>=0) {
                    $scope.workflow_step_remove_input_output(index);
                    node.remove();
                }
                else {
                    console.warn('Error 8161'); // This should never happen
                }
            }
            else {
               // If this does not belong to the root node, delete it.
               node.remove();
            }
        }
        else if (data.type == 'workflow') {
            if (!data.belongto) {
                $scope.toast('Cannot remove the root workflow', 'error');
            }
            else {
                remove_successors(node);
                node.remove();
            }
        }

    };

    /*
    * Called by ui.js
    * Clicked a step node on cytoscape graph
    */
    $scope.workflop_step_node_clicked = function(step) {

        //console.log('CLICKED STEP NDOE:');
        //console.log(step);

        //When a node is clicked then we "update" the node, we do not add it.
        $scope.workflow_step_add_update_label = 'Update'; 

        //One update might be the change of the node name. We allow this,
        //but we need to keep track of the "previous" name so that we delete the right node.
        $scope.workflow_step_previous_step = step;

        $scope.workflows_step_name = step.name;
        $('#editWorkflowNameLabel').addClass('active');
        workflow_step_editor.setValue(step.bash, -1);

        //Open STEP accordion
        window.openEditWorkflowBtn_click();
        $timeout(function(){M.updateTextFields()}, 10); // FIXME We need to make sure that M.updateTextFields() is run AFTER openEditWorkflowBtn_click()
        
    };

    /*
    * Worfklows --> Input/Outpus --> Add variable button ('+') --> Pressed 
    */
    $scope.workflow_step_add_input_output = function() {
        $scope.workflow_input_outputs.push({name:'', description: '', out:false});
    };

    /*
    * Worfklwos --> Inputs/Outputs --> Remove Variable button ('-') --> Pressed
    */
    $scope.workflow_step_remove_input_output = function(index) {
        $scope.workflow_input_outputs.splice(index, 1);
        //workflow_input_outputs should never be empty
        if (!$scope.workflow_input_outputs.length) {
            $scope.workflow_step_add_input_output();
        }
    };

    /*
    * Workflows --> Input/Outputs --> (Alter Input / Output variables) --> Update button --> pressed
    */
    $scope.workflow_step_input_output_update_pressed = function() {

        var nodes_to_add = [];

        $scope.workflow_input_outputs.forEach(function(input_output){
            if (input_output.name && input_output.description) {
                nodes_to_add.push({
                    name: input_output.name,
                    description: input_output.description,
                    type: input_output.out ? 'output' : 'input',
                    belongto: null
                })
            }
        });

        //console.log('Input / Output Variable to add:');
        //console.log(nodes_to_add);

        if (nodes_to_add.length) {
            window.buildTree(nodes_to_add, {name: $scope.workflow_info_name, edit: null}); // FIXME. SEE A46016A6E393 
            $scope.workflow_update_tab_completion_info_to_step();
        }
    };

    /*
    * Workflows --> Save button --> pressed 
    * See also: tool_create_save_pressed 
    */
    $scope.workflows_create_save_pressed = function() {


        $scope.ajax(
            'workflows_add/',
            {
                workflows_search_name: $scope.workflow_info_name,
                workflow_info_forked_from : $scope.workflow_info_forked_from,

                workflow_website : $scope.workflow_website,
                workflow_description : $scope.workflow_description,
                workflow_changes: $scope.workflow_changes,
                workflow_json : cy.json()
            },
            function(data) {
                $scope.workflow_info_created_at = data['created_at'];
                $scope.workflow_info_edit = data['edit'];
                $scope.workflows_info_editable = false;
                workflow_step_editor.setReadOnly(true);

                $scope.toast('Workflow successfully saved', 'success');
            },
            function(data) {
                $scope.workflows_info_error_message = data['error_message'];
                $scope.toast($scope.workflows_info_error_message, 'error');
            },
            function(statusText) {
                $scope.workflows_info_error_message = statusText;
                $scope.toast($scope.workflows_info_error_message, 'error');
            }
        );
    };

    /*
    * Workflows --> Fork Icon --> Pressed
    */
    $scope.workflows_info_fork_pressed = function() {
        if (!$scope.username) {
            //It will never reach here. FORK is disabled in UI if user is not logged in.
            $scope.toast("Login to create new Workflows", 'error');
            return;
        }

        //After fork, we should change the IDs 
        window.forkWorkflow();

        $scope.workflows_info_editable = true;
        $scope.toast("Workflows successfully forked. Press Save after completing your edits", 'success');

        $scope.workflow_info_forked_from = {
            'name': $scope.workflow_info_name,  
            'edit': $scope.workflow_info_edit
        }
        $scope.workflow_changes = '';
        workflow_step_editor.setReadOnly(false);

        //Update Step Editor Tab completion 
        $scope.workflow_update_tab_completion_info_to_step();
    };

    /*
    * Called from ui.js, when a user drags a worklfow in current workflow
    * workflow = {'name': ... , 'edit': '...'}
    */
    $scope.workflow_add_workflow = function(workflow) {
        console.log('WORKFLOW TO BE ADDED:');
        console.log(workflow);

        //Fetch info of this workflow
        $scope.ajax(
            'workflows_search_3/',
            {
                workflow_name : workflow.name,
                workflow_edit : workflow.edit
            },
            function(data) {
                workflow_cytoscape = data['workflow'];
                
                //Create a single worfklow node
                //var workflow_node_to_add;
                //workflow_cytoscape.elements.nodes.forEach(function(node) {
                //    if (node.data.type=='workflow' && node.data.root) {
                //        workflow_node_to_add = {
                //            name: node.data.name,
                //            edit: node.data.edit,
                //            type: 'workflow'
                //        };
                //    }
                //});

                //the information regarding edges exists on the nodes. 
                //We do not have to pass the complete worfklow, or edger information.
                var nodes_to_add = []
                workflow_cytoscape.elements.nodes.forEach(function(node){ nodes_to_add.push(node.data) });
                window.buildTree(nodes_to_add, {name: $scope.workflow_info_name, edit: null});  
				
				//TODO  check if it is correct (added by Galateia)
				window.cy_close_successors();
            },
            function(data) {
                $scope.toast("ERROR 81711", "error");
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        );
    };

    /*
    * worfklows --> info (right panel) --> button "Clear" --> Pressed
    */
    $scope.workflow_info_clear_pressed = function() {
        window.clear($scope.workflow_info_name);
    };

    /*
    * worfklows --> info (right panel) --> button "FIT" --> Pressed
    */
    $scope.workflow_info_fit_pressed = function() {
        window.fit();
    };

    /*
    * worfklows --> info (right panel) --> button "Run" --> Pressed
    */
    $scope.workflow_info_run_pressed = function() {
        window.OBCUI.runWorkflow();
    };


    // WORKFLOWS END 


}); 

