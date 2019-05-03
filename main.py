from utils.args import get_args
from utils.config import process_config, process_config_test

from data_loader.rgb_data_loader import RGBTrainGenerator, RGBCVGenerator
from models.resnetRGB_model import ResNetRGBModel
from trainer.resnetRGB_trainer import ResNetRGBTrainer

from data_loader.persistence_data_loader import PersistenceTrainGenerator, PersistenceCVGenerator
from models.Persistence_model import PersistenceModel
from trainer.Persistence_trainer import PersistenceTrainer

#from models.resnetPersistence_model import ResNetPersistenceModel

from data_loader.combined_data_loader import CombinedTrainGenerator, CombinedCVGenerator
from models.resnetCombined_model import ResNetCombinedModel
from trainer.resnetCombined_trainer import ResNetCombinedTrainer


from models.customModel import CustomModel
from trainer.custom_trainer import CustomTrainer

'''
Data distribution:
             Train     Val    Test
Malignant    38322    2036     509
Benign       18635    2035     517
'''

args = get_args()
config = process_config(args)


def main():

    args = get_args()
    config = process_config(args)

    print '\n', config, '\n'

    print '\n', config.tensorboard, '\n'


    if config.rgb:
        print '-'*60
        print 'Training on RGB images'
        print '-'*60
        train_rgb(config)

    elif config.combined:
        print '-'*60
        print 'Training on Combined images'
        print '-'*60
        train_combined(config)

    elif config.custom:
        print '-'*60
        print 'Training Custom model'
        print '-'*60
        train_custom(config)


    else:
        print '-'*60
        print 'Training on Persistence images'
        print '-'*60
        train_persistence(config)



def train_combined(config):

    print 'Creating combined model'
    model = ResNetCombinedModel(config)

    print 'Creating data generators'
    train_generator = CombinedTrainGenerator(config)
    cv_generator = CombinedCVGenerator(config)

    print 'Creating trainer'
    trainer = ResNetCombinedTrainer(model.model, config)

    print 'Training'
    trainer.train(train_generator, cv_generator)



def train_persistence(config):
    print 'Creating data generators'
    train_generator = PersistenceTrainGenerator(config)
    cv_generator = PersistenceCVGenerator(config)

    print 'creating model'
    model = PersistenceModel(config)
    #model = ResNetPersistenceModel(config)

    print 'Creating trainer'
    trainer = PersistenceTrainer(model.model, config)

    print 'Training....'
    trainer.train(train_generator, cv_generator)




def train_custom(config):
    print 'Training on Persistence images (Custom)'
    print 'Creating data generators'
    train_generator = PersistenceTrainGenerator(config)
    cv_generator = PersistenceCVGenerator(config)

    print 'creating model'
    model = CustomModel(config)

    print 'Creating trainer'
    trainer = CustomTrainer(model.model, config)

    print 'Training....'
    trainer.train(train_generator, cv_generator)




def train_rgb(config):
    print 'Creating data generators'
    train_generator = RGBTrainGenerator(config)
    cv_generator = RGBCVGenerator(config)

    print 'creating model'
    model = ResNetRGBModel(config)

    print 'Creating trainer'
    trainer = ResNetRGBTrainer(model.model, config)

    print 'Training....'
    trainer.train(train_generator, cv_generator)



if __name__ == "__main__":
    main()
