from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^add_reference/$', views.add_reference, name='add_reference'),
    url(r'^get_references/$', views.get_references, name='get_references'),
    url(r'^get_reference/$', views.get_reference, name='get_reference'),
    url(r'^reference_suggestions/$', views.reference_suggestions, name='reference_suggestions'),
    url(r'^get_tools/$', views.get_tools, name='get_tools'),
    url(r'^get_tools_ui/$', views.get_tools_ui, name='get_tools_ui'),
    url(r'^add_tool/$', views.add_tool, name='add_tool'),
    url(r'^jstree_tool/$', views.jstree_tool, name='jstree_tool'),
    url(r'^jstree_tool_dependencies/$', views.jstree_tool_dependencies, name='jstree_tool_dependencies'),
    url(r'^get_tool_dependencies/$', views.get_tool_dependencies, name='get_tool_dependencies'), #get_tool_dependencies
    url(r'^get_tool_variables/$', views.get_tool_variables, name='get_tool_variables'), # get_tool_variables

    url(r'^get_reports/$', views.get_reports, name='get_reports'),
    url(r'^get_reports_ui/$', views.get_reports_ui, name='get_reports_ui'),
    url(r'^add_report/$', views.add_report, name='add_report'),
    url(r'^jstree_report/$', views.jstree_report, name='jstree_report'),

    url(r'^add_workflow/$', views.add_workflow, name='add_workflow'),
    url(r'^get_workflows/$', views.get_workflows, name='get_workflows'),
    url(r'^jstree_wf/$', views.jstree_wf, name='jstree_wf'),
    url(r'^get_workflow/$', views.get_workflow, name='get_workflow'),

]


