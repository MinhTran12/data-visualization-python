from tkinter import *
from tkinter import messagebox
import graphDrawer
import forceDirectedLayout

## you can use a random starting node! But the layout has the best result if you use the nodes with
## the most edges in the middle: for DFS this is 49 and for BFS this is 11

### available network type: random, tree
import screenSettings

root = Tk()
height= int(screenSettings.screen_height)
width = int(screenSettings.screen_width)
root.geometry(str(width) + "x" + str(height))
entry = Entry(root)
layout_options = ["random", "tree", "force directed", "layered layout", "multilayer layout", "projection"]
start_node_options = ["random", "low degree", "high degree"]
start_layout_options = ["random", "semi random", "circle", "tree"]
type_options = ["BFS", "DFS"]
dataset_options = ["LesMiserables.dot", "JazzNetwork.dot", "noname.dot", "easy.dot", "easy2.dot", "LeagueNetwork.dot", "devonshiredebate_withonlytwoclusters.dot"]
dr_options = ["t-SNE", "MDS", "ISOMAP"]
force_options = ["Eades", "Reingold", "Reingold - Grid"]

def drawLeft():
    leftcanvas.delete("all")
    layout_type = variable_layout.get()
    type = variable_type.get()
    dataset = variable_dataset.get()
    node = variable_start_node.get()
    random = (node == "random")
    start_node = 0
    if node == "low degree":
        start_node = 11
    elif node == "high degree":
        start_node = 12

    graphDrawer.draw_graph(leftcanvas, dot_file_name=dataset,
                           network_type=layout_type,
                           search_algorithm=type,
                           starting_node=start_node,
                           starting_layout=variable_start_layout.get(),
                           inertia=bool(inertia.get()),
                           gravitation=bool(gravitation.get()),
                           angle=bool(angle.get()),
                           scale=bool(scale.get()),
                           position=bool(position.get()),
                           visibility=bool(visibility.get()),
                           tree_extra_edges=bool(bonusEdges.get()),
                           get_random_node=random,
                           draw_numbers=bool(nodeId.get()),
                           force_directed_algo=variable_force.get(),
                           dr=variable_projection.get()
                           )

def drawRight():
    rightcanvas.delete("all")
    layout_type = variable_layout.get()
    type = variable_type.get()
    dataset = variable_dataset.get()
    node = variable_start_node.get()
    random = (node == "Random")
    start_node = 0
    if node == "Low degree":
        start_node = 11
    else:
        start_node = 12

    graphDrawer.draw_graph(rightcanvas, dot_file_name=dataset,
                           network_type=layout_type,
                           search_algorithm=type,
                           starting_node=start_node,
                           starting_layout=variable_start_layout.get(),
                           inertia=bool(inertia.get()),
                           gravitation=bool(gravitation.get()),
                           angle=bool(angle.get()),
                           scale=bool(scale.get()),
                           position=bool(position.get()),
                           visibility=bool(visibility.get()),
                           tree_extra_edges=bool(bonusEdges.get()),
                           get_random_node=random,
                           draw_numbers=bool(nodeId.get()),
                           force_directed_algo=variable_force.get(),
                           dr=variable_projection.get()
                           )

def do_zoom1(event):
    x = leftcanvas.canvasx(event.x)
    y = leftcanvas.canvasy(event.y)
    factor = 1.001 ** event.delta
    leftcanvas.scale(ALL, x, y, factor, factor)

def do_zoom2(event):
    x = rightcanvas.canvasx(event.x)
    y = rightcanvas.canvasy(event.y)
    factor = 1.001 ** event.delta
    rightcanvas.scale(ALL, x, y, factor, factor)

# creation of select boxes and buttons
angle = IntVar(root)
scale = IntVar(root)
position = IntVar(root)
visibility = IntVar(root)
inertia = IntVar(root)
gravitation = IntVar(root)
variable_layout = StringVar(root)
variable_start_layout = StringVar(root)
variable_type = StringVar(root)
variable_dataset = StringVar(root)
variable_start_node = StringVar(root)
bonusEdges = IntVar(root)
nodeId = IntVar(root)
variable_projection = StringVar(root)
variable_force = StringVar(root)


# set default value
angle.set(0)
scale.set(0)
position.set(0)
visibility.set(0)
inertia.set(0)
gravitation.set(0)
variable_layout.set(layout_options[0])
variable_start_layout.set(start_layout_options[0])
variable_type.set(type_options[0])
variable_dataset.set(dataset_options[3])
variable_start_node.set(start_node_options[0])
bonusEdges.set(0)
nodeId.set(0)
variable_projection.set(dr_options[0])
variable_force.set(force_options[0])

