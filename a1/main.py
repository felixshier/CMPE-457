# Image manipulation
#
# You'll need Python 3 and must install these packages:
#
#   numpy, PyOpenGL, Pillow, GLFW
#
# Note that file loading and saving (with 'l' and 's') are not
# available if 'haveTK' below is False.  If you manage to install
# python-tk, you can set that to True.  Otherwise, you'll have to
# provide the filename in 'imgFilename' below.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component 
# of each pixel when doing intensity changes.


import sys, os, math

try: # NumPy
  import numpy as np
except:
  print( 'Error: NumPy has not been installed.' )
  sys.exit(0)

try: # Pillow
  from PIL import Image
except:
  print( 'Error: Pillow has not been installed.' )
  sys.exit(0)

try: # PyOpenGL
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print( 'Error: PyOpenGL has not been installed.' )
  sys.exit(0)

try: # GLFW
  import glfw
except:
  print( 'Error: GLFW has not been installed.' )
  sys.exit(0)



# Globals

windowWidth  = 600 # window dimensions
windowHeight =  800

imgDir      = 'images'
imgFilename = 'pup.jpg'

loadedImage  = None  # image originally loaded
currentImage = None  # image being displayed

# initialize past transformations variable
T_p = [[1, 0, 0], 
       [0, 1, 0],
       [0, 0, 1]]

# initialize current transformation variable
T_c = None

# File dialog (doesn't work on Mac OSX)

haveTK = False

if haveTK:
  import Tkinter, tkFileDialog
  root = Tkinter.Tk()
  root.withdraw()

  

# Apply an arbitrary (invertible) 3x3 homogeneous transformation to
# oldImage and store it in newImage.  Both images already exist and
# have the same dimensions.  Use backward projection.

def transformImage( oldImage, newImage, forwardTransform ):

    # Get image info
  
    width, height = oldImage.size # (same as newImage.size)

    srcPixels = oldImage.load()
    dstPixels = newImage.load()

    # Using backward projection, fill in the dstPixels array by
    # finding, for each location dstPixels[dstX,dstY], the
    # corresponding source location srcPixels[srcX,srcY], and copying
    # the source pixel to the destination pixel.  If the source pixel
    # is outside the image, put black in the destination pixel.  Since
    # the pixels are stored as YCbCr, use (0,128,128) as the pixel
    # value, which is black in that colourspace.

    # [YOUR CODE HERE]

    # set T_inv as inverse transformation matrix
    T_inv = np.linalg.inv(forwardTransform)

    ## backward projection ##

    # loop through pixels
    for x in range(width):
      for y in range(height):
        # map each 2D point (x,y) to the 3D point (x,y,k) where k = 1
        newPoint3D = np.array([x, y, 1])
        # use T_inv to find what point (u,v,w) in old image is mapped to (x,y,k) in new image
        oldPoint3D = np.dot(T_inv, newPoint3D)
        # divide by w to revert back to 2D coordinates
        oldPoint3D = oldPoint3D / oldPoint3D[-1]

        # map pixels

        # if (u,v) is outside of old image - set corresponding (x,y) pixel value to be black
        if (oldPoint3D[0] < 0) or (oldPoint3D[0] >= width) or (oldPoint3D[1] < 0) or (oldPoint3D[1] >= height):
          dstPixels[x,y] = (0,128,128)
        # if (u,v) is in old image - set corresponding (x,y) pixel value to be equal to (u,v) pixel value
        else:
          dstPixels[x,y] = srcPixels[oldPoint3D[0], oldPoint3D[1]]

# Scale an image by s around its centre

