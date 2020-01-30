
# Introduction
[OpenBio.eu](https://www.openbio.eu) is an environment for open and collaborative science. 
On OpenBio you can search, create, store, use, share and comment Tools and Workflows that take part in open scientific experiments. 
But let's take things from the beginning...

This is the home page of the OpenBio.eu platform:
![img](screenshots/screen_1.png)



## Tools/Data
Tools and Data are indistinguishable in the platform. 
 


## Workflows 
A workflow should contain one (and only one) "main" step. When the Workflow gets executed this is the step that gets called. All other steps should (directly or in-directly) get called from this step. This is similar to the "main" function in C/C++/Java.

### Nodes
* Octagon: a Workflow
* Green Circle: Step
* Green Circle with RED Border: A main step
* Green Circle with BLACK Border: A step that it is main in a sub-workflow 
* Round Rectangle: A tool
* Round Rectangle with green border: An input node
* Round Rectangle with red border: An output node

## API
```bash
curl -H 'Accept: application/json; indent=4'  http://0.0.0.0:8200/platform/rest/tools/
```

