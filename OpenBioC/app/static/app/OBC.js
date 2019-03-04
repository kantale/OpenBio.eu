
var lang = ace.require("ace/ext/language_tools");

var tool_installation_editor = ace.edit("tool_installation_editor");
tool_installation_editor.setTheme("ace/theme/textmate");
tool_installation_editor.session.setMode("ace/mode/sh");

var tool_validation_editor = ace.edit("tool_validation_editor");
tool_validation_editor.setTheme("ace/theme/textmate");
tool_validation_editor.session.setMode("ace/mode/sh");

var workflow_step_editor = ace.edit("workflow_step_editor");
workflow_step_editor.setTheme("ace/theme/textmate");
workflow_step_editor.session.setMode("ace/mode/sh");

workflow_step_editor.setOptions({
    enableBasicAutocompletion: true,
    enableSnippets: true,
    enableLiveAutocompletion: true
});

var compl = {
  identifierRegexps: [/[a-zA-Z_0-9\.\$\-\u00A2-\uFFFF]/],
  getCompletions: function (editor, session, pos, prefix, callback) {
    //alert(prefix);

    callback(null, [
    {
    	 caption: 'ABCDEFGHI',
    	 value: 'ABCDEFGHI',
    	 meta: 'TOOL'
    },
    {
    	 caption: 'KLM',
    	 value: 'NOP',
    	 meta: 'STEP'

    }
    ]);
    //return;
  }
}


// https://stackoverflow.com/questions/28920998/custom-autocompleter-and-periods
lang.setCompleters();
lang.addCompleter(compl);

/*
* It is important to register these events AFTER load so that they are triggered after custom JSTREE functions
* More: https://groups.google.com/forum/#!topic/jstree/BYppISuCFRE
*/