def scaleImage( oldImage, newImage, s ):

    # use gobal variables T_c (current transformation) and T_p (past transformations)
    global T_c, T_p

    print( 'scale by %f' % s )

    # Scale the image around its centre by the factor 's'.  Do the
    # same thing as in translateImage(), where a tranformation is set
    # up and then passed in to transformImage().  You code should not
    # do any more than set up the transformation and call
    # transformImage().  You can use Numpy's 'dot' function to
    # multiply matrices.

    # image centre
    cx = oldImage.size[0]/2
    cy = oldImage.size[1]/2

    # [ YOUR CODE HERE ]

    # transformation 1: move image cx pixels right and cy pixels up (move origin to center)
    T1 = np.array( [[1,0,cx],
                   [0,1,cy],
                   [0,0,1]] )

    # transformation 2: scale image by a factor of s in the x and y directions (from origin)
    T2 = np.array( [[s,0,0],
                   [0,s,0],
                   [0,0,1]] )

    # transformation 3: move image cx pixels left and cy pixels down (move center to origin)
    T3 = np.array( [[1,0,-cx],
                   [0,1,-cy],
                   [0,0,1]] )

    # combine transformations to obtain new transformation (note the order: T3 applied to image first)
    T = np.dot(np.dot(T1, T2), T3)

    # current transformation = new transformation * past transformations
    T_c = np.dot(T, T_p)

    # Call the generic transformation code using current transformation

    transformImage( oldImage, newImage, T_c )
    
  

def rotateImage( oldImage, newImage, theta ):

    # use gobal variables T_c (current transformation) and T_p (past transformations)
    global T_c, T_p
    
    print( 'rotate by %f degrees' % (theta*180/3.14159) )

    # Rotate the image around its centre by angle 'theta'.  This is
    # very similar to scaleImage(), so do that function first.
    
    # [ YOUR CODE HERE ]

    # image centre
    cx = oldImage.size[0]/2
    cy = oldImage.size[1]/2

    # transformation 1: move image cx pixels right and cy pixels up (move origin to center)
    T1 = np.array( [[1,0,cx],
                   [0,1,cy],
                   [0,0,1]] )

    # transformation 2: rotate image by theta radians (around origin)
    T2 = np.array( [[math.cos(theta),-math.sin(theta),0],
                   [math.sin(theta),math.cos(theta),0],
                   [0,0,1]] )

    # transformation 3: move image cx pixels left and cy pixels down (move center to origin)
    T3 = np.array( [[1,0,-cx],
                   [0,1,-cy],
                   [0,0,1]] )

    # combine transformations to obtain new transformation (note the order: T3 applied to image first)
    T = np.dot(np.dot(T1, T2), T3)

    # current transformation = new transformation * past transformations
    T_c = np.dot(T, T_p)

    # Call the generic transformation code using current transformation

    transformImage( oldImage, newImage, T_c )

    
def translateImage( oldImage, newImage, x, y ):

    # use gobal variables T_c (current transformation) and T_p (past transformations)
    global T_c, T_p
    
    print( 'translate by %f,%f' % (x,y) )

    # Compute the homogeneous transformation
  
    T = np.array( [[1,0,x],
                   [0,1,y],
                   [0,0,1]] )

    # current transformation = new transformation * past transformations
    T_c = np.dot(T, T_p)

    # Call the generic transformation code using current transformation

    transformImage( oldImage, newImage, T_c )



# Set up the display and draw the current image

def display( window ):

    # Clear window

    glClearColor ( 1, 1, 1, 0 )
    glClear( GL_COLOR_BUFFER_BIT )

    # rebuild the image

    img = currentImage.convert( 'RGB' )

    width  = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image

    baseX = (windowWidth-width)/2
    baseY = (windowHeight-height)/2

    glWindowPos2i( int(baseX), int(baseY) )

    # Get pixels and draw

    imageData = np.array( list( img.getdata() ), np.uint8 )

    glDrawPixels( width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData )

    glfw.swap_buffers( window )

    

# Handle keyboard input

def keyCallback( window, key, scancode, action, mods ):

  if action == glfw.PRESS:
    
    if key == glfw.KEY_ESCAPE:	# quit upon ESC
      sys.exit(0)

    elif key == 'l':
        if haveTK:
            path = tkFileDialog.askopenfilename( initialdir = imgDir )
            if path:
                loadImage( path )

    elif key == 's':
        if haveTK:
            outputPath = tkFileDialog.asksaveasfilename( initialdir = '.' )
            if outputPath:
                saveImage( outputPath )

    else:
        print( 'key =', key ) # DO NOT TOUCH THIS LINE



# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage( path ):

    global loadedImage, currentImage

    loadedImage = Image.open( path ).convert( 'YCbCr' ).transpose( Image.FLIP_TOP_BOTTOM )
    currentImage = loadedImage.copy()


def saveImage( path ):

    currentImage.transpose( Image.FLIP_TOP_BOTTOM ).convert('RGB').save( path )
    


# Handle window reshape


