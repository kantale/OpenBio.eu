
# Version changes and updates

### 0.1.7 (Not yet released)
* Bugs Fixed
   * [When deleting a tool from a WF parent WFs continue having it #156](https://github.com/kantale/OpenBioC/issues/156)

### 0.1.5 (18 February 2020)
* Bugs Fixed
   * [Provide the ability to not require static site #136](https://github.com/kantale/OpenBioC/issues/136)
   * [Downloaded bash.sh should not halt execution when input parameters are missing](https://github.com/kantale/OpenBioC/issues/154)
   * [Cannot get DAG from empty workflow #153](https://github.com/kantale/OpenBioC/issues/153)
* Features:
   * [Draft Tools/Data and Workflows #141](https://github.com/kantale/OpenBioC/issues/145)
   * [Offer the ability to disconnect workflows and tools from workflows #155](https://github.com/kantale/OpenBioC/issues/155)
   * [Add execution environment option in profile #142](https://github.com/kantale/OpenBioC/issues/142)
   * [Upvote / Downvote Tools and Workflows #128](https://github.com/kantale/OpenBioC/issues/128)
   * [Preview markdown #135](https://github.com/kantale/OpenBioC/issues/135)
   * [Add execution environment option in profile #142](https://github.com/kantale/OpenBioC/issues/142)

### 0.1.4 (21 November 2019)
* Features:
   * [Download Workflows in CWL #113](https://github.com/kantale/OpenBioC/issues/113)
   * [Access to basic environment variables #137](https://github.com/kantale/OpenBioC/issues/137)
   * [Add a Download button in Tools #118](https://github.com/kantale/OpenBioC/issues/118)

### 0.1.3 (30 October 2019)
* Bugs Fixed:
   * [Cannot change the name of a "main" step #134](https://github.com/kantale/OpenBioC/issues/134)
* Features:
   * Discussion has upvotes/downvotes. Also assign a "Note", "Agree", "Disagree" label in every comment
   * [Allow search by username #129](https://github.com/kantale/OpenBioC/issues/129)
   * [Avoid unnecessary comminutation between executor-server #132](https://github.com/kantale/OpenBioC/issues/132)
   * [Add a default "main" step to every new workflow #133](https://github.com/kantale/OpenBioC/issues/133)

### 0.1.2 (13 October 2019)
* Features:
   * Add discourse graph. This is a beta, first try.
* Bugs Fixed:
   * [Output nodes cannot have the same name as steps in workflows #114](https://github.com/kantale/OpenBioC/issues/114)
   * [Cannot delete input/output node from "-" button #125](https://github.com/kantale/OpenBioC/issues/125)
   * [Tool variable cannot have the "dot" character #117](https://github.com/kantale/OpenBioC/issues/117)

### 0.1.1 (30 September 2019)
* Features:
   * Disable "Process DOI" button during process [issue](https://github.com/kantale/OpenBioC/issues/122)
   * Removed a reference to a static site with funding and consortium information [issue](https://github.com/kantale/OpenBioC/issues/123)
* Bugs Fixed:
   * [step is lost while being edit in workflow fork action #121](https://github.com/kantale/OpenBioC/issues/121)
   * [Forked WFs were not visible in JStree #120](https://github.com/kantale/OpenBioC/issues/120)

### 0.1 (22 July 2019)
* First major release!
* Completely redesigned the UI with Materialize
* Simple, unique Search function. A search returns all relevant ROs.
* Added Questions And Answers as ROs
* Every Tool and Workflow has a Discussion section
* Added Reports
    * Workflows can get downloaded in JSON format or in standaline BASH scripts
    * Upon execution, a "Report" is generated with a unique random id. 
    * Reports are visualized in a Timeline
    * Click in a node in the timeline to see the relevant nodes and edges that are running
* Added References
    * Get the details of a Reference from a DOI (with the "PROCESS" button)
    * Get the details of a Reference from a BIBTEX (with the "PROCESS BIBTEX" button)
* Added Users as ROs.
    * Edit the profile of the signed-in user.
    * Show profile info for any user
* Created executor.py that undertakes the task of creating an executable BASH script from a workflow.
* Text in documentation of ROs and in discussion supports markdown.
* Created "innerlinks" Link a RO from another RO:
    * Tools: t/name/version/edit
    * Datasets: d/name/version/edit
    * Workflow: w/name
    * References: r/name
    * Report: report/id
    * question and comments: c/id
* Create permanent links that are clickable from outside the platform
* Edit a RO while browsing other ROs (you can only edit one type of RO at a time though)
* Added (draft) documentation in platform
* Fixed many bugs..

### 0.0.3 (20 September 2018)
* Checked 3 different libraries for tree integration in angular:
   * https://github.com/wix/angular-tree-control
   * https://github.com/angular-ui-tree/angular-ui-tree
   * https://github.com/ezraroi/ngJsTree 
* We chose the last (ngJsTree) because it seemed to be the most actively developed and uses JSTree which has extensive documentation, and [community](https://stackoverflow.com/questions/tagged/jstree). 
* Tool search shows an interactive JStree
* Tools have a Dependencies Tab
   * Users can drag and drop from the search to the dependency tab
   * Users can right click on the dependency graph (only on the top-rooted nodes) to delete dependencies
   * Check if dependency import is correct
* Tools have an Installation Tab
   * Installed [ace.js](https://ace.c9.io/)
   * Installation and Validation BASH commands through ace.js
   * Added Variables. Each tools has a set of visible (from other tools/WFs/..) variables.
   * On the top of this tab there is a tree that shows: Dependencies + Variables (of the dependencies)
   * Drag and Drop from variables tree to the ace.js editors (Allow only variables)

### 0.0.2 (30 August 2018)
* FIX #1: The port on verification URLs is hardcoded
* Created Tool/Data Form
* Responsive UI
* Tools can be created, searched and forked.

### 0.0.1 (22 August 2018)
* Basic Project setup: 
   * Django 2.1
   * Bootstrap 4.1.3
   * JQuery 3.3.1
   * Angular 1.7.2
* Register / Login / Edit User's Profile
* Mail setup with Postfix 3.1.0
* Validate email with token
* Reset email with token 

