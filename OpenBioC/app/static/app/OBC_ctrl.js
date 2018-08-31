
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



app.controller("OBC_ctrl", function($scope, $http, $filter) {
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
        $scope.tools_info_editable = false; // Can we edit tools_info ?
        $scope.tools_info_forked_from = null; //From which tool is this tool forked from?
        $scope.tools_search_list = []; //A list with tools search results
        $scope.tool_changes = ''; // Changes from forked
        $scope.tool_installation_init = '# Insert the BASH commands that install this tool\n# The following tools are available:\n#  apt-get, wget\n\n';
        $scope.tool_validation_init = '# Insert the BASH commands that confirm that this tool is correctly installed\n# In success, this script should return 0 exit code.\n# A non-zero exit code, means failure to validate installation.\n\nexit 1\n';
        $scope.tool_info_validation_message = '';
    };

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
    	$scope.inner_hide_all_navbar();
        $scope.inner_hide_all_error_and_general_messages();

        $scope.show_signup = true;
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

    /*
    * Navbar --> Tools/Data --> pressed
    */
    $scope.navbar_tools_pressed = function() {
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
                $scope.tools_search_list = data['tools_search_list'];
            },
            function(data) {

            },
            function(statusText) {

            }
        );
    };

    /*
    * Search SPECIFIC tool. Update IP
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
    * Navbar -> Tools/Data --> Appropriate input --> "Create New" button --> Pressed
    */
    $scope.toools_search_create_new_pressed = function() {

        if (!$scope.username) {
            $scope.tools_info_error_message = 'Login to create new tools';
            return;
        }

        $scope.show_tools_info = true;
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

        tool_installation_editor.setValue($scope.tool_installation_init, -1);
        tool_validation_editor.setValue($scope.tool_validation_init, -1);

    };

    /*
    * Navbar --> Tools/data --> Appropriate input --> "Create New" button --> Pressed --> Filled input --> Save (button) --> Pressed
    */
    $scope.tool_create_save_pressed = function() {
        $scope.ajax(
            'tools_add/',
            {
                'tools_search_name': $scope.tools_info_name,
                'tools_search_version': $scope.tools_info_version,
                'tool_website': $scope.tool_website,
                'tool_description': $scope.tool_description,
                'tool_forked_from': $scope.tools_info_forked_from,
                'tool_changes': $scope.tool_changes
            },
            function(data) {
                $scope.tools_info_success_message = 'Tool/Data successfully saved';
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
        $scope.tools_info_editable = false;
        $scope.tools_search_3(item);
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
        $scope.tools_info_success_message = "Create a new Edit of this Tool/Data";
        $scope.tools_info_forked_from = {
            'name': $scope.tools_info_name, 
            'version': $scope.tools_info_version, 
            'edit' :$scope.tools_info_edit
        }
        $scope.tool_changes = '';
    };

    /*
    * Navbar --> tools/data --> Aprioprate input (search) --> Create New (tool, pressed) --> Installation (tab, pressed) --> Validate (pressed)
    */
    $scope.tool_info_validate_pressed = function() {
        $scope.tool_info_validation_message = 'Not yet implemented';
    };

}); 


