# eigenHelper
Eigenmode visualisation for simple frame and beam structures.
This browser app allows the user to build simple frame and beam
structures, assign specific material and geometric properties.
Various types of supports are available, and it is also possible
to define hinge-ends for the elements.
The calfem-based engine assembles the global mass and
stiffness matrices and solves the corresponding eigenvalue problem.
The obtained eigenvectors are used to reconstruct mode shapes of the structure, which are plotted for closer inspection.

Copyright (c) 2022 Adam Sciegaj

# Demonstration

# Installation

Build the Docker container with

`docker build -t eigenhelper -f Dockerfile .`

Run the Docker container with

`docker run -p 80:5006 eigenhelper:latest`

The app can then be accessed at
[localhost](http://localhost)

# Usage
A short reference can be displayed (and hidden) by clicking the top toggle "Show/Hide Help". The app id divided into four main modules - Node, Element,  Support, and Solver, which need to be used in this exact order.

## Node module
In the node module, the user specifies all the nodes which are present in the model. **Note that hinges are defined later in the Element module - not here!**

To define the node, the user specifies its x- and y-coordinates in the designated input fields and clicks "Add Node" button. The Node ID input field is updated automatically after a node is created, but can also be updated manually if more refined control over node numbering is needed.

When a node is defined, it is at once plotted on the canvas. It is possible to hide nodes by clicking on the corresponding entry in the legend. To hide node numbers, click the "Hide Node Numbers" toggle above the plot window.
Clicking the "Show Node Info" toggle located above the graph window lists
all nodes that are currently present in the model along with their coordinates.

To delete a node with a specific ID, enter this ID in the "Node to be deleted" input field and click "Remove Node".
**Note that Node ID is always an integer, even though some nodes can be displayed with and "-H" suffix to signify that they represent a hinge.**
It is also possible to remove all nodes at once by clicking the appropriate button - this can be used to quickly clear the model and start from the beginning.

After all the necessary nodes have been defined, the user exits the module by clicking on the "Define Elements" button, after which the Element module is activated.

## Element module
In the element module, the user specifies all the elements which define the structure.

To define an element, the user specifies the start and end nodes (denoted A and B, respectively).
If an end contains a hinge (i.e., is free to rotate), an appropriate checkbox must be selected (Hinge at A creates a hinge at the beginning of the element, while Hinge at B creates a hinge at the end of the element).
Following that, material properties (Young's modulus and density) and cross-section geometry (area and area moment of inertia) need to be specified. Those input field accept float values.
When the above is specified, the element can be created by clicking "Add Element" button.

When an element is created, it is at once plotted on the canvas. It is possible to hide all elements by clicking on the corresponding entry in the legend. To hide element numbers, click the "Hide Element Numbers" toggle above the plot window.
Clicking the "Show Element Info" toggle located above the graph window lists
all elements that are currently present in the model along with their nodes.

To delete an element with a specific ID, enter this ID in the "Element to be deleted" input field and click "Remove Element".
It is also possible to remove all elements at once by clicking the appropriate button.

After all elements have been defined, the user exits the module by clicking on the "Define Supports" button, after which the Support module is activated.

## Support module
In the support module, the user defined the boundary conditions for the model.

Currently, there are six possible support types to choose from (S1-S6).
To choose a support, click on the appropriate button.
To help the user, the symbol of the currently chosen support is highlighted.
Having chosen the support, the user enters the ID of the node where the support is supposed to be and clicks on "Add Support".
Only one support can be added to a node.

When a support is created, its symbol is plotted on the canvas. It is possible to hide the support symbols by clicking on the corresponding entry in the legend.
Clicking the "Show Support Info" toggle located above the graph window lists
all supports that are currently present in the model along with their nodes.

To remove support from a node with specific ID, enter that ID into the "Remove support at node" input field and click on Remove Support.
Like previously, it is also possible to remove all supports from the model by
clicking on the "Remove All Supports" button.

After all supports have been defined, the user exits the module by clicking on the "Check Model" button, after which the Solver module is activated.


## Solver module
If the model was defined correctly and the stiffness matrix is not singular, the model passes the check, and the "Solve" button appears.
By clicking this button, the eigenvalue problem is solved and the Solver module is activated.

To begin with, the first mode shape is directly shown on the canvas along with the corresponding natural frequency.
It is possible to hide the mode shape on the plot by clicking the corresponding entry in the legend.
To change the mode shape, the user can use the spinner (or enter the number of the mode shape) to specify which mode shape is to be plotted. 
It is possible to adjust the scale of the plotted mode shape by appropriate adjustment of the slider.
Pressing the "Flip" button changes the sense of the eigenvectors, for a more comprehensive view of free vibrations.

## Miscellaneaous
Have fun playing with eigenHelper!