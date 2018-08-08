from django.shortcuts import render

from .arkalos_views import register, login, logout, \
	add_reference, get_references, get_reference, reference_suggestions, \
	get_tools, get_tools_ui, add_tool, jstree_tool, jstree_tool_dependencies, get_tool_dependencies, get_tool_variables, \
	get_reports, get_reports_ui, add_report, jstree_report, \
	add_workflow, get_workflows, jstree_wf, get_workflow

def index(request):

	production = False
	if request.method == 'GET':
		if 'token' in request.GET:
			token = request.GET['token']
			if token=='A71B27C1919C':
				production = True
			else:
				pass
		else:
			pass
	else:
		pass # return HttpResponseNotFound('<h1>Page not found</h1>')	

	if production:
		# Check if user is authenticated
		is_authenticated = request.user.is_authenticated()

		context = {
			'include_static': True, 
			'username' : request.user.username if is_authenticated else '',
		}

		return render(request, 'app/index.html', context)
	else:
		return render(request, 'app/index_under_construction.html', {})


