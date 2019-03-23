
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

        //Clear input/output variables
        $scope.workflow_input_outputs = [{name: '', description: '', out:true}];

        //Update Step Editor Tab completion 
        $scope.workflow_update_tab_completion_info_to_step();
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
                generateToast($scope.tools_info_error_message, 'red lighten-2 black-text', 'stay on');

            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
                generateToast($scope.tools_info_error_message, 'red lighten-2 black-text', 'stay on');
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
        // $('.tooltipped').tooltip('close');
        $scope.tool_variables.splice(index, 1);
    };

    /*
    * Navbar --> tools/data --> Appropriate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "+" (variables) (pressed)
    */
    $scope.tools_info_add_variable = function() {
        // $('.tooltipped').tooltip('close');
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
                        generateToast('You cannot edit this workflow. You can fork it, or create a new one.', 'red lighten-2 black-text', 'stay on');
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
                    for (var i=0; i<data['dependencies_jstree'].length; i++) {
                        if (typeof data['dependencies_jstree'][i].variables !== 'undefined') {
                        }
                        else {
                            data['dependencies_jstree'][i].variables = [];
                        }
                    }

                    window.buildTree(data['dependencies_jstree']); //FIXME SEE A46016A6E393 
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
                generateToast(data['error_message'], 'red lighten-2 black-text', 'stay on');
            },
            function(statusText) {
                generateToast(statusText, 'red lighten-2 black-text', 'stay on');
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
                    caption: 'call(' + this_data.label + ')',
                    value: 'call(' + this_data.label + ')',
                    meta: 'STEP'
                });
            }
            else if (this_data.type=='input' || this_data.type=='output') {
                completion_info.push({
                    caption: this_data.type + '/' + this_data.name,
                    value: '$(' + this_data.type + '__' + this_data.name + ')',
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

        //Update tab completion info to step ace editor
        $scope.workflow_update_tab_completion_info_to_step();

        //Open accordion
        window.openEditWorkflowBtn_click();

        $scope.workflows_step_name = ''; //Clear STEP name
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1); //Add default comment 
    };

    /*
    * Remove commends from text
    # Everything that starts with '#'
    */
    $scope.remove_bash_comments = function(t) {
        
        var no_comments = [];
        var t_splitted = t.split('\n');

        t_splitted.forEach(function(line){
            //Check if this line is a comment
            if (line.match(/^[\s]*#/)) {
                //This is a comment. Ignore it
            }
            else {
                //This is not a comment
                no_comments.push(line);
            }
        });

        return no_comments.join('\n');
    };

    /*
    * Return a list of steps that are called in this bash script
    */
    $scope.get_steps_from_bash_script = function(t) {

        var steps = [];

        //Remove bash comments
        var no_comments = $scope.remove_bash_comments(t);

        var splitted = no_comments.split('\n');
        splitted.forEach(function(line) {
            var results = line.match(/((^call)|([\s]+call))\([\w]+\)/g); // Matches: "call(a)" , "  call(a)", "ABC call(a)", "ABC   call(a)"
            if (results) {
                results.forEach(function(result) {
                    var step_name = result.match(/call\(([\w]+)\)/)[1];

                    //Is there a node with type step and name step_name ?
                    if (cy.$("node[type='step'][label='" + step_name + "']").length) {
                        //Add it only if it not already there
                        if (!steps.includes(step_name)) {
                            steps.push(step_name);
                        }
                    } 
                });
            }
        });

        return steps;
    };

    /*
    * Return a list of input output variables from the bash script 
    */ 
    $scope.get_input_outputs_from_bash_script = function(t) {

        //Remove bash comments. DUPLICATE FIXME
        var no_comments = $scope.remove_bash_comments(t);
        var inputs = [];
        var outputs = [];

        var splitted = no_comments.split('\n');
        splitted.forEach(function(line) {
            var results = line.match(/\$\((input|output)__[a-zA-Z0-9][\w]*\)/g); // [^_\w] Does not work??? 
            if (results) {
                results.forEach(function(result){
                    var splitted = result.match(/\$\((input|output)__([\w]+)\)/);
                    var input_output = splitted[1];
                    var variable_name = splitted[2];
                    //Does this variable exist in cytoscape?
                    if (cy.$("node[type='" + input_output + "'][id='" + variable_name + "']").length) {
                        //It exists
                        //Add them in their relevant list only if they are not already there
                        if (input_output == "input") {
                            if (!inputs.includes(variable_name)) {
                                inputs.push(variable_name);
                            }
                        }
                        else if (input_output == "output") {
                            if (!outputs.includes(variable_name)) {
                                outputs.push(variable_name);
                            }
                        }
                    }
                });
            }
        });

        return {inputs: inputs, outputs: outputs};

    };

    /*
    * Return a list of tools whose variables are used in this bash script
    */
    $scope.get_tools_from_bash_script = function(t) {
        var tools = [];

        //Remove bash comments
        var no_comments = $scope.remove_bash_comments(t);

        var splitted = no_comments.split('\n');
        splitted.forEach(function(line){
           var results =  line.match(/\$\([\w]+__[\w\.]+__[\d]+__[\w]+\)/g);
           if (results) {
               results.forEach(function(result){
                    var splitted_ids = result.match(/\$\(([\w]+__[\w\.]+__[\d]+)__([\w]+)\)/);
                    var tool_id = splitted_ids[1] + '__2';
                    var variable_id = splitted_ids[2];
                    //Does this tool_id exist?
                    var cy_tool_node = cy.$("node[type='tool'][id='" + tool_id + "']");
                    if (cy_tool_node.length) {
                        //IT EXISTS!

                        //Does this tool has a variable with name: variable_id ?
                        var tool_tool_variables = cy_tool_node.data().variables;
                        tool_tool_variables.forEach(function(variable){
                            if (variable.name == variable_id) {
                                //Add it if it not already there
                                if (!tools.includes(tool_id)) {
                                    tools.push(tool_id);
                                }
                            }
                        });

                    }

               });
            }
        });

        return tools;
    };

    /*
    * workflows --> Step --> Button: Add Step --> Clicked 
    */
    $scope.workflow_step_add = function() {

        if (!$scope.tools_name_regexp.test($scope.workflows_step_name)) {
            $scope.workflow_step_error_message = 'Invalid step name';
            return;
        }

        $scope.workflow_step_error_message = '';

        var bash_commands = workflow_step_editor.getValue(); //BASH Commands
        var steps = $scope.get_steps_from_bash_script(bash_commands); //STEPS
        var tools = $scope.get_tools_from_bash_script(bash_commands); //TOOLS
        var input_output = $scope.get_input_outputs_from_bash_script(bash_commands); // INPUT/OUTPUTS
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
            outputs: input_output.outputs
        }];

        //Always when updating the graph, update also tab completion data for step editor! FIXME!! (bundle these things together!) A46016A6E393
        window.buildTree(step_node);
        $scope.workflow_update_tab_completion_info_to_step();


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
                    type: input_output.out ? 'output' : 'input'
                })
            }
        });

        //console.log('Input / Output Variable to add:');
        //console.log(nodes_to_add);

        if (nodes_to_add.length) {
            window.buildTree(nodes_to_add); // FIXME. SEE A46016A6E393 
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

                generateToast('Workflow successfully saved', 'green lighten-2 black-text', 'stay on');


            },
            function(data) {
                $scope.workflows_info_error_message = data['error_message'];
                generateToast($scope.workflows_info_error_message, 'red lighten-2 black-text', 'stay on');

            },
            function(statusText) {
                $scope.workflows_info_error_message = statusText;
                generateToast($scope.workflows_info_error_message, 'red lighten-2 black-text', 'stay on');
            }
        );
    };

    /*
    * Workflows --> Fork Icon --> Pressed
    */
    $scope.workflows_info_fork_pressed = function() {
        if (!$scope.username) {
            //It will never reach here. FORK is disabled in UI if user is not logged in.
            generateToast("Login to create new Workflows", 'red lighten-2 black-text', 'stay on');
            return;
        }

        $scope.workflows_info_editable = true;
        generateToast("Workflows successfully forked. Press Save after completing your edits", 'green lighten-2 black-text', 'stay on'); 

        $scope.workflow_info_forked_from = {
            'name': $scope.workflow_info_name,  
            'edit': $scope.workflow_info_edit
        }
        $scope.workflow_changes = '';
        workflow_step_editor.setReadOnly(false);

    };

    /*
    * Called from ui.js, when a user drags a worklfow in current workflow
    * workflow = {'name': ... , 'edit': '...'}
    */
    $scope.workflow_add_workflow = function(workflow) {
        //console.log('WORKFLOW TO BE ADDED:');
        //console.log(workflow);

        //Fetch info of this workflow
        $scope.ajax(
            'workflows_search_3/',
            {
                workflow_name : workflow.name,
                workflow_edit : workflow.edit
            },
            function(data) {
                workflow_cytoscape = data['workflow'];
                
                //Create the nodes that will be added 
                var nodes_to_add = []
                workflow_cytoscape.elements.nodes.forEach(function(node){ nodes_to_add.push(node.data) });
                window.buildTree(nodes_to_add);  
            },
            function(data) {
                generateToast("ERROR 81711", 'red lighten-2 black-text', 'stay on');
            },
            function(statusText) {
                generateToast("ERROR 81761", 'red lighten-2 black-text', 'stay on');
            }
        );
    };

    /*
    * worfklows --> info (right panel) --> button "Clear" --> Pressed
    */
    $scope.workflow_info_clear_pressed = function() {
        window.clear();
    };

    /*
    * worfklows --> info (right panel) --> button "FIT" --> Pressed
    */
    $scope.workflow_info_fit_pressed = function() {
        window.fit();
    };



    // WORKFLOWS END 


}); 

