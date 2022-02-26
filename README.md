# OpenBio.eu
[OpenBio.eu](https://www.openbio.eu) is an open collaborative workflow management system. It is focused (but not limited!) to the bioinformatics community.

## Documentation
[Here is an incomplete documentation](https://kantale.github.io/OpenBio.eu/)

## Discord 
[Join our discord server](https://discord.com/invite/V6kVUDYHFC) for questions, suggestions and comments.

## Features
Main features include:
* No DSL (Domain Specific Language) required. Do you have a bash script that installs a tool (or dataset)? Just copy paste it!
* Completely web based. You do not have to install anything. Use openbio.eu for your everyday science tasks from your browser.
* Simple workflow structure. Drag'n'drop a tool (or dataset) to add it in a workflow. Do the same for a workflow! Workflows can contain other workflows indefinitely.
* Drag'n'drop a tool to another tool's dependency panel to add it as a dependency.
* Simple mental mondel. Tools have variables (think: environment variables). For example: ```installation_path=path/to/executable```. Worfklows have input and output variables as well. For example ```input_data=path/to/data```, ```results=path/to/results```. Create your workflow steps according to the values of these variables.
* No DSL to describe workflow steps (and structure). Simply describe your steps in bash. Each workflow step is available as a bash function.
* You have absolutely no idea about bash? You don't have to. Reading environment variables (which is as simple as "```$my_var```") is all you need to know.
* Use python, or perl, or java or.. any language you like, to do your analysis. Call these tools the same way you would call them from the command line.
* Does it support iterations? conditional execution? Yes. In fact it supports anything bash supports (even recursion).
* What name should I use for my tool/dataset/workflow? Anything you like. Each tool/data is identified by a name (anything you want), a version (anything you want) and an id provided by the system. Similarly each workflow is identified by a name (anything you want) and an id provided by the system. The combination tool_name/tool_version/id and worfklow_name/id is quaranteed to by unique. The namespace is unique and global.
* Fork existing tools/workflows to create your own versions.
* Add markdown descriptions to these objects. Use ```t/tool_name/tool_version/id``` and ```w/worfklow_name/id``` to link to an object anywhere in the site.
* Each object has a Questions and Answers section.
* Add scientific references. Link with ```r/reference_name```. Bored to add all bibliographic details for a paper? Just add the [DOI](https://www.doi.org/). The system will get the rest.
* Execute workflows on your own enviroment. You do not have to share code or data with openbio.eu. Only the bash commands that install/download them. Monitor the execution, during runtime in a graphic interface.
* ...more to come

## Directories
* OpenBio: The awesome OpenBio platform! This directory also contains:
    * app/ The Django application of the project
    * ExecutionEnvironment. The Execution Environment of openbio.eu . Use [executor.py](ExecutionEnvironment/executor.py) to execute a worfklow in json format that you downloaded from openbio.eu.
* [deployment_notes.md](deployment_notes.md): Some notes on how to deploy on an Ubuntu 16.04 server
* discourse-graph. A very experimental effort to add a discourse graph to the discussion of objects in openbio.eu.
* tests/. Selenium tests.

## For Developers
We will be very happy to accept Pull Requests. The project does not have any active development or contribution guidelines at the moment.

## Contributors
Main developer is [Alexandros Kanterakis](https://www.ics.forth.gr/cbml/index_main.php?l=e&c=730) [mail](mailto:alexandros.kanterakis@gmail.com), [twitter](https://www.twitter.com/kanterakis). For a complete list of current contributors see [CONTRIBUTORS.md](CONTRIBUTORS.md)

## Funding
This research has been co‐financed by the European Union and Greek national funds through the Operational Program Competitiveness, Entrepreneurship and Innovation, under the call RESEARCH – CREATE – INNOVATE (project code: T1EDK - 05275)

## Posters / Conferences / Papers
* [Poster in BOSC2019](https://f1000research.com/posters/8-1350), DOI: https://doi.org/10.7490/f1000research.1117273.1

## More
* Twitter: https://twitter.com/openbioe/