# creation of labels
label_layout = Label(root)
label_start_node = Label(root)
label_starting_layout = Label(root)
label_tree_type = Label(root)
label_dataset = Label(root)
label_force_directed = Label(root)
label_layered_layout = Label(root)
label_tree = Label(root)
projection_label = Label(root)
label_force = Label(root)

button_layout = OptionMenu(root, variable_layout, *layout_options)

label_layout['text'] = "Layout"
button_start_node = OptionMenu(root, variable_start_node, *start_node_options)
label_start_node['text'] = "Starting node"
button_starting_layout = OptionMenu(root, variable_start_layout, *start_layout_options)
label_starting_layout['text'] = "Starting layout"
button_tree_type = OptionMenu(root, variable_type, *type_options)
label_tree_type['text'] = "Type of search"
button_dataset = OptionMenu(root, variable_dataset, *dataset_options)
label_dataset['text'] = "Dataset"
projection_label['text'] = "Dimensionality Reduction"
button_dr = OptionMenu(root, variable_projection, *dr_options)
label_force['text'] = "Force Directed"
button_force = OptionMenu(root, variable_force, *force_options)

left = Button(root, text="Draw Left", command = drawLeft)
right = Button(root, text="Draw Right", command = drawRight)
angle_button = Checkbutton(root,text="Angle compatibility", variable=angle)
scale_button = Checkbutton(root,text="Scale compatibility", variable=scale)
position_button = Checkbutton(root,text="Position compatibility", variable=position)
visibility_button = Checkbutton(root,text="Visibility compatibility", variable=visibility)
inertia_button = Checkbutton(root, text="Inertia", variable=inertia)
gravitation_button = Checkbutton(root, text="Gravitation", variable=gravitation)
bonusEdges_button = Checkbutton(root, text="Show only tree edges", variable=bonusEdges)
nodeId_button = Checkbutton(root, text="Show Node IDs", variable=nodeId)

label_force_directed['text'] = "Options for force directed layout"
label_tree['text'] = "Option for tree layout"
label_layered_layout['text'] = "Similarities for layered layout"


# labels placement
label_dataset.place(x=5, y=height-130)
label_layout.place(x=5, y=height-100)
label_tree_type.place(x=5, y=height-70)
label_starting_layout.place(x=5, y=height-40)

label_start_node.place(x=250, y=height-100)
projection_label.place(x=250, y=height-130)
label_force.place(x=250, y=height - 70)

# dropdowns placement
button_dataset.place(x=105, y=height-135)
button_layout.place(x=105, y=height-105)
button_tree_type.place(x=105, y=height-75)
button_starting_layout.place(x=105, y=height-45)

button_dr.place(x=400, y=height-135)
button_start_node.place(x=400, y=height-105)
button_force.place(x=400, y=height-75)

## selectboxes for force directed layout
label_force_directed.place(x=500, y=height-130)
inertia_button.place(x=500, y=height-110)
gravitation_button.place(x=500, y=height-90)

## selectbox for tree layout
label_tree.place(x=500, y=height-60)
bonusEdges_button.place(x=500, y=height-40)

## selectboxes for layered layout
label_layered_layout.place(x=700, y=height-130)
angle_button.place(x=700, y=height - 110)
scale_button.place(x=700, y=height - 90)
position_button.place(x=700, y=height - 70)
visibility_button.place(x=700, y=height - 50)

## extra options
nodeId_button.place(x=width-130, y=height-50)

# draw buttons
left.place(x=width-100, y=height-110)
right.place(x=width-100, y=height-80)


leftcanvas = Canvas(root, width=width/2, height=(height - 140), background="#ffffff")
rightcanvas = Canvas(root, width=width/2, height=(height - 140), background="#ffffff")
leftcanvas.grid(column=1, row=1)
leftcanvas.bind("<MouseWheel>", do_zoom1)
leftcanvas.bind('<ButtonPress-1>', lambda event: leftcanvas.scan_mark(event.x, event.y))
leftcanvas.bind("<B1-Motion>", lambda event: leftcanvas.scan_dragto(event.x, event.y, gain=1))
rightcanvas.grid(column=2, row=1)
rightcanvas.bind("<MouseWheel>", do_zoom2)
rightcanvas.bind('<ButtonPress-1>', lambda event: rightcanvas.scan_mark(event.x, event.y))
rightcanvas.bind("<B1-Motion>", lambda event: rightcanvas.scan_dragto(event.x, event.y, gain=1))
root.mainloop()