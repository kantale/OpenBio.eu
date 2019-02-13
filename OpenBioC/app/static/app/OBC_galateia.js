
var tool_installation_editor = ace.edit("tool_installation_editor");
tool_installation_editor.setTheme("ace/theme/textmate");
tool_installation_editor.session.setMode("ace/mode/sh");


var tool_validation_editor = ace.edit("tool_validation_editor");
tool_validation_editor.setTheme("ace/theme/textmate");
tool_validation_editor.session.setMode("ace/mode/sh");

/*
* It is important to register these events AFTER load so that they are triggered after custom JSTREE functions
* More: https://groups.google.com/forum/#!topic/jstree/BYppISuCFRE
*/
window.onload = function () {


	//Disable drop event. So that users cannot drop tool nodes in the installation/validation editors
	tool_installation_editor.container.addEventListener("drop", function (e) {
		//This doesn't work
    	//e.preventDefault();
    	//return false;

      	//Curiously.. this works!
    	tool_installation_editor.undo();
	});

	tool_validation_editor.container.addEventListener("drop", function (e) { // drop
    	tool_validation_editor.undo();
	});

	//Galateia's code
	if (true) { //Activate/deactivate code
	

		/* initialize global variables */
		//var cola,svg,root,treeData; // Alex commented it out. There were undefined 

		//We should run these commands only once!
		var mynodes=[],mylinks=[],children=[],tmp_children=[], parents=[];

		var width = 768, height = 517;

	    var color = d3.scaleOrdinal(d3.schemeCategory20);


		obc_cola = cola.d3adaptor(d3)
		        .linkDistance(100)
		        .avoidOverlaps(true)
		        .handleDisconnected(false)
		        .size([width, height]);	

		//svg = d3.select("body").append("svg")
		svg = d3.select("#d3wf").append("svg")
		        .attr("width", width)
		        .attr("height", height)
				.classed("svg-content-responsive", true)
			.call(d3.zoom().on("zoom", function () {
				svg.attr("transform", d3.event.transform)
			})
			.scaleExtent([1,2])
            .translateExtent([[0,0],[width,height]])
			).on("dblclick.zoom", null);
		
		
		

		//buildTree(); // Run this for initialization

		/* Function that initializes cola and tree root */	
		//function buildTree() {
		window.buildTree = function(workflow) {
			/*
			Example of workflow
			var workflow = [
				    {
				        "id": "a",
				        "parent": "#"
				    },
				    {
				        "id": "b",
				        "parent": "a"
				    },
				        {
				        "id": "d",
				        "parent": "a"
				    },
				        {
				        "id": "c",
				        "parent": "b"
				    }	        
			];

			*/
			
			//NEW STUFF
			//get existing data if any and merge them with new data		
			if(window.treeData) workflow = workflow.concat(treeData);
			
				workflow.forEach(function(d) {
					if(d.parent=='#') {
						root = d;
						if(mynodes.indexOf(root) == -1) mynodes.push(root);
					 }			
				});
			
			
				treeData = workflow;
				
				
				update();	
				
				if (false) {
					d3.json("/static/app/data.json", function (error, data) {

						/* read the given data */	
					
						data.forEach(function(d) {
							if(d.parent=='#'){
								root = d;
								mynodes.push(root);
							}			
						});
				
						treeData = data;	
						update();	  
						  
					});	
				}
				
			
		} // buildTree

		/** update graph: add and remove nodes/links **/
		function update() {

		
			d3.selectAll("svg > *").remove();
			
			//call the function to add the links to final nodes	
			addLinks();
			
			/** constraints **/	
			/*
			var el = document.getElementById("d3wf"),	
			x = el.offsetLeft, y = el.offsetTop,
			constraints = [];			
			var realGraphNodes = mynodes.slice(0),
			virtualNodes = mynodes,
			pageBounds = { x: x, y: y, width: 768, height: 517 },
            page = svg.append('rect').attr('id', 'page').attr(pageBounds),
            nodeRadius = 10,
            topLeft = { x: pageBounds.x, y: pageBounds.y, fixed: true },
            tlIndex = virtualNodes.push(topLeft) - 1,
            bottomRight = { x: pageBounds.x + pageBounds.width, y: pageBounds.y + pageBounds.height, fixed: true },
            brIndex = virtualNodes.push(bottomRight) - 1;
			
			
			for (var i = 0; i < mynodes.length; i++) {
				constraints.push({ axis: 'x', type: 'separation', left: tlIndex, right: i, gap: nodeRadius });
				constraints.push({ axis: 'y', type: 'separation', left: tlIndex, right: i, gap: nodeRadius });
				constraints.push({ axis: 'x', type: 'separation', left: i, right: brIndex, gap: nodeRadius });
				constraints.push({ axis: 'y', type: 'separation', left: i, right: brIndex, gap: nodeRadius });
			}
			console.log("constraints : "+constraints);
			mynodes = realGraphNodes;
			*/
			//initialize cola: .nodes(virtualNodes)
			
			

			/* initialize cola */  
			  obc_cola
				//.nodes(virtualNodes)
	            .nodes(mynodes)
				.links(mylinks)
				//.constraints(constraints)
	            .start();
				
			// define arrow markers for graph links
			svg.append('svg:defs').append('svg:marker')
			.attr('id', 'end-arrow')
				.attr('viewBox', '0 -5 10 10')
				.attr('refX', 10)
				.attr('markerWidth', 6)
				.attr('markerHeight', 6)
				.attr('orient', 'auto')
				.append('svg:path')
				.attr('d', 'M0,-5L10,0L0,5')
				.attr('fill', '#515151');	
		
				

			var margin = 6;	
			var pad = 3;
		

			var node = svg.selectAll(".node")
	          .data(mynodes)
	          .enter().append("rect")
	            .attr("class", "node")
	            .attr("rx", 5).attr("ry", 5)
				.style("fill", '#C6E9D9') //color based on type
	            .call(obc_cola.drag)
				.on("dblclick", collapse);
				
				var link = svg.selectAll(".link")
	            .data(mylinks)
	            .enter().append("line")
				.attr("class", function(d){ return ["link", d.source, d.target].join(" "); })
				.call(obc_cola.drag);
				
				var label = svg.selectAll(".label")
                .data(mynodes)
                .enter().append("text")
                .attr("class", "label")
                .text(function (d) { return d.text; })
                .call(obc_cola.drag)
				.on("dblclick", function (d) { collapse(d); })
                .each(function (d) {
                    var b = this.getBBox();
                    var extra = 2 * margin + 2 * pad;
                    d.width = b.width + extra;
                    d.height = b.height + extra;
                });
				

			obc_cola.on("tick", function () {
				
				/*
					node.attr("x", function (d) { return d.x; })
					    .attr("y", function (d) { return d.y; });
				*/
				
				/*	
		            node.attr("x", function (d) {
							var newdim = d.x - nodeWidth / 2 + 3 ;
							return Math.max(0, Math.min(760, newdim));
								
						})
	                .attr("y", function (d) { 
							var newdimy = d.y - nodeHeight / 2 + 3 ;
							return Math.max(0, Math.min(510, newdimy)); 
	
					});
				*/
				
				 // node.attr("cx", function(d) { return d.x = Math.max(r, Math.min(w - margin, d.x)); })
				//	.attr("cy", function(d) { return d.y = Math.max(r, Math.min(h - margin, d.y)); });
				
				node.each(function (d) { d.innerBounds = d.bounds.inflate(-margin); })
                    .attr("x", function (d) { return d.innerBounds.x; })
                    .attr("y", function (d) { return d.innerBounds.y; })
                    .attr("width", function (d) { return d.innerBounds.width(); })
                    .attr("height", function (d) { return d.innerBounds.height(); });
						
							
				link.each(function (d) {
						d.route = cola.makeEdgeBetween(d.source.innerBounds, d.target.innerBounds, 5);
						if (isIE())  this.parentNode.insertBefore(this, this);
					});

				link.attr("x1", function (d) { return d.route.sourceIntersection.x; })
					.attr("y1", function (d) { return d.route.sourceIntersection.y; })
					.attr("x2", function (d) { return d.route.arrowStart.x; })
					.attr("y2", function (d) { return d.route.arrowStart.y; });	
								
					
				 label
                    .attr("x", function (d) { return d.x })
                    .attr("y", function (d) { return d.y + (margin + pad) / 2 });
				
	          
	        });
			
		} // update end
		
	/** Toggle nodes' children on double click **/	
  function collapse(d) {
    
		  if(d.children){  	////if clicked node has already open children CLOSE them
			
			//do not include the ones with flag "open"
			d.children  = d.children.filter(function(y) {return y.flag!=="open";});
						
			//remove (not flaged) children nodes from total nodes
			mynodes  = mynodes.filter(function(x) {return d.children.indexOf(x) < 0; });
						
				//remove children RECURSIVELY
				var my_children=d.children;
				d.children=null;	
					my_children.forEach(function(f){
						if(f.children) collapse(f);
					})

			}else { 	////if clicked node has closed children, OPEN them
	
			tmp_children = findChildren(d);
			mynodes = mynodes.concat(tmp_children);	//add children to total nodes		
			if(tmp_children.length > 0) d.children = tmp_children; //each node has an array of its' children
			tmp_children=[];
		
		}
		
		//update graph with the new nodes(removed or added)
		update();
  }
  //collapse end
  
  
  //find all children of a given node
  function findChildren(d){
		treeData.forEach(function(n) {
			// add children nodes
				if(n.parent==d.id){
				//check if already exists in nodes (can be a child of another node)
					if(!existsInNodes(n)){	
						tmp_children.push(n);
					}else{
					 //add NEW PARENTS and OPEN FLAG to existing node
					 addNodeInfo(n);				 
					}
				}	
		})  
		
		return tmp_children;
  
  }
  
    //check if a node object exists in mynodes
	function existsInNodes(n){
		var answer=false;
			mynodes.find(function(item, i){	
				if(item.id==n.id)
				answer=true;
			})
		
		return answer;
	}
	
	//add new link to existing node (when new parent is added)
	function addNodeInfo(n){	

		mynodes.find(function(item, i){	
			if(item.id==n.id){ //if it is already part of the graph	add a flag so it stays always open
				item.flag="open";
				
				mynodes.find(function(item2, i2){	
				   if(item2.id==n.parent){
			   
					   //check if parents exists
					   if(typeof item.parents!== "undefined"){
						   if(item.parents.indexOf(item2.id) < 0){
									parents.push(item2.id);
									item.parents=item.parents.concat(parents);
									parents=[];
								}
					    }else{
						   parents.push(item2.id);
						   item.parents=parents;
						   parents=[];
						   
						 }			
					}
			
				})
				
				//add recursively the OPEN FLAG
				addOpenFlag(item.parent);
				if(item.parents) { 
					item.parents.forEach(function(i){
						addOpenFlag(i);
					})
				}

			}
			
		})	
	}
	
	function addOpenFlag(item){

		mynodes.forEach(function(f){
			if(item === f.id){
				f.flag="open";
				addOpenFlag(f);
				} 
			})

	}

   //** his function adds all the links to the approproate nodes **//
   function addLinks(){
   		mylinks=[];
		var mysource, mytarget;
		mynodes.find(function(item, i){

			mytarget=i;
			
			mynodes.find(function(item_, i_){ //add link from parent node
				if(item_.id === item.parent) 
				{
					mysource =i_;	
					mylinks.push({source: mysource,target:mytarget});
				}					
			});
											
			if(typeof item.parents!=="undefined"){ //add links from the extra parents if any		
				mynodes.find(function(item_, i_){			
					item.parents.forEach(function(p) {
						if(item_.id === p) 
						mysource =i_;		
						mylinks.push({source: mysource,target:mytarget});	
					})
				
				});		
			}
			
		});

   }


	 	//Initialize with an empty workflow
	 	window.initTree = function() {
	 		mynodes=[],mylinks=[],children=[],tmp_children=[];
	 		window.buildTree([]); // [] means empty workflow
	 	}
	 	window.initTree();
	 	
	} // if (true)

		//clear function
		window.clear=function() {
		
			mynodes=[],mylinks=[],children=[],tmp_children=[];
			window.treeData=[];
			update();
			
	 	}
		
		//fit function
		window.fit=function(){
			d3.select("svg").attr("transform", "translate(0,0)");
			//d3.selectAll("svg > *").attr("transform", "translate(0,0)");
		}
	
	
		//expand all function
		window.expand=function(){
			treeData.forEach(function(f){
				collapse(f);				
			})
			
		}

		function isIE() { return ((navigator.appName == 'Microsoft Internet Explorer') || ((navigator.appName == 'Netscape') && (new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})").exec(navigator.userAgent) != null))); }
		
	// END OF GALATEIA's code

	//kantale's effort
	if (false) {
								//COLA SETUP
								var height = 500;
								var width = 960;
								var svg = d3.select("#d3wf").append("svg")
								        //.attr("width", width)
								        .attr("width", '100%')
								        .attr("height", height)
								        .style("border-style", "solid")
								        .style("border-width", "1px");


								var ark_cola = cola.d3adaptor(d3)
								        .linkDistance(100)
								        .avoidOverlaps(true)
								        .handleDisconnected(false)
										.size([width, height]);

								// define arrow markers for graph links
								//http://bl.ocks.org/rkirsling/5001347
								svg.append('svg:defs').append('svg:marker')
								    .attr('id', 'end-arrow')
								    .attr('viewBox', '0 -5 10 10')
								    .attr('refX', 6)
								    .attr('markerWidth', 10)
								    .attr('markerHeight', 10)
								    .attr('orient', 'auto')
								  .append('svg:path')
								    .attr('d', 'M0,-5L10,0L0,5')
								    .attr('fill', '#000');


								var main_g = svg.append("g");
								var wf_g = svg.append("g");


								/*
								* 
								*/
								window.update_workflow = function() {

														var color = d3.scaleOrdinal(d3.schemeCategory20);
													    graph = {
													    	nodes: [
														    	{name:'a'},
														    	{name:'b'}
														    ],
													    	links: [
														    	{source:0, target:1},
													    	]
													    };

													    // packing respects node width and height
													    graph.nodes.forEach(function (v) { v.width = 10, v.height = 10 })

													    ark_cola
													        .nodes(graph.nodes)
													        .links(graph.links)
													        .start(); 

													    var link = svg.selectAll(".link")
													        .data(graph.links)
													      .enter().append("line")
													        .attr("class", "link")
													        .style("stroke-width", 3);

													    var node = svg.selectAll(".node")
													        .data(graph.nodes)
													      .enter().append("circle")
													        .attr("class", "node")
													        .attr("r", 5)
													        .style("fill", function (d) { return color(d.group); })
													        .call(ark_cola.drag);

													    node.append("title")
													        .text(function (d) { return d.name; });

													    ark_cola.on("tick", function () {
													        link.attr("x1", function (d) { return d.source.x; })
													            .attr("y1", function (d) { return d.source.y; })
													            .attr("x2", function (d) { return d.target.x; })
													            .attr("y2", function (d) { return d.target.y; });

													        node.attr("cx", function (d) { return d.x; })
													            .attr("cy", function (d) { return d.y; });
													        //ark_cola.stop();
													    });



								};

	}

	// https://github.com/ezraroi/ngJsTree/issues/20
	// We have to register the event on the document.. 
	$(document).on('dnd_stop.vakata', function (e, data) {
		var target = $(data.event.target);

		//We assume that only a single node is been moved
		if (data.data.nodes.length != 1) {
			return;
		}

		var this_id = data.data.nodes[0]; // plink/1.9/3/1"
		//var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
		var this_id_array = JSON.parse(this_id);

		//console.log('Stopped:', this_id);
		//console.log('Stopped ID:', this_id_array[3]);

		if (this_id_array[3] === "1") { // We are moving an item from the tool search tree

			//The tools that we are dragging.
			var tool = {
				'name': this_id_array[0],
				'version': this_id_array[1],
				'edit': this_id_array[2],
			};


			if (target.closest('#tools_dep_jstree_id').length) { // We are dropping it to the dependency tool js tree div

				//console.log('Right stop');
				//console.log(tool);

				angular.element($('#angular_div')).scope().$apply(function(){
					angular.element($('#angular_div')).scope().tool_get_dependencies(tool, 1); // 1 = drag from search jstree to dependencies jstree
				});
			}
			else if (target.closest('#d3wf').length) { // We are dropping it to the workflow graph editor

				angular.element($('#angular_div')).scope().$apply(function(){
					angular.element($('#angular_div')).scope().tool_get_dependencies(tool, 2); // 2 = drag from search jstree to workflow editing
				});

				//window.update_workflow();
			}

		}
		else if (this_id_array[3] == "3") { // We are moving a variable from the dependency + variable tree
			if (target.closest('#tool_installation_editor').length) { // Adding to installation bash editor
				// https://stackoverflow.com/a/42797383/5626738 
				if (!tool_installation_editor.getReadOnly()) {
					tool_installation_editor.session.insert(tool_installation_editor.getCursorPosition(), '$' + this_id_array[0]);
				}
			}
			else if (target.closest('#tool_validation_editor').length) { // Adding to validation bash editor
				if (!tool_validation_editor.getReadOnly()) {
					tool_validation_editor.session.insert(tool_validation_editor.getCursorPosition(), '$' + this_id_array[0]);
				}
			}
		}

	});

	/*
	* JSTree item moves. Change the class (for visualization only)
	*/
	$(document).on('dnd_move.vakata', function (e, data) {
//		$('#vakata-dnd').find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
//		return;
		var target = $(data.event.target);
		var this_id = data.data.nodes[0]; // plink/1.9/3/1"

		//var this_id_array = this_id.split('/'); //[ "plink", "1.9", "3", "1" ]
		var this_id_array = JSON.parse(this_id);


		if (this_id_array[3] == '1') { // This is an item from tools_search tree
			
			if (
				(target.closest('#tools_dep_jstree_id').length && (!tool_installation_editor.getReadOnly())) || //We allow it if it is over the div with the tree AND the the tool_installation_editor is not readonly (this is a workaround to avoid checking angular: tools_info_editable)
				(target.closest('#d3wf').length) // The Workflow graph editor
			   ) { 
				data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
			}
			else {
				data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
			}
		}

		else if (this_id_array[3] == "3") { // This is an item from validation js tree

			if (
				(target.closest('#tool_installation_editor').length && (!tool_installation_editor.getReadOnly())) || 
				(target.closest('#tool_validation_editor').length   && (!tool_validation_editor.getReadOnly()))       ) {
				data.helper.find('.jstree-icon').removeClass('jstree-er').addClass('jstree-ok');
			}
			else {
				data.helper.find('.jstree-icon').removeClass('jstree-ok').addClass('jstree-er');
			}

		}


	});


};
