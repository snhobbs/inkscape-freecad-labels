## Goals
+ Make a label in inkscape or any other SVG exporting program
+ Export the label as paths only (no fonts)
+ Import into FreeCAD
+ Turn the label into objects that can be placed on an objects surface to mark a label


## Approach

### Generate Path Only SVG
+ The inkscape label to paths is describe [here](https://gist.github.com/snhobbs/85aaf8b2750a3a163d3579257b71d124)
+ Make sure that all objects are closed, instead of lines solid objects need to be used.

### Import to FreeCAD

+ <https://wiki.freecad.org/Import_text_and_geometry_from_Inkscape/en>
+ <https://www.youtube.com/watch?v=L-jqKb0f-78&ab_channel=61quick>

1. File->import filename.svg
2. Open SVG as geometry

We now have a collection of a ton of individual objects, one for each individual path.

#### Issues
+ Paths with loops come up as seperate paths, eg. an o has the outer and inner loop as seperate paths. These need to be combined into a single sketch to extrude properly.
+ There are many parts each of which will need to be their own body or joined to another body.

#### Algorithm
+ Cycle through all parts, find the ones that are completely within another and XOR them
+ For non-intersecting paths use the draft->upgrade tool
+ Make each into their own body and extrude
+ Join the objects using a boolean XOR. This will keep the positively extruded parts and subtract the negative extrusion.
