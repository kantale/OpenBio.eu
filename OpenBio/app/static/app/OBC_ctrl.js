
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

app.controller("OBC_ctrl", function($scope, $sce, $http, $filter, $timeout, $log) {
    /*
    * ok some things that are here perhaps could be placed elsewhere.. 
    * https://docs.angularjs.org/api/ng/directive/ngInit
    */
    $scope.init = function() {
        $scope.username = window.username; // Empty username means non-authenticated user.
        $scope.general_success_message = window.general_success_message;
        $scope.general_alert_message = window.general_alert_message;
        $scope.password_reset_token = window.password_reset_token;
        $scope.user_is_validated = window.user_is_validated;
        $scope.profile_clients = window.profile_clients; // The execution engines of the user

        $scope.main_container_show = true;
        $scope.profile_container_show = false;
        $scope.documentation_container_show = false;

        $scope.inner_hide_all_navbar();
        $scope.inner_hide_all_error_messages();
        
        $scope.tools_search_tools_number = null; // Number of tools found on search
        //$scope.tools_search_create_disabled = true; // Navbar --> Tools/Data --> Search navbar --> Create New disabled

        $scope.tools_name_regexp = /^\w+$/ ;
        $scope.tools_version_regexp = /^[\w\.]+$/ ;
        $scope.tools_edit_regexp = /^\d+$/; 
        $scope.tools_search_warning= "";

        //$scope.set_tools_info_editable(false);
        $scope.tools_info_editable = false; // Can we edit tools_info ?

        $scope.tools_info_forked_from = null; //From which tool is this tool forked from?
        $scope.tools_info_edit_state = false; //Are we editing this tool?
        $scope.tool_changes = ''; // Changes from forked
        // TODO : fix the values (the debian versions is not correct for Dockerfile)
        $scope.os_choices = window.OBC_OS_CHOICES;

//        $scope.chooseOs=[
//            {group:'Ubuntu',name:'Ubuntu:14.04',value:'ubuntu:14.04'},
//            {group:'Ubuntu',name:'Ubuntu:16.04',value:'ubuntu:16.04'},
//            {group:'Debian',name:'Debian 8 (Jessie)',value:'jessie'},
//            {group:'Debian',name:'Debian 9 (Stretch)',value:'stretch'},
//            {group:'Debian',name:'Debian 10 (Buster)',value:'buster'}
//        ];
        
        $scope.tool_installation_init = '# Insert the BASH commands that install this tool\n# You can use these environment variables: \n# ${OBC_TOOL_PATH}: path to tools directory \n# ${OBC_DATA_PATH}: path to data directory\n\n';
        $scope.tool_validation_init = '# Insert the BASH commands that confirm that this tool is correctly installed\n# In success, this script should return 0 exit code.\n# A non-zero exit code, means failure to validate installation.\n\nexit 1\n';
    
        $scope.tool_variables = [{name: '', value: '', description: ''}];
        $scope.tools_var_jstree_id_show = true;

        $scope.workflows_info_editable = false;
        $scope.workflow_website = '';
        $scope.workflow_description = '';
        $scope.workflow_changes = '';
        $scope.workflow_info_forked_from = null; // From which workflow was this workflow forked from?
        $scope.workflows_info_edit_state = false; //Are we editing this workflow?
        $scope.workflows_info_error_message = '';
        $scope.workflows_step_name = '';
        $scope.workflows_step_main = false;
        $scope.workflows_step_description = '';
        $scope.worfklows_step_ace_init = '# Insert the BASH commands for this step.\n# You can use the variable ${OBC_WORK_PATH} as your working directory.\n# Also read the Documentation about the REPORT and the PARALLEL commands.\n\n';
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
        $scope.workflow_step_error_message = '';
        $scope.workflow_run_disabled = false; // Show the RUN button ?

        //The input and output variables of the workflow
        $scope.workflow_input_outputs = [{name: '', description: '', out:true}]; // {name: 'aa', description: 'bb', out:true}, {name: 'cc', description: 'dd', out:false}

        //Report init data:
        $scope.report_workflow_name = '';
        $scope.report_workflow_edit = '';
        $scope.report_workflow_run = '';
        $scope.report_tokens = [];
 
        //Init generic qa data
        $scope.qa_gen = {
            "tool": {},
            "workflow": {}
        };

        $scope.scheduled_main_search_changed = false; // https://openfolder.sh/django-tutorial-as-you-type-search-with-ajax
        $scope.signup_forgot_password_show = false; 

        $scope.show_sign_in = false;
        $scope.show_sign_up = false;
        $scope.show_reset_password = false;

        $scope.references_button_process_doi_activated = true;

        $scope.get_init_data();

    };

    //TODO. BETTER NAME?
    $scope.itemArray = [
        {id: 1, name: 'Tools and Data'},
        {id: 2, name: 'Workflows'}
    ];

    $scope.selected = { value: $scope.itemArray[0] };

    /*
    * https://stackoverflow.com/a/21757855/5626738 
    * https://github.com/angular/angular.js/issues/16593 
    * NOT USED! (see issue #74)
    */ 
    $scope.trust_url = function(url) {
        return $sce.trustAsResourceUrl(url);
    };

    /*
    * Anytime we change tools_info_editable we need the UI to respond.
    * Add here explicit stuff that should change when tools_info_editable change
    */ 
    $scope.set_tools_info_editable = function(b) {
        $scope.tools_info_editable = b;
    };

    /*
    * Helper function that perform ajax calls
    * success_view: what to do if data were correct and call was successful
    * fail_view: What to do if call was succesful but data where incorrect
    * fail_ajax: what to do if ajax call was incorrect / System error
    */
    $scope.ajax = function(url, data, success_view, fail_view, fail_ajax) {
        // URL should always end with '/'

        //console.log('Before Ajax, data:');
        //console.log(data);

        data.csrftoken = CSRF_TOKEN;

        $http({
            headers: {
                "Content-Type": 'application/json',
                //"Access-Control-Allow-Origin": "*", // TODO : REMOVE THIS!
                //"X-CSRFToken" : getCookie('csrftoken'),
                "X-CSRFToken" : window.CSRF_TOKEN,
            },
            method : "POST",
            url : "/platform/" + url, 
            data : data
        }).then(function mySucces(response) {
            // $scope.myWelcome = response.data;
            // alert(JSON.stringify(response));
            if (response['data']['success']) {
                //console.log('AJAX SUCCESS:');
                //console.log(response['data']['success']);
                success_view(response['data']);
            }
            else {
                //console.log('AJAX ERROR:');
                fail_view(response['data']);
            }
            
        }, function myError(response) {
            //console.log('AJAX SYSTEM ERROR:');
            //console.log(response.statusText);
            if (response.statusText) {
                fail_ajax(response.statusText);
            }
            else {
                fail_ajax('Internal Error. Server not responding');
            }
        });
    };

    /*
    * Generate a toast
    */
    $scope.toast = function(message, type) {
        if (type == 'error') {
            generateToast(message, 'red lighten-2 black-text', 'stay on');
        }
        else if (type == 'success') {
            generateToast(message, 'green lighten-2 black-text', 'stay on');
        }
        else if (type == 'warning') {
            generateToast(message, 'orange lighten-2 black-text', 'stay on');
        }
        else {
            console.warn('Error: 8133 Unknown toast type: ' + type);
        }
    };

    /*
    * Generate a "Validate" toast
    */
    $scope.validation_toast = function(message) {
        $scope.toast(message + ' <button class="waves-effect waves-light btn red lighten-3 black-text" onclick="window.OBCUI.send_validation_mail()">Validate</button>', 'error');
    };

    /*
    * Navbar --> Documentation (link) --> Clicked
    */
    $scope.documenation_navbar_clicked = function() {
        $scope.profile_container_show = false;
        $scope.main_container_show = false;
        $scope.documentation_container_show = true;
    };

    /*
    * Navbar --> Documentation (link) --> Clicked --> Cancel (link) --> Clicked
    */
    $scope.documentation_cancel_clicked = function() {
        $scope.profile_cancel_clicked();
    };

    /*
    * Profile --> Cancel --> clicked 
    */
    $scope.profile_cancel_clicked = function() {
        $scope.profile_container_show = false;
        $scope.documentation_container_show = false;
        $scope.main_container_show = true;
    };

    /*
    * Sidebar user menu --> Profile --> Clicked
    */
    $scope.navbar_profile_clicked = function() {
        $scope.main_container_show = false;
        $scope.documentation_container_show = false;
        $scope.profile_container_show = true;

        //Fetch profile info
        $scope.ajax(
            'users_search_3/',
            {
                'username': $scope.username
            },
            function(data) {
                $scope.profile_firstname = data['profile_firstname'];
                $scope.profile_lastname = data['profile_lastname'];
                $scope.profile_email = data['profile_email'];
                $scope.profile_website = data['profile_website'];
                $scope.profile_affiliation = data['profile_affiliation'];
                $scope.profile_publicinfo = data['profile_publicinfo'];
                $scope.profile_created_at = data['profile_created_at'];
                $scope.profile_clients = data['profile_clients'];

                //If the server did not return any client. Add an empty placeholder
                if (!$scope.profile_clients.length) {
                    $scope.profile_clients = [{name: '', client: ''}];
                }
                else {
                    //Push an empty 
                    $scope.profile_clients.push({name: '', client: ''});
                }

                $timeout(function(){M.updateTextFields()}, 10);
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
    * profile --> Edits --> update button --> pressed
    */
    $scope.profile_update_clicked =  function() {
        $scope.ajax(
            'users_edit_data/',
            {
                username: $scope.username,
                profile_firstname: $scope.profile_firstname,
                profile_lastname: $scope.profile_lastname,
                profile_website: $scope.profile_website,
                profile_affiliation: $scope.profile_affiliation,
                profile_publicinfo: $scope.profile_publicinfo
            },
            function(data) {
                $scope.toast('Profile data succesfully changed', 'success');
                $scope.profile_cancel_clicked(); //Hide profile
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
    * Profile --> Execution Clients --> '+' --> clicked 
    */
    $scope.profile_add_client = function(index) {
        //alert('hello!');
        //alert($scope.profile_clients[index].name);

        $scope.ajax(
            'user_add_client/',
            {
                name: $scope.profile_clients[index].name,
                client: $scope.profile_clients[index].client
            },
            function(data) {
                $scope.toast('Execution Client added succesfully', 'success');
                $scope.profile_clients = data['profile_clients'];
                $scope.profile_clients.push({name: '', client: ''});
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
    * Profile --> Execution Clients --> '-' --> clicked
    */
    $scope.profile_delete_client = function(index) {

        $scope.ajax(
            'user_delete_client/',
            {
                name: $scope.profile_clients[index].name,
            },
            function(data) {
                $scope.toast('Execution Client deleted succesfully', 'success');
                $scope.profile_clients = data['profile_clients'];
                $scope.profile_clients.push({name: '', client: ''});
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
    * DEPRECATED
    */ 
//    $scope.profile_save_pressed = function() {
//        $scope.main_container_show = true;
//        $scope.profile_container_show = false;
//    };

    /*
    * Signup --> forgot password (link) --> clicked 
    */
    $scope.signup_forgot_password_clicked = function() {
        $scope.signup_forgot_password_show = !$scope.signup_forgot_password_show;
    };

    /*
    * Hide everything 
    */
    $scope.inner_hide_all_navbar = function() {
    	$scope.show_login = false;
        //$scope.show_signup = false;
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
    * Navbar --> Sign in --> pressed 
    */
    $scope.navbar_signup_pressed = function() {
    	// $scope.inner_hide_all_navbar(); // FROM OLD UI. NOT RELEVANT IN M
        //$scope.inner_hide_all_error_and_general_messages(); // FROM OLD UI. NOT RELEVANT IN M

        //$scope.show_signup = true; // FROM OLD UI. NOT RELEVANT IN M

        //$scope.signup_error_message = '';
        //$scope.login_error_message = '';
        //$("#signModal").modal('open');
        $scope.show_sign_in = true;
        $scope.show_sign_up = false;
        $scope.show_reset_password = false;
        M.Modal.getInstance($("#signModal")).open();
    };

    /*
    * Navbar --> Sign in (pressed) --> New user? Sign up! (link) --> pressed
    */
    $scope.new_user_sign_up = function() {

        //$('#signInForm').animateCss('fadeOut', function () {});

        $scope.show_sign_in = false;
        $scope.show_sign_up = true;
        $scope.show_reset_password = false;

        $('#signUpForm').animateCss('fadeIn', function () {});
    };

    /*
    * Navbar --> Sign in (pressed) --> New user? Sign up! (link) --> pressed --> Already a member? Sign in! (link) --> pressed
    */
    $scope.new_user_sign_in = function() {

        //$('#signUpForm').animateCss('fadeOut', function () {});
        $scope.show_sign_in = true;
        $scope.show_sign_up = false;
        $scope.show_reset_password = false;
        $('#signInForm').animateCss('fadeIn', function () {});

    };

    /*
    * Send a validation email
    */
    $scope.send_validation_email = function() {
        $scope.ajax(
            'send_validation_email/',
            {},
            function(data) {
                $scope.toast('A validation email has been sent to: ' + data['email'], 'success');
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
                //$scope.show_signup = false;
                //$scope.general_success_message = 'Thank you for registering to openbio.eu . A validation link has been sent to ' + $scope.signup_email;
                //$scope.general_alert_message = '';
                $scope.toast('Thank you for registering to openbio.eu . A validation link has been sent to ' + $scope.signup_email, 'success');

                // Sign up modal close + Sign in modal close.
                $("#signModal").modal('close');
            },
            function (data) {
                //$scope.signup_error_message = data['error_message'];
                //$scope.general_success_message = '';
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                //$scope.signup_error_message = statusText;
                //$scope.general_success_message = '';
                $scope.toast(statusText, 'error');
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
                window.user_is_validated = data['user_is_validated'];
                $scope.user_is_validated = data['user_is_validated'];
                $scope.username = data['username'];
                window.profile_clients = data['profile_clients'];
                $scope.profile_clients = data['profile_clients'];

                $scope.show_login = false;

                //Close modal sign in 
                $("#signModal").modal('close');

                //console.log('$scope.user_is_validated:');
                //console.log($scope.user_is_validated);
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
    * DEPRECATED
    */
//    $scope.user_profile_update_pressed = function() {
//        $scope.ajax(
//            'user_data_set/',
//            {
//                'user_first_name': $scope.user_first_name,
//                'user_last_name': $scope.user_last_name,
//                'user_email': $scope.user_email,
//                'user_website': $scope.user_website,
//                'user_public_info': $scope.user_public_info
//            },
//            function(data) {
//                $scope.user_profile_success_message = 'User\'s profile updated';
//            },
//            function(data) {
//                $scope.user_profile_error_message = data['error_message'];
//            },
//            function(statusText) {
//                $scope.user_profile_error_message = statusText;
//            }
//        );
//    };

    /*
    * Fetch user data
    * DEPRECETATED
    */
    //$scope.inner_fetch_user_data = function() {
    //    $scope.ajax(
    //        'user_data_get/',
    //        { // This is empty deliberately. Get the user data of the logged in user.
    //        },
    //        function(data) {
    //            $scope.user_first_name = $filter('ifNull')(data['user_first_name'], '');
    //            $scope.user_last_name = $filter('ifNull')(data['user_last_name'], '');
    //            $scope.user_email = data['user_email'];
    //            $scope.user_website = $filter('ifNull')(data['user_website'], '');
    //            $scope.user_public_info = $filter('ifNull')(data['user_public_info'], '');
    //        },
    //        function(data) {
    //            $scope.user_profile_error_message = data['error_message']; // Never executed
    //        },
    //        function(statusText) {
    //            $scope.user_profile_error_message = statusText;
    //        }
    //    );
    //};

    /*
    * Navbar (after login) --> username --> pressed
    * DEPRECETATED
    */
//    $scope.navbar_username_pressed = function() {
//        $scope.inner_hide_all_navbar();
//        $scope.show_user_profile = true;
//        $scope.user_profile_success_message = '';
//        $scope.inner_fetch_user_data();
//    };


//    /*
//    * Navbar -> Login -> password reset -> clicked
//    */
//    $scope.login_password_reset_pressed = function() {
//        $scope.inner_hide_all_navbar();
//        $scope.show_reset_password_email = true;
//    };

    /*
    * Signup --> forgot password (link) clicked --> send account information (button) clicked
    */
    $scope.login_password_reset_email_send_pressed = function() {
        // reset_password_email 
        $scope.ajax(
            'reset_password_email/',
            {
                'reset_password_email': $scope.reset_password_email
            },
            function(data) {
                $scope.signup_forgot_password_show = false;
                $scope.toast('An email with instructions to reset your password was sent to ' + $scope.reset_password_email, 'success');
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
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
                'password_reset_password': $scope.reset_signup_password,
                'password_reset_confirm_password': $scope.reset_signup_confirm_password,
                'password_reset_token': $scope.password_reset_token
            },
            function(data) {
                $scope.password_reset_token = '';
                $scope.toast('Your password has been reset', 'success');
                M.Modal.getInstance($("#signModal")).close();

            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        );
    };

    /// ### SEARCH
    /*
    * Changed the main search
    */ 
    $scope.main_search_changed = function() {
        //toggle on the search progress. It will be toggled off from $scope.all_search_2() that will be called eventually
        document.getElementById('leftPanelProgress').style.display = 'block';

        // https://openfolder.sh/django-tutorial-as-you-type-search-with-ajax
        if ($scope.scheduled_main_search_changed) {
            $timeout.cancel($scope.scheduled_main_search_changed);
        }

        $scope.scheduled_main_search_changed = $timeout(function() {
            $scope.all_search_2();
        }, 700);

        //$scope.all_search_2();
    };

    /*
    * Search on all objects!
    */
    $scope.all_search_2 = function() {

        //If search criteria are empty do not perform any search
        if (!$.trim($scope.main_search).length) {
            $scope.init_search_results(); //Remove every counter
            document.getElementById('leftPanelProgress').style.display = 'none'; //Toggle off the search progress
            return;
        }

        $scope.ajax(
            'all_search_2/',
            {
                'main_search': $scope.main_search
            },
            function(data) {

                //Tools
                $scope.tools_search_tools_number = data['tools_search_tools_number'];
                angular.copy(data['tools_search_jstree'], $scope.tools_search_jstree_model);

                //Workflows
                $scope.workflows_search_tools_number = data['workflows_search_tools_number'];
                angular.copy(data['workflows_search_jstree'], $scope.workflows_search_jstree_model);  

                //Reports
                $scope.main_search_reports_number = data['main_search_reports_number'];
                angular.copy(data['reports_search_jstree'], $scope.reports_search_jstree_model);

                //References
                $scope.main_search_references_number = data['main_search_references_number'];
                angular.copy(data['references_search_jstree'], $scope.references_search_jstree_model);

                //Users
                $scope.main_search_users_number = data['main_search_users_number'];
                angular.copy(data['users_search_jstree'], $scope.users_search_jstree_model);

                // Q&As
                $scope.main_search_qa_number = data['main_search_qa_number'];
                angular.copy(data['qa_search_jstree'], $scope.qa_search_jstree_model);

                //Toggle off the search progress
                document.getElementById('leftPanelProgress').style.display = 'none';

            },
            function(data) {
                $scope.toast('Error 8922. Main search failed', 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        );
    };

    /// END OF SEARCH

    /// TOOLS 

    /*
    * Runs from init() at startup
    * Fetch init data from server. 
    */
    $scope.get_init_data = function() {
        //$scope.inner_hide_all_navbar();
        //$scope.show_tools = true;
        //$scope.tools_search_1();

        
        $scope.init_search_results();
    };

    /*
    * Initialize Research Objkect counters
    */
    $scope.init_search_results = function() {

        //-1 values mean: DO NOT SHOW

        $scope.tools_search_tools_number = -1
        angular.copy([], $scope.tools_search_jstree_model);

        //Workflows
        $scope.workflows_search_tools_number = -1
        angular.copy([], $scope.workflows_search_jstree_model);  

        //Reports
        $scope.main_search_reports_number = -1
        angular.copy([], $scope.reports_search_jstree_model);

        //References
        $scope.main_search_references_number = -1
        angular.copy([], $scope.references_search_jstree_model);

        //Users
        $scope.main_search_users_number = -1
        angular.copy([], $scope.users_search_jstree_model);

        // Q&As
        $scope.main_search_qa_number = -1
        angular.copy([], $scope.qa_search_jstree_model);

    }

    /*
    *  Get the number of all tools
    * NOT USED !
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
//    $scope.tools_search_2 = function() {
//        $scope.ajax(
//            'tools_search_2/',
//            {
//                'tools_search_name': $scope.tools_search_name,
//                'tools_search_version': $scope.tools_search_version,
//                'tools_search_edit': $scope.tools_search_edit
//            },
//            function(data) {
//                $scope.tools_search_tools_number = data['tools_search_tools_number'];
//                angular.copy(data['tools_search_jstree'], $scope.tools_search_jstree_model);
//
//            },
//            function(data) {
//
//            },
//            function(statusText) {
//
//            }
//        );
//    };

    /*
    *  Search workflows after search items changed
    */
//    $scope.workflows_search_2 = function() {
//        $scope.ajax(
//            'workflows_search_2/',
//            {
//                'workflows_search_name': $scope.workflows_search_name,
//                'workflows_search_edit': $scope.workflows_search_edit
//            },
//            function(data) {
//                $scope.workflows_search_tools_number = data['workflows_search_tools_number'];
//                angular.copy(data['workflows_search_jstree'], $scope.workflows_search_jstree_model);  
//
//            },
//            function(data) {
//                $scope.toast(data['error_message'], 'error');
//            },
//            function(statusText) {
//                $scope.toast(statusText, 'error');
//            }
//        );
//    };


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

                //Hide all right panel accordions
                $scope.hide_all_right_accordions('tools');

                //Open tool right panel windows
                document.getElementById('createToolDataDiv').style.display = 'block';
                M.Collapsible.getInstance($('#createToolDataAccordion')).open(0);


                $scope.tool_info_username = data['username'];
                $scope.tool_website = data['website'];
                $scope.tool_description = data['description'];
                $scope.tool_description_html = data['description_html'];
                $scope.tool_changes = data['changes'];
                $scope.tool_info_created_at = data['created_at'];
                $scope.tool_score = data['tool_score'];
                $scope.tool_voted = data['tool_voted'];
                $scope.tools_info_forked_from = data['forked_from'];
                $scope.tools_info_name = item.name;
                $scope.tools_info_version = item.version;
                $scope.tools_info_edit = item.edit;
                $scope.tools_info_success_message = '';
                $scope.tools_info_error_message = '';
                $scope.tools_info_draft = data['draft'];

                //Set chip data
                window.OBCUI.set_chip_data('toolChips', data['tool_keywords']);
                window.OBCUI.chip_disable('toolChips');

                angular.copy(data['dependencies_jstree'], $scope.tools_dep_jstree_model);
                angular.copy(data['variables_js_tree'], $scope.tools_var_jstree_model);
                $scope.tool_variables = data['variables'];

                // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/find
                // find and save the selected os when the user search specific tool
                //$scope.tool_os_choices = $scope.os_choices.find(function(element){return element.value === data['tool_os_choices'][0]})  ; // Take just the first. The model allows for multiple choices
                $scope.tool_os_choices_tmp = data['tool_os_choices']; 

                //console.log($scope.tool_os_choices_tmp);

                //The server returns data['tool_os_choices'] which has the structure that ui-select "wants"
                //Nevertheless $scope.tool_os_choices is the model for the select element.
                //This variable (tool_os_choices) MUST HAVE items from the variable in the ng-repeat attribute (in our case $scope.os_choices)
                //Since os_choices is in the ng-repeat attribute, it has a private $$hashKey key, which might differ from run to run.  
                //As an effect we cannot simply do: $scope.tool_os_choices = data['tool_os_choices']; 
                //Here we make sure that tool_os_choices has identical elements with the ones in os_choices.
                //Is there any better way to do this?
                $scope.tool_os_choices = [];
                $scope.os_choices.forEach(function (element){
                    for (var i=0; i<$scope.tool_os_choices_tmp.length; i++) {
                        if ($scope.tool_os_choices_tmp[i].value === element.value) {
                            $scope.tool_os_choices.push(element);
                        }
                    }
                });

                //console.log('$scope.tool_os_choices:');
                //console.log($scope.tool_os_choices);
                $('#tool_os_choices_select').formSelect();

                tool_installation_editor.setValue(data['installation_commands'], -1);
                tool_validation_editor.setValue(data['validation_commands'], -1);
                tool_installation_editor.setReadOnly(true);
                tool_validation_editor.setReadOnly(true);
                $scope.tools_var_jstree_id_show = true; // Show variable/dependency tree

                $scope.tool_info_validation_status = data.validation_status;
               // $scope.tool_info_validation_stdout = data.stdout;
               // $scope.tool_info_validation_stderr = data.stderr;
                $scope.tool_info_validation_errcode = data.errcode;
                $scope.tool_info_validation_created_at = data.validation_created_at;

                $timeout(function(){M.updateTextFields()}, 10); //Update text fields so that we don't get a crumbled text input

                $scope.tool_keywords = data['tool_keywords'];
  
                $scope.qa_gen['tool'].object_pk = data['tool_pk'];
                $scope.qa_gen['tool'].qa_thread = data['tool_thread'];
                $scope.qa_gen['tool'].qa_comment_id = data['tool_comment_id'];
                $scope.qa_gen['tool'].qa_comment_title = data['tool_comment_title'];
                $scope.qa_gen['tool'].qa_comment_created_at = data['tool_comment_created_at'];
                $scope.qa_gen['tool'].qa_comment_username = data['tool_comment_username'];
            },
            function (data) {
                $scope.toast('Error 5429', 'error');
            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
            }
        );
    };

    /*
    *   navbar --> Tools --> Search sidebar --> Name or Version or Name Change
    *   See also: workflows_search_input_changed 
    */
//    $scope.tools_search_input_changed = function() {
//
//        //if ((!$scope.tools_search_name) && (!$scope.tools_search_version) && (!$scope.tools_search_edit)) {
//        //    $scope.tools_search_warning = '';
//        //    return;
//        //}
//
//        //if (!$scope.username) {
//        //    $scope.tools_search_warning = 'Login to create new tools';
//        //    return;
//        //}
//
//        //Check tool name
//        if ($scope.tools_search_name) {
//            if (!$scope.tools_name_regexp.test($scope.tools_search_name)) {
//                $scope.tools_search_warning = 'Invalid Tool name';
//                return;
//            }
//        }
//
//        //Check tool version
//        if ($scope.tools_search_version) {
//            if (!$scope.tools_version_regexp.test($scope.tools_search_version)) {
//                $scope.tools_search_warning = 'Invalid Version value';
//                return;
//            }
//        }
//
//
//        //Check edit version
//        //if (!$scope.tools_edit_regexp.test($scope.tools_search_edit)) {
//        //    $scope.tools_search_warning = 'Invalid Edit value';
//        //    return;
//        //};
//
//        //Check edit version
//        if ($scope.tools_search_edit) {
//            if (!$scope.tools_edit_regexp.test($scope.tools_search_edit)) {
//                $scope.tools_search_warning = 'Invalid Edit value';
//                return;
//            }
//            $scope.tools_search_warning = 'Edit value should be empty to create new tools';
//            $scope.tools_search_2();
//            return; 
//        }
//
//        //Everything seems to be ok
//        $scope.tools_search_warning = '';
//        $scope.tools_search_2();
//    };

    /*
    *   navbar --> Tools --> Search sidebar --> Combobox Workflows --> Name or Version or Name Change
    *   See also tools_search_input_changed
    */
//    $scope.workflows_search_input_changed = function() {
//        //Check workflow name
//        if ($scope.workflows_search_name) {
//            if (!$scope.tools_name_regexp.test($scope.workflows_search_name)) {
//                $scope.workflows_search_warning = 'Invalid Workflow name';
//                return;
//            }
//        }
//
//        //Check edit value
//        if ($scope.workflows_search_edit) {
//            if (!$scope.tools_edit_regexp.test($scope.workflows_search_edit)) {
//                $scope.workflows_search_warning = 'Invalid Edit value';
//                return;
//            }
//            $scope.workflows_search_warning = 'Edit value should be empty to create new Workflows';
//            $scope.workflows_search_2(); 
//            return; 
//        }
//
//        //Everything seems to be ok
//        $scope.workflows_search_warning = '';
//        $scope.workflows_search_2();
//
//    };


    /*
    * Create new tool button pressed.
    * All checks are ok.
    */
    $scope.tools_plus_button_clicked = function(is_new) {

        //Is user registered?
        if (!$scope.username) {
            $scope.toast('Login to create a new Tool or Data!', 'error');
            return;
        }

        //Is user's email validated?
        if (!$scope.user_is_validated) {
            $scope.validation_toast('Validate your email to create a new Tool or Data!');
            return;
        }

        $scope.tools_search_warning = '';

        //Close Workflow right panel
        //window.cancelWorkflowBtn_click();

        //Triggers animation to open right window
        //window.createToolDataBtn_click();

        //Hide all right panel accordions
        $scope.hide_all_right_accordions('tools');

        //Open tool right panel windows
        document.getElementById('createToolDataDiv').style.display = 'block';
        M.Collapsible.getInstance($('#createToolDataAccordion')).open(0);


        //$scope.show_tools_info = true;
        //$scope.show_workflows_info = false; // TODO. THIS SHOULDN'T BE HERE

        $scope.set_tools_info_editable(true);
        $scope.tools_info_draft = true;
        $scope.tools_info_edit_state = false;

        if (!is_new) {
            //This is not a new tool. So.. left values unchanged.
            return;
        }

        //$scope.tools_info_editable = true;
        $scope.tool_info_created_at = null;
        $scope.tools_info_forked_from = null;
        $scope.tools_info_name = ''; // $scope.tools_search_name;
        $scope.tools_info_version = ''; // $scope.tools_search_version;
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

        // Default operating system is ubuntu:16.04 . FIXME!
        // $scope.tool_os_choices = $scope.os_choices.find(function(element){return element.value === 'ubuntu:16.04'});

        $scope.tool_os_choices = [];
        $scope.os_choices.forEach(function (element){
            if (element.value == 'posix') {
                $scope.tool_os_choices.push(element);
            }
        });


        //console.log('$scope.os_choices:');
        //console.log($scope.os_choices);
        //console.log('$scope.tool_os_choices:');
        //console.log($scope.tool_os_choices);
        //$('#tool_os_choices_select').formSelect();
        $timeout(function(){$('#tool_os_choices_select').formSelect();}, 100);

        //Delete all chip
        window.OBCUI.delete_all_chip_data('toolChips');
        window.OBCUI.chip_enable('toolChips'); // Enable them
    };

    /*
    * Tools/Data --> CANCEL (header) --> Clicked
    */
    $scope.tools_button_cancel_clicked = function() {
        $scope.hide_all_right_accordions('');
        $scope.tools_info_editable = false;
    };
    /*
    * Workflows --> CANCEL (header) --> Clicked
    */
    $scope.workflows_button_cancel_clicked = function() {
        $scope.hide_all_right_accordions('');
        $scope.workflows_info_editable = false;
    };

    /*
    * Reports --> CANCEL (header) --> Clicked
    */
    $scope.references_button_cancel_clicked = function() {
        $scope.hide_all_right_accordions('');
        $scope.references_info_editable = false;
    };

    /*
    * QAs --> CANCEL (header) --> Clicked
    */
    $scope.qas_button_cancel_clicked = function() {
        $scope.hide_all_right_accordions('');
        $scope.qa_info_editable = false;
    };

    /*
    * Navbar -> Tools/Data --> Appropriate input --> "Create New" button --> Pressed
    */
//    $scope.tools_search_create_new_pressed = function() {
//
//        if (!$scope.username) {
//            //$scope.tools_info_error_message = 'Login to create new tools';
//            $scope.tools_search_warning = 'Login to create new tools';
//            return;
//        }
//
//        //Check if tool search name and version are non empty 
//        if (!($scope.tools_search_name && $scope.tools_search_version)) {
//            $scope.tools_search_warning = 'Name and Version should not be empty';
//            return;
//        }
//
//        //Edit SHOULD BE EMPTY!
//        if ($scope.tools_search_edit) {
//            $scope.tools_search_warning = 'An edit number will be assigned after you save your tool (leave it empty)';
//            return;
//        }
//
//        //If workflows are editable then raise a modal to ask user if she want to lose all edits.
//        if ($scope.workflows_info_editable) {
//            $scope.tools_search_raise_edit_are_you_sure_modal('TOOLS_CREATE_BUTTON');
//            return;
//        }
//
//        // Everything seems ok.
//        $scope.tools_search_create_new_pressed_ok();
//
//    };

    /*
    * The name of the workflow has changed
    * The variable workflow_info_name has changed
    */
    $scope.workflow_info_name_changed = function() {
        cy.$('node[type="workflow"][!belongto]').data('label', $scope.workflow_info_name);
    };

    /*
    * Called when ANY "+" button is clicked and when ANY jstree node is clicked!
    */
    $scope.raise_modal_check = function() {
        if ($scope.tools_info_editable) {
            $scope.modal_message = 'You have unsaved info in Tools/Data.';
            return true;
        }
        if ($scope.workflows_info_editable) {
            $scope.modal_message = 'You have unsaved info in Workflows.';
            return true;
        }

        return false;
    };

    /*
    * Workflows --> "+" (Create new) --> pressed 
    * is_new: Is this a new workflow?
    */
    $scope.workflows_plus_button_clicked = function(is_new) {

        //Check if user is registered
        if (!$scope.username) {
            $scope.toast('Login to create a new workflow!', 'error');
            return
        }

        //Is user's email validated?
        if (!$scope.user_is_validated) {
            $scope.validation_toast('Validate your email to create a new workflow!');
            return;
        }

        //Close tool accordion
        //$scope.set_tools_info_editable(false);
        //$scope.tools_info_editable = false;
        //window.cancelToolDataBtn_click();

        //Open Workflows accordion
        //window.createWorkflowBtn_click();

        //Hide all other right panel components
        $scope.hide_all_right_accordions('workflows');

        //Show workflows accordion
        document.getElementById('workflowsRightPanel').style.display = 'block';
        M.Collapsible.getInstance($('#workflowsRightPanelGeneralAccordion')).open(0);

        if (!is_new) {
            return; // Do not clear UI
        }

        $scope.workflow_info_name = '';
        $scope.workflows_info_username = $scope.username;
        $scope.workflows_info_editable = true; // Workflow right panel is editable
        $scope.workflows_info_edit_state = false; // We clicked plus to create a new workflow. This is not an editing state
        $scope.workflows_info_draft = true;
        $scope.workflow_info_created_at = null;
        $scope.workflow_info_forked_from = null;
        $scope.workflow_website = '';
        $scope.workflow_description = '';

        //Clear keyword chips
        window.OBCUI.delete_all_chip_data('workflowChips');
        window.OBCUI.chip_enable('workflowChips');

        //Clear graph
        $scope.workflow_info_clear_pressed();

        //Clear STEP
        $scope.workflows_step_name = '';
        $scope.workflows_step_main = false;
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
    * Get a list of dependecies for the current tool
    */
    $scope.get_tool_dependencies = function() {
        //Get the dependencies
    
        var tool_dependencies = [];
        for (var i=0; i<$scope.tools_dep_jstree_model.length; i++) {
            //Add only the roots of the tree
            if ($scope.tools_dep_jstree_model[i].parent === '#') {
                tool_dependencies.push($scope.tools_dep_jstree_model[i]); //Although we only need name, version, edit, we pass the complete object 
            }
        }

        return tool_dependencies;
    };


    /*
    * Navbar --> Tools/data --> Appropriate input --> "Create New" button --> Pressed --> Filled input --> Save (button) --> Pressed
    * See also: workflows_create_save_pressed 
    * save tool save add tool add 
    */
    $scope.tool_create_save_pressed = function() {

        //Check if tool name and version are valid
        if (!$scope.tools_name_regexp.test($scope.tools_info_name)) {
            $scope.toast('Invalid tool name. Allowed characters are: a-z, A-Z, 0-9, _', 'error');
            return;
        }

        if ($scope.tools_info_name.includes('__')) {
            $scope.toast('Tool name cannot include __', 'error');
            return;            
        }

        if (!$scope.tools_version_regexp.test($scope.tools_info_version)) {
            $scope.toast('Invalid tool version. Allowed characters are: a-z, A-Z, 0-9, _, .', 'error');
            return;
        }

        if ($scope.tools_info_version.includes('__')) {
            $scope.toast('Tool version cannot contain "__"', 'error');
            return;
        }

        if ($scope.tools_info_version.includes('..')) {
            $scope.toast('Tool version cannot contain ".."', 'error');
            return;
        }

        //Get the dependecies of this tool
        var tool_dependencies = $scope.get_tool_dependencies();

        //console.log('tool_create_save_pressed: tool_os_choices');
        //console.log($scope.tool_os_choices);

        $scope.ajax(
            'tools_add/',
            {   'username':$scope.username,
                'tools_search_name': $scope.tools_info_name,
                'tools_search_version': $scope.tools_info_version,
                'tools_search_edit': $scope.tools_info_edit, // We need this in case this is a draft and we need to edit it
                'tool_website': $scope.tool_website,
                'tool_description': $scope.tool_description,
                'tool_keywords': window.OBCUI.get_chip_data('toolChips'),
                'tool_forked_from': $scope.tools_info_forked_from,
                'tool_changes': $scope.tool_changes,
                'tool_os_choices' : $scope.tool_os_choices,
                'tool_dependencies': tool_dependencies,
                'tool_variables': $scope.tool_variables,
                'tool_installation_commands': tool_installation_editor.getValue(),
                'tool_validation_commands': tool_validation_editor.getValue(),
                'tool_edit_state' : $scope.tools_info_edit_state // Are we editing this tool ?
            },
            function(data) {
                $scope.tools_info_success_message = 'Tool/Data successfully saved';
                $scope.toast($scope.tools_info_success_message, 'success');
                $scope.set_tools_info_editable(false);
                //$scope.tools_info_editable = false;
                $scope.tool_edit_state = false;
                $scope.tool_info_created_at = data['created_at'];
                $scope.tools_info_edit = data['edit'];
                //$scope.tools_search_input_changed(); //Update search results

                //Disable chip
                window.OBCUI.chip_disable('toolChips');

                //Set installation and validation editors to readonle 
                tool_installation_editor.setReadOnly(true);
                tool_validation_editor.setReadOnly(true);
                $scope.tools_var_jstree_id_show = false;  // Hide tool + variables dependency tree

                //Load Chips
                $scope.tool_keywords = window.OBCUI.get_chip_data('toolChips');

                //Get markdown
                $scope.tool_description_html = data['description_html'];

                //Load comment thread
                $scope.qa_gen['tool'].object_pk = data['tool_pk'];
                $scope.qa_gen['tool'].qa_thread = data['tool_thread'];

                //Set Score, and upvote / downvotes arrows
                $scope.tool_score = data['score'];
                $scope.tool_voted = data['voted']; // {'up': false, 'down': false};

                //This tool is not any more in an edit state (if it was)
                $scope.tools_info_edit_state = false;

                //EXPERIMENTAL. UPDATE SEARCH RESULTS
                $scope.all_search_2();
            },
            function(data) {
                $scope.tools_info_error_message = data['error_message'];
                $scope.toast($scope.tools_info_error_message, 'error');
            },
            function(statusText) {
                $scope.tools_info_error_message = statusText;
                $scope.toast($scope.tools_info_error_message, 'error');
            }
        );
    };

    /*
    * Tool in draft mode --> EDIT button --> pressed 
    * tool edit tool . edit pressed 
    */
    $scope.tool_edit_pressed = function() {
        $scope.tools_info_editable = true;
        $scope.tools_info_edit_state = true;
        tool_installation_editor.setReadOnly(false);
        tool_validation_editor.setReadOnly(false);

        //If the variables fetched are empty, add a dummy variable for the UI
        if (!$scope.tool_variables.length) {
            $scope.tool_variables = [{name: '', value: '', description: ''}];
        }
    };

    /*
    * Workflow in draft mode --> EDIT button --> pressed 
    * workflow edit workflow . edit pressed 
    */
    $scope.workflow_edit_pressed = function() {
        $scope.workflows_info_edit_state = true;
        $scope.workflows_info_fork_pressed('EDIT');
    };

    /*
    * We have a "Yes" response from the "are you sure" modal. 
    * Diseminate on the action.
    */
    $scope.are_you_sure_modal_post_action = function(action) {
        if (action == 'DELETE' || action == 'FINALIZE') {
            $scope.ro_finalize_delete_pressed($scope.warning_modal_ro, $scope.warning_modal_action, true);
            return;
        }
        else if (action == 'DISCONNECT') {
            $scope.disassociate_workflow_tool($scope.node, true);
            return;
        }
        else if (action == 'DELETENODE') {
            $scope.workflow_cytoscape_delete_node($scope.node_id, true);
            return;
        }
        else if (action == 'DELETEREPORT') {
            $scope.report_refresh($scope.report_refresh_action, true);
            return;
        }
    };

    /*
    * Tool/Workflow in draft mode --> FINALIZE button --> pressed 
    * tool finalize tool
    * workflow finalize workflow  
    * actions: 
    *   FINALIZE --> finalize tool
    *   DELETE --> Delete toool
    * confirm: If False: Raise confirm Modal. If True: Do it!
    * ro : 'tool' / 'workflow'
    */
    $scope.ro_finalize_delete_pressed = function(ro, action, confirm) {

        $scope.warning_modal_ro = ro;
        if (action == 'DELETE' && !confirm) {
            $scope.warning_modal_message = 'This ' + ro +' will be permanently deleted. Are you sure?';
            $scope.warning_modal_action = 'DELETE';
            $('#deleteModal').modal('open');
            return;
        }
        else if (action == 'FINALIZE' && !confirm) {
            $scope.warning_modal_message = 'You will not be able to make any more changes to this ' + ro + '. Are you sure?';
            $scope.warning_modal_action = 'FINALIZE';
            $('#deleteModal').modal('open');
            return;
        }

        //Form the object that we will send to backend
        var to_send = {};
        if (ro == 'tool') {
            to_send.tools_info_name = $scope.tools_info_name;
            to_send.tools_info_version = $scope.tools_info_version;
            to_send.tools_info_edit = $scope.tools_info_edit; // We need this in case this is a draft and we need to edit it
        }
        else if (ro == 'workflow') {
            to_send.workflow_info_name = $scope.workflow_info_name;
            to_send.workflow_info_edit = $scope.workflow_info_edit; // We need it in case this is a a draft and we need to edit it
        }
        to_send.action = action;
        to_send.ro = ro;


        $scope.ajax(
            'ro_finalize_delete/',
            to_send,
            function (data) {
                if (ro == 'tool') {
                    if (action == 'FINALIZE') {
                        $scope.tools_info_draft = false;
                        $scope.tools_info_edit_state = false;
                        $scope.tools_info_editable = false;
                        $scope.toast('Tool is finalized!', 'success');
                        $scope.all_search_2(); // Update search results
                    }
                    else if (action == 'DELETE') {
                        $scope.toast('Tool is deleted!', 'success');
                        $scope.tools_button_cancel_clicked(); // Empty all right space
                        $scope.all_search_2(); // Update search results

                    }
                }
                else if (ro == 'workflow') {
                    if (action == 'FINALIZE') {
                        $scope.workflows_info_draft = false;
                        $scope.workflows_info_edit_state = false;
                        $scope.workflows_info_editable = false;
                        cy.$('node[type="workflow"][!belong]').data({'draft':false}); // Set root workflow as non draft 
                        $scope.toast('Workflow is finalized!', 'success');
                        $scope.all_search_2(); // Update search results
                    }
                    else if (action == 'DELETE') {
                        $scope.toast('Workflow is deleted!', 'success');
                        $scope.workflows_button_cancel_clicked(); // Empty all right space
                        $scope.all_search_2(); // Update search results
                    }
                }
            },
            function (data) {
                $scope.toast(data['error_message'], 'error');
            },
            function (statusText) {
                $scope.toast(statusText, 'error');
            }

        );
    };


    /*
    * Navbar --> tools/data --> Appropriate Input --> List Item --> clicked
    * tool node clicked tool clicked 
    */
    $scope.tools_search_show_item = function(item) {
        $scope.show_tools_info = true;
        $scope.show_workflows_info = false;
        $scope.set_tools_info_editable(false);
        //$scope.tools_info_editable = false;
        $scope.tools_search_3(item);
        M.updateTextFields(); // The text inputs in Materialize needs to be updated after change.
    };

    /*
    * Navbar --> tools/data --> Appropriated Input (search) --> List Item --> clicked --> Fork --> pressed
    * tool fork tool
    */
    $scope.tool_info_fork_pressed = function() {

        if (!$scope.username) {
            $scope.tools_info_error_message = 'Login to create new tools';
            return;
        }

        //Is user's email validated?
        if (!$scope.user_is_validated) {
            $scope.validation_toast('Validate your email to create a new Tool or Data!')
            return;
        }

        $scope.set_tools_info_editable(true);
        //$scope.tools_info_editable = true;
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

        // Set the operating system. Practically we are setting tool_os_choices = tool_os_choices ... But that was the only way I could do it
        // $scope.tool_os_choices = $scope.os_choices.find(function(element){return element.value === $scope.tool_os_choices.value});

        //console.log('tool_info_fork_pressed: tool_os_choices:');
        //console.log($scope.tool_os_choices);


        $timeout(function(){$('#tool_os_choices_select').formSelect();}, 100);

        // The new tool is unvalidated
        $scope.tool_info_validation_status = 'Unvalidated';
        $scope.tool_info_validation_created_at = null;

        // Enable chip edit
        window.OBCUI.chip_enable('toolChips'); // Enable them

        // Every fork os a draft
        $scope.tools_info_draft = true;
    };

    /*
    *  Create the bash script that we will submit to the controller for validation
    */
    $scope.create_bash_script_for_validation = function(installation_bash, validation_bash) {
        return installation_bash + '\n' + validation_bash;
    };

    /*
    * Called from $scope.tool_info_validate_pressed upon receiving "queued" status
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
                $scope.tool_info_validation_status = 'Queued';
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
    * Navbar --> tools/data --> Existing tool --> Installation (tab, pressed) --> Validate (pressed)
    */
    $scope.tool_info_validate_pressed = function() {
        // var ossel = $scope.osSelection;
        var installation_bash = tool_installation_editor.getValue();
        var validation_bash = tool_validation_editor.getValue();

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
                ostype: $scope.tool_os_choices.value // user selected os
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
                $scope.toast('Validation Server is unavailable. Please try later.', 'error');
            }
        );
    };

    /*
    * Navbar --> tools/data --> Existing tool --> Installation (tab, pressed) --> Validate refresh (pressed)
    */ 
    $scope.tool_info_validate_refresh_pressed = function() {
        $scope.ajax(
            'tool_validation_status/',
            {
                tool: {
                    name: $scope.tools_info_name,
                    version: $scope.tools_info_version,
                    edit: $scope.tools_info_edit                    
                }
            },
            function(data) {
                $scope.tool_info_validation_status = data['validation_status'];
            //    $scope.tool_info_validation_stdout = data.stdout;
            //    $scope.tool_info_validation_stderr = data.stderr;
                $scope.tool_info_validation_errcode = data.errcode;
                // console.log('DATA');
                // console.log(data);

                
                $scope.tool_info_validation_created_at = data['validation_created_at'];
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
    * Navbar --> tools/data --> Aprioprate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "-" (variables) (pressed)
    */
    $scope.tools_info_remove_variable = function(index) {
        // $('.tooltipped').tooltip('close');
        $scope.tool_variables.splice(index, 1);
    };

    /*
    * If there is an environment variable declared, check that it referres only OBC_*_PATH variables
    * See also: https://github.com/kantale/OpenBioC/issues/137
    */
    $scope.check_basic_environment_vars = function(value) {
        var rs=[
            /\$\{(\w+)\}/g, // Get all ${XYZ}
            /\$(\w+)/g, // Get all $XYZ
        ] 

        var env_vars = ['OBC_TOOL_PATH', 'OBC_DATA_PATH', 'OBC_WORK_PATH'];

        for (var i=0; i<rs.length; i++) {
            var r=rs[i];
            var match = r.exec(value);
            while (match!=null) {
                var var_name = match[1];
                if (!env_vars.includes(var_name)) {
                    return 'The only variables that you can use are: ${OBC_TOOL_PATH}, ${OBC_DATA_PATH} and ${OBC_WORK_PATH}';
                }
                match = r.exec(value);
            }            
        }

        return '';
    };

    /*
    * Navbar --> tools/data --> Appropriate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> "+" (variables) (pressed)
    */
    $scope.tools_info_add_variable = function() {
        // $('.tooltipped').tooltip('close');

        //These are essentially the same controls we do for tool version and tool name
        //Check if tool variable name and version are valid

        //Take the last variable
        var last_variable = $scope.tool_variables[$scope.tool_variables.length-1];

        if (!$scope.tools_name_regexp.test(last_variable.name)) {
            $scope.toast('Invalid variable name. Allowed characters are: a-z, A-Z, 0-9, _', 'error');
            return;
        }

        if (last_variable.name.includes('__')) {
            $scope.toast('Variable name cannot include __', 'error');
            return;
        }

        //Check for environment variables in the value
        var check = $scope.check_basic_environment_vars(last_variable.value);
        if (check) {
            $scope.toast(check, 'error');
            return;
        }

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
                    throw "ERROR: 3988"; // This should never happen
                }
                //Delete the node
                tree.splice(this_index, 1);
                break;
            }
        }
    };

    /*
    * Get the dependencies of this tool
    * This is called from ui.js
    * what_to_do == 1: drag and drop FROM SEARCH TREE TO DEPENDENCY TREE
    * what_to_do == 2: dran and drop FROM SEARCH TREE TO CYTOSCAPE CYWORKFLOW DIV
    */
    $scope.tool_get_dependencies = function(tool, what_to_do) {

        // If the tools_info_editable is not editbaled we are not allowed to drop items 
        if (what_to_do == 1 && (!$scope.tools_info_editable)) {
            return;
        }

        $scope.ajax(
            'tool_get_dependencies/',
            {
                'tool_name': tool.name,
                'tool_version': tool.version,
                'tool_edit': tool.edit,
                'what_to_do': what_to_do // We are passing also what_to_do. If what_to_do==2 then also fetch installation instructions
            },
            function(data) {

                if (what_to_do == 1) { // DRAG FROM TOOL SEARCH TREE TO DEPENDENCY TREE
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
                            //$scope.tools_info_error_message = 'This tool is already in the dependency tree';
                            $scope.toast('This tool is already in the dependency tree', 'error');
                            return;
                        }
                    }

                    //Check if any of the dependencies that we imported contains... the tool itself!
                    for (var i=0; i<data['dependencies_jstree'].length; i++) {
                        var this_tool = data['dependencies_jstree'][i];
                        if (this_tool.name == $scope.tools_info_name && this_tool.version == $scope.tools_info_version && this_tool.edit == $scope.tools_info_edit) {
                            $scope.toast('You cannot add a tool as a dependency to.. itself!', 'error');
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
                else if (what_to_do == 2) { //drag and drop FROM TOOLS SEARCH TREE TO CYTOSCAPE WORKFLOW DIV
                    //console.log('UPDATE THE GRAPH WITH: dependencies_jstree');
                    //console.log(data['dependencies_jstree']);
                    //console.log('variables_jstree:');
                    //console.log(data['variables_jstree']);

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

                    //Make sure that all dependencies_jstree nodes have:
                    // a variables field
                    // a belongto fields
                    // a disconnencted field
                    for (var i=0; i<data['dependencies_jstree'].length; i++) {
                        if (typeof data['dependencies_jstree'][i].variables !== 'undefined') {
                        }
                        else {
                            data['dependencies_jstree'][i].variables = [];
                        }
                        data['dependencies_jstree'][i].belongto = null;
                        data['dependencies_jstree'][i].disconnected = false;
                    }

                    //console.log('dependencies_jstree:');
                    //console.log(data['dependencies_jstree']);

                    //window.buildTree(data['dependencies_jstree'], {name: $scope.workflow_info_name, edit: null}); //FIXME SEE A46016A6E393
                    window.buildTree(data['dependencies_jstree'], {name: 'root', edit: null}); //FIXME SEE A46016A6E393 
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

                    //console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {
                    "icons": false
                }
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
            //plugins : ['dnd', 'types'],
            plugins: ['dnd'],
            //types : {default : {icon : 'fa fa-cog'}},
            dnd: {
                is_draggable : function(node) {
                    return true;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []
    };

    /*
    * Should the changes on the model, be reflected on the tree? 
    */
    $scope.tools_search_jstree_config_apply = function() {
        return true;
    };
    $scope.reports_search_jstree_config_apply = function() {
        return true;
    };
    $scope.references_search_jstree_config_apply = function() {
        return true;
    };
    $scope.users_search_jstree_config_apply = function() {
        return true;
    };
    $scope.qa_search_jstree_config_apply = function() {
        return true;
    };



    $scope.tools_search_jstree_model_init = [];
    $scope.tools_search_jstree_model = [];
    angular.copy($scope.tools_search_jstree_model_init, $scope.tools_search_jstree_model);

    $scope.reports_search_jstree_model_init = [];
    $scope.reports_search_jstree_model = [];
    angular.copy($scope.reports_search_jstree_model_init, $scope.reports_search_jstree_model);

    $scope.references_search_jstree_model_init = [];
    $scope.references_search_jstree_model = [];
    angular.copy($scope.references_search_jstree_model_init, $scope.references_search_jstree_model);

    $scope.users_search_jstree_model_init = [];
    $scope.users_search_jstree_model = [];
    angular.copy($scope.users_search_jstree_model_init, $scope.users_search_jstree_model);

    $scope.qa_search_jstree_model_init = [];
    $scope.qa_search_jstree_model = [];
    angular.copy($scope.qa_search_jstree_model_init, $scope.qa_search_jstree_model);


    /* 
    * Raise a modal "all your edits will be list. Are you aure?". Raised when:
    * 1. Click an item in the jstree tools
    * 2. Click Cancel in Tool Search
    * the results are capture by function: tools_search_jstree_modal_editable(yes_no)
    */
//    $scope.tools_search_raise_edit_are_you_sure_modal = function(who_called_me) {
//        M.Modal.getInstance($("#warningModal")).open();
//        $("#warningModal").data('who_called_me', who_called_me);
//
//    };

    /*
    * An item in tool tree on the search panel is selected
    * Defined in: tree-events="select_node:tools_search_jstree_select_node" 
    * See also: workflows_search_jstree_select_node 
    */
    $scope.tools_search_jstree_select_node = function(e, data) {
        //console.log(data.node.data.name);

        if ($scope.tools_info_editable) {
            $scope.toast('There are unsaved info on Tools/Data. Save or press Cancel', 'error');
            return;
        }

        $scope.tools_search_show_item(data.node.data);
        return;

        //Check if the tool pane is editable. If we do not include this check. All edits will be lost!
        //If it is editable, show a modal (see function tools_search_jstree_modal_editable)

        //Save in a variable the data of the item that has been clicked
//        $scope.modal_data = data;
//        if ($scope.tools_info_editable || $scope.workflows_info_editable) {
//            $scope.tools_search_raise_edit_are_you_sure_modal('TOOL_SEARCH_JSTREE');
//        }
//        else {
//            // Pressed an item in tool search tree, but the tool_info is not editable
//            // Simulate a YES response from warning modal
//            $("#warningModal").data('who_called_me', 'TOOL_SEARCH_JSTREE');
//            $scope.tools_search_jstree_modal_editable(true);
//        }
//
    };

    /*
    * A node in the reports search js tree is clicked .
    */
    $scope.reports_search_jstree_select_node = function(e, data) {
        //console.log('Reports node clicked');
        //console.log(data);

        //The user might have clicked on a workflow node.
        if (data.node.data.type == 'report') {

            $scope.report_workflow_run = data.node.data.run;
            $scope.reports_search_3({run: data.node.data.run});
        }
    };

    /*
    * A node on the references search js tree is clicked.
    */
    $scope.references_search_jstree_select_node = function(e, data) {
        //console.log('References node clicked');
        //console.log(data);

        if ($scope.references_info_editable) {
            $scope.toast('There are unsaved info on References. Save or press Cancel', 'error');
            return;
        }

        $scope.references_search_3({name: data.node.data.name});
    };

    /*
    * A node on the users search js tree is clicked
    */
    $scope.users_search_jstree_select_node = function(e, data) {
        //console.log('Users node clicked');

        //Fetch user data
        $scope.ajax(
            'users_search_3/',
            {
                'username': data.node.data.username
            },
            function(data) {

                $scope.hide_all_right_accordions('users'); // Hide everything except users

                $scope.user_username = data['profile_username'];
                $scope.user_firstname = data['profile_firstname'];
                $scope.user_lastname = data['profile_lastname'];
                $scope.user_email = data['profile_email'];
                $scope.user_website = data['profile_website'];
                $scope.user_affiliation = data['profile_affiliation'];
                $scope.user_publicinfo = data['profile_publicinfo'];
                $scope.user_created_at = data['profile_created_at'];

                //Open right panel
                document.getElementById('userDataDiv').style.display = 'block';
                M.Collapsible.getInstance($('#userDataAccordion')).open(0);

                $timeout(function(){M.updateTextFields()}, 10);
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
    * Fetch the data from a single Q&A and update the UI
    */
    $scope.qa_search_3 = function(qa) {
        // Fetch thread
        $scope.ajax(
            'qa_search_3/',
            {
                'qa_id': qa.id
            },
            function(data) {
                $scope.qa_title = data['qa_title'];
                $scope.qa_comment = data['qa_comment'];
                $scope.qa_comment_html = data['qa_comment_html'];
                $scope.qa_comment_id = data['qa_id']; // The primary key to the Comment object in db
                $scope.qa_username = data['qa_username'];
                $scope.qa_created_at = data['qa_created_at'];
                $scope.qa_score = {score: data['qa_score']};
                $scope.qa_voted = data['qa_voted'];

                $scope.qa_info_editable = false;
                $scope.qa_show_new_comment = false;

//                $scope.qa_thread = [
//                    {'comment': 'comment 1', 'id': 1, 'replying': false},
//                    {'comment': 'comment 2', 'id': 2, 'replying': false}
//                ];
                
                $scope.qa_thread = data['qa_thread'];
                $scope.qa_visualize_pressed();
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
    * Generic version of $scope.qa_search_3
    * Fetch the data from a single Q&A and update the UI 
    * Duplicate code. FIXME !
    */
    $scope.gen_qa_search_3 = function(object_pk, qa_type) {
        // Fetch thread
        $scope.ajax(
            'gen_qa_search_3/',
            {
                'object_pk': object_pk,
                'qa_type': qa_type
            },
            function(data) {
                //$scope.qa_title = data['qa_title']; // There is no qa_title in generic
                //$scope.qa_comment = data['qa_comment']; // There is no qa_comment in generic
                //$scope.qa_comment_html = data['qa_comment_html']; // There is no qa_comment_html in generic

                //$scope.qa_comment_id = data['qa_id']; // The primary key to the Comment object in db

                $scope.qa_gen[qa_type].qa_comment_id = data['qa_id'];   // The primary key to the Comment object in db
                                                                        // -1, means has no comments

                // $scope.qa_info_editable = false; // No use in generic

                //$scope.qa_show_new_comment = false;
                $scope.qa_gen[qa_type].qa_show_new_comment = false

//                $scope.qa_thread = [
//                    {'comment': 'comment 1', 'id': 1, 'replying': false},
//                    {'comment': 'comment 2', 'id': 2, 'replying': false}
//                ];
                
                //$scope.qa_thread = data['qa_thread'];
                $scope.qa_gen[qa_type].qa_thread = data['qa_thread'];
                $scope.qa_gen[qa_type].qa_score = {score: data['qa_score']};
                $scope.qa_gen[qa_type].qa_voted = data['qa_voted'];

                if (qa_type == 'tool') {
                    $scope.tool_visualize_pressed();
                }
                else if (qa_type == 'workflow') {
                    $scope.workflow_visualize_pressed();
                }
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
    * A node in the Q&A search js tree is clicked
    */ 
    $scope.qa_search_jstree_select_node = function(e, data) {
        //console.log('Q&A node clicked');

        $scope.hide_all_right_accordions('qas'); // Close all right accordions except QAs

        document.getElementById('QARightPanel').style.display = 'block';
        // M.Collapsible.getInstance($('#QARightPanelAccordion')).open();

        //Fetch a QA data
        $scope.qa_comment_id = data.node.data.id;
        //console.log('QA node clicked. qa_id:', $scope.qa_comment_id);
        $scope.qa_search_3({id: $scope.qa_comment_id});
    };

    /*
    * Convert $scope.report_tokens to a data array for timeline
    */
    $scope.convert_report_tokens_to_timeline_data = function () {
                
        var ret = [];   
        var i=0;    
        $scope.report_tokens.forEach(function (tdata) {

		//create groups 
		if(tdata.status.split(" ")[0]==='workflow' || tdata.status.split(" ")[0]==='step'){
			mygroup = 1;
			myClass = 'workflow';
		}
		else if(tdata.status.split(" ")[0]==='tool'){
			mygroup = 2;
			myClass = 'tool';
		}
		else{
			mygroup = 3; //TODO check the possible group names
			myClass = 'default';
		}
		
		
		//manage names
		if(tdata.status.split(" ")[0]==='step')
			myname = tdata.node_anim_params.status_fields.name.split("__")[1];
		else
			myname = tdata.node_anim_params.status_fields.name;
			
			
            i++;
            ret.push({
                    id: i, 
					group: mygroup,
                    content: myname, 
					className: myClass,
                    start: new Date(tdata.created_at), //.toISOString().split('T')[0], 
                    params: tdata.node_anim_params}
            );
        });

        return ret;
    };

    /*
    * Reports --> Refresh --> button click
    * In cases when a workflow is executed from the OBC client. Update the status
    * action: 
    * 1 --> refresh
    * 2 --> pause
    * 3 --> resume
    * 4 --> Delete
    */
    $scope.report_refresh = function(action, confirm) {

        if (action == 4) {
            // Delete
            if ($scope.report_client) { // Is there a client trying to run it?
                if ($scope.report_client_status == 'RUNNING') { // Is it in running stage?
                    $scope.toast('The report is in RUNNING stage. Pause it first before deleting it', 'error');
                    return ;
                }
            }

            //Show modal 
            if (!confirm) {
                $scope.warning_modal_message = 'You are about to delete this report. Are your sure?';
                $scope.warning_modal_action = 'DELETEREPORT';
                $scope.report_refresh_action = action; // Pass the parameter
                $('#deleteModal').modal('open');
                return;
            }

        }

        $scope.ajax(
            'reports_refresh/',
            {
                report_workflow_action: action,
                report_workflow_name: $scope.report_workflow_name,
                report_workflow_edit: $scope.report_workflow_edit,
                report_workflow_run:  $scope.report_workflow_run
            },
            function(data) {

                if (action == 4) { // Delete
                    $scope.toast('Report is deleted!', 'success');
                    $scope.hide_all_right_accordions('');
                    $scope.all_search_2(); // Update search results
                    return;
                }

                $scope.report_url = data['report_url'];
                $scope.report_log_url = data['report_log_url'];
                $scope.report_client_status = data['report_client_status'];
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
    * Called from reports_search_jstree_select_node
    * Show a Report on the UI
    */
    $scope.reports_search_3 = function(report) {
        $scope.ajax(
            'reports_search_3/',
            {
                'run': report.run
            },
            function(data) {

                //Hide all right accordions
                $scope.hide_all_right_accordions('reports');

                //Open right report panel
                document.getElementById('reportsRightPanel').style.display = 'block';
                M.Collapsible.getInstance($('#reportsRightPanelAccordion')).open(0);

                //Fill data
                $scope.report_workflow_name = data['report_workflow_name'];
                $scope.report_workflow_edit = data['report_workflow_edit'];
                $scope.report_client = data['report_client']; // True/False . True: It is created through an OBC client
                $scope.report_url = data['report_url'];
                $scope.report_log_url = data['report_log_url'];
                $scope.report_visualization_url = data['report_visualization_url'];
                $scope.report_monitor_url = data['report_monitor_url'];
                $scope.report_client_status = data['report_client_status'];
                $scope.report_username = data['report_username'];
                $scope.report_created_at = data['report_created_at'];
                $scope.report_tokens = data['report_tokens'];

				//console.log('$scope.report_tokens');
				//console.log($scope.report_tokens);
				
                /* Create the report workflow*/
                window.createRepTree(data['workflow'].elements);

                //Update timeline 
                var timeline_data = $scope.convert_report_tokens_to_timeline_data();
				//window.OBCUI.init_timeline(timeline_data);
                window.OBCUI.set_timeline(timeline_data);
				

            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        )
    };

    /*
    * Called from references_search_jstree_select_node
    * Call the backend, fetch the data for a unique reference and update the UI
    */
    $scope.references_search_3 = function(reference) {
        $scope.ajax(
            'references_search_3/',
            {
                'name': reference.name
            },
            function(data) {
                $scope.references_name = data['references_name'];
                $scope.references_title = data['references_title'];
                $scope.references_doi = data['references_doi'];
                $scope.references_url = data['references_url'];
                $scope.references_notes = data['references_notes'];
                $scope.references_BIBTEX = data['references_BIBTEX'];
                $scope.references_formatted = data['references_html'];
                $scope.references_created_at = data['references_created_at']; // We currently do not do anything with this.
                $scope.references_username = data['references_username']; // We currently do not do anything with this.

                $scope.hide_all_right_accordions('references');
                document.getElementById('referencesRightPanel').style.display = 'block';
                M.Collapsible.getInstance($('#referencesRightPanelAccordion')).open(0);

                $scope.references_info_editable = false;

                $timeout(function(){M.updateTextFields()}, 10);
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
    * References "+" button clicked (create/add) a new Reference
    * is_new : is this a new reference (+ button clicked), if false, the UNSAVED button has been clicked
    */
    $scope.references_plus_button_clicked = function(is_new) {

        if (!$scope.username) {
            $scope.toast('Login to create a new reference!', 'error');
            return;
        }

        //Is user's email validated?
        if (!$scope.user_is_validated) {
            $scope.validation_toast('Validate your email to create a new reference!');
            return;
        }


        $scope.hide_all_right_accordions('references');

        document.getElementById('referencesRightPanel').style.display = 'block';
        M.Collapsible.getInstance($('#referencesRightPanelAccordion')).open(0);

        $scope.references_info_editable = true;

        if (!is_new) {
            return; //Do not update UI
        }

        //Empty all fields
        $scope.references_name = '';
        $scope.references_title = '';
        $scope.references_doi = '';
        $scope.references_url = '';
        $scope.references_notes = '';
        $scope.references_BIBTEX = '';
        $scope.references_formatted = '';
        $scope.references_created_at = null;
        $scope.references_username = null;

        $timeout(function(){M.updateTextFields()}, 10);

    };

    /*
    * Called from ng-repeat in the list of Report tokens
    * Called whenever an item is clicked 
    * Updates the cyrep graph 
    */
    $scope.nodeAnimation_public = function(node_anim_params) {
        //console.log('node_anim_params:');
        //console.log(node_anim_params);
        window.nodeAnimation_public(node_anim_params); // Also performs edge animation
    };
	
	
    /*
    * Called by Yes/No on Modal "All tool edits will be lost!"
    * M.Modal.getInstance($("#warningModal")).open()
    * tools_search_jstree_modal_editable_response = True // YES IS PRESSED!
    * tools_search_jstree_modal_editable_response = False // NO IS PRESSED!
    * Who called me value: 
    * TOOLS_CANCEL_BUTTON, WORKFLOWS_CANCEL_BUTTON, TOOL_SEARCH_JSTREE, WORKFLOWS_CREATE_BUTTON, TOOLS_CREATE_BUTTON
    */
//    $scope.tools_search_jstree_modal_editable = function(yes_no) {
//        $scope.tools_search_jstree_modal_editable_response = yes_no;
//
//        //Who called me?
//        var who_called_me = $("#warningModal").data('who_called_me');
//
//        //If modal is open, close it
//        if (M.Modal.getInstance($("#warningModal")).isOpen) {
//            M.Modal.getInstance($("#warningModal")).close();
//        }
//
//        if ($scope.tools_search_jstree_modal_editable_response) { // She clicked YES
//            console.log('CLICKED YES MODAL');
//            console.log('MODAL DATA:');
//            console.log($scope.modal_data);
//
//            console.log('WHO CALLED MODAL:');
//            console.log(who_called_me);
//
//            if (who_called_me == 'TOOL_SEARCH_JSTREE') { // This means, she clicked YES AFTER clicking on tools js tree 
//                console.log('MODAL WHO CALLED ME: TOOL_SEARCH_JSTREE');
//                $scope.tools_search_show_item($scope.modal_data.node.data);
//                window.createToolDataBtn_click();
//                window.cancelWorkflowBtn_click();
//                $scope.set_tools_info_editable(false);
//                //$scope.tools_info_editable = false;
//                $scope.workflows_info_editable = false;
//            }
//            else if (who_called_me == 'TOOLS_CREATE_BUTTON') {
//                $scope.set_tools_info_editable(false);
//                $scope.tools_plus_button_clicked();
//            }
////            else if (who_called_me == 'TOOLS_CANCEL_BUTTON') {
////                console.log('MODAL WHO CALLED ME: TOOLS_CANCEL_BUTTON');
////                window.cancelToolDataBtn_click(); // Close Tool panel
////                $scope.set_tools_info_editable(false);
////                //$scope.tools_info_editable = false;
////            }
////            else if (who_called_me == 'WORKFLOWS_CANCEL_BUTTON') {
////                console.log('MODAL WHO CALLED ME: WORKFLOWS_CANCEL_BUTTON');
////                $scope.workflows_info_editable = false;
////                window.cancelWorkflowBtn_click(); // Close WORFKLOW accordion
////           }
//            else if (who_called_me == 'WORKFLOWS_CREATE_BUTTON') {
//                $scope.workflows_search_create_new_pressed_ok();
//            }
//            else {
//                throw "ERROR: 7847"; // This should never happen
//            }
//
//        }
//
//    };


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
                    //console.log('Second Tree Operation:', operation);

                    if (operation == 'copy_node') {
                        //$scope.tools_dep_jstree_model.push({'id': 'eee', 'parent': '#', 'text': 'ddddd'});
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {
                    "icons": false
                }

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
            plugins : ['dnd', 'contextmenu'],
//            types : {
//                default : {
//                    icon : 'fa fa-cog'
//                }
//            },
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
                    //console.log('Third Tree Operation:', operation);

                    if (operation == 'copy_node') {
                        //$scope.tools_dep_jstree_model.push({'id': 'eee', 'parent': '#', 'text': 'ddddd'});
                        return false;
                    }
                    else if (operation == 'move_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {
                    "icons": false
                }

            },
//            types : {
//                tool : {
//                    icon : 'fa fa-cog'
//                },
//                variable : {
//                    icon : 'fa fa-star' // other ideas: bullseye , dot-circle , star , circle  
//                }
//            },
            version : 1, // Remnant. DELETE IT
            plugins : ['dnd'],
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
    * Dissasociate a tool or a workflow
    * node is cytoscape node 
    * Called from ui.js right click in cy node --> Disconnect
    */
    $scope.disassociate_workflow_tool = function(node, confirm) {

        if (!$scope.workflows_info_editable) {
            $scope.toast('This workflow is not in an edit stage.', 'error');
            return;
        }

        var node_data = node.data();
        if (!node_data.draft) {
            $scope.toast('You can disconnect only DRAFT tools or workflows', 'error');
            return;
        }

        if (!node_data.belongto) {
            $scope.toast('You cannot disconnect the root workflow', 'error');
            return;
        }

        if (!node_data.type == 'workflow') {
            $scope.toast('Error 5718', 'error'); //Sanity check
            return;
        }

        if (node_data.disconnected) {
            $scope.toast('This workflow is already disconnected', 'error');
            return;
        }

        //Now we can perform the disconnection. Confirm it
        if (!confirm) {
            var data = node.data();
            $scope.warning_modal_message = 'You are about to disconnect ' + data.type + ' ' + data.label + ' from this workflow. Changes on ' + data.label + ' will not further affect this workflow. You cannot undo this operation. Are your sure?';
            $scope.warning_modal_action = 'DISCONNECT';
            $scope.node = node; // Pass the parameter
            $('#deleteModal').modal('open');
            return;
        }

        if (node_data.type == 'workflow') {
            //disconnect a workflow

            // Get all successor workflows AND TOOLS and tag them as disconnected
            node.successors('node[type="workflow"] , node[type="tool"]').forEach(function(succesor_node){
                succesor_node.data('disconnected', true);
                succesor_node.data('draft', false); // disconnected workflows are not draft
            });
            node.data('disconnected', true);
            node.data('draft', false);
        }
        else if (node_data.type == 'tool') {
            //disconnect a tool
            // Get all successor tools and tag them as disconnected
            node.successors('node[type="tool"]').forEach(function(succesor_node){
                succesor_node.data('disconnected', true);
                succesor_node.data('draft', false); // disconnected workflows are not draft
            });
            node.data('disconnected', true);
            node.data('draft', false);
        }

    };

    //JSTREE workflows_search
    $scope.workflows_search_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                check_callback : function(operation, node, node_parent, node_position, more) { //https://stackoverflow.com/a/23486435/5626738

                    //console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {"icons": false}
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
            //plugins : ['dnd', 'types'],
            plugins: ['dnd'],
            types : {default : {icon : 'fa fa-sitemap' }},
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


    // Report search jstree config
    $scope.reports_search_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                check_callback : function(operation, node, node_parent, node_position, more) { //https://stackoverflow.com/a/23486435/5626738

                    //console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {"icons": false}
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
            //plugins : ['dnd', 'types'],
            plugins : ['dnd'],
            //types : {default : {icon : 'fa fa-sitemap'}},
            dnd: {
                is_draggable : function(node) {
                    return true;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []
    };

    // References search jstree config
    $scope.references_search_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                check_callback : function(operation, node, node_parent, node_position, more) { //https://stackoverflow.com/a/23486435/5626738

                    //console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {"icons": false}
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
            //plugins : ['dnd', 'types'],
            plugins : ['dnd'],
            //types : {default : {icon : 'fa fa-sitemap'}},
            dnd: {
                is_draggable : function(node) {
                    return true;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []
    };

    // Users search jstree config
    $scope.users_search_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                check_callback : function(operation, node, node_parent, node_position, more) { //https://stackoverflow.com/a/23486435/5626738

                    //console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {"icons": false}
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
            //plugins : ['dnd', 'types'],
            plugins : ['dnd'],
            //types : {default : {icon : 'fa fa-sitemap'}},
            dnd: {
                is_draggable : function(node) {
                    return true;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []
    };

    // Q&A search jstree config
    $scope.qa_search_jstree_config = {
            core : {
                multiple : false,
                animation: true,
                error : function(error) {
                    $log.error('treeCtrl: error from js tree - ' + angular.toJson(error));
                },
                check_callback : function(operation, node, node_parent, node_position, more) { //https://stackoverflow.com/a/23486435/5626738

                    //console.log('First Tree Operation:', operation);

                    if (operation === "move_node") {
                        return false;
                    }
                    else if (operation === 'copy_node') {
                        return false;
                    }

                    return true;
                },
                worker : true,
                themes: {"icons": false}
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
            //plugins : ['dnd', 'types'],
            plugins : ['dnd'],
            //types : {default : {icon : 'fa fa-sitemap'}},
            dnd: {
                is_draggable : function(node) {
                    return true;
                }
            }
            //plugins : ['types','checkbox']
            //plugins : []
    };


    /*
    * An item in workflow tree on the search panel is selected
    * Defined in: tree-events="select_node:workflows_search_jstree_select_node" 
    * See also: tools_search_jstree_select_node
    */
    $scope.workflows_search_jstree_select_node = function(e, data) {

        if ($scope.workflows_info_editable) {
            $scope.toast('There are unsaved info on Workflows. Save or press Cancel', 'error');
            return;
        }

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
        //window.cancelToolDataBtn_click();
        //window.createWorkflowBtn_click();

        //Hide all right panel accordions
        $scope.hide_all_right_accordions('workflows');

        //Show right panel accordion
        document.getElementById('workflowsRightPanel').style.display = 'block';
        M.Collapsible.getInstance($('#workflowsRightPanelGeneralAccordion')).open(0);


        $scope.workflows_info_editable = false;
        $scope.workflows_search_3(item);
        //M.updateTextFields();
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
                $scope.workflow_description_html = data['description_html'];
                $scope.workflow_info_forked_from = data['forked_from'];
                $scope.workflow_changes = data['changes'];
                $scope.workflow_score = data['workflow_score']; // For upvotes / downvotes
                $scope.workflow_voted = data['workflow_voted']; //Check if this workflow is voted from the user 
                $scope.workflows_info_draft = data['draft'];

                // Load the graph. TODO: WHAT HAPPENS WHEN WE CLICK TO NODE? IT IS NOT REGISTERED
                window.initializeTree();
                cy.json(data['workflow']);
                cy.resize();
				if(window.menu!==null) window.menu.destroy();
				if(window.input_menu!==null) window.input_menu.destroy();
                window.cy_setup_events();
				
                // Make step editor readonly
                workflow_step_editor.setReadOnly(true);
                // Clear all STEP fields
                $scope.workflow_info_add_step_clicked();

                // Load the input/output variables
                // $scope.workflow_input_outputs . [{name: '', description: '', out:true}];
                $scope.workflow_input_outputs = [];
                if (cy.$('node[type="input"] , node[type="output"]').length) {
                    cy.$('node[type="input"] , node[type="output"]').forEach(function(variable){
                        var data = variable.data();
                        //Make sure that this input/output belongs to this workflow
                        if ((data.belongto.name == $scope.workflow_info_name) && (data.belongto.edit==$scope.workflow_info_edit)) {
                            $scope.workflow_input_outputs.push({name: data.name, description: data.description, out: data.type === 'output'});
                        }
                    });
                }
                // $scope.workflow_input_outputs should never be empty. FIXME: Build an initializer function
                if (! $scope.workflow_input_outputs.length) {
                    $scope.workflow_input_outputs = [{name: '', description: '', out:true}];
                }

                // Set keyowords to chips
                window.OBCUI.set_chip_data('workflowChips', data['keywords']);
                window.OBCUI.chip_disable('workflowChips');

                $scope.workflow_keywords = data['keywords'];

                // This is a fresh WF. There is no "previous step"
                $scope.workflow_step_previous_step = false;

                // Update text fields
                $timeout(function(){M.updateTextFields()}, 10);

                // Set the thread of this workflow
                $scope.qa_gen['workflow'].object_pk = data['workflow_pk'];
                $scope.qa_gen['workflow'].qa_thread = data['workflow_thread'];
                $scope.qa_gen['workflow'].qa_comment_id = data['workflow_comment_id'];
                $scope.qa_gen['workflow'].qa_comment_title = data['workflow_comment_title'];
                $scope.qa_gen['workflow'].qa_comment_created_at = data['workflow_comment_created_at'];
                $scope.qa_gen['workflow'].qa_comment_username = data['workflow_comment_username'];

                // Run fit cytoscape. If the graph has been edited we need to reposition all nodes. 
                $timeout(function(){$scope.workflow_info_fit_pressed()}, 10);
                
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

            var this_node_belong_to_show_edit = this_data.belongto.edit ? '/' + this_data.belongto.edit : ''; //The workflow edit to show on tab completion
            //var this_node_belong_to_value_edit = this_data.belongto.edit ? this_data.belongto.edit : 'null'; // The workflow edit as a variable on tab completion

            if (this_data.type=='tool') {
                this_data.variables.forEach(function(variable) {
                    completion_info.push({
                        caption: 'tool/' + this_data.name + '/' + this_data.version + '/' + this_data.edit + '/' +  variable.name,
                        value: '${' + this_data.name.replace(/\./g, '_') + '__' + this_data.version.replace(/\./g, '_') + '__' + this_data.edit + '__' + variable.name + '}',
                        meta: variable.description
                    });
                });
            }
            else if (this_data.type=='step') {

                completion_info.push({
                    //caption: 'call(' + this_data.label + '/' + this_data.belongto.name + '/' + this_node_belong_to_show_edit + ')',
                    caption: 'step/' + this_data.label + '/' + this_data.belongto.name + this_node_belong_to_show_edit,
                    //value: 'call(' + this_data.label + '__' + this_data.belongto.name + '__' + this_node_belong_to_value_edit + ')',
                    //value: 'step__' + this_data.label + '__' + this_data.belongto.name + '__' + this_node_belong_to_value_edit ,
                    value: window.create_step_id(this_data, this_data.belongto),
                    meta: 'STEP'
                });
            }
            else if (this_data.type=='input' || this_data.type=='output') {
                completion_info.push({
                    caption: this_data.type + '/' + this_data.name + '/' + this_data.belongto.name + this_node_belong_to_show_edit,
                    //value: '${' + this_data.type + '__' + this_data.name + '__' + this_data.belongto.name + '__' + this_node_belong_to_value_edit + '}',
                    value: '${' + window.create_input_output_id(this_data, this_data.belongto) + '}',
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
    * Workflow --> Step --> Clear
    */
    $scope.workflow_info_add_step_clicked = function() {

        $scope.workflow_step_add_update_label = 'Add'; 

        //Update tab completion info to step ace editor
        $scope.workflow_update_tab_completion_info_to_step();

        //Open accordion
        //window.openEditWorkflowBtn_click();

        $scope.workflows_step_name = ''; //Clear STEP name
        $scope.workflows_step_main = false; 

        $scope.workflow_step_previous_step = false;
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1); //Add default content
    };

    /*
    * workflows --> Step --> Button: Add/Update --> Clicked
    * We either ADD the step or UPDATE the step. add step add update step update edit step edit. 
    */
    $scope.workflow_step_add = function() {

        if (!$scope.tools_version_regexp.test($scope.workflows_step_name)) {
            $scope.workflow_step_error_message = 'Invalid step name. Allowed characters are: a-z, A-Z, 0-9, ., _';
            return;
        }

        if ($scope.workflows_step_name.includes('__')) {
            $scope.workflow_step_error_message = 'Step name cannot contain "__"';
            return;
        }

        if ($scope.workflows_step_name.includes('..')) {
            $scope.workflow_step_error_message = 'Step name cannot contain ".."';
            return;
        }

        // Check that ONLY ONE step is declared as "main" on THAT workflow (nested workflow can have other main steps)
        // If we setting this value to true and there is already a main step, throw an error
        if ($scope.workflows_step_main) {

            //If this is an update, then the user can should be able to change the name (or content) of a main node
            //See https://github.com/kantale/OpenBioC/issues/134 
            var escape_check = false;
            if ($scope.workflow_step_add_update_label == 'Update') {
                var step_update_data = cy.$('node[id="' +  $scope.workflow_step_previous_step.id + '"]').data();
                if (step_update_data.main) {
                    //This node was a main and now is set to main. No need to check for multiple mains
                    escape_check = true; 
                }
                else {
                    //This node was NOT a main and now is set to main. We need to check how many other mains exist
                    escape_check = false;
                }
            }

            if (!escape_check) {
                var selected_nodes = cy.$('node[type="step"][?main]');
                for (var i=0; i<selected_nodes.length; i++) {
                    var current_node = selected_nodes[i];
        
                    if (current_node.data().belongto.edit === null) {
                        if (current_node.data().name != $scope.workflows_step_name) {
                            $scope.toast("There is already a 'main' step for this workflow", "error");
                            $scope.workflows_step_main = false;
                            return;
                        }
                    }
                }
            }
        }

        var step_belong_to = null; //By default 
        var edges_connected_to_me = []; //The edges that are connected to this step.

        //Is this an UPDATE or an ADD?
        if ($scope.workflow_step_add_update_label == 'Update') {
            // If this is an update then delete the previous node
            
            //Keep the belong to info of the step before deleting it
            step_belong_to = cy.$('node[id="' +  $scope.workflow_step_previous_step.id + '"]').data().belongto;

            //Keep the edges of the steps that call me
            cy.$('node[id="' + $scope.workflow_step_previous_step.id + '"]').incomers('node[type="step"]').forEach(function(ele, i, eles){
                edges_connected_to_me.push({group:'edges', data: window.OBCUI.create_step_calls_step_edge(ele.id(), $scope.workflow_step_previous_step.id).data}); 
            });

            //Keep the edges of the input variable that we read
            //cy.$('node[id="' + $scope.workflow_step_previous_step.id + '"]').incomers('node[type="input"]').forEach(function(ele, i, eles){
            //    edges_connected_to_me.push({group:'edges', data: window.OBCUI.create_step_read_input_edge($scope.workflow_step_previous_step.id, ele.id()).data});
            //});

            //Delete the node
            cy.$('node[id="' +  $scope.workflow_step_previous_step.id + '"]').remove();
        }
        else if ($scope.workflow_step_add_update_label == 'Add') {
            // If this is an add then check if we are adding a step with a name that already exists.
            var this_step_id = window.create_step_id({name: $scope.workflows_step_name}, {name: $scope.workflow_info_name, edit: null});
            step_belong_to = {name: 'root', edit: null}; // If we are adding a new step, add it to the root workflow

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
            main: $scope.workflows_step_main,
            sub_main: false,
            type: 'step',
            bash: bash_commands,
            steps: steps,
            tools: tools,
            inputs: input_output.inputs,
            outputs: input_output.outputs,
            belongto: null
        }];

        //Always when updating the graph, update also tab completion data for step editor! FIXME!! (bundle these things together!) A46016A6E393
        //window.buildTree(step_node, {name: $scope.workflow_info_name, edit: null});
        //window.buildTree(step_node, {name: 'root', edit: null});
        window.buildTree(step_node, step_belong_to);

        //If we deleted the step node we need to restore the edges that were previously connected to this step. 
        cy.add(edges_connected_to_me);

        $scope.workflow_update_tab_completion_info_to_step();

        //Empty STEP fields. Perhaps call the $scope.workflow_info_add_step_clicked() function??
        $scope.workflows_step_name = '';
        $scope.workflows_step_main = false;
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
        $scope.workflow_step_add_update_label = 'Add';

        //Close STEP accordion
        M.Collapsible.getInstance($('#editWorkflowAccordion')).close();

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
        $scope.workflows_step_main = false;
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
        $scope.workflow_step_add_update_label = 'Add';
    
    };

    /*
    * Called from UI.js . Right Click a node in cytoscape --> delete
    * Check https://github.com/kantale/OpenBioC/issues/119#issuecomment-530693822 for details on how to do delete a node.
    */
    $scope.workflow_cytoscape_delete_node = function(node_id, confirm) {

        //Cannot edit a saved worfklow
        if (!$scope.workflows_info_editable) {
            $scope.toast('Cannot edit a saved workflow. Fork it to make edits.', 'error');
            return;
        }

        var node = cy.$('node[id="' + node_id + '"]');
        var data = node.data();
        var node_label = data.label;

        //Raise modal to check if sure
        if (!confirm) {
            $scope.node_id = node_id;
            $scope.warning_modal_message = 'You are about to delete ' + data.type + ' ' + data.label + '. Are you sure?';
            $scope.warning_modal_action = 'DELETENODE';
            $('#deleteModal').modal('open');
            return;
        }


        if (data.type == 'step') {
            // Check if this step is called by another step or calls another step. If yes throw an error message.
            // Check if this step calls another step
            var t = node.outgoers('node[type="step"]');
            if (t.length) {
                $scope.toast('Cannot delete node: ' + node_label + '. It calls the step: ' + t.first().data().label, "error");
                return;
            }
            // Check if this step is called by another step
            var t = node.incomers('node[type="step"]');
            if (t.length) {
                $scope.toast('Cannot delete node: ' + node_label + '. It is called from step: ' + t.first().data().label, 'error');
                return;
            }

            //If both conditions are ok, Delete the step
            node.remove();
            //Update tab completion info
            $scope.workflow_update_tab_completion_info_to_step();
        }
        else if (data.type == 'input' || data.type=='output') {
            if (data.type == 'input') {
                // Check if this input is read by any step
                var t = node.outgoers('node[type="step"]');
                if (t.length) {
                    $scope.toast('Cannot delete input: ' + node_label + '. Its value is read from step: ' + t.first().data().label, 'error');
                    return;
                }
            }
            else if (data.type == 'output') {
                //Check if this output is set by any step
                var t = node.incomers('node[type="step"]');
                if (t.length) {
                    $scope.toast('Cannot delete output: ' + node_label + '. Its value is set from step: ' + t.first().data().label, 'error');
                    return;
                }
            }
            else {
                console.warn('Error 8911'); // This should never happen
            }
            // If it belongs to the root workflow, we should also update the UI
            if (window.OBCUI.cy_belongs_to_root_wf(node)) {
                //Get the index of the input
 
                var index = -1;
                for (var i=0; i<$scope.workflow_input_outputs.length; i++) {
                    if ($scope.workflow_input_outputs[i].name == data.name && $scope.workflow_input_outputs[i].out == (data.type=='output')) {
                        index = i;
                        break;
                    }
                }
                if (index<0) {
                    //This should never happen
                    console.warn('Error 8161'); // This should never happen
                }
 
                //Remove from workflow_input_outputs list
                $scope.workflow_input_outputs.splice(index, 1);

                //workflow_input_outputs should never be empty
                if (!$scope.workflow_input_outputs.length) {
                    $scope.workflow_step_add_input_output();
                }

            }
            //Remove from graph 
            node.remove();

            //Update tab completion 
            $scope.workflow_update_tab_completion_info_to_step();
        }
        else if (data.type == 'tool') {
            //Check if this tool is used by any step. If yes throw an error
            var t = node.incomers('node[type="step"]');
            if (t.length) {
                $scope.toast('Cannot delete tool: ' + data.label + '. It is used in step: ' + t.first().data().label, 'error');
                return;
            }

            // Check if this tool is a dependency to another tool that is used by any step. If yes throw an error.
            var ok = true;
            //Get the tools that depend from this tool
            node.predecessors('node[type="tool"]').forEach(function (element){
                //Get the steps that use this tool

                if (!ok) {
                    return; // Speed up the test
                }

                var t = element.incomers('node[type="step"]');
                if (t.length) {
                    $scope.toast('Cannot delete tool: ' + data.label + '. It is a dependency to tool: ' + element.data().label + ' which is used in step: ' + t.first().data().label , 'error');
                    ok = false;  // This does not return from function workflow_cytoscape_delete_node
                }
            });
            if (!ok) {
                return; //This does
            }

            // Check if this tool is a dependency to another tool
            var t = node.predecessors('node[type="tool"]');
            if (t.length) {
                $scope.toast('Cannot delete tool: ' + data.label + '. It is a dependency to tool: ' + t.first().data().label, 'error');
                return;
            }

            //Check if there are any tools that this tool is directly dependent from, and will be left hanging if we delete this tool
            //Get all tools that this tool depends from
            var t = node.outgoers('node[type="tool"]');
            if (t.length) {
                //For each tool that this tool is directly dependent, check if it is attached to any workflow
                t.forEach(function(element) {
                    //Is this element attached to any workflow?
                    if (!element.incomers('node[type="workflow"]').length) {
                        //This element is a tool that if we delete the tool node, will be left hanging
                        //Create an edge to the workflow where it belongs
                        var source_id = window.OBCUI.create_workflow_id(element.data().belongto);
                        var target_id = element.id();
                        var edge_id = window.OBCUI.create_workflow_edge_id(source_id, target_id);
                        cy.add([{ group: 'edges', data: { id: edge_id, source: source_id, target: target_id, edgebelongto: 'true' }}]);

                    }
                });
            }
            //Delete the node
            node.remove()

            //Update tab completion 
            $scope.workflow_update_tab_completion_info_to_step();
        }
        else if (data.type == 'workflow') {
            if (!data.belongto) {
                $scope.toast('Cannot remove the root workflow', 'error'); // TESTED 
                return
            }
            
            // Get all predecessor of this workflow
            var wf_predecessors = node.predecessors('node[type="workflow"]');

            // Get all successor workflows
            var wf_successors = node.successors('node[type="workflow"]');

            // this workflow + successor workflow
            var all_successor_wf = node.union(wf_successors);

            var nodes_to_delete = all_successor_wf;

            // all workflows
            var all_workflows = cy.$('node[type="workflow"]');

            // All workflows without all_successor_wf
            var all_without_node_wfs = all_workflows.difference(all_successor_wf);

            // Get all steps of these workflows
            var wf_steps = all_successor_wf.outgoers('node[type="step"]');
            nodes_to_delete = nodes_to_delete.union(wf_steps);

            var ok = true;

            wf_steps.forEach(function(element) {

                if (!ok) {
                    return;
                }

                // Check if there is any step that is called by another step that does not belong to all_successor_wf
                var a = element.incomers('node[type="step"]'); // Take the steps that call this step
                var b = a.incomers('node[type="workflow"]'); // Take the workflows of these steps
                var c = b.intersection(all_without_node_wfs); // Check if these workflows do not belong to the successors of this workflow

                if (c.length) {
                    $scope.toast('Cannot delete workflow: ' + node_label + '. It contains step: ' + element.data().label + ' which is called by a step that belongs to workflow: ' + c.first().data().label, 'error'); // TESTED
                    //                                                                                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ <<-- WHICH STEP?? TODO
                    ok = false;
                    return;
                }

                // Check if there is any step that calls another step that does not belong to all_successor_wf
                var a = element.outgoers('node[type="step"]'); // Take that steps that are called by this step (element)
                var b = a.incomers('node[type="workflow"]'); // Take the workflows of these steps
                var c = b.intersection(all_without_node_wfs); // Checl if these workflows do not belong to all_successor_wf
                if (c.length) {
                    $scope.toast('Cannot delete workflow: ' + node_label + '. It contains step: ' + element.data().label + ' which calls a step that belongs to workflow: ' + c.first().data().label, 'error'); // TESTED
                    ok = false;
                    return;
                }

            });

            if (!ok) {
                return;
            }

            // Get all inputs of these workflows
            var wf_input = all_successor_wf.outgoers('node[type="input"]');
            nodes_to_delete = nodes_to_delete.union(wf_input);

            wf_input.forEach(function(element) {

                if (!ok) {
                    return;
                }

                //Check if there is a step outside of all_successor_wf that reads this input
                var a = element.outgoers('node[type="step"]'); // Take all steps that read this input
                var b = a.incomers('node[type="workflow"]'); // Take the WFs of these step
                var c = b.intersection(all_without_node_wfs); // Check that these workflows do not belong to all_successor_wf
                if (c.length) {
                    $scope.toast('Cannot delete workflow: ' + node_label + '. It contains the input: ' + element.data().label + ' which is read by a step that belongs to workflow: ' + c.first().data().label, 'error'); // TESTED 
                    ok = false;
                    return;
                }

            });

            if (!ok) {
                return;
            }

            // Get all outputs of these workflows
            var wf_output = all_successor_wf.outgoers('node[type="output"]');
            nodes_to_delete = nodes_to_delete.union(wf_output);

            wf_output.forEach(function(element) {
                if (!ok) {
                    return;
                }

                //Check is there is any step outside of all_successor_wf that sets this output
                var a = element.incomers('node[type="step"]'); //Take all steps that set this output
                var b = a.incomers('node[type="workflow"]'); // Take all the workflows of these steps
                var c = b.intersection(all_without_node_wfs); // Check that these workflows do not belong to all successor_wfs
                if (c.length) {
                    $scope.toast('Cannot delete workflow: ' + node_label + '. It contains the output: ' + element.data().label + ' which is set by a step that belongs to workflow: ' + c.first().data().label, 'error'); // TESTED 
                    ok = false;
                    return;
                }
            });
            if (!ok) {
                return;
            }

            //Take all tools 
            cy.$('node[type="tool"]').forEach(function(tool_element){

                // console.log('Examinig tool: ' + tool_element.id());

                if (!ok) {
                    return;
                }

                var tool_data = tool_element.data();
                //Take all successor wfs
                all_successor_wf.forEach(function (wf_element){

                    // console.log('   Checking successor WF:' + wf_element.id())

                    if (!ok) {
                        return;
                    }

                    var wf_data = wf_element.data();

                    //Does this tool belong to any all_successor_wf?
                    if ((tool_data.belongto.name == wf_data.name) && (tool_data.belongto.edit == wf_data.edit)) {

                        // console.log('   This tool should be deleted.')

                        //This tool belong to the successor WFs. We are about to delete this tool. Can we?
                        nodes_to_delete = nodes_to_delete.union(tool_element);

                        //Is this tool used by any step outside the all_successor_wf?
                        var a = tool_element.incomers('node[type="step"]'); // Take all steps that use this tool
                        var b = a.incomers('node[type="workflow"]'); // Take the workflows of these steps
                        var c = b.intersection(all_without_node_wfs); // Is any of these workflows outside the successor wf (this node)?
                        if (c.length) {
                            $scope.toast('Cannot delete workflow: ' + node_label + '. It contains the tool: ' + tool_element.data().label + ' which is used by a step in the workflows: ' + c.first().data().label , 'error'); // TESTED 
                            ok=false;
                            return;
                        }

                        //Is this tool a dependency to any tool outside the all_successor_wf ?
                        var a = tool_element.incomers('node[type="tool"]'); // Take all tools that have this tool as a dependency
                        a.forEach(function (dep_tool_element) {

                            // console.log('      Tool: ' + tool_element.data().id + ' is a dependency to: ' + dep_tool_element.id());

                            if (!ok) {
                                return;
                            }

                            var dep_tool_element_data = dep_tool_element.data();

                            //deep_tool_element depends from tool_element
                            //Take all workflows outside this node
                            all_without_node_wfs.forEach(function (all_without_node_wfs_element){

                                // console.log('         This is an outside wf: ' + all_without_node_wfs_element.id());

                                if (!ok) {
                                    return
                                }

                                var all_without_node_wfs_element_data = all_without_node_wfs_element.data();

                                //Is dep_tool_element belongto all_without_node_wfs_element ?
                                if ((dep_tool_element_data.belongto.name == all_without_node_wfs_element_data.name) && (dep_tool_element_data.belongto.edit == all_without_node_wfs_element_data.edit)) {
                                    $scope.toast('Cannot delete workflow: ' + node_label + '. It contains the tool: ' + tool_data.label + ' which is a dependency to tool: ' + dep_tool_element_data.label + ' and belongs to workflow: ' + all_without_node_wfs_element_data.label, 'error');
                                    ok=false;
                                    return;
                                }
                            });
                        });

                        if (!ok) {
                            return;
                        }

                    }
                });

                if (!ok) {
                    return;
                }
            });

            if (!ok) {
                return;
            }

            // Delete this workflow
            nodes_to_delete.remove();

        }

        //Perhaps we have deleted the node with $scope.workflows_step_name. If this is the case, then update UI.
        if ($scope.workflows_step_name) {
            //Does this node exist?
            if (!cy.$('#' + $scope.workflows_step_name).length) {
                //This node does not exist. 

                //Empty STEP fields
                $scope.workflows_step_name = '';
                $scope.workflows_step_main = false;
                workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);
                $scope.workflow_step_add_update_label = 'Add'; 
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
        $scope.workflows_step_main = step.main;
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

        //Check for errors
        var error_message = $scope.workflow_step_input_output_check_if_correct();

        if (error_message) {
            $scope.toast(error_message, 'error');
            return;
        }

        //Add an extra item for the next variable
        $scope.workflow_input_outputs.push({name:'', description: '', out:false});

        //Add variables to the graph
        $scope.workflow_step_input_output_update_pressed();

    };

    /*
    * Worfklows --> Inputs/Outputs --> Remove Variable button ('-') --> Pressed
    */
    $scope.workflow_step_remove_input_output = function(index) {

        //Get the node cytoscape id
        var name = $scope.workflow_input_outputs[index].name;
        var type = $scope.workflow_input_outputs[index].out ? 'output' : 'input';
        var node_id = window.create_SIO_id({name: name, type: type}, {name: 'root', edit: null});

        //Remove the node
        $scope.workflow_cytoscape_delete_node(node_id);

    };

    /*
    * Check if the input/output parameter is correct.
    * Return the error_message or an empty string if everything is ok
    */
    $scope.workflow_step_input_output_check_if_correct = function() {

        var error_message = '';
        var nodes_names = [];

        $scope.workflow_input_outputs.forEach(function(input_output){
            if (input_output.name && input_output.description) {

                //Check that variables are ok
                if (!$scope.tools_name_regexp.test(input_output.name)) {
                    error_message = 'Variable: "' + input_output.name + '" has an invalid name (allowed characters:a-zA-Z0-9 and _)';
                    return;
                }
                if (input_output.name.includes('__')) {
                    error_message = 'Variable "' + input_output.name + '" contains "__". This is not allowed.';
                    return;
                }

                if (input_output.name == 'output') {
                    error_message = 'Variable cannot have the name "output"';
                    return;
                }
                else if (input_output.name == 'input') {
                    error_message = 'Variable cannot have the name "input"';
                    return;
                }
                if (nodes_names.indexOf(input_output.name) > -1) {
                    error_message = 'Variable: "' + input_output.name + '" exists more than once';
                    return;
                }

                nodes_names.push(input_output.name);
            }
        });

        return error_message;
 

    };

    /*
    * Called from workflow_step_add_input_output.
    * Adds input/output parameters to the graph
    * input update input output update output
    */
    $scope.workflow_step_input_output_update_pressed = function() {

        var nodes_to_add = [];
        var nodes_names = [];

        $scope.workflow_input_outputs.forEach(function(input_output){
            if (input_output.name && input_output.description) {

                nodes_names.push(input_output.name);

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
            //window.buildTree(nodes_to_add, {name: $scope.workflow_info_name, edit: null}); // FIXME. SEE A46016A6E393
            window.buildTree(nodes_to_add, {name: 'root', edit: null}); // FIXME. SEE A46016A6E393 
            $scope.workflow_update_tab_completion_info_to_step();
        }
    };

    /*
    * Workflows --> Save button --> pressed 
    * See also: tool_create_save_pressed 
    * add workflow add save workflow save 
    */
    $scope.workflows_create_save_pressed = function() {

        //Check workflow name
        if (!$scope.tools_name_regexp.test($scope.workflow_info_name)) {
            $scope.toast('Invalid Workflow name. Allowed characters: a-z, A-Z, 0-9, _, .', 'error');
            return;
        }

        if ($scope.workflow_info_name.includes('__')) {
            $scope.toast('Workflow name cannot contain "__"', 'error');
            return;
        }

        if ($scope.workflow_info_name.includes('..')) {
            $scope.toast('Workflow name cannot contain ".."', 'error');
            return;
        }


        $scope.ajax(
            'workflows_add/',
            {
                workflow_info_name: $scope.workflow_info_name,
                workflow_info_edit: $scope.workflow_info_edit, // We want this in order to delete the workflow, when we are saving a new edit
                workflow_info_forked_from : $scope.workflow_info_forked_from,

                workflow_website : $scope.workflow_website,
                workflow_description : $scope.workflow_description,
                workflow_changes: $scope.workflow_changes,
                workflow_keywords: window.OBCUI.get_chip_data('workflowChips'),
                workflow_json : cy.json(),
                workflow_edit_state : $scope.workflows_info_edit_state // Are we editing this tool ?
            },
            function(data) {
                $scope.workflow_info_created_at = data['created_at'];
                $scope.workflow_info_edit = data['edit'];
                $scope.workflow_description_html = data['description_html'];
                $scope.workflows_info_editable = false;
                $scope.workflow_edit_state = false;
                workflow_step_editor.setReadOnly(true);

                $scope.toast('Workflow successfully saved', 'success');
                //$scope.workflows_search_input_changed(); //Update search results

                //When we save a workflow, the UI keeps the cy version that has not been processed by the server
                //This version contains "null" values for the root id. Hence, we fetch it from the server.
                $scope.workflows_search_3({name: $scope.workflow_info_name, edit:data['edit']});

                $scope.workflow_keywords = window.OBCUI.get_chip_data('workflowChips');

                //Load comment thread
                $scope.qa_gen['workflow'].object_pk = data['workflow_pk'];
                $scope.qa_gen['workflow'].qa_thread = data['workflow_thread'];

                //Set score and upvote / downvote arrows
                $scope.workflow_score = data['score'];
                $scope.workflow_voted = data['voted']; // {'up': false, 'down': false};

                //EXPERIMENTAL. UPDATE SEARCH RESULTS
                $scope.all_search_2();

                //Close STEP accordion
                M.Collapsible.getInstance($('#editWorkflowAccordion')).close();
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
    * workflow fork workflow 
    * action: If 'FORK' this is a fork. If 'EDIT' this is an edit
    */
    $scope.workflows_info_fork_pressed = function(action) {
        if (!$scope.username) {
            //It will never reach here. FORK is disabled in UI if user is not logged in.
            $scope.toast("Login to create new Workflows", 'error');
            return;
        }

        //Is user's email validated?
        if (!$scope.user_is_validated) {
            $scope.validation_toast('Validate your email to create a new Workflow!');
            return;
        }

        //After fork, we should change the IDs 
        window.forkWorkflow();

        $scope.workflows_info_editable = true;
        if (action == 'FORK') {
            $scope.toast("Workflow successfully forked. Press Save after completing your edits", 'success');

            $scope.workflow_info_forked_from = {
                'name': $scope.workflow_info_name,  
                'edit': $scope.workflow_info_edit
            }
            $scope.workflow_changes = '';
        }

        //Initialize step editor
        workflow_step_editor.setReadOnly(false);
        $scope.workflows_step_name = '';
        $scope.workflows_step_main = false;
        workflow_step_editor.setValue($scope.worfklows_step_ace_init, -1);

        //Make Chips editable
        window.OBCUI.chip_enable('workflowChips');

        //Update Step Editor Tab completion 
        $scope.workflow_update_tab_completion_info_to_step();

        //Every fork is a draft
        $scope.workflows_info_draft = true;
    };

    /*
    * Called from ui.js, when a user drags a worklfow in current workflow
    * workflow = {'name': ... , 'edit': '...'}
    * drag and drop workflow 
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
                //We do not have to pass the complete worfklow, or edge information.
                var nodes_to_add = [];
                workflow_cytoscape.elements.nodes.forEach(function(node){
                    if (node.data.type == 'step') {
                        //We store the information whether or not this step used to be the main step of the DND'd WF

                        //If it is already a sub_main, do not change it.
                        if (!node.data.sub_main) {
                            node.data.sub_main = node.data.main;
                        }
                        //There can only be one main step on the workflow! See issue: #121
                        node.data.main=false;
                    }
                    else if (node.data.type == 'tool') {
                        //If we are adding a workflow, buildTree function, expects the label of the node to exist in the cy_label field
                        //cy_label is the label used in the jstree search tree
                        node.data.cy_label = node.data.label;

                        //By default all tools are not disconnected
                        node.data.disconnected = false;
                    }
                    else if (node.data.type == 'workflow') {
                        //By default the root node of the the workflow that we imported is in connected stage
                        if ((node.data.name == workflow.name) && (node.data.edit == workflow.edit)) {
                            node.data.disconnected = false;
                        }
                    }

                    //Add All Nodes 
                    nodes_to_add.push(node.data);
                });
                //window.buildTree(nodes_to_add, {name: $scope.workflow_info_name, edit: null});
                window.buildTree(nodes_to_add, {name: 'root', edit: null});
                $scope.workflow_update_tab_completion_info_to_step();
				
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
        // All root workflows have id: root!
        window.clear('root');

        //Add main_step node
        $scope.workflows_step_name = 'main_step';
        $scope.workflow_step_add_update_label = 'Add';
        $scope.workflows_step_main = true;
        $scope.workflow_step_add();

        //If the user pressed "clear" and the name is set. Then change the name on the wf root of graph
        if ($scope.workflow_info_name) {
            $scope.workflow_info_name_changed();
        }

    };

    /*
    * worfklows --> info (right panel) --> button "FIT" --> Pressed
    */
    $scope.workflow_info_fit_pressed = function() {
        window.fit();
    };


    /*
    * tool --> info (right panel) --> button "Run" --> Pressed
    * See also: workflow_info_download_pressed
    * download_type = "JSON" or "BASH"
    */
    $scope.tool_info_download_pressed = function(download_type) {
        //Gather all information required for running this tool

        //Get the dependencies of the current tool
        var tool_dependencies = $scope.get_tool_dependencies();

        $scope.ajax(
            'download_tool/',
            {
                'tools_search_name': $scope.tools_info_name,
                'tools_search_version': $scope.tools_info_version,
                'tools_search_edit': $scope.tools_info_editable ? 0 : $scope.tools_info_edit,
                'tool_variables': $scope.tool_variables,
                'tool_dependencies': tool_dependencies,
                'tool_os_choices' : $scope.tool_os_choices,
                'tool_installation_commands': tool_installation_editor.getValue(),
                'tool_validation_commands': tool_validation_editor.getValue(),
                'tool_draft': $scope.tools_info_draft, 
                'download_type': download_type
            },
            function (data) {
                $scope.download_data(download_type, data, 'tool', $scope.tools_info_editable);
            },
            function (data) {
                $scope.toast(data['error_message'], 'error');
            },
            function (statusText) {
                $scope.toast(statusText, 'error');
            }

        );

    };


    /*
    * Download a file
    * download_type can be 'BASH' or 'JSON'
    * callend by workflow_info_download_pressed and tool_info_download_pressed
    * caller = 'tool', 'workflow'
    * editable: True/False. Is the [tool/wf] editable?
    */
    $scope.download_data = function(download_type, data, caller, editable) {
        // https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
        if (download_type == 'JSON') {
            $("#hiddena").attr({
                "download" : 'workflow.json',      
                "href" : "data:," + data['output_object']
            }).get(0).click();
        }
        else if (download_type == 'BASH') {
            var output_filename = 'bash.sh';
            if (data['nice_id']) {
                output_filename = 'bash_' + data['nice_id'] + '.sh';
            }

            $("#hiddena").attr({
                "download" : output_filename,      
                "href" : "data:," + data['output_object']
            }).get(0).click();
        }
        else if (download_type == 'CWLTARGZ') {
            var output_filename = 'workflow.tar.gz';
            $("#hiddena").attr({
                "download" : output_filename,      
                "href" : "data:application/gzip," + data['output_object']
            }).get(0).click();
        }
        else if (download_type == 'CWLZIP') {
            var output_filename = 'workflow.zip';
            $("#hiddena").attr({
                "download" : output_filename,      
                "href" : "data:application/zip," + data['output_object']
            }).get(0).click();   
        }
        else if (download_type == 'AIRFLOW') {
            var output_filename = 'airflow.py';
            $("#hiddena").attr({
                "download" : output_filename,      
                "href" : "data:," + data['output_object']
            }).get(0).click();              
        }

        else {
            throw "ERROR: 4576"; // This should never happen
        }

        var warning_message = '<ul>';
        if (caller == 'workflow') {
            if (editable) {
                warning_message += '<li>Runs of unsaved workflows will not generate reports</li>';
            }
            else if ($scope.workflows_info_draft) {
                warning_message += '<li>This is a DRAFT workflow. Although this workflow can be executed, the execution will not generate a report.</li>';
            }
            else if (!data['report_created']) {
                warning_message += '<li>You are not a registered user or your email is not validated. Although this workflow can be executed, the execution will not generate a report.</li>';
            }
        }
        else if (caller == 'tool') {
            warning_message += '<li>Tool/Data installation will not generate reports</li>';
        }
        warning_message += '<li><b>SECURITY WARNING: always run scripts in a sandboxed environment!</b></li>'
        warning_message += '</ul>'
        $scope.toast(warning_message, 'warning');

    };

    /*
    * worfklows --> info (right panel) --> button "Download" --> Pressed
    * download_type = "JSON" or "BASH"
    */
    $scope.workflow_info_download_pressed = function(download_type) {
        var workflow_options = window.OBCUI.get_workflow_options();

        // Check for uncheck options
        if (false) { // WE ARE DISABLING THIS! Users can set them in executor
            var unset_options = [];
            for (var option in workflow_options) {
                if (workflow_options[option] === null) {
                    unset_options.push(option);
                }
            }

            if (unset_options.length) {
                $scope.toast('Please set all input variables. Unset variables: ' + unset_options.join(', '), 'error');
                return;
            }
        }

        $scope.ajax(
            'download_workflow/',
            {
                'workflow_options': workflow_options,
                'workflow': {
                    'name': $scope.workflow_info_name,
                    'edit': $scope.workflow_info_edit
                },
                'download_type': download_type,
                'workflow_info_editable': $scope.workflows_info_editable, // Is this workflow saved?
                'workflow_json' :  $scope.workflows_info_editable ? cy.json() : {} //If this is editable get the cytoscape graph. otherwise we do not need it. 
            },
            function(data) {
                //console.log('data:');
                //console.log(data);
                $scope.download_data(download_type, data, 'workflow', $scope.workflows_info_editable);
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast('Error: 3811 ' + statusText, 'error');
            }
        );
		
    };

    /*
    * Pressed "RUN" in workflows after selecting a profile_client name
    */
    $scope.workflow_info_run_pressed = function(profile_name) {

        $scope.workflow_run_disabled = true;
        $scope.toast('Please wait while the workflow is submitted for execution..', 'success');

        $scope.ajax(
            'run_workflow/',
            {
                'profile_name': profile_name,
                'name': $scope.workflow_info_name,
                'edit': $scope.workflow_info_edit,
                'workflow_options': window.OBCUI.get_workflow_options() //Get the workflow_options from the UI 
            },
            function (data) {
                $scope.toast('Workflow submitted for execution with a Report id: ' + data['nice_id'], 'success');
                $scope.workflow_run_disabled = false;
                $scope.all_search_2(); // Update search results
            },
            function (data) {
                $scope.toast(data['error_message'], 'error');
                $scope.workflow_run_disabled = false;
            },
            function (statusText) {
                $scope.toast('Error: 3812 ' + statusText, 'error');
                $scope.workflow_run_disabled = false;
            }
        );
    };

    // WORKFLOWS END 

    // REPORTS START


    // REPORTS END 

    // REFERENCES START

    /*
    * References --> Insert BIBTEX text --> Generate --> Clicked 
    */
    $scope.references_generate_clicked = function() {
        $scope.ajax(
            'references_generate/',
            {
                'references_BIBTEX': $scope.references_BIBTEX
            },
            function(data) {
                $scope.references_formatted = data['references_formatted'];
                $scope.references_name = data['references_name'];
                $scope.references_title = data['references_title'];
                $scope.references_doi = data['references_doi'];
                $scope.references_url = data['references_url'];

                $timeout(function(){M.updateTextFields()}, 10);
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
    * References --> Insert DOI --> Button "Process DOI" --> clicked
    */
    $scope.references_process_doi_pressed = function() {

        //Deactivate "PROCESS DOI" button
        $scope.references_button_process_doi_activated = false;

        $scope.ajax(
            'references_process_doi/',
            {
                'references_doi': $scope.references_doi
            },
            function(data) {
                $scope.references_BIBTEX = data['references_BIBTEX']

                //DUPLICATE CODE!! from references_generate_clicked 
                //We do not call references_generate_clicked to save one ajax call
                $scope.references_formatted = data['references_formatted'];
                $scope.references_name = data['references_name'];
                $scope.references_title = data['references_title'];
                //$scope.references_doi = data['references_doi'];
                $scope.references_url = data['references_url'];

                $timeout(function(){M.updateTextFields()}, 10);
                $scope.references_button_process_doi_activated = true; //Reactivate PROCESS DOI button
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
                $scope.references_button_process_doi_activated = true; //Reactivate PROCESS DOI button
            },
            function(statusText) {
                $scope.toast(statusText, 'error'); 
                $scope.references_button_process_doi_activated = true; //Reactivate PROCESS DOI button
            }
        );
    };

    /*
    * References --> Save --> Pressed
    */
    $scope.references_create_save_pressed = function() {

        //Check reference name
        if ($scope.references_name) {
            if (!$scope.tools_name_regexp.test($scope.references_name)) {
                $scope.toast('Invalid References name', 'error');
                return;
            }
        }
        else {
           $scope.toast('References Name is required', 'error'); 
           return;
        }

        //Check Title
        if (!$scope.references_title) {
            $scope.toast('References Title is required', 'error'); 
            return;
        }

        //Check URL
        if (!$scope.references_url) {
            $scope.toast('References url is required', 'error'); 
            return;
        }

        $scope.ajax(
            'references_add/',
            {
                'references_name': $scope.references_name,
                'references_title': $scope.references_title,
                'references_url': $scope.references_url,
                'references_doi': $scope.references_doi,
                'references_notes': $scope.references_notes,
                'references_BIBTEX': $scope.references_BIBTEX
            },
            function(data) {
                $scope.toast('Reference successfully saved', 'success');
                $scope.references_info_editable = false;

                $scope.references_formatted = data['references_formatted'];
                $scope.references_created_at = data['references_created_at'];
                $scope.references_username = data['references_username'];
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        );

    };

    // REFERENCES END 

    // QA
    /*
    * Q&A --> New Q&A --> Add Title + Comment --> Save button --> pressed 
    */ 
    $scope.qa_create_save_pressed = function() {

        if (!$scope.username) {
            $scope.toast('Plese login to post a new comment', 'error');
            return;
        }

        $scope.ajax(
            'qa_add_1/',
            {
                qa_title: $scope.qa_title,
                qa_comment: $scope.qa_comment
            },
            function(data) {
                $scope.toast('Comment successfully saved', 'success');
                $scope.qa_info_editable = false;
                $scope.qa_comment_id = data['id'];
                $scope.qa_comment_html = data['comment_html'];
                $scope.qa_thread = [];

                //EXPERIMENTAL!!! UPDATE SEARCH RESULTS
                $scope.all_search_2();
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
    * Q&A "+" button clicked (create/add) a new Question
    * is_new: if true: Clear the UI, if False: do not clear it.
    */
    $scope.qa_plus_button_clicked = function(is_new) {

        if (!$scope.username) {
            $scope.toast('Login to post a new question!', 'error');
            return;
        }

        //Is user's email validated?
        if (!$scope.user_is_validated) {
            $scope.validation_toast('Validate your email to post a new question!');
            return;
        }


        $scope.hide_all_right_accordions('qas');

        document.getElementById('QARightPanel').style.display = 'block';
        // M.Collapsible.getInstance($('#QARightPanelAccordion')).open();

        $scope.qa_info_editable = true;

        if (!is_new) {
            return; // Do not clear the UI
        }


        $scope.qa_title = '';
        $scope.qa_comment = '';
    };

    /* 
    * Recursively search and set replying status
    * Takes a whole thread and sets a replying flag=True to the node that we are currently replying
    */
    $scope.qa_set_replying = function(current_scope, current_id, value) {
        for (var i=0; i<current_scope.length; i++) {
            if (current_scope[i].id == current_id) {
                current_scope[i].replying = value;
            }
            else {
                current_scope[i].replying = false;
            }
            $scope.qa_set_replying(current_scope[i].children, current_id, value);
        }
    }


    /*
    * Q&A --> Show thread --> Reply button --> Clicked 
    */
    $scope.qa_reply_button_clicked = function(id) {

        $scope.qa_set_replying($scope.qa_thread, id, true);
        $scope.qa_current_reply_1 = '';
        $scope.qa_current_reply_2 = '';
        $scope.qa_current_reply_3 = '';
        $scope.qa_current_reply_4 = '';
        $scope.qa_reply_opinion = 'note';

    };

    /*
    * Generic version of qa_reply_button_clicked
    * Tool/WF --> Q&A --> Show thread --> Reply button --> Clicked 
    */
    $scope.gen_qa_reply_button_clicked = function(id, qa_type) {
        $scope.qa_set_replying($scope.qa_gen[qa_type].qa_thread, id, true);
        $scope.qa_gen[qa_type].qa_current_reply_1 = '';
        $scope.qa_gen[qa_type].qa_current_reply_2 = '';
        $scope.qa_gen[qa_type].qa_current_reply_3 = '';
        $scope.qa_gen[qa_type].qa_current_reply_4 = '';
        $scope.qa_gen[qa_type].qa_reply_opinion = 'note';

    };

    /*
    * Q&A --> Show Thread --> reply to a comment --> add text --> Save button --> Clicked 
    */
    $scope.qa_reply_save_button_pressed = function(id, comment, opinion) {
        //console.log('Reply to id: ', id);
        //console.log('Comment:', comment);

        //console.log('qa_current_reply:', $scope.qa_current_reply);

        $scope.qa_add_comment(id, comment, opinion);
        $scope.qa_current_reply_1 = '';
        $scope.qa_current_reply_2 = '';
        $scope.qa_current_reply_3 = '';
        $scope.qa_current_reply_4 = '';
        $scope.qa_reply_opinion = 'note';

    };

    /*
    * Generic version of qa_reply_save_button_pressed
    * Tools/WF --> Q&A --> Show Thread --> reply to a comment --> add text --> Save button --> Clicked
    */
    $scope.gen_qa_reply_save_button_pressed = function(id, comment, opinion, qa_type) {
        // $scope.gen_qa_add_comment = function(comment_pk, object_pk, comment, qa_type) 

        $scope.gen_qa_add_comment(id, $scope.qa_gen[qa_type].object_pk, comment, opinion, qa_type);
        $scope.qa_gen[qa_type].qa_current_reply_1 = '';
        $scope.qa_gen[qa_type].qa_current_reply_2 = '';
        $scope.qa_gen[qa_type].qa_current_reply_3 = '';
        $scope.qa_gen[qa_type].qa_current_reply_4 = '';
    };

    /*
    * Q&A --> Show Thread --> reply to a comment --> add text --> Cancel button --> Clicked 
    */
    $scope.qa_reply_cancel_button_pressed = function(id) {
        $scope.qa_set_replying($scope.qa_thread, id, false);
    };

    /*
    * Generic version of qa_reply_cancel_button_pressed
    * Tool/WF --> Q&A --> Show Thread --> reply to a comment --> add text --> Cancel button --> Clicked 
    */
    $scope.gen_qa_reply_cancel_button_pressed = function(id, qa_type) {
        $scope.qa_set_replying($scope.qa_gen[qa_type].qa_thread, id, false);
    };

    /*
    * Called by:
    * 1. qa_comment_save_button_pressed to save a new comment (not reply)
    * 2. qa_reply_save_button_pressed to save a REPLY (not comment)
    */
    $scope.qa_add_comment = function(id, comment, opinion) {
        $scope.ajax(
            'qa_add_comment/',
            {
                'qa_id': id, // The id of root comment
                'qa_comment': comment,
                'qa_opinion': opinion
            },
            function(data) {
                //Update the UI
                $scope.qa_search_3({id: $scope.qa_comment_id});
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
    * Generic version qa_add_comment 
    */
    $scope.gen_qa_add_comment = function(comment_pk, object_pk, comment, opinion, qa_type) {
        $scope.ajax(
            'gen_qa_add_comment/',
            {
                'comment_pk': comment_pk, // The id of root comment
                'object_pk': object_pk,
                'qa_comment': comment,
                'qa_opinion': opinion,
                'qa_type': qa_type
            },
            function(data) {
                //Update the UI
                //$scope.qa_search_3({id: $scope.qa_comment_id});
                $scope.gen_qa_search_3(object_pk, qa_type)
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
    * Q&A --> Show Thread --> Add Comment -(!NOT REPLY!) -> Add text --> Save button --> Clicked 
    */
    $scope.qa_comment_save_button_pressed = function() {
        //console.log('Save comment');
        //console.log('QA_COMMENT_ID: ', $scope.qa_comment_id);
        //console.log('Current Comment:', $scope.qa_current_comment);

        $scope.qa_add_comment($scope.qa_comment_id, $scope.qa_current_comment, $scope.qa_comment_opinion);

        $scope.qa_show_new_comment = false;
    };

    /*
    * Generic version of qa_comment_save_button_pressed
    * Tools/WF --> Q&A --> Show Thread --> Add Comment -(!NOT REPLY!) -> Add text --> Save button --> Clicked 
    */
    $scope.gen_qa_comment_save_button_pressed = function(qa_type) {
        // $scope.gen_qa_add_comment = function(comment_pk, object_pk, comment, qa_type)  

        $scope.gen_qa_add_comment(
            null, 
            $scope.qa_gen[qa_type].object_pk, 
            $scope.qa_gen[qa_type].qa_current_comment,
            $scope.qa_gen[qa_type].qa_comment_opinion,
            qa_type);

        $scope.qa_gen[qa_type].qa_show_new_comment = false;
    };

    /*
    * Q&A --> Show Thread --> Add Comment -(!NOT REPLY!) -> Add text --> Cancel button --> Clicked 
    */
    $scope.qa_comment_cancel_button_pressed = function() {
        $scope.qa_show_new_comment = false;
        $scope.qa_current_comment = '';
    };

    /*
    * Generic version of qa_comment_cancel_button_pressed
    * Tool/WG --> Q&A --> Show Thread --> Add Comment -(!NOT REPLY!) -> Add text --> Cancel button --> Clicked 
    */
    $scope.gen_qa_comment_cancel_button_pressed = function(qa_type) {
        $scope.qa_gen[qa_type].qa_show_new_comment= false;
        $scope.qa_gen[qa_type].qa_current_comment = '';
    };


    /*
    * Q&A --> Show tread --> "Add Comment" button --> pressed
    */
    $scope.qa_add_comment_button_pressed = function() {
        $scope.qa_show_new_comment = true;
        $scope.qa_current_comment = '';
        $scope.qa_comment_opinion = 'note';
    };

    /*
    * Same as qa_add_comment_button_pressed but generic
    */
    $scope.gen_qa_add_comment_button_pressed = function(qa_type) {
        //console.log('$scope.qa_gen:');
        //console.log($scope.qa_gen)

        //console.log('qa_type:', qa_type);

        $scope.qa_gen[qa_type].qa_show_new_comment = true;
        $scope.qa_gen[qa_type].qa_current_comment = '';
        $scope.qa_gen[qa_type].qa_current_comment_preview = {'html': ''};
        $scope.qa_gen[qa_type].qa_comment_opinion = 'note';
    };


    /*
    * Q&A --> Show thread --> "Visualize" --> Accordion Down
    * It used to have a button, this is why it is called "pressed()"
    * Just a wrapper for discourse_visualize_pressed defined in discourse.js
    * Through this function we pass all required angular vars
    */
    $scope.qa_visualize_pressed = function() {
        discourse_visualize_pressed(
            $scope.qa_comment_id,
            $scope.qa_username,
            $scope.qa_title,
            $scope.qa_created_at,
            $scope.qa_thread,
            'cydisc'
        )

    };


    // QA END

    /*
    * Tools --> Show thread --> "Visualize" --> Accordion Down
    * It used to have a button, this is why it is called "pressed()"
    * Just a wrapper for discourse_visualize_pressed defined in discourse.js
    * Through this function we pass all required angular vars
    */
    $scope.tool_visualize_pressed = function() {
        discourse_visualize_pressed(
            $scope.qa_gen.tool.qa_comment_id,
            $scope.qa_gen.tool.qa_comment_username,
            $scope.qa_gen.tool.qa_comment_title,
            $scope.qa_gen.tool.qa_comment_created_at,
            $scope.qa_gen.tool.qa_thread,
            'cydisc-tool'
        )

    };

    /*
    * Workflows --> Show thread --> "Visualize" --> Accordion Down
    * It used to have a button, this is why it is called "pressed()"
    * Just a wrapper for discourse_visualize_pressed defined in discourse.js
    * Through this function we pass all required angular vars
    */
    $scope.workflow_visualize_pressed = function() {
        discourse_visualize_pressed(
            $scope.qa_gen.workflow.qa_comment_id,
            $scope.qa_gen.workflow.qa_comment_username,
            $scope.qa_gen.workflow.qa_comment_title,
            $scope.qa_gen.workflow.qa_comment_created_at,
            $scope.qa_gen.workflow.qa_thread,
            'cydisc-workflow'
        )

    };

    /*
    * Hide all right accordions except from a single one
    * except: The right panel not to close
    */
    $scope.hide_all_right_accordions = function(except) {

        if (except != 'tools') {
            document.getElementById('createToolDataDiv').style.display = 'none';
            M.Collapsible.getInstance($('#createToolDataAccordion')).close();
        }

        if (except != 'workflows') {
            document.getElementById('workflowsRightPanel').style.display = 'none';
            M.Collapsible.getInstance($('#workflowsRightPanelGeneralAccordion')).close();
        }

        if (except != 'reports') {
            // Hide reports
            document.getElementById('reportsRightPanel').style.display = 'none';
            M.Collapsible.getInstance($('#reportsRightPanelAccordion')).close();
        }

        if (except != 'references') {
            //Hide references
            document.getElementById('referencesRightPanel').style.display = 'none';
            M.Collapsible.getInstance($('#referencesRightPanelAccordion')).close();
        }

        if (except != 'users') {
            //Hide Users
            document.getElementById('userDataDiv').style.display = 'none';
            M.Collapsible.getInstance($('#userDataAccordion')).close();
        }

        if (except != 'qas') {
            //Hide Q&A
            document.getElementById('QARightPanel').style.display = 'none';
            // M.Collapsible.getInstance($('#QARightPanelAccordion')).close();
        }
    }

    /*
    * called by ui.js --> interlink()
    * Handle interlinks
    */
    $scope.interlink = function(args) {
        if (args.type == 't' || args.type == 'd') {
            //Open a tool/data
            $scope.tools_search_jstree_select_node(null, {node:{data: args}});
        }
        else if (args.type == 'w') {
            //Open a workflow
            $scope.workflows_search_jstree_select_node(null, {node:{data: args}});
        }
        else if (args.type == 'r') {
            $scope.references_search_jstree_select_node(null, {node:{data: args}});
        }
        else if (args.type == 'u') {
            $scope.users_search_jstree_select_node(null, {node:{data: args}});
        }
        else if (args.type == 'c') {
            $scope.qa_search_jstree_select_node(null, {node:{data: args}});
        }
        else if (args.type == 'report') {
            $scope.reports_search_jstree_select_node(null, {node: {data: args}});
        }
    };

    /*
    * ng-click from IN/OUT worfklow variables
    */
    $scope.workflow_input_output_toggle = function(index) {
        //console.log('ffff:');
        //console.log(index);

        $scope.workflow_input_outputs[index].out = !$scope.workflow_input_outputs[index].out;
    };

    /*
    * This should be at the bottom(!) of the controller: 
    * https://stackoverflow.com/questions/15458609/how-to-execute-angularjs-controller-function-on-page-load
    */
    $scope.show_reset_password_from_ui = function() {
        if ($scope.password_reset_token) {
            $scope.show_reset_password = true;
            $scope.reset_signup_username = window.reset_signup_username;
            $scope.reset_signup_email = window.reset_signup_email;
            M.Modal.getInstance($("#signModal")).open();

            $timeout(function(){M.updateTextFields()}, 10);
        }
    };

    /*
    * A thumbs-up or thumbs-down was pressed on a tool or on a workflow
    * ro = 'tool', or 'workflow'
    * upvote = True --> upvote, false-->downvote
    */
    $scope.updownvote_tool_workflow = function(ro, upvote) {

        var ro_obj = {};
        //Get the TOOL
        if (ro=='tool') {
            ro_obj = {
                'name': $scope.tools_info_name,
                'version': $scope.tools_info_version,
                'edit': $scope.tools_info_edit
            }
        }
        else if (ro=='workflow') {
            ro_obj = {
                'name': $scope.workflow_info_name,
                'edit': $scope.workflow_info_edit
            }
        }
        else {
            return;
        }

        $scope.ajax(
            'updownvote_tool_workflow/',
            {
                'ro': ro,
                'ro_obj': ro_obj,
                'upvote': upvote,
            },
            function(data) {
                if (ro=='tool') {
                    $scope.tool_score = data['score'];
                    $scope.tool_voted = data['voted'];
                }
                else if (ro=='workflow') {
                    $scope.workflow_score = data['score'];
                    $scope.workflow_voted = data['voted'];
                }
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
    * A thumbs-up or thumbs-down was pressed on a comment
    * comment_id is the id of the comment
    * upvate: true --> Upvote, false --> downvote
    * score is an object that contains a score atttribute
    * voted is the current voted state: i.e. {'up': false, 'down': true}
    */
    $scope.updownvote_comment = function(comment_id, upvote, score, voted) {

        if (upvote && voted['up']) {
            //You cannot upvote twice
            $scope.toast('You have already upvoted this post', 'error'); // This is ugly. Remove? FIXME
            return;
        }
        if ((!upvote) && voted['down'] ) {
            //You cannot downvote twice
            $scope.toast('You have already downvoted this post', 'error'); //This is ugly. Remove? FIXME
            return;
        }

        $scope.ajax(
            'updownvote_comment/',
            {
                'comment_id': comment_id,
                'upvote': upvote
            },
            function (data) {
                score.score = data['score']; // We do the score.score thing, to pass the score by reference (see right_panel.html)
                voted['up'] = data['voted']['up']; 
                voted['down'] = data['voted']['down'];
            },
            function (data) {
                $scope.toast(data['error_message'], 'error');
            },
            function (statusText) {
                $scope.toast(statusText, 'error');
            }
        );
    };

    /*
    * Called when we hit the "Preview" tab in a field that supports markdown preview
    * event: The click event
    * source: A string. Where it happened. It can also be an object. In that case it sets the 'html' attribute.
    * original: The original (with markdown) content 
    */ 
    $scope.angular_previewTabClicked = function(event, source, original) {

        $scope.ajax(
            'markdown_preview/',
            {
                'text': original
            },
            function(data) {

                var html = data['html'];

                if (source === 'tool_description') {
                    $scope.tool_description_preview = html;
                }
                else if (source === 'workflow_description') {
                    $scope.workflow_description_preview = html;
                }
                else if (source === 'qa_comment') {
                    $scope.qa_comment_preview = html;
                }
                else if (source === 'qa_current_comment') {
                    $scope.qa_current_comment_preview = html;
                }
                else if (source === 'qa_current_reply_1') {
                    $scope.qa_current_reply_1_preview = html;
                }
                else if (source === 'qa_current_reply_2') {
                    $scope.qa_current_reply_2_preview = html;
                }
                else if (source === 'qa_current_reply_3') {
                    $scope.qa_current_reply_3_preview = html;
                }
                else if (source === 'qa_current_reply_4') {
                    $scope.qa_current_reply_4_preview = html;
                }
                else {
                    source.html = html;
                }

                previewTabClicked (event);
            },
            function(data) {
                $scope.toast(data['error_message'], 'error');
            },
            function(statusText) {
                $scope.toast(statusText, 'error');
            }
        );

    };

}); 

