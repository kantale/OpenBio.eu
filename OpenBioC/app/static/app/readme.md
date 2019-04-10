Instead of wget you can use:

```
curl -O -J -L <URL>

-O, --remote-name          Write output to a file named as the remote file  
-J, --remote-header-name   Use the header-provided filename
-L, --location      Follow redirects (H) 
```

This is useful for example in windows when using git bash prompt.  

Also to extract the bash commands of this file that contain the ```<!-- run -->``` header run:
```
python get_bash_commands.py 
```

### jQuery 3.3.1 . REQUIRED

<!-- run -->
```
wget https://code.jquery.com/jquery-3.3.1.min.js
```

### JQuery UI 1.12. . NOT REQUIRED
https://jqueryui.com/download/


### Bootstrap 4.1.3 . NOT REQUIRED 

```
wget https://github.com/twbs/bootstrap/releases/download/v4.1.3/bootstrap-4.1.3-dist.zip
```

### Angular 1.7.2 . REQUIRED 

For more .map files see here: https://code.angularjs.org/1.7.2 

<!-- run -->
```
wget https://ajax.googleapis.com/ajax/libs/angularjs/1.7.2/angular.min.js
wget https://code.angularjs.org/1.7.2/angular.min.js.map 

```

Not minified version:
wget https://ajax.googleapis.com/ajax/libs/angularjs/1.7.2/angular.js

### Angular Sanitize 1.7.2 . REQUIRED 
<!-- run -->
```
wget -O "v1.7.2.tar.gz" https://github.com/angular/bower-angular-sanitize/archive/v1.7.2.tar.gz
tar zxvf v1.7.2.tar.gz
```


### select2 ATTENTION THIS IS A VERY OLD RELEASE 4 Nov 2013 !!! . REQUIRED 

<!-- run -->
```
wget -O "select2_3.4.5.tar.gz" https://github.com/select2/select2/archive/3.4.5.tar.gz
tar zxvf select2_3.4.5.tar.gz
```

### selectize js ATTENTION! VERY OLD!! (25 Nov 2013) https://github.com/selectize/selectize.js/releases?after=v0.11.0 . REQUIRED 

<!-- run -->
```
wget -O "selectizejs-0.8.5.tar.gz" https://github.com/selectize/selectize.js/archive/v0.8.5.tar.gz
tar zxvf selectizejs-0.8.5.tar.gz
```

### Angular UI select . REQUIRED 

<!-- run -->
```
wget -O "v0.19.8.tar.gz" https://github.com/angular-ui/ui-select/archive/v0.19.8.tar.gz
tar zxvf v0.19.8.tar.gz
```

### ACE 1.4.1 . REQUIRED 
wget -O "v1.4.1.tar.gz" https://github.com/ajaxorg/ace-builds/archive/v1.4.1.tar.gz
*IMPORTANT!* Remove will-change from .js

vim ace-builds-1.4.1/src-min-noconflict/ace.js 

Change with:
```
sed -i 's/will-change: transform;//g' ace-builds-1.4.1/src-min-noconflict/ace.js
```

<!-- run -->
```
wget -O "v1.4.1.tar.gz" https://github.com/ajaxorg/ace-builds/archive/v1.4.1.tar.gz
tar zxvf v1.4.1.tar.gz
sed -i 's/will-change: transform;//g' ace-builds-1.4.1/src-min-noconflict/ace.js
```

### Angular tree 2.22.6 . NOT REQUIRED
wget https://github.com/angular-ui-tree/angular-ui-tree/archive/v2.22.6.tar.gz

### angular-tree-control 0.2.28. NOT REQUIRED
wget https://github.com/wix/angular-tree-control/archive/0.2.28.tar.gz

### Context-menu 2.7.0 (required by angular-tree-control) NOT REQUIRED
wget https://github.com/swisnl/jQuery-contextMenu/archive/2.7.0.tar.gz

### JStree 3.3.5 . REQUIRED 

<!-- run -->
```
wget -O "3.3.5.tar.gz" https://github.com/vakata/jstree/archive/3.3.5.tar.gz
tar zxvf 3.3.5.tar.gz
```

### ng-jstree 0.0.10 . REQUIRED 

<!-- run -->
```
wget -O "v0.0.10.tar.gz" https://github.com/ezraroi/ngJsTree/archive/v0.0.10.tar.gz
tar zxvf v0.0.10.tar.gz
```

### Font awesome 4.7.0 (glyphicons) . REQUIRED 
https://fontawesome.com/v4.7.0/

<!-- run -->
```
mkdir fontawesome
wget -O "fontawesome/font-awesome-4.7.0.zip" https://fontawesome.com/v4.7.0/assets/font-awesome-4.7.0.zip
cd fontawesome; unzip font-awesome-4.7.0.zip
```

### D3 V4 . NOT REQUIRED 
wget https://d3js.org/d3.v4.min.js

### WebCola v. 3.3.8 . NOT REQUIRED 
wget https://github.com/tgdwyer/WebCola/archive/v3.3.8.tar.gz

## Create a bundle for everything

tar cvf send.tar angular.js angular.min.js d3.v4.min.js jquery-3.3.1.js jquery-3.3.1.min.js css fontawesome ui-select-0.19.8 jstree-3.3.5 bower-angular-sanitize-1.7.2 ngJsTree-0.0.10 ace-builds-1.4.1 WebCola-3.3.8/ js

### Materialize v1.0.0 . REQUIRED

<!-- run -->
```
wget -O "materialize-v1.0.0.zip" https://github.com/Dogfalo/materialize/releases/download/1.0.0/materialize-v1.0.0.zip 
unzip materialize-v1.0.0.zip 
```

### https://github.com/google/material-design-icons . REQUIRED 

<!-- run -->
```
wget -O "material-design-icons-v3.0.1_tar.gz" https://github.com/google/material-design-icons/archive/3.0.1.tar.gz
tar zxvf material-design-icons-v3.0.1_tar.gz
```

### Animate 3.7.0 . NOT REQUIRED 
wget https://daneden.github.io/animate.css/

### Cytoscape 3.4.0 . REQUIRED 

<!-- run -->
```
wget -O "v3.4.0.tar.gz" https://github.com/cytoscape/cytoscape.js/archive/v3.4.0.tar.gz 
tar zxvf v3.4.0.tar.gz
```

### popper 1.14.7 . REQUIRED 

<!-- run -->
```
wget -O "popper.min.js" https://unpkg.com/popper.js@1.14.7/dist/umd/popper.min.js
```

### cytoscape popper 1.0.4 . REQUIRED 

<!-- run -->
```
wget -O "v1.0.4.tar.gz" https://github.com/cytoscape/cytoscape.js-popper/archive/v1.0.4.tar.gz 
tar zxvf v1.0.4.tar.gz
```

### Tippy 4.0.1 . REQUIRED 

<!-- run -->
```
wget -O "tippy.min.js" https://unpkg.com/tippy.js@4.0.1/umd/index.all.min.js
wget -O "tippy.css" https://unpkg.com/tippy.js@4.0.1/index.css
```

### cytoscape js cxt menu . REQUIRED 

<!-- run -->
```
wget -O "v3.0.2.tar.gz" https://github.com/cytoscape/cytoscape.js-cxtmenu/archive/v3.0.2.tar.gz
tar zxvf v3.0.2.tar.gz
```


