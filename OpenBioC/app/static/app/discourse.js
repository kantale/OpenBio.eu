
/*
* Called from ui.js : window.cydisc = discourse_setup_cytoscape();
* Inits the discourse cytoscape graph
*/
function discourse_setup_cytoscape() {
    
    var cydisc = cytoscape({
        container: document.getElementById('cydisc'), // container to render in. defined in right_panel.html <div id="cydisc"></div>
        boxSelectionEnabled: false,
        autounselectify: true,
        elements: [],
        style: [
		    {
			    selector: 'node',
				css: {
			        'content': 'data(label)',
					'font-size': '12pt'
				}
			},
			{
				selector: 'edge',
				css: {
					'width': 3,
					'curve-style': 'bezier',
					'target-arrow-shape': 'triangle'
				}
			},
			{
				selector: 'edge[type="neutral"]',
				style: {
					'line-color': 'gray',
					'target-arrow-color': 'gray',
				}
			},
			{
				selector: 'edge[type="neutral-note"]',
				style: {
					'line-color': 'gray',
					'line-style': 'dashed',
					'target-arrow-color': 'gray',
				}
			},
			{
				selector: 'node[type="solution"]',
				style: {
					'background-color': 'yellow'
				}
			},
			{
				selector: 'node[type="issue"]',
				style: {
					'background-color': 'blue'
				}
			},
			{
				selector: 'node[type="note"]',
				style: {
					'background-color': 'gray'
				}
			},
			{
				selector: 'node[type="position-in-favor"]',
				style: {
					'background-color': 'green'
				}
			},
			{
				selector: 'node[type="position-against"]',
				style: {
					'background-color': 'red'
				}
			}
        ],

        //zoom: 1,
        pan: { x: 0, y: 0 },

        layout: {
            name: 'dagre',
            rankDir: 'BT'
        }
    });

    cydisc.ready(function () {           // Wait for nodes to be added  
        cydisc.layout({                   // Call layout
            name: 'dagre',
            rankDir: 'BT'
        }).run();

        //This removes the attribute: position: 'absolute' from the third layer canvas in cytoscape.    
        document.getElementById("cydisc").querySelector('canvas[data-id="layer2-node"]').style.position = null;
    });

    cydisc.resize();

    //Setup tippy.
    //tippy elements are defined in index.html (at the end, rught after angular scope)
    var tippyDiv;
    cydisc.on('mouseover', 'node', function(event) {
        var a = event.target;
            $('#tippy-text').html(a.data().tooltipText);
            $('#tippy-author-name').text(a.data().author);
            $('#tippy-date').text(a.data().date);
          //$('#tippy-date').text((new Date(a.data().date)).toLocaleString('en-GB', { timeZone: 'UTC' }));
            var makeTippy = function(node){
                return tippy(node.popperRef(), {
                    content: function(){
                        var div = document.getElementById('tippy-popup');
                        return div.innerHTML;
                    },
                    trigger: 'manual',
                    arrow: true,
                    placement: 'bottom',
                    hideOnClick: true,
                    multiple: true,
                    sticky: true,
                    theme: 'tomato'
                });
            };
        tippyDiv = makeTippy(a);
        tippyDiv.show();
    });

    cydisc.on('mouseout', 'node', function(event) {
        tippyDiv.hide();
    });

    return cydisc;
};


/*
* Deletes all elements of a cytoscape discourse graph
*/
function discourse_clear(){
    window.cydisc.remove('edge, node');


    window.cydisc.resize();
    window.cydisc.reset();
    window.cydisc.center();
}

/*
* Called when the "visualization" button is pressed in Q&A
* It is called through the angular wrapper $scope.qa_visualize_pressed
*/
function discourse_visualize_pressed(
    qa_comment_id,
    qa_username,
    qa_title,
    qa_created_at,
    qa_thread
    ) {

    var nodes = [];
    var edges = [];

    /*
    * Takes as input the html comment. Creates a label
    */
    function create_node_label(input) {
        var label = input.replace(/<\/?[^>]+(>|$)/g, "");
        if (label.length >= 20) {
            return label.slice(0, 20) + '...';
        }
        return label;
    }

    /*
    * Takes as input a comment. Returns a cytoscape node
    */
    function create_node(comment) {
        var type = 'note';
        if (comment['opinion'] == 'agree') {
            type = 'position-in-favor';
        }
        else if (comment['opinion'] == 'disagree') {
            type = 'position-against';
        }
        else if (comment['opinion'] == 'solution') {
            type = 'solution';
        }
        else if (comment['opinion'] == 'issue') {
            type = 'issue';
        }

        return {
            group: 'nodes',
            data: {
                id: comment.id,
                author: comment.username,
                label: create_node_label(comment.comment_html),
                tooltipText: comment.comment_html,
                date: comment.created_at,
                type: type
            }
        }
    }

    /*
    * Same as the create_node, but creates the root node
    */
    function create_root_node() {
        return {
            group: 'nodes',
            data: {
                id: qa_comment_id,
                author: qa_username,
                label: create_node_label(qa_title),
                tooltipText: qa_title,
                date: qa_created_at,
                type: 'issue'
            }
        }
    }

    /*
    * Recursively take a commend in the thread
    * Add cytosscape nodes and edges 
    */
    function create_nodes_edges_of_thread(thread, root_node) {
        thread.forEach(function(comment) {
            var this_node = create_node(comment);
            nodes.push(this_node);
            var edge_type = 'neutral';
            if (this_node.data.type == 'note') {
                edge_type = 'neutral-note';
            }
            edges.push({
                group: 'edges',
                data: {type: edge_type, source: this_node.data.id, target: root_node.data.id}
            });

            if (comment.children) {
                 create_nodes_edges_of_thread(comment.children, this_node);
            }
        });
    }

    //Empty the graph
    discourse_clear();

    // Create and add the root node
    var root_node = create_root_node();
    nodes.push(root_node);

    // Create the rest of the nodes, edges
    create_nodes_edges_of_thread(qa_thread, root_node);

    // Add nodes and edges
    window.cydisc.add(nodes);
    window.cydisc.add(edges);

    // Redraw layout, so they appear nicely
    window.cydisc.layout({                    // Call layout
        name: 'dagre',
        rankDir: 'BT'
    }).run();

    // cytoscape boilerplate..
    window.cydisc.resize();
    window.cydisc.center();

};