def windowReshapeCallback( window, newWidth, newHeight ):

    global windowWidth, windowHeight

    windowWidth  = newWidth
    windowHeight = newHeight



# Mouse state on initial click

initX = 0
initY = 0

button = None



# Handle mouse click/release

def mouseButtonCallback( window, btn, action, keyModifiers ):

    global button, initX, initY, T_p, T_c

    if action == glfw.PRESS:

        button = btn
        initX, initY = glfw.get_cursor_pos( window ) # store mouse position

    elif action == glfw.RELEASE:

        button = None

        # once mouse is released - set T_p (past transformations) to T_c (current transformation)
        T_p = T_c

    

# Handle mouse motion.  We don't want to transform the image and
# redraw with each tiny mouse movement.  Instead, just record the fact
# that the mouse moved.  After events are process in
# glfw.wait_events(), check whether the mouse moved and, if so, act on
# it.

mousePositionChanged = False

def mouseMovementCallback( window, x, y ):

  global mousePositionChanged

  if button is not None: # button is down
    mousePositionChanged = True



def actOnMouseMovement( window, button, x, y ):

    global currentImage

    if button == glfw.MOUSE_BUTTON_LEFT: # translate

        # Get amount of mouse movement
      
        diffX = x - initX
        diffY = y - initY

        translateImage( loadedImage, currentImage, diffX, -diffY ) # (y is flipped)

    elif button == glfw.MOUSE_BUTTON_RIGHT: # rotate

        # Get initial position w.r.t. window centre
      
        initPosX = initX - float(windowWidth)/2.0
        initPosY = initY - float(windowHeight)/2.0

        # Get current position w.r.t. window centre
        
        newPosX = x - float(windowWidth)/2.0
        newPosY = y - float(windowHeight)/2.0

        # Find angle from initial to current positions (around window centre)
        
        theta = math.atan2( -newPosY, newPosX ) - math.atan2( -initPosY, initPosX ) # (y is flipped)

        rotateImage( loadedImage, currentImage, theta )

    elif button == glfw.MOUSE_BUTTON_MIDDLE: # scale

        # Get initial position w.r.t. window centre
      
        initPosX = initX - float(windowWidth)/2.0
        initPosY = initY - float(windowHeight)/2.0
        initDist = math.sqrt( initPosX*initPosX + initPosY*initPosY )
        if initDist == 0:
            initDist = 1

        # Get current position w.r.t. window centre
        
        newPosX = x - float(windowWidth)/2.0
        newPosY = y - float(windowHeight)/2.0
        newDist = math.sqrt( newPosX*newPosX + newPosY*newPosY )

        scaleImage( loadedImage, currentImage, newDist / initDist )



# Initialize GLFW and run the main event loop

def main():

    global mousePositionChanged, button
    
    if not glfw.init():
        print( 'Error: GLFW failed to initialize' )
        sys.exit(1)

    window = glfw.create_window( windowWidth, windowHeight, "Assignment 1", None, None )

    if not window:
        glfw.terminate()
        print( 'Error: GLFW failed to create a window' )
        sys.exit(1)

    glfw.make_context_current( window )

    glfw.swap_interval( 1 )  # redraw at most every 1 screen scan

    # Callbacks
    
    glfw.set_key_callback( window, keyCallback )
    glfw.set_window_size_callback( window, windowReshapeCallback )
    glfw.set_mouse_button_callback( window, mouseButtonCallback )

    # The following causes mouse movement to be tracked continuously.
    # Usually, this would be done only when the mouse button is
    # pressed, and stopped when the mouse button is released.  But my
    # implementation of python GLFW appears not to permit a 'None'
    # value to be passed in for the second argument to stop tracking.
    # So we have to track continuously.

    glfw.set_cursor_pos_callback( window, mouseMovementCallback )

    loadImage( os.path.join( imgDir, imgFilename ) )

    display( window )

    # Main event loop

    prevX, prevY = glfw.get_cursor_pos( window )

    while not glfw.window_should_close( window ):

        glfw.wait_events()

        currentX, currentY = glfw.get_cursor_pos( window )
        if currentX != prevX or currentY != prevY:
          actOnMouseMovement( window, button, currentX, currentY )

        display( window )

    glfw.destroy_window( window )
    glfw.terminate()



if __name__ == '__main__':
    main()
