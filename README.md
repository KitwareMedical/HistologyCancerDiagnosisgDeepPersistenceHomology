# Histology Cancer Diagnosis Deep Persistence Homology

# Training
To train a model run:
```shell
python main.py --data=<Path-to-data-directory> --config=<Path-to-config-file> --results=<Path-to-results-directory>
```

All models use Tensorboard by default in the callback.  
The results directory will be created if it already doesn't exist.  

To find the optimum learning rate using [One-Cycle-Learning-Rate](https://github.com/titu1994/keras-one-cycle) policy run the command as follows:  
```shell
python main.py --data=<Path-to-data-directory> --config=<Path-to-config-file> --results=<Path-to-results-directory> --findLR=True
```
This will run the iterations for only one epoch and save the Learning Rate vs Loss curve in '<results>/LRFinder/' directory.


The models currenty use one of the following two optimizers: 
* SGD: if optimizer is set to "sgd" in config file. Uses [One-Cyclic-Learning-Rate](https://github.com/titu1994/keras-one-cycle#training-with-onecyclelr) policy to update the learning rate.
* Adam: if optimizer is set to "adam" in config file. Uses [Reduce-LR-On-Plateau](https://keras.io/callbacks/#reducelronplateau) to control the learning rate.


Arguments for main.py:  
```shell
--data <Path to data directory>                :  Path to data directory
--findLR True                                  :  Runs the model for one epoch and saves the LR vs Loss graph
--config <Path to config file>                 :  Path to config file
--results <Path to Result directory>           :  Directory to store model checkpoint, Tensorboard logs and LRFinder results
--load_checkpoint <Path to hdf5 file>          :  model weights for initialization
--checkpoint_RGB <Path to hdf5 file>           :  Valid only if combined is set to True. This will load the weights from RGB model into combined model
--checkpoint_Persistence <Path to hdf5 file>   :  Valid only if combined is set to True. This will load the weights from Persistence model into combined model
--set_weights True                             :  Uses inverse class weights if set True (used for unbalanced data) otherwise treats data as balanced
--use_focal_loss True                          :  Uses focal loss if set to True (change parameters alpha and gamma in config file) 
```

Specify the exp name in config as "Combined", "Persistence" or "RGB" to train on that particular data.


# Evaluation 


Arguments for test.py:  
```shell
--test_dir <Path to test data directory>       :  The test directory must contain the folders : malignant/ and benign/ as shown in the data structure below
--config_dir <Path to config folder>           :  The config_dir directory must contain the model.config file and the directory checkpoint/ which has hdf5 files 
```
The script will save the ROC curve and pickle dump the evaluation metrics in the config directory.

## Project Structure

```
├── main.py                   - main script that runs the whole pipeline.
│
│
├── base/                     - this folder contains the abstract classes of the project components
│   ├── base_data_loader.py   - this file contains the abstract class of the data loader.
│   ├── base_model.py         - this contains file the abstract class of the model.
│   └── base_trainer.py       - this file contains the abstract class of the trainer.
│
│
├── models/                   - this folder contains the models for both persistence and RGB data.
│   └── Persistence_model.py
│   └── resnetRGB_model.py
│   └── resnetCombined_model.py
│
│
├── trainer/                  - this folder contains the trainers for both persistence and RGB images.
│   └── Persistence_trainer.py
│   └── resnetRGB_trainer.py
│   └── resnetCombined_trainer.py
│
│
├── data_loader/              - this folder contains the data loaders for both persistence and RGB.
│   └── persistence_data_loader.py
│   └── rgb_data_loader.py
│   └── combined_data_loader.py
│
│
├── configs/                  - this folder contains the model, the training and the TDA parameters in config file.
│   └── model.config          - The stats.pkl consists of dictionary of source means and variances of original RGB images
│   └── stats.pkl             - which are used for Reinhard color normalization of patches
│
│
└── utils/                    - this folder contains various utils required by the project.
     ├── args.py              - util functions for parsing arguments.
     ├── config.py            - util functions for parsing the config files.
     ├── tda_utils.py         - util functions for computing persistence images.
     ├── evaluate.py          - contains functions to load test data and model for testing.
     └── metrics.pkl          - contains implementations of metrics which are displayed while training.

```

## Data directory structure

```
<data-directory>
│
│
├── train/
│     ├── malignant/
│     │      ├── persistence_images/
│     │      └── rgb/
│     │
│     └── benign/ 
│            ├── persistence_images/
│            └── rgb/
│
├── val/
│     ├── malignant/
│     │      ├── persistence_images/
│     │      └── rgb/
│     │
│     └── benign/ 
│            ├── persistence_images/
│            └── rgb/
│
└── test/
      ├── malignant/
      │      ├── persistence_images/
      │      └── rgb/
      │
      └── benign/ 
             ├── persistence_images/
             └── rgb/
```


# Documentation

Patches are generated from RGB images with a size of (1024,1024,3). Not all patches are useful for training as most of them contain significant background or very less number of nuclei making them unsuitable for persistence image computation or for training.

## Preprocessing 
The generated patches are rejected based on the following rules:  

* **The image is low contrast** (computed using [skimage.exposure.is_low_contrast](http://scikit-image.org/docs/dev/api/skimage.exposure.html#skimage.exposure.is_low_contrast))  
The funtion computes upper percentile (default 99) and the lower percentile (default 1) of the intensity values from the image. An image is considered low contrast if its range of brightness falls below a fraction (default 0.05) of the data type's maximum intensity value (255 in our case).  

* **The image is background image** (computed using [simple-mask](https://digitalslidearchive.github.io/HistomicsTK/histomicstk.utils.html?highlight=simple%20mask#histomicstk.utils.simple_mask) function from HistomicsTK)  
A binary image is obtained from simple mask function representing the foreground and the background. The foreground percent is computed for the entire image from this mask. The image is rejected if the foreground is less than 30% of the image area.  

* **Nuclei channel thresholding**  
The nuclei stain is computed by first normalizing the image to LAB standard using [Reinhard](https://digitalslidearchive.github.io/HistomicsTK/_modules/histomicstk/preprocessing/color_normalization/reinhard.html#reinhard) color normalization.  Supervised deconvolution is then performed to obtain the nuceli stain. Foreground and background are separated from the nuclei channel by thresholding and morphology operations. The percentage of pixels lying in foreground is computed. The image is rejected if this foreground percent is less than 10% of the image area.  

* **RGB thresholding** [Original Paper](https://www.ncbi.nlm.nih.gov/pubmed/28549410)  
The percentage of RGB pixels are calculated in an image which have all pixel values greater than or equal to 200. If this percentage is greater than 70% (i.e. the image has mainly white background), the image is rejected.  

Only those images are taken for training which survive all the 4 tests mentioned above.


# Results

|                  |  __AUC__   |__Accuracy__|  __F1__  | __Precision__ |  __Recall__ |
|------------------|------------|------------|----------|---------------|-------------|
|      RGB         |   0.9369   |    0.8103  |  0.8370  |     0.7427    |    0.9587   | 
|   Persistence    |   0.7816   |    0.7205  |  0.7421  |     0.6984    |    0.7917   |
| RGB+Persistence  | **0.9463** |  **0.8193**|**0.8435**|   **0.7530**  |  **0.9587** |

