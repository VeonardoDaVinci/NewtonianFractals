import bpy
import numpy as np 
import os
import bpy
from bpy import context, data, ops
import time
from PIL import Image
from PIL import ImageColor as ic

from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.props import (
    IntProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
)


def main(context):
        #Addon data
    #context = bpy.context.area
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)
    mat = bpy.context.active_object.active_material
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
    texImage.location = (100,100)


    TOL = 1.e-8
    #clrs = [ic.getrgb("hsv(0, 100%, 100%)"), ic.getrgb("#db504a"), ic.getrgb("#ff6f59"), ic.getrgb("#254441"),
    #        ic.getrgb("#43aa8b"), ic.getrgb("#b2b09b")]
            
    startcolor = [70, 0, 0]
    endcolor = [20, 100, 100]


    def interpolate(startValue, endValue, stepNumber, lastStepNumber, min):
        return (endValue - startValue) * (stepNumber - min) / (lastStepNumber - min + 1) + startValue


    def generate_color_map(colors, nroots):
        colormap = {}
        for n in range(0, nroots):
            colormap[str(float(n))] = colors[n]
            print(colormap)
        return colormap


    def set_pixel_color(x, y, colormap, data, image):
        image.putpixel((x, y), colormap[str(data[x, y])])
        return image


    def set_pixel_color_from_iter(x, y, data, image, startcolor, endcolor, max=1000, mode="hue"):
        if mode == "hue":
            image.putpixel((x, y), ic.getrgb(
                "hsv(" + str(interpolate(startcolor[0], endcolor[0], data[x, y], max, np.amin(data))) + ", 100%, 100%)"))
            return image
        elif mode == "saturation":
            image.putpixel((x, y), ic.getrgb("hsv(" + str(startcolor[0]) + ", " + str(
                interpolate(startcolor[1], endcolor[1], data[x, y], max, np.amin(data))) + "%, 100%)"))
            return image
        elif mode == "brightness":
            image.putpixel((x, y), ic.getrgb("hsv(" + str(startcolor[0]) + ", 100%, " + str(
                interpolate(startcolor[2], endcolor[2], data[x, y], max, np.amin(data))) + "%)"))
            return image


    def newton(z0, f, fprime, MAX_IT=100, R=1):
        """The Newton-Raphson method applied to f(z).

        Returns the root found, starting with an initial guess, z0, or False
        if no convergence to tolerance TOL was reached within MAX_IT iterations.

        """

        z = z0
        for i in range(MAX_IT):
            dz = f(z) / fprime(z)
            if abs(dz) < TOL:
                return [z, i]
            z -= R * dz
        return [False, i]


    def plot_newton_fractal(f, fprime, n=200, domain=(-5, 5, -5, 5)):
        """Plot a Newton Fractal by finding the roots of f(z).

        The domain used for the fractal image is the region of the complex plane
        (xmin, xmax, ymin, ymax) where z = x + iy, discretized into n values along
        each axis.

        """

        roots = []
        m = np.zeros((n, n))
        iterationmap = np.zeros((n, n))


        def get_root_index(roots, r):
            """Get the index of r in the list roots.

            If r is not in roots, append it to the list.

            """

            try:
                return np.where(np.isclose(roots, r, atol=TOL))[0][0]
            except IndexError:
                roots.append(r)
                return len(roots) - 1

        count = 0

        xmin, xmax, ymin, ymax = domain

        file = open("data.txt", "w")

        for ix, x in enumerate(np.linspace(xmin, xmax, n)):
            count += 1
            file.write("\n")
            for iy, y in enumerate(np.linspace(ymin, ymax, n)):
                z0 = x + y * 1j
                # z0 = 1
                nn = newton(z0, f, fprime)
                r = nn[0]
                iterationmap[iy, ix] = nn[1]
                if r is not False:
                    ir = get_root_index(roots, r)
                    m[iy, ix] = ir
                    # print(m[iy,ix])
                    file.write(str(m[iy, ix]))

        file.close()
        # print(count)

        # nroots = len(roots)
        # colormap = generate_color_map(clrs, nroots)
        # print(colormap)
        image = Image.new("RGB", (n, n))
        for x in range(n):
            for y in range(n):
                # print(m[x, y])
                # image = set_pixel_color(x, y, colormap, m, image)
                image = set_pixel_color_from_iter(y, x, iterationmap, image, startcolor, endcolor, np.amax(iterationmap), "hue")
        name = str(int(time.time()))+"fractal.png"
        newfile_name = os.path.join( directory , name)
        image.save(newfile_name)
        image = Image.open(newfile_name)
        image.show()
        print(newfile_name)
        print(image.filename)
        texImage.image = bpy.data.images.load(image.filename)

    f = lambda z: z ** 7 - z ** 3 - z - 4
    fprime = lambda z: 7 * z ** 6 - 3 * z ** 2 - 1

    plot_newton_fractal(f, fprime, n=100)

class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Render Fractal"

    def execute(self, context):
        main(context)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(SimpleOperator.bl_idname, text=SimpleOperator.bl_label)


class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Fractal Texture Generator"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        # Big render button
        layout.label(text="Render:")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.simple_operator")


classes = (
    SimpleOperator,
    LayoutDemoPanel,
)

def register():
    from bpy.utils import register_class
#    bpy.utils.register_class(LayoutDemoPanel)
#    bpy.utils.register_class(SimpleOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    
    for cls in classes:
        register_class(cls)



def unregister():
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(SimpleOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
