import numpy as np
from PIL import Image
from PIL import ImageColor as ic
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# A list of colors to distinguish the roots.
# colors = ['r', 'g', 'y']
# clrs = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255)]
TOL = 1.e-8
clrs = [ic.getrgb("hsv(0, 100%, 100%)"), ic.getrgb("#db504a"), ic.getrgb("#ff6f59"), ic.getrgb("#254441"),
        ic.getrgb("#43aa8b"), ic.getrgb("#b2b09b")]
startcolor = [250, 0, 0]
endcolor = [300, 100, 100]


def interpolate(startValue, endValue, stepNumber, lastStepNumber, min):
    return (endValue - startValue) * (stepNumber - min) / (lastStepNumber - min + 1) + startValue


def generate_color_map(colors, nroots):
    colormap = {}
    for n in range(0, nroots):
        colormap[str(float(n))] = colors[n]
        print(colormap)
    return colormap
    # image = Image.new("RGBA", (500, 500))


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


def plot_newton_fractal(f, fprime, n=200, domain=(-1, 1, -1, 1)):
    """Plot a Newton Fractal by finding the roots of f(z).

    The domain used for the fractal image is the region of the complex plane
    (xmin, xmax, ymin, ymax) where z = x + iy, discretized into n values along
    each axis.

    """

    roots = []
    m = np.zeros((n, n))
    iterationmap = np.zeros((n, n))

    # im = Image.new('RGBA',(n*2,n*2),"map.png")
    # im = Image.open("test.png","r")
    # a = np.asarray(im)
    # print(a)

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
            r = newton(z0, f, fprime)[0]
            iterationmap[iy, ix] = newton(z0, f, fprime)[1]
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
            image = set_pixel_color_from_iter(y, x, iterationmap, image, startcolor, endcolor, np.amax(iterationmap), "saturation")

    image.show()

    # if nroots > len(colors):
    #     # Use a "continuous" colormap if there are too many roots.
    #     cmap = 'hsv'
    # else:
    #     # Use a list of colors for the colormap: one for each root.
    #     cmap = ListedColormap(colors[:nroots])

    # plt.imshow(m, cmap=cmap, origin='lower')
    # plt.axis('off')
    # plt.show()


f = lambda z: z ** 4 - 1
fprime = lambda z: 4 * z ** 3

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    plot_newton_fractal(f, fprime, n=500)
