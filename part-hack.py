'''
Run using AppImage python:
~/.FreeCAD/squashfs-root/usr/bin/python

First add the location of FreeCAD.so to the PYTHONPATH: PYTHONPATH=${PYTHONPATH}:.FreeCAD/squashfs-root/usr/lib


+ Extracting app-image: ~/bin/freecad --appimage-extract
+ https://stackoverflow.com/questions/67325416/how-to-embed-freecad-in-a-python-virtual-environment

+ Paths that are separated like lower case is need to be seperated. Enter the path group, cut and paste the path
+ Intersection parts need to have their paths combined. Select the two parts in inkscape and make a union.

+ To use the parts export all as a step file
+ to use as an extrusion set the depth to the desired level and use the embed tool in freecad
+ to use as an indent set some large pad length, place at the desired depth, and use the Part->cut tool

+ NOTE during export if the bodies in the part are not visible it will raise "<Import> ImportOCAF2.cpp(1159): fout_top#Part has null shape". Toggle their visibility and it will fix this
'''


import click
import FreeCAD
import BOPTools.SplitFeatures
import Draft
import Part
import os


def parts_intersect(parta, partb):
  '''
  This is hacky and depends on the text being exported as a single path and read in FreeCAD as multiple paths

  Letters with seperate sections have to be broken into seperate paths at the SVG export.
  '''
  return parta.Label in partb.Label or partb.Label in parta.Label


def is_sub_path(label):
    return (len(label)>len("path00000")) and (label[-3:-1] == "00")


def get_base_name(label):
    if is_sub_path(label):
        return label[:-3]
    return label


def main(fname, outfname, pad_length):
    FreeCAD.loadFile(fname) # the SVG is now the active document
    doc = FreeCAD.activeDocument()

    '''
    cycle through objects in doc, if two object intersect take the xor of them. Since we're doing text we only do this once.
    Sort parts by label, assume only 2 sections per part.
    '''

    base_parts = dict()

    for path in doc.Objects:
        base = get_base_name(path.Label)
        if base not in base_parts:
            base_parts[base] = []
        base_parts[base].append(path)

    processed_objects = []

    for key, value in base_parts.items():
        print(key, value)
        if len(value) > 1:
            j = BOPTools.SplitFeatures.makeXOR(name='XOR')
            j.Objects = value
            j.Proxy.execute(j)
            processed_objects.append(j)
        else:
            processed_objects.extend(value)


    '''
    Make each object a sketch
    Make sketches into parts
    '''

    parts = []
    sketches = []
    for part in processed_objects:
        sketch = Draft.make_sketch(part, autoconstraints=True)
        if sketch is None:
            print(f"Error in part {part} {vars(part)}, failed to make sketch, skipping")
            continue
        sketches.append(sketch)
        name = f'Body_{sketch.Label}'
        body = doc.addObject('PartDesign::Body', name)
        # print(body, body.Label, name, doc.getObjectsByLabel(name))
        # doc.recompute()
        body.Group = [sketch]
        parts.append(body)

        pad_name = f'Pad_{body.Label}'
        pad = body.newObject('PartDesign::Pad', pad_name)
        # pad = doc.getObject(pad_name)
        pad.Profile = sketch
        pad.Length = pad_length
    doc.recompute()

    #j = BOPTools.SplitFeatures.makeXOR(name='XOR')
    #j.Objects = parts
    #j.Proxy.execute(j)


    base, ext = os.path.splitext(outfname)
    grouped_parts = doc.addObject('App::Part','Part')
    grouped_parts.addObjects(parts)

    doc.saveAs(outfname)
    #Part.export(grouped_parts, f"{base}.step")


@click.command()
@click.option("--fname", "-f", required=True, help="SVG input")
@click.option("--out", "-o", required=True, help="Output filename")
@click.option("--length", "-l", default=10, help="Extrusion length")
def click_main(fname, out, length):
    main(fname, out, length)


if __name__ == "__main__":
    click_main()
