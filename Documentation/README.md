# Introduction
This is an incomplete documentation of the platform.

[OpenBio.eu](https://www.openbio.eu) is an environment for open and collaborative science. On OpenBio you can search, create, store, use, share and comment Tools and Workflows that take part in open scientific experiments. This is the documentation of OpenBio but it is written like a tutorial. Maybe in the future we will offer both in two separate documents. Most of this tutorial and examples assume that you have created an account and that you have verified your email.


## Before we start

Before we move on to create our new Tool or Dataset you need to know a few crucial things about the platform. What makes openbio.eu different from other platforms?

1. **OpenBio.eu is able to "run" objects.**
There are many repositories that store tools, data and workflows.  Examples are [bio.tools](https://bio.tools/), [osf.io](https://osf.io/) and [omictools](https://omictools.com/). These repositories offer very rich description and annotation of these objects, but they lack one crucial abilitiy: to actually run this object (i.e. tool, workflow) on a computer that you have access to. OpenBio.eu is a repository of research objects that focus on this ability.Therefore, when you add or edit a new tool, data or workflow you need to provide explicit instruction of how to install the tool, download the data or execute the workflow. 

2. **OpenBio.eu's language for object installation/download/execution description is Bash.**
Since you need to provide explicit instructions of how to install a tool, download data or execute a workflow, we need a computer language to do so. We chose [Bash](https://www.gnu.org/software/bash/). Some people will find Bash, difficult or outdated. Nevertheless Bash is the defacto glue language of the [\*nix universe](https://en.wikipedia.org/wiki/Unix-like). Bash is present by default in OSx and even [Windows 10 supports it natively](https://docs.microsoft.com/en-us/windows/wsl/install-win10). By hosting our code in Bash we make sure that it is directly executable in as many as possible environments. 

   Also: **Hosting code in Bash does not mean that other languages are excluded**. 
   On the contrary, Bash was chosen because it is easy to link together different languages, programs, other scripts and logic in a common script.

3. **In OpenBio.eu Tools and Data are the same type of objects.**
Most Workflow Management Systems and Open Science environments distinguish Tools from Data. Users have to declare different properties for each, store them in different tables etc. OpenBio.eu does not make this distinction. Tool and Data are exactly the same type of objects, this is why on the remaining of this text, we will refer to these as "Tools/Data".

   But why is that? Semantically and in the context of a Workflow Management System, Tools and Data do not actually have any differences! Tools have dependencies but data are useless without the presence of other data. We need commands to download, configure, compile and install tools but data need to be downloaded and most of the times they also need to be decompressed, pre-processed and installed. Also it is very common tools and data to co-exist in a dependency tree of other tools and data. 

## Outlook of OpenBio.eu
First of all OpenBio.eu is a [Single-page application](https://en.wikipedia.org/wiki/Single-page_application). You might have already noticed this. Interacting with openbio.eu does not change the links shown in your browser. So techically there isn't any "front page". When entering OpenBio.eu what you see is:

![img](screenshots/screen_1.png)

The screen is divided in two parts. The left part is a search panel for various objects. The right panel displays these objects and is also a space for editing and.. experimentation.

Let's start with the first item on the left panel which is Tools/Data.

## Tools/Data
Click the green '+' button on the Tools/Data row of the left panel to create a new Tool/Data. 
Something like this will show up:
![img](screenshots/screen_2.png)

Set a name of your tool (or dataset) and a version. Available characters are ```a-z```, ```A-Z```, ```0-9``` and ```_``` for both fields. For the purpose of this tutorial let's assume that you entered ``my_tool`` as name and "1" as version.  

Other fields are:
* Website (Optional). This needs to be a valid URL.
* Description (Obligatory). You can use markdown and you can also preview your edits. For the purpose of this tutorial let's assume you entered "```An example tool```".
* Keywords (Optional)

Now save the tool/data by pressing the disc icon. Your tool/data is now saved. This is what you will see:

![img](screenshots/screen_3.png)

Let's focus on the ```my_tool/1/1``` part (the last digit might be different in your case). What is this?

Each Tool/Data has a unique ID in openbio.eu. This unique ID is comprised by three parts:
* The name that you have declared.
* The version that you have declared. 
* A number provided by the system, called "edit". This number is derived so that the Name/Version/Edit of this tool/data is unique. 

**In OpenBio.eu we refer to a unique tool with the following schema: ```<Name>/<Version>/<Edit>```. For example: ```my_tool/1/1```. This can be interpreted as "tool named my_tool version 1, edit 1".**

Here is the philosophy behind this naming/ID-ing scheme. In a repository of scientific objects, we want to store Tools/Data. Tools and Data have names and they also have versions (for Data they might also be called "releases"). An example is [Samtools version 1.8](https://github.com/samtools/samtools/releases/tag/1.8) and [1000 Genomes Project data release 20130502](ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/). In most scientific Tool/Data repositories these have a unique string based ID. For example could be called "Samtools" or "1000 Genomes Project", but that wouldn't identify precisely the research object at least not for reproducubility standards. Versions need to be part of the names. Then we face another problem which is that OpenBio.eu is a crowdsourced environment where you can name your Tool/Data however you like. This means that under the name/version Samtools/1.9 you can include Bash commands that download 1000 Genomes Project data (or anything else..). The solution here is to let anyone choose whatever name/version they like, but add on the ID of the Tool/Data a number (edit) that is provided by the system. That way we can have Samtools/1.8/1 created from user A and Samtools/1.8/2 created from user B. These two can be two completely unrelated Tool/Data objects. We should also let other users show preferences on which Tool/Data is better. This is possible with updvotes and downvotes that we describe later.


### Downloading a Tool/Data 
On the "Download" dropdown, select "BASH executable". A file named ```bash.sh``` get's downloaded. As you might have guessed you can actually execute this file. If you don't know how, there are many online resources to help you on that (just google: run .sh file). Before executing it, you should read carefully the following:

**Always execute scripts that you have downloaded from openbio.eu (or from anywhere on the Internet..) in a [sandboxed environment](https://en.wikipedia.org/wiki/Sandbox_%28computer_security%29). If you don't know what that is then DO NOT RUN IT! OpenBio.eu takes absolutely no liability on damages caused by executing scripts downloaded from openbio.eu.**

Now, assuming that you moved the downloaded script in a sandboxed environment, one way to run it is with:
```bash
bash bash.sh
```

The output is:
```
OBC: Workflow name: root
OBC: Workflow edit: 0
OBC: Workflow report: None
OBC: INSTALLING TOOL: my_tool/1/1
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 FAILED
OBC: CALLING STEP: step__main__root__None    CALLER: main
OBC: Output Variables:
```

Let's break this down. When you download a tool a new Workflow is created (we will see more on Workflows, later). Workflows have a name and an edit (similar to Tools/Data having a name a version and an edit). Since here you downloaded a Tool/Data and not a Workflow, a dummy workflow is created that has the name "root" and edit 0. Also the execution of a Workflow creates a "Report" (more on this later as well..). The interesting part is:

```
OBC: INSTALLING TOOL: my_tool/1/1
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
```

```OBC```  stands for "OpenBio-C" which is the name of the project. Everything that is printed that is OpenBio.eu specific, has the "OBC" suffix so that you can filter this out easily. Initially the script tries to Install the tool by running the "Installation commands" of the tool. The line ```OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED``` tell us, that the execution of the "Installation commands" has finished. Then it moves to the the execution of the "Validation commands":

```
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 FAILED
```

Here we notice that the "Validation commands" have failed! Why is that?

Let's move back to the platform. On the left part of the platform, on the search input, we can search for ```my_tool```. The one created by you appears:

![img](screenshots/screen_4.png)

On the items that appear, click the one that you created before (i.e. my_tool/1/1). Now on the right panel unfold the "Installation" commands. There you will notice two Bash editors, the one titled "Installation Commands" and the other is called "Validation Commands":

![img](screenshots/screen_5.png)

**Installation Commands** are Bash commands that install this tool/data. For example here you can include commands that download, compile and install a tool or download, decompress and pre-process a dataset.

**Validation Commands** are Bash commands that validate that this tool/data has been installed correctly. For example here you can add commands that check if the tool can be executed with some simple input or check if the data has the expected [checksum](https://en.wikipedia.org/wiki/Checksum). 

Here we notice that initially ```Installation Commands``` are empty whereas ```Validation Commands``` contain an ```exit 1```. The exit code of the ```Installation Commands``` is not checked. The exit code of the ```Validation Commands``` is checked. On your scripts you should add logic on the ```Validation Commands``` so that if the installation of a tool/data cannot be validated, then an ```exit 1``` (or exit with any non-zero number) should be executed. 

As it is right now, the ```Installation Commands``` and the ```Validation Commands``` cannot be edited. To do so click on the ```EDIT``` button on the top of the page. Upon pressing "EDIT" you will notice that many elements on the page became editable. One of these is the ```Installation Commands``` and the ```Validation Commands```. Change the ```Installation Commands``` so that it includes the command:

```bash
echo "installing tool my_tool"
```

And change the ```Validation Commands``` so that it will always exits 0 (this is actually a bad practice, always do some actual checks before exiting with 0).

```bash
exit 0
```

The environment should look like this:

![img](screenshots/screen_6.png)

Now press "SAVE" again, then Download the "BASH executable" as before and run the ```bash.sh``` again in a sandboxed environment. Now you will notice that the validation status has changed to ```SUCCEEDED```:

```
OBC: Workflow name: root
OBC: Workflow edit: 0
OBC: Workflow report: None
OBC: INSTALLING TOOL: my_tool/1/1
installing tool my_tool
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 SUCCEEDED
OBC: CALLING STEP: step__main__root__None    CALLER: main
Output Variables:
```

Also notice the output of the "Istallation Commands": ```installing tool my_tool```. 

So far we have shown that OpenBio.eu is a repository of "downloadable" Tool/Data where each one has Installation and Validation commands in Bash language. The next part is to demonstrate the use of tool/data variables.

### Tool/Data Variables 
When you have installed a Tool/Data you need to let other scripts know where these tools/data are. Apart from the installation path of the Tool/Data there might be other pieces of information that you want to share with other tools/data or with other workflows. This piece of information can be stored in the Tool/Data Variables section. Each Tool/Data variable has a name, a value and a description. 

Let's edit again the my_tool Tool/Data. Click the "EDIT" button, unfold the "Installation" panel and go to the bottom of this panel. There, add a variable with the name: ```var_1``` , value ```hello world``` and description: ```my first variable```. Click SAVE. This is what it should look like:

![img](screenshots/screen_7.png)

Now download again the BASH Executable, and run it. The output should be:

```
Workflow name: root
Workflow edit: 0
Workflow report: None
OBC: INSTALLING TOOL: my_tool/1/1
installing tool my_tool
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 SUCCEEDED
OBC: SET my_tool__1__1__var_1="hello world"   <-- my first variable 
OBC: CALLING STEP: step__main__root__None    CALLER: main
Output Variables:
```

Notice that after validating the tool, it sets the variable named ```my_tool__1__1__var_1``` the value ```hello world```. The name of the variable (```my_tool__1__1__var_1```) can be interpreted as "variable named var_1 of the tool my_tool with version 1 and edit 1".

### Tool/Data dependencies 
Suppose that the we have another tool/data which depends from my_tool. Let's call this tool/data 'another_tool' and assume version 1. Since in OpenBio.eu we *have to* insert the installation / validation Bash commands, we also *have to* declare the depencencies of this tool/data. Click the '+' button on Tools/Data and add ```another_tool``` as name and ```1``` as version. Also unfold the 'Dependencies panel'

Next, enter ```my_tool``` on the search text field on the left and locate the item on the results that you created before. Now drag and drop this item in the Dependencies panel (red border):

![img](screenshots/screen_8.png)  

This is how you declare Tool/Data dependencies in OpenBio.eu. It is important to note that during the installation of Tool/Data ```another_tool```, the ```my_tool``` will be installed first. Also the variables of ```my_tool``` are accessible in the Installation and Validation Commands of ```another_tool```. To use them, simply select them from the tree that appears above the Bash editors and drop them in the Bash editors:

![img](screenshots/screen_9.png)

Ta see what has happened we can add some dummy Installation and Validation Commands and we can also add a variable in ```another_tool```. For example add the following in the Installation commands:

```bash
echo "Installing another_tool"
echo "The value of tool var_1 from my_tool/1/1 is:"
echo "${my_tool__1__1__var_1}"
```

And the following in the Validation Commands:
```bash
echo "validating another_tool"
exit 0
```

We can also add a variable named ```var_2```. Now the data on ```another_tool``` should look like this: 

![img](screenshots/screen_10.png)


Now if we save, Download the "Bash Executable", and run it we will see something like this:

```
OBC: Workflow name: root
OBC: Workflow edit: 0
OBC: Workflow report: None
OBC: INSTALLING TOOL: my_tool/1/1
installing tool my_tool
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 SUCCEEDED
OBC: SET my_tool__1__1__var_1="hello world"   <-- my first variable 
OBC: INSTALLING TOOL: another_tool/1/1
Installing another_tool
The value of tool var_1 from my_tool/1/1 is:
hello world
OBC: INSTALLATION OF TOOL: another_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: another_tool/1/1
validating another_tool
OBC: VALIDATION FOR TOOL: another_tool/1/1 SUCCEEDED
OBC: SET another_tool__1__1__var_2="hello from another tool"   <-- my second var 
OBC: CALLING STEP: step__main__root__None    CALLER: main
OBC: Output Variables:
```

Here we notice a few things:
* ```my_tool``` was installed and validated before ```another_tool```. This is because ```my_tool``` is a dependency to ```another_tool```.
* During the installation of ```another_tool```, the value of the variable var_1 from my_tool/1/1 is printed. Generally, all tool/data variables, are accessible from any tool/data that is installed after them. 

### The ${OBC_TOOL_PATH} and ${OBC_DATA_PATH} variables 
On your installation scripts, you are encouraged to use the ```${OBC_TOOL_PATH}``` variable as the root path of all the installed tools of OpenBio.eu. For example when you want to download a file, decompress an archive or install a tool you are encouraged to do this in a directoty that lies under ```${OBC_TOOL_PATH}```. For example you can do:

```bash
MY_TOOL_PATH=${OBC_TOOL_PATH}/my_tool
mkdir ${MY_PATH}
wget -O ${MY_TOOL_PATH}/tool.tgz http://www.example.com/tool.tgz
```

By confirming to this, you can let other users define the desired location they want to install the OpenBio.eu tools. They can do this by simply exporting the variable ${OBC_TOOL_PATH} on bash. Similarly you are encouraged to use the variable ${OBC_DATA_PATH} to define the location of the data downloaded from Bash scripts in OpenBio.eu. These variables can be used as values in the Tool/Data variables. For Example:

![img](screenshots/screen_11.png)

Notice the value of variable ```INSTALLATION_PATH``` that includes the ```${OBC_TOOL_PATH}``` variable. Now we can define the value of ${OBC_TOOL_PATH} and then run the bash.sh script. The output is (some lines were removed for brevity):
```
#> export OBC_TOOL_PATH=/my/precious/location
#> bash bash.sh 
The installation path is: /my/precious/location/another_tool
OBC: SET another_tool__1__1__var_2="hello from another tool"   <-- my second var 
OBC: SET another_tool__1__1__INSTALLATION_PATH="/my/precious/location/another_tool"   <-- installation path 
```

### Finalizing and Forking tool/data
You may have noticed that so far you can save and edit a Tool/Data as many times as you want. Of course only the creator of a Tool/Data is allowed to edit it. This functionality has two side effects:

* Allowing to make changes to a Tool/Data, strips out the "reproducibility" of these objects. What if an experiment is based on a Data and the creator decides to change the installation instructions? This might affect the reproducibility of the experiment. 
* Allowing only the creator to edit a Tool/Data strips out the crowdsourcing ability. What if a user wants to make an edit to the tool/data of another user?

To battle these issues, we employ two mechanisms. The first is the "Finalizing". By Finalizing a Tool/Data you permanently "freeze" this object from changes. You cannot edit a Tool/Data that has been finalized. Also Tool/Data that have not been finalized are labelled as **DRAFT**. It is a good practice to Finalize your Tool/Data after thorough testing. DRAFT Tool/Data should not be used in "serious" analysis since computational reproducibility is not guaranteed. The philosophy behind the "Finalizing" mechanism is to test and experiment with DRAFT tools/data, but once these object are ready to be used as independent components in public scientific pipelines, then they should be finalized.  

The second mechanism is "forking". By forking a Tool/Data you can create an indentical Tool/Data object that is owned by you. Every forked Tool/Data is by default in a "draft" stage. Both Draft and Finalized Tools/Data can be forked. Let's see how it looks. Select the tool named ```another_tool``` that you created before. You can do that by entering ```another_tool/1``` in the search box on the left panel. From all the items that appear under the Tools/Data section, select the one created by you (or anything else that you like and you want to fork..). Once you click this item, a card with the details of this Tool/Data appears on the right. Now click the "Fork" button which is the rightmost button on the top of this card. Now the card becomes editable and you can make whatever changes you like. On this card there is an "Edit Summary" field that is obligatory. Here you should briefly describe the changes that you made from the original object. Once you complete with these changes you can save the new object. This is what it looks like:

![img](screenshots/screen_12.png)

There are a few things to notice here:
* On the left side of the platform, where the search results appear, you can see that there is a new Tool/Data object named ```another_tool/1/2```. This object is "under" the ```another_tool/1/1```. **Search results appear as a tree of objects. Parent-Child nodes mean that Childs where forked from Parenst**.
* The platform assigned a new "edit" number to the newly created Tool/Data. Remember that each Tool/Data has a unique ID which is comprised by three parts. A "name", a "version" and an "edit". Although the user sets the "name" and the "version", the "edit" is assigned by the platform. The new object that was created by forking ```another_tool/1/1``` has the same name and the same version, but different edit. This is also shown on the top of the right panel which states "forked from t/another_tool/1/1". Again the edit numbers might be different in your case.

### Deleting a Tool/Data 
Deleting Tool/Data is possible if:
* You own (have created) this Tool/Data.
* The Tool/Dats is in Draft stage
* There isn't any Tool/Data that uses this Tool as a dependency.
* There isn't any workflow that uses this Tool.

The deletion is permanent from the database and there is no action to restore it. 

## Workflows
[Scientific Workflow Management Systems (SWMS)](https://en.wikipedia.org/wiki/Scientific_workflow_system) have been around for many decades. [This awesome list](https://github.com/pditommaso/awesome-pipeline) contains hundreds of frameworks, libraries, platforms, languages, etc for managing and organizing tools and data into pipelines. OpenBio.eu is not exactly "Yet another SWMS". The purpose of OpenBio.eu is not to teach you "the correct language", or "data model" or "abstraction" in order to create scientific pipelines. The purpose is to help you create, publish and share your pipeline in whatever language / model / SWMS you like. There is only one prerequisite. The pipeline should be able to be expressed somehow in Bash. For example if your pipeline is a python script that runs with:

```bash
python my_awesome_pipeline.py --input input_file --output output_file
```

This is good enough for OpenBio.eu since this is valid Bash. But if the pipeline requires a GUI (Graphical User Interface), then chances are that OpenBio.eu is not for you. 

Now let's start. On the left part of the platform click the green "+" button on "Workflows" section. This is what you will see:

![img](screenshots/screen_13.png)

Add a name to the workflow i.e. ```my_workflow``` and also add a description  (i.e. "my first workflow"). These two fields are obligatory. On the description you can use markdown. By default a new Workflow in OpenBio contains a single "step" which is called "main_step". On the workflow graph click the node "main_step". The Step editor below unfolds. Now you can edit this step. Enter: ```echo "Hello from my_workflow"``` and click "UPDATE". Save this new workflow by clicking on the "Save" icon which is the rightmost on the top of this card. With the Workflow saved the platform should look like this:

![img](screenshots/screen_14.png)

The most important part here is that the name of the workflow appears as ```my_workflow/1```. This is because a unique ID of a workflow is comprised by two parts:
* A "name" provided by the user
* A number called "edit" provided from the platform.

The naming/ID-ing scheme is exactly the same as with Tools/Data. The only difference is that Workflows do not have versions. The idea here is that Tools/Data are items that get "fetched" (i.e. downloaded) from the Internet. They have versions that are maintained externally (outside OpenBio.eu), hence the "version" is part of the identity of a Tool/Data. On the other hand, Workflows are sets of Tool/Data, plus the logic that combines them for the purpose of an analysis. Workflow are merely constructs that exist only in OpenBio.eu this is why they don't have "version". Nevertheless they do have an edit, so it is possible to have multiple Workflows with the same name. 

Now, let's download and run this workflow. Select "BASH Executable" from the "Downlood" dropdown. A file named "bash.sh" gets donloaded. Run this as before (i.e. with ```bash bash.sh```). The output should be:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
OBC: Output Variables:
```

Notice that unlike before, when we run a Tool/Data object, it shows the Workflow name and Workflow edit. The "report" part will be explained later. Let's break the line: ```OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main```:
* OBC: Stands for OpenBio-C (the name of the project). 
* ```step__main_step__my_workflow__1``` Means that we are executing the step called "main_step" that belongs to the workflow ```my_workflow/1```. 
* ```CALLER: main``` means that this step is the "main" step, and it is not called from another step.

The output ```Hello from my_workflow``` is the output from the command ```echo "Hello from my_workflow"``` that you entered in the main_step earlier. 

### Creating and Calling Steps
Let's add a new step at the Workflow. First click the "EDIT" button on the ```my_workflow/1``` workflow. Click in the "Step" section, add the name "new_step" and add the following Bash commands:

```bash
echo "Hello from new_step"
```

This is what it should look like:

![img](screenshots/screen_15.png)

Now press the "ADD" button. A new node has been added on the workflow that represents the new step:

![img](screenshots/screen_16.png)

Although we have added a new step, we haven't declared how to call it. Let's alter the workflow so that the step ```main_step``` calls the step ```new_step```. Click on the ```main_step``` node. The Bash editor for the ```main_step``` opens. Then you can change the Bash commands from:

```bash
echo "Hello from my_workflow"
```

to:

```bash
echo "Hello from my_workflow"
step__new_step__root__null
```

But what does the ```step__new_step__root__null``` mean? This actually means "call the step ```new_step``` that belongs to the root workflow". We will see later that workflows can contain other workflows. Also workflows have steps. A step in a workflow can have the same name with another step in another workflow. Therefore when you call a step you need to declare to which workflow this step belongs. Also ```root_null``` is the name of the main workflow, or else the workflow that is being edited right now. Now press the "UPDATE" button to update the ```main_step```. The workflow has been changed and an edge from step ```main_step``` to step ```new_step``` has been added:

![img](screenshots/screen_17.png)

Now we can save these edits (press the save button on top-right), download the workflow (press Download-->Bash Executable) and run the file that gets downloaded (with ```bash bash.sh```). The output is:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: Output Variables:
```

Notice that the first step called is the ```main_step``` that prints ```Hello from my_workflow```. Then this step calls ```new_step``` that prints ```Hello from new_step```. Now it is time to discuss one of the main features of OpenBio.eu and why OpenBio is **not** a typical Workflow Management System:

**In OpenBio.eu steps are called from other steps. Or else in OpenBio.eu you do not define step order, instead you define step logic.** In most Workflow Management Systems like [Galaxy](https://galaxyproject.org/), [Nextflow](https://www.nextflow.io/) and [Taverna](http://www.taverna.org.uk/download/workbench/2-5/bioinformatics/) a user has to define two things: The first is steps and the second is Workflows. Steps (or *Processes* in Nextflow, *Tools* in Galaxy, *Services* in Taverna, ...) are independent execution components that can take part in one or many analyses. A workflow is a combination of Steps. A workflow usually defines the order in which the steps have to be executed. This abstraction is fine and has been used for decades in scientific computing. This abstraction is good because it serves a useful isolation between the execution (steps) and the execution flow (Workflow). 

There is though a fundamental difference between this abstraction and the typical abstraction used in computer programming. In programming, "steps call other steps" as in "functions call other functions". In programming, you do not use different language syntax to differentiate between the things that can be called (steps) and the things that call them (workflows). In contrast, everything you do in programming "sits" inside a function. This function can call or be called by other functions. Yet in typical Workflow Management Systems, you cannot "call" a step from another step (unless you do something hack-ish like run the workflow execution engine from inside the step). Even worse, in WMS it is difficult (if not possible) to use  fundamental programming constructs like conditional executions (if.. else..) and iterations (for.. while..). 

In OpenBio.eu, steps belong to workflows. **BUT** you do not "call" workflows. You call steps. Then.. how did we run ```my_workflow``` which is a workflow? Every workflow has one (and only one) *main* step. When you download a workflow and you execute it, what you actually execute is the main step of this workflow. This is like the main function in [c/c++](https://en.cppreference.com/w/cpp/language/main_function), [java](https://docs.oracle.com/en/java/javase/13/docs/api/jdk.compiler/com/sun/tools/javac/Main.html) or the ```if __name__ == '__main__':``` [logic in python](https://stackoverflow.com/questions/419163/what-does-if-name-main-do). So, OpenBio.eu **does not** have any algorithm to determine the execution order of steps. It simply calls the main step of the workflow and lets.. Bash take it from there. From a step you can call other steps that belong to any workflow. You can even call.. yourself. Also, you can use any Bash construct (if, while, for, ...) to control flow, so conditional execution and iteration is natively supported. Main steps have a red border color on the graph. Also, there is a "main" checkbox in the step editing panel, so that you can change which step is main. If more than one steps have been defined as main, or none, an error will appear upon trying to save the workflow.

The whole point of OpenBio.eu project is to offer a Workflow Management System that has the flexibility of a programming language, does not require installation in your computer to run it, and does not forcing you a new DSL (Domain Specific Language). The following chapters will illuminate more this philosophy. 

### Workflows in Workflows
Create a new workflow and name it "another_workflow". Click the node with the main_step and edit the Bash commands. Add:

```bash
echo "hello from another_workflow"
```

Click "Update" on this step and save this workflow. Now enter ```my_workflow``` on the search input on the left panel and select the workflow that you created before. Then click the Edit button. Here, we want to include the ```another_workflow``` into ```my_workflow```. To do that enter ```another_workflow``` on the search input of the left panel and locate the ```another_workflow/1``` object that you created before. Drag and Drop this workflow on the graph of ```my_workflow```:

![img](screenshots/screen_18.png)

The result should be:

![img](screenshots/screen_19.png)

**Note: The rendering of the graph might be different on your browser. You might have to move around the ```another_workflow/1``` node so that the graph in your broswer looks exactly like the one in this example.**

Let's explore a bit the semantics of this graph. Octagons represent Workflows. Red Octagon means that this workflow is in draft stage. The "root" workflow sits on the top of the graph and its name is ```my_workflow/1```. There are three items that belong to this workflow: (1) the step ```new_step```, (2) the step ```main_step``` and (3) the workflow ```another_workflow/1```. This is why there are tree dotted edges from the ```my_workflow/1``` node. Dotted edges mean "contain". From these steps, step ```main_step``` calls ```new_step```. This is why there is a normal edge from ```main_step``` to ```new_step```. Also ```main_step``` that belongs to ```my_workflow/1``` has a red border, meaning that this is the main_step of *this* workflow (the one that you are editing right now). Workflow ```another_workflow/1``` has one item. This is the step ```main_step``` node on the bottom of the graph. This node has a black border meaning that this is the main step of the workflow that it belongs to. Remember that a workflow can have one and only one main step. When you are importing a workflow into another workflow, the main step of the imported workflow stops from being main. Nevertheless, it is shown on the graph (the black border) that it "used to be the main step". This is to help you identify which step calls the rest on this workflow.

So although we have imported ```another_workflow/1``` we do not call any of its steps. Let's edit new_step and call the main_step of ```another_workflow/1```. Click the node "new_step" and on the Bash editor write: "step". The following auto-completion menu appears:

![img](screenshots/screen_20.png)

This menu helps you to choose a step. Available options are: step ```new_step``` of the root workflow, step ```main_step``` of the root workflow and step ```main_step``` of the ```another_workflow/1``` workflow. Select the last (```step/main_step/another_workflow/1```). Then click "UPDATE". Now the workflow becomes:

![img](screenshots/screen_21.png)

Save the workflow. We can Download (Button DOWNLOAD-->Bash Exutable) and run (```bash bash.sh```) this workflow. The output of this execution appears:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: CALLING STEP: step__main_step__another_workflow__1    CALLER: new_step__my_workflow__1
hello from another_workflow
OBC: Output Variables:
```

Here you see that the execution order is defined from the order of which each step is calling other steps. 

### Input/Output Parameters of Workflows
So far you might be wondering: How do I pass input values to a workflow and how do I get the output? You can define input/output variables through the user interface. For example, edit ```my_workflow/1``` and unfold the Inputs/Outputs panel. Then, add an input variable with the name ```threshold``` and an output variable with the name ```result```. Also add any description you like. It should look like this:

![img](screenshots/screen_22.png)

Input and Output variables are visible also in the workflow graph:

![img](screenshots/screen_23.png)

Input variables are rectangles with round corners and green border. Output variables are rectanges with round corners and red border.

Input and output variables behave similar to tool variables. They are Bash variables that can be accessed in any part of the workflow. For example let's read the value of the threshold and print it. This can be done by any step of the workflow. We can do that from ```main_step``` of ```my_workflow/1```. Click this node and edit the Bash commands. On any part you can type "input". An autocomplete menu appears that shows all the input nodes:

![img](screenshots/screen_24.png)

The only option is: ```input/threshold/root``` or else the input node named ```threshold``` that belongs to the root workflow. Choose this and this node is entered in the Bash editor as a Bash variable. Here we will make some additional edits on the Bash editor so that the script prints the value of ```input/threshold/root```. Change the Bash commands so that it reads like:

```bash
echo "Hello from my_workflow"
echo "Input Threshold is: ${input__threshold__root__null}"
step__new_step__my_workflow__1
```

Press "UPDATE" on the step editor. The graph now has become something like this:

![img](screenshots/screen_25.png) 

Note the new edge from the input node ```threshold``` to step node ```main_step```. Save the workflow (pres the save icon), download (DOWNLOAD-->Bash Executable) and run the workflow (```bash bash.sh```). You will notice that the execution stops and prompts for a value for the input parameter ```threshold```:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: Input parameter: input__threshold__my_workflow__1 (Input threshold value) has not been set by any step. Enter value: 
input__threshold__my_workflow__1=
```

Or else: "I couldn't get a value for the input parameter named ```threshold``` that belongs to ```my_workflow/1```". To continue, enter a value (i.e. ```4.5```) and press Enter. Now the output is:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: The following input commands have not been set by any step. Please define input values:
OBC: Input parameter: input__threshold__my_workflow__1 (Input threshold value) has not been set. Enter value: 4.5
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
Input Threshold is: 4.5
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: CALLING STEP: step__main_step__another_workflow__1    CALLER: new_step__my_workflow__1
hello from another_workflow
OBC: Output Variables:
OBC: output__result__my_workflow__1 = 
```

What's new here is that the workflow has a an input parameter. OpenBio.eu checks first to see if this parameter has been set by any step. Since we haven't set a value to this parameter from any step (we are only reading this value), it prompts the user for a value. Halting script execution to prompt for an input value is perhaps an inconvenient way to get parameter inputs. You can also set the value of this parameter from the command line. Run:

```bash
bash bash.sh --input__threshold__my_workflow__1=4.5
```

The script now doesn't halt to get a value for ```input__threshold__my_workflow__1```. 

What about *output* variables? You may have noticed that the output variable named ```results``` that we defined before did not get any value from any step. This is why we see the line: ```OBC: output__result__my_workflow__1 = ``` on the output of ```bash.sh```. Let's change that. Edit again the workflow ```my_workflow/1``` (press the EDIT button), click the ```new_step``` and on the BASH editor type: ```output```. You will see the following autocomplete menu:

![img](screenshots/screen_26.png)

The only output variable is the one named "results" and belongs to the root workflow. Edit the Bash commands of this step so that it looks like this.

```bash
echo "Hello from new_step"
step__main_step__another_workflow__1
output__result__root__null=120
```

Press "UPDATE" on this step. The workflow graph now looks like this:

![img](screenshots/screen_27.png)

Notice that a new edge has been created connecting step ```new_step``` with the output node ```results```. If we save, download and run the workflow with:

```bash
bash bash.sh --input__threshold__my_workflow__1=4.5
```

The output will be:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
Input Threshold is: 4.5
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: CALLING STEP: step__main_step__another_workflow__1    CALLER: new_step__my_workflow__1
hello from another_workflow
OBC: Output Variables:
OBC: output__result__my_workflow__1 = 120
```

The difference here is that the values of the output variables are printed at the end.

### Reading/Writing Input/Output variable between workflows
The input/output variables in OpenBio.eu have a different meaning than that of typical Workflow Management Systems. Let's break it down a bit. Assume a workflow that has the following steps:

``` 
- Step A has input input K and output M
- Step B has input M and output L
- Step C has input L and output N
```

With this information it is easy to figure out that the workflow structure should be: A --> B --> C. Actually most WMS do exactly this. The execution order of steps is determined by matching the output of step S<sup>1</sup> to the input of step S<sup>2</sup>. If they match then the step S<sup>1</sup> should run before S<sup>2</sup> and this is usually shown in Workflow graphs as S<sup>1</sup> --> S<sup>2</sup>. 

As we mentioned before, OpenBio.eu takes a different stance in determining step order. The step creator mentions explicitly which step to call. Therefore the step order is not determined *implicitly* by input/output variables but *explicitly* by call statements. Therefore in OpenBio.eu the same workflow should be written (in pseudocode, this is not Bash) as:

```
M = Step_A(K)
L = Step_B(M)
N = Step_C(L)
```

Notice how this form is more intuitive, especially if you have basic programming knowledge in any language. To summarise:

**In typical WMS, input/outputs are used to determine execution order. In OpenBio.eu input/output variables behave like function arguments (inputs) and return statements (outputs). Execution order is defined explicitly by the user.** 

Of course every approach has its own merits. What is best is up to you to decide, but let's experiment a bit with this idea. Remember that ```my_workflow/1``` has an input called ```threshold```. Suppose that we want to build a workflow that will contain the workflow ```my_workflow/1``` and will always use the value 5.5 on the ```threshold``` input variable. Or else we want to *call* ```my_workflow/1``` with ```threshold=5.5``` from another workflow. Create the workflow ```constant_threshold``` and add on the graph the workflow ```my_workflow/1```. To do that, search ```my_workflow/1``` on the left panel, locate this workflow object and drag and drop it on the graph of the right panel. Click the ```main_step``` node that belongs to the ```constant_workflow/1``` and add the following Bash commands:

```bash
input__threshold__my_workflow__1=5.5 # Setting the input value 
step__main_step__my_workflow__1 # Calling the step main_step of the workflow my_workflow/1
```

Practically here we set the input value of the workflow ```my_workflow/1``` to 5.5 and then we call it. Press UPDATE, the workflow now looks like this:

![img](screenshots/screen_28.png) 

If we save, download and run the workflow, the output is:

```
OBC: Workflow name: constant_threshold
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: CALLING STEP: step__main_step__constant_threshold__1    CALLER: main
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main_step__constant_threshold__1
Hello from my_workflow
Input Threshold is: 5.5
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: CALLING STEP: step__main_step__another_workflow__1    CALLER: new_step__my_workflow__1
hello from another_workflow
OBC: Output Variables:
```

Notice that, when executing the ```bash.sh``` script, we don't have to provide a value of the input variable ```threshold``` of the ```my_workflow/1``` workflow. This input is set from the step ```main_step``` of the ```constant_threshold/1``` workflow. Practically we *called* a workflow after setting its input value. 


Let's see another example. Create a workflow with the name ```A```, that has an input ```K``` and an output ```M```. Add the following Bash command on the ```main_step```:

```bash
output__M__A__1=$(expr ${input__K__A__1} + 3) # M = K + 3
```

Create another workflow with the name ```B```, that has an input ```M``` and an output ```L```. Add the following commands on the ```main_step```:

```bash
output__L__B__1=$(expr ${input__M__B__1} \* 5) # # L = M * 5 
```

Create another workflow with the name ```C```, that has an input ```L``` and an output ```N```. Add the following commands on the ```main_step```:

```bash
output__N__C__1=$(expr ${input__L__C__1} - 2) # N = L - 2
```

These three workflows, each contains a single step. The step performs a simple mathematical operation on the input variable and saves the output on the output variable. Now we can combine these three workflows in a forth workflow. Create a workflow with the name ```combine```. For each of one of the workflows ```A```, ```B```, ```C```, locate them via search on the left panel and drag and drop them on the graph of the ```combine``` workflow. On the ```combine``` workflow add a input variable ```K``` and an output variable ```N```. Finally, On the main_step of the ```combine``` workflow add the following Bash commands:

```bash
input__K__A__1=${input__K__combine__1} # Set the input of the A workflow as the input of the root workflow
step__main_step__A__1 # Call main_step of the A workflow
input__M__B__1=${output__M__A__1} # Set the input of the B workflow as the output of the A workflow
step__main_step__B__1 # Call main_step of the B workflow
input__L__C__1=${output__L__B__1} # Set the input of the C workflow as the output of the B workflow
step__main_step__C__1 # Call main_step of the C workflow
output__N__combine__1=${output__N__C__1} # Set the output of the root workflow as the output of the C workflow
```

The workflow looks like this:

![img](screenshots/screen_29.png)

Actually here we have "chained" three workflows. In pseudocode, what we have done is:

```
K : input

M = step_a(K) # Calls M = K + 3
L = step_b(M) # Calls L = M * 5 
N = step_c(L) # Calls N = L - 2

N: output
```

If we save, download and run this workflow with:

```bash
bash bash.sh  --input__K__combine__1=2
```

the output will be:

```bash 
OBC: Workflow name: combine
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: CALLING STEP: step__main_step__combine__1    CALLER: main
OBC: CALLING STEP: step__main_step__A__1    CALLER: main_step__combine__1
OBC: CALLING STEP: step__main_step__B__1    CALLER: main_step__combine__1
OBC: CALLING STEP: step__main_step__C__1    CALLER: main_step__combine__1
OBC: Output Variables:
OBC: output__N__combine__1 = 23
```

The output is 23 since the input is 2 and we applied the pseudocode presented above. To recap, in OpenBio.eu the user has to explicitly set (1) the input/output of each step and (2) define which steps call which. To illiustrate how this is different from other Workflow Management Systems let's take a look from [this workflow from Common Workflow Language tutorial](https://www.commonwl.org/user_guide/21-1st-workflow/index.html):

```
#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
  tarball: File
  name_of_file_to_extract: string

outputs:
  compiled_class:
    type: File
    outputSource: compile/classfile

steps:
  untar:
    run: tar-param.cwl
    in:
      tarfile: tarball
      extractfile: name_of_file_to_extract
    out: [extracted_file]

  compile:
    run: arguments.cwl
    in:
      src: untar/extracted_file
    out: [classfile]
```

What is described here is a workflow that has two inputs (```tarball```, ```name_of_file_to_extract```) and one output ```compile/classfile```. The workflow has two steps: 
* Step ```untar``` has inputs ```tarball```, ```name_of_file_to_extract``` and output ```extracted_file```.
* Step ```compile``` has input ```extracted_file``` and output ```compile/classfile```.

Notice that nowhere in this description is mentioned which step will run first and which second. This is implied from input/output variables. Here it is trivial to deduce that step ```untar``` will run first and step ```compile``` will run second. Yet in complex workflows the resolution of execution order requires special algorithms. Also sometimes this complexity makes workflow editing and maintaining a difficult and error-prone procedure. In Computer Science terminology, OpenBio.eu is an effort to bring workflows closer to the [structured programming](https://en.wikipedia.org/wiki/Structured_programming) paradigm as opposed to the [flow-based programming](https://en.wikipedia.org/wiki/Flow-based_programming) paradigm that are mostly modeled today.


### Adding Tools/Data in workflows
Adding Tools/Data in workflows is easy as adding other Workflows. For example let's locate the workflow ```my_workflow/1``` that we have created in the previous steps on the left panel. Select it and then press "EDIT". Now on the left panel, locate the tool ```another_tool/1```. Drag and drop ```another_tool/1``` to the graph of ```my_workflow/1```. The graph should look like this:

![img](screenshots/screen_30.png)

Notice that the graph has two additional nodes: ```another_tool/1/1``` and ```my_tool/1/1```. Both are red rectangles with round edges. Round rectagles are nodes that represent tools/data. Red means that these tools/data are in draft stage. Notice also that there is edge from ```another_tool/1/1``` to ```my_tool/1/1```. This means that ```another_tool/1/1``` depends from ```my_tool/1/1```. Save the workflow, download it and run it with:

```bash
bash bash.sh --input__threshold__my_workflow__1=4.5
```

The output is:

```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: INSTALLING TOOL: my_tool/1/1
installing tool my_tool
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 SUCCEEDED
OBC: SET my_tool__1__1__var_1="hello world"   <-- my first variable 
OBC: INSTALLING TOOL: another_tool/1/1
Installing another_tool
The value of tool var_1 from my_tool/1/1 is:
hello world
The installation path is: /another_tool
OBC: INSTALLATION OF TOOL: another_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: another_tool/1/1
validating another_tool
OBC: VALIDATION FOR TOOL: another_tool/1/1 SUCCEEDED
OBC: SET another_tool__1__1__var_2="hello from another tool"   <-- my second var 
OBC: SET another_tool__1__1__INSTALLATION_PATH="/another_tool"   <-- installation path 
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
Input Threshold is: 4.5
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: CALLING STEP: step__main_step__another_workflow__1    CALLER: new_step__my_workflow__1
hello from another_workflow
OBC: Output Variables:
OBC: output__result__my_workflow__1 = 120
```

The important thing to notice here is that the installation and validation Bash commands of the tools/data that take part in a workflow are execute *before* the Bash commands of any step. Or else, first we install tools/data and then we execute the rest parts of a workflow. Remember also that the tool ```another_tool/1/1``` has a variable named ```INSTALLATION_PATH```. We can access this variable at any step of the worfklow. For example, edit the workflow ```my_workflow/1```, click on the step node ```main_step``` of this workflow and at the Bash editor, at any part type: "input" the following autocomplete menu appears:

![img](screenshots/screen_31.png)

This is to help you locate the variable of a Tool/Data that you want to use. Select the ```INSTALLATION_PATH``` variable and print it. The Bash commands should look like this:

```bash
echo "Hello from my_workflow"
echo "Input Threshold is: ${input__threshold__my_workflow__1}"
step__new_step__my_workflow__1

echo "The value of INSTALLATION_PATH variable of another_tool/1/1 is:"
echo ${another_tool__1__1__INSTALLATION_PATH}
```

Press UPDATE and then save the workflow. The workflow now looks like this:

![img](screenshots/screen_32.png)

Notice the new edge from the ```main_step``` of ```my_workflow/1``` to the tool ```another_tool/1/1```. Or else, this step is using the tool ```another_tool/1/1```. Save the workflow, download it and run it with:

```bash
export OBC_TOOL_PATH=my/favorite/path
bash bash.sh --input__threshold__my_workflow__1=4.5
```

The output is:
```
OBC: Workflow name: my_workflow
OBC: Workflow edit: 1
OBC: Workflow report: None
OBC: INSTALLING TOOL: my_tool/1/1
installing tool my_tool
OBC: INSTALLATION OF TOOL: my_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: my_tool/1/1
OBC: VALIDATION FOR TOOL: my_tool/1/1 SUCCEEDED
OBC: SET my_tool__1__1__var_1="hello world"   <-- my first variable 
OBC: INSTALLING TOOL: another_tool/1/1
Installing another_tool
The value of tool var_1 from my_tool/1/1 is:
hello world
The installation path is: my/favorite/path/another_tool
OBC: INSTALLATION OF TOOL: another_tool/1/1 . COMPLETED
OBC: VALIDATING THE INSTALLATION OF THE TOOL: another_tool/1/1
validating another_tool
OBC: VALIDATION FOR TOOL: another_tool/1/1 SUCCEEDED
OBC: SET another_tool__1__1__var_2="hello from another tool"   <-- my second var 
OBC: SET another_tool__1__1__INSTALLATION_PATH="my/favorite/path/another_tool"   <-- installation path 
OBC: CALLING STEP: step__main_step__my_workflow__1    CALLER: main
Hello from my_workflow
Input Threshold is: 4.5
OBC: CALLING STEP: step__new_step__my_workflow__1    CALLER: main_step__my_workflow__1
Hello from new_step
OBC: CALLING STEP: step__main_step__another_workflow__1    CALLER: new_step__my_workflow__1
hello from another_workflow
The value of INSTALLATION_PATH variable of another_tool/1/1 is:
my/favorite/path/another_tool
OBC: Output Variables:
OBC: output__result__my_workflow__1 = 120
```

Notice the output:
```
The value of INSTALLATION_PATH variable of another_tool/1/1 is:
my/favorite/path/another_tool
```

This is printed from the ```main_step``` of ```my_workflow/1```. You might wonder why it is printed under the line ```hello from another_workflow```. Remember that the lines:

```bash
echo "The value of INSTALLATION_PATH variable of another_tool/1/1 is:"
echo ${another_tool__1__1__INSTALLATION_PATH}
```

are *after* the line:

```bash
step__new_step__my_workflow__1
```

so OpenBio.eu first calls ```new_step``` from ```my_workflow/1``` and then prints the value of the ```INSTALLATION_PATH``` variable.

Also open the workflow ```constant_threshold/1```. You will notice that the graph has changed!

![img](screenshots/screen_33.png)

Both ```another_tool/1/1``` and ```my_tool/1/1``` have been entered in the graph. But if we didn't edit ```constant_threshold/1```, how the graph was chaged? Workflow ```constant_threshold/1``` contains workflow ```my_workflow/1``` and we changed ```my_workflow/1``` by adding these two tools. Hence, ```constant_threshold/1``` also has changed. Remember that only draft workflows and tools/data can be changed. So if your pipeline contains only finalized entities, it is guaranteed that it will not change in the future. 

### The OBC_WORK_PATH variable 
Similar to variables ```OBC_TOOL_PATH``` and ```OBC_DATA_PATH```, you can use the ```OBC_WORK_PATH```. OpenBio.eu expects that this Bash variable has been set externally in you environment. You are encouraged to use this variable to refer on the path that is used during the analysis. For example to store you temporary data or your final results. 


### Finalizing a workflow 
If you try to finalize the ```constant_threshold/1``` workflow you will receive an error: ```This workflow cannot be finalized. It contains 2 draft workflow(s). For example: another_workflow/1```. A finalized workflow cannot be changed, so it cannot contain a draft workflow or a draft tool/data. So first finalize the draft components of a workflow and then finalize the workflow. 

### Worfklow graph, node semantics
Here we list the different types of nodes on the workflow graph:
* Red Octagon: a fraft Workflow
* Grey Octagon: A finalized workflow
* Green Circle: Step
* Green Circle with RED Border: A main step
* Green Circle with BLACK Border: A step that it is main in a sub-workflow 
* Red Round Rectangle: A draft tool
* Frey Round Rectangle: A finalized tool
* Grey Round Rectangle with green border: A workflow input
* Grey Round Rectangle with red border: A workflow output


## API
```bash
curl -H 'Accept: application/json; indent=4'  http://0.0.0.0:8200/platform/rest/tools/
```
### Airflow DAG 
```
curl "http://0.0.0.0:8200/platform/rest/workflows/my_workflow/1/?dag=true" 
```



