import tensorflow as tf


def dice_coef(y_true, y_pred, smooth=1.0, **kwargs):

    intersection = tf.reduce_sum(y_true * y_pred, axis=[1,2,3])
    coef = (tf.constant(2.) * intersection + tf.constant(smooth)) / \
           (tf.reduce_sum(y_true, axis=[1,2,3]) + tf.reduce_sum(y_pred, axis=(1,2,3)) + tf.constant(smooth))
    return tf.reduce_mean(coef)



def dice_coef_loss(y_true, y_pred, smooth=1.0, **kwargs):

    intersection = tf.reduce_sum(y_true * y_pred, axis=(1, 2, 3))

    term1 = -tf.log(tf.constant(2.0) * intersection + smooth)
    term2 = tf.log(tf.reduce_sum(y_true, axis=(1, 2, 3)) +
                   tf.reduce_sum(y_pred, axis=(1, 2, 3)) + smooth)
    
    term1 = tf.reduce_mean(term1)
    term2 = tf.reduce_mean(term2)
    
    loss = term1 + term2

    return loss


CHANNEL_LAST = True
if CHANNEL_LAST:
    concat_axis = -1
    data_format = 'channels_last'

else:
    concat_axis = 1
    data_format = 'channels_first'

tf.keras.backend.set_image_data_format(data_format)


def define_model(input_tensor, use_upsampling=False, n_cl_out=1, dropout=0.2, print_summary = False, activation_function='relu', seed=0xFEEDFACE, **kwargs):


    # Set keras learning phase to train
    tf.keras.backend.set_learning_phase(True)

    # Don't initialize variables on the fly
    tf.keras.backend.manual_variable_initialization(False)

    inputs = tf.keras.layers.Input(tensor=input_tensor, name='Images')

    if activation_function == 'relu':
        activation = tf.nn.relu
    elif activation_function == 'leakyrelu':
        activation = tf.nn.leaky_relu
            
    params = dict(kernel_size=(3, 3), activation=activation,
                  padding='same', data_format=data_format,
                  # kernel_initializer='he_uniform')
                  kernel_initializer=tf.keras.initializers.he_uniform(seed=seed))
#                   kernel_initializer=tf.keras.initializers.he_normal(seed=0xFEEDFEACE))
#                   tf.keras.initializers.RandomUniform(minval=0.01, maxval=0.5, seed=0xFEEDFACE))
    
    conv1 = tf.keras.layers.Conv2D(name='conv1a', filters=32, **params)(inputs)
    conv1 = tf.keras.layers.Conv2D(name='conv1b', filters=32, **params)(conv1)
    pool1 = tf.keras.layers.MaxPooling2D(name='pool1', pool_size=(2, 2))(conv1)

    conv2 = tf.keras.layers.Conv2D(name='conv2a', filters=64, **params)(pool1)
    conv2 = tf.keras.layers.Conv2D(name='conv2b', filters=64, **params)(conv2)
    pool2 = tf.keras.layers.MaxPooling2D(name='pool2', pool_size=(2, 2))(conv2)

    conv3 = tf.keras.layers.Conv2D(name='conv3a', filters=128, **params)(pool2)
    conv3 = tf.keras.layers.Dropout(dropout)(conv3) ### Trying dropout layers earlier on, as indicated in the paper
    conv3 = tf.keras.layers.Conv2D(name='conv3b', filters=128, **params)(conv3)

    pool3 = tf.keras.layers.MaxPooling2D(name='pool3', pool_size=(2, 2))(conv3)

    conv4 = tf.keras.layers.Conv2D(name='conv4a', filters=256, **params)(pool3)
    conv4 = tf.keras.layers.Dropout(dropout)(conv4) ### Trying dropout layers earlier on, as indicated in the paper
    conv4 = tf.keras.layers.Conv2D(name='conv4b', filters=256, **params)(conv4)

    pool4 = tf.keras.layers.MaxPooling2D(name='pool4', pool_size=(2, 2))(conv4)

    conv5 = tf.keras.layers.Conv2D(name='conv5a', filters=512, **params)(pool4)
    conv5 = tf.keras.layers.Conv2D(name='conv5b', filters=512, **params)(conv5)

    if use_upsampling:
        up6 = tf.keras.layers.concatenate([tf.keras.layers.UpSampling2D(name='up6', size=(2, 2))(conv5), conv4], axis=concat_axis)
    else:
        up6 = tf.keras.layers.concatenate([tf.keras.layers.Conv2DTranspose(name='transConv6', filters=256, data_format=data_format,
                           kernel_size=(2, 2), strides=(2, 2), padding='same')(conv5), conv4], axis=concat_axis)

    conv6 = tf.keras.layers.Conv2D(name='conv6a', filters=256, **params)(up6)
    conv6 = tf.keras.layers.Conv2D(name='conv6b', filters=256, **params)(conv6)

    if use_upsampling:
        up7 = tf.keras.layers.concatenate([tf.keras.layers.UpSampling2D(name='up7', size=(2, 2))(conv6), conv3], axis=concat_axis)
    else:
        up7 = tf.keras.layers.concatenate([tf.keras.layers.Conv2DTranspose(name='transConv7', filters=128, data_format=data_format,
                           kernel_size=(2, 2), strides=(2, 2), padding='same')(conv6), conv3], axis=concat_axis)

    conv7 = tf.keras.layers.Conv2D(name='conv7a', filters=128, **params)(up7)
    conv7 = tf.keras.layers.Conv2D(name='conv7b', filters=128, **params)(conv7)

    if use_upsampling:
        up8 = tf.keras.layers.concatenate([tf.keras.layers.UpSampling2D(name='up8', size=(2, 2))(conv7), conv2], axis=concat_axis)
    else:
        up8 = tf.keras.layers.concatenate([tf.keras.layers.Conv2DTranspose(name='transConv8', filters=64, data_format=data_format,
                           kernel_size=(2, 2), strides=(2, 2), padding='same')(conv7), conv2], axis=concat_axis)


    conv8 = tf.keras.layers.Conv2D(name='conv8a', filters=64, **params)(up8)
    conv8 = tf.keras.layers.Conv2D(name='conv8b', filters=64, **params)(conv8)

    if use_upsampling:
        up9 = tf.keras.layers.concatenate([tf.keras.layers.UpSampling2D(name='up9', size=(2, 2))(conv8), conv1], axis=concat_axis)
    else:
        up9 = tf.keras.layers.concatenate([tf.keras.layers.Conv2DTranspose(name='transConv9', filters=32, data_format=data_format,
                           kernel_size=(2, 2), strides=(2, 2), padding='same')(conv8), conv1], axis=concat_axis)


    conv9 = tf.keras.layers.Conv2D(name='conv9a', filters=32, **params)(up9)
    conv9 = tf.keras.layers.Conv2D(name='conv9b', filters=32, **params)(conv9)

    conv10 = tf.keras.layers.Conv2D(name='Mask', filters=n_cl_out, kernel_size=(1, 1),
                    data_format=data_format, activation='sigmoid')(conv9)

    model = tf.keras.models.Model(inputs=[inputs], outputs=[conv10])

    if print_summary:
        print (model.summary())

    return conv10


def sensitivity(y_true, y_pred, smooth = 1. ):

    intersection = tf.reduce_sum(y_true * y_pred)
    coef = (intersection + smooth) / (tf.reduce_sum(y_true) + smooth)
    return coef

def specificity(y_true, y_pred, smooth = 1. ):

    intersection = tf.reduce_sum(y_true * y_pred)
    coef = (intersection + smooth) / (tf.reduce_sum(y_pred) + smooth)
    return coef
