# Denoising_Convolutional_AutoEncoder(Tranpose).py

# Denoising Trajectory Data using Convolutional Auto Encoder
# This file uses Conv2DTranpose in Decoding part

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

import sys
stdout = sys.stdout

file_name = 'Denoising_Convolutional_AutoEncoder_(Tranpose)'
output_stream = open( 'log({}).txt'.format( file_name ), 'wt' )
error_stream = open( 'errors({}).txt'.format( file_name ), 'wt' )
sys.stdout = output_stream
sys.stderr = error_stream

SIZE = 432

# Image Load #
stdout.write( 'Start Load Images... \n' )

import os, cv2, glob
import numpy as np

currDir = '/taejin/Taejin/TrajectoryAugmentation/'
saveDir = currDir + 'Trajectory-Augumentation/'
dataDir = currDir + 'Trajectory_Data/432-Image/'

## Load Train Data ##
def GetImage( path ):
	img = cv2.imread( path, 0 )
	resized = cv2.resize( img, ( SIZE, SIZE ) )

	return resized

X_trainDir = dataDir + 'Input-50/'
Y_trainDir = dataDir + 'Val/'

X_train, Y_train = [ ], [ ]

os.chdir( X_trainDir )
X_trainFiles = glob.glob( '*png' )
for f in X_trainFiles:
	X_train.append( GetImage( f ) )

os.chdir( Y_trainDir )
Y_trainFiles = glob.glob( '*png' )
for f in Y_trainFiles:
	Y_train.append( GetImage( f ) )

## Load Test Data ##
testDir = dataDir + 'Test_Image/'

X_test = [ ]

os.chdir( testDir )
testFiles = glob.glob( '*png' )
for f in testFiles:
	X_test.append( GetImage( f ) )

## Resize Images for CNN ##
X_train, Y_train = np.array( X_train ), np.array( Y_train )
X_test = np.array( X_test )

X_train = X_train.astype( 'float32' ) / 255.
Y_train = Y_train.astype( 'float32' ) / 255.
X_test = X_test.astype( 'float32' ) / 255.

print( X_train.shape, Y_train.shape, X_test.shape )

X_train = np.reshape( X_train, ( len( X_train ), SIZE, SIZE, 1 ) )
Y_train = np.reshape( Y_train, ( len( Y_train ), SIZE, SIZE, 1 ) )
X_test = np.reshape( X_test, ( len( X_test ), SIZE, SIZE, 1 ) )

print( 'train shape (X, Y): ({},{})'.format( X_train.shape, Y_train.shape ) )
print( 'test shape (X): ({})'.format( X_test.shape ) )

stdout.write( 'Finish Load Images! \n' )

# Construct Model #
stdout.write( 'Start Make Model... \n' )

## Hyper Parameter ##
kernel = ( 3, 3 )
pooling = ( 2, 2 )
acti, pad = 'relu', 'same'
encoding_channels = [ 64, 32, 16 ]
decoding_channels = reversed( encoding_channels )

## Input Image ##
input_img = layers.Input( shape = ( SIZE, SIZE, 1 ) )

## Encoding ##
for i, channel in enumerate(encoding_channels):
	if not i: # if i is 0
		x = layers.Conv2D( channel, kernel, activation = acti, padding = pad )( input_img )
	else:
		x = layers.Conv2D( channel, kernel, activation = acti, padding = pad )( x )
	x = layers.MaxPooling2D( pooling, padding = pad )( x )

## Decoding ##
for channel in decoding_channels:
	x = layers.Conv2DTranspose( channel, kernel, activation = acti, padding = pad )( x )
	x = layers.UpSampling2D( pooling )( x )

output = layers.Conv2DTranspose( 1, kernel, activation = 'sigmoid', padding = 'same' )( x )

## Compile Model ##
autoencoder = keras.models.Model( input_img, output )
autoencoder.compile( optimizer = 'adadelta', loss = 'binary_crossentropy' )

autoencoder.summary()

stdout.write( 'Finish Making Model! \n' )

# Train Model #
stdout.write( 'Start Training Model... \n' )

## Hyper Parameter ##
EPOCH = 50
BATCH = 20
SHUFFLE = True

history = autoencoder.fit( X_train, Y_train, epochs = EPOCH, batch_size = BATCH, shuffle = SHUFFLE )

stdout.write( 'Finish Train Model! \n' )

# Test Model #
stdout.write( 'Start Testing Model... \n' )
decoded_img = autoencoder.predict( X_test )

import matplotlib.pyplot as plt

os.chdir( saveDir )
n = 10
plt.figure( figsize = ( 20, 4 ) )
for i in range( n ):
	ax = plt.subplot( 2, n, i + 1 )
	plt.imshow( X_test[i].reshape( SIZE, SIZE ) )
	plt.gray()

	ax.get_xaxis().set_visible( False )
	ax.get_yaxis().set_visible( False )

	ax = plt.subplot( 2, n, n + i + 1 )
	plt.imshow( decoded_img[i].reshape( SIZE, SIZE ) )
	plt.gray()

	ax.get_xaxis().set_visible( False )
	ax.get_yaxis().set_visible( False )

plt.savefig( 'Result.png', dpi = 300 )
plt.show()

stdout.write( 'Finish Testing Model! \n' )

stdout.write( 'Good job\n' )

output_stream.close()
error_stream.close()