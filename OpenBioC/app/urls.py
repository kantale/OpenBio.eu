from django.urls import path, re_path

from . import views

urlpatterns = [
	path('', views.index),
	re_path(r'^[td]/(?P<tool_name>[\w]+)/(?P<tool_version>[\w\.]+)/(?P<tool_edit>[\d]+)/$', views.index), # tool link
	re_path(r'^w/(?P<workflow_name>[\w]+)/(?P<workflow_edit>[\d]+)', views.index), # workflow link
	re_path(r'^r/(?P<reference_name>[\w]+)', views.index), # reference link
	re_path(r'^u/(?P<user_username>[\w]+)', views.index), # user link
	re_path(r'^c/(?P<comment_id>[\d]+)', views.index), # comment link
	re_path(r'^report/(?P<report_run>[\w]+)', views.index), # report link
	path('register/', views.register), # Register a new user 
	path('login/', views.login), # Login a user
	path('logout/', views.logout), # Logout a user
	path('reset_password_email/', views.reset_password_email), # Reset password email
	path('password_reset/', views.password_reset), # Reset user password 
	path('send_validation_email/', views.send_validation_email), # Send a validation email
#	path('user_data_get/', views.user_data_get), # Get data from a LOGGED IN user
#	path('user_data_set/', views.user_data_set), # Set data for a LOGGED IN user
#	path('tools_search_1/', views.tools_search_1), # Search tools (get tool number) from sidebar
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
	path('all_search_2/', views.all_search_2), # Called on main search on-change . Construct jstrees. 
	path('reports_search_3/', views.reports_search_3), # Search (and get the details) for a specific SINGLE Report. 
	path('references_generate/', views.references_generate), # Generate a HTML reference from BIBTEX 
	path('references_process_doi/', views.references_process_doi), # Generate a BIBTEX entry from DOI
	path('references_add/', views.references_add), # Add a new reference
	path('references_search_3/', views.references_search_3), # Search (and get the details) for a specific SINGLE Reference
	path('users_search_3/', views.users_search_3), # Search and get the results for a single user
	path('users_edit_data/', views.users_edit_data), # User changes (edit), profile info data
	path('qa_add_1/', views.qa_add_1), # Add a new Title and a new comment.
	path('qa_search_3/', views.qa_search_3), # Get a unique Q&A thread 
	path('gen_qa_search_3/', views.gen_qa_search_3), # Generic version of the above.  Get a unique Q&A thread  
	path('qa_add_comment/', views.qa_add_comment), # Add a comment to a Q&A
	path('gen_qa_add_comment/', views.gen_qa_add_comment), # Genetic version of the above # Add a comment to a QA

]
