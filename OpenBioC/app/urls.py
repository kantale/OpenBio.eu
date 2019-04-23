from django.urls import path, re_path

from . import views

urlpatterns = [
	path('', views.index),
	path('register/', views.register), # Register a new user 
	path('login/', views.login), # Login a user
	path('logout/', views.logout), # Logout a user
	path('reset_password_email/', views.reset_password_email), # Reset password email
	path('password_reset/', views.password_reset), # Reset user password 
	path('user_data_get/', views.user_data_get), # Get data from a LOGGED IN user
	path('user_data_set/', views.user_data_set), # Set data for a LOGGED IN user
	path('tools_search_1/', views.tools_search_1), # Search tools (get tool number) from sidebar
	path('tools_search_2/', views.tools_search_2), # icontains search for tools from search
	path('workflows_search_2/', views.workflows_search_2), # icontains search for workflows from search
	path('tools_search_3/', views.tools_search_3), # Search for a specific tool
	path('tools_add/', views.tools_add), # Add a new tool
	path('tool_get_dependencies/', views.tool_get_dependencies), # Get a JSTREE with a dependencies of this tool
	path('workflows_add/', views.workflows_add), # Add (or Save) a new workflow 
	path('workflows_search_3/', views.workflows_search_3), # Search (and get the details) for a specific SINGLE workflow. 
	path('run_workflow/', views.run_workflow), # Acceps a workflow_options and workflow object. Runs a workflow

	path('tool_info_validation_queued/', views.tool_info_validation_queued), # Connect validation task with tool
	path('callback/', views.callback), # Called from controller in order to update validation status
	path('tool_validation_status/', views.tool_validation_status), # Query validation status if tool
	re_path(r'^tool_stdout/(?P<tools_info_name>[\w]+)/(?P<tools_info_version>[\w\.]+)/(?P<tools_info_edit>[\d]+)/$', views.tools_show_stdout), # Show stdout of tool
	path('report/', views.report), # Called from executor.py 
]