from PIL import Image
from collections.abc import Callable

class Kernel:
    def __init__(self, data, centre, size):
        self.data = data
        self.centre = centre
        self.size = size
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value

def load_kernel(image: Image):
    centre_x = 0
    centre_y = 0

    image = image.convert('RGB') # rgb format
    pixels = image.load()
    width, height = image.size
    kernel = [ [1]*height for _ in range(width) ]

    for x in range(width):
        for y in range(height):
            data = pixels[x, y]
            if data == (255, 0, 0):
                centre_x = x
                centre_y = y
            elif data == (0, 0, 0):
                kernel[x][y] = 0

    return Kernel(kernel, (centre_x, centre_y), (width, height))

def kernel_operate(image: Image, kernel: Kernel, default_value: int, update_function: Callable[[int, int], int]):
    image = image.convert('L') # greyscale
    output = image.copy()

    pixels = image.load()
    output_pixels = output.load()

    width, height = image.size

    for x in range(width):
        for y in range(height):
            new: int = default_value

            # Iterate for the kernel overlaid on the image, centered on that coordinate
            for dx in range(kernel.size[0]):
                x_shifted = x + dx - kernel.centre[0]

                if x_shifted >= 0 and x_shifted < width:
                    for dy in range(kernel.size[1]):
                        y_shifted = y + dy - kernel.centre[1]

                        if y_shifted >= 0 and y_shifted < height:
                            # Where the kernel is present, update the value to set
                            if kernel[dx][dy] == 1:
                                new = update_function(new, pixels[x_shifted, y_shifted])
            
            output_pixels[x, y] = new
    
    return output
            
# Elementary Operations
def erode(image: Image, kernel: Kernel):
    return kernel_operate(image, kernel, 255, min)

def dilate(image: Image, kernel: Kernel):
    return kernel_operate(image, kernel, 0, max)

# Derived Operations
def open(image: Image, kernel: Kernel):
    return dilate(erode(img, kernel), kernel)

def close(image: Image, kernel: Kernel):
    return erode(dilate(img, kernel), kernel)

def white_top_hat(image: Image, kernel: Kernel):
    opened = open(image, kernel).load()

    image = image.copy()
    pixels = image.load()

    width, height = image.size

    for x in range(width):
        for y in range(height):
            pixels[x, y] = pixels[x, y] - opened[x, y]
    
    return image

def black_top_hat(image: Image, kernel: Kernel):
    closed = close(image, kernel).load()
    
    image = image.copy()
    pixels = image.load()

    width, height = image.size

    for x in range(width):
        for y in range(height):
            pixels[x, y] = closed[x, y] - pixels[x, y]
    
    return image

## Test

try:
    kernel = load_kernel(Image.open('kernel-circle.png'))
    img = Image.open('PerlinClouds.png')
    
    erode(img, kernel).save('output/eroded.png')
    dilate(img, kernel).save('output/dilated.png')

    close(img, kernel).save('output/closed.png')
    open(img, kernel).save('output/opened.png')

    white_top_hat(img, kernel).save('output/white_top_hat.png')
    black_top_hat(img, kernel).save('output/black_top_hat.png')

except IOError as err:
    print(err)
