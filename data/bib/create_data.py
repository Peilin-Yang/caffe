import os,sys
import argparse
import subprocess

def image_path_from_index(image_set, index):
    """
    Construct an image path from the image's "index" identifier.
    """
    if image_set == 'training':
        image_path = os.path.join('JPEGImages',
                image_set, index.split('-')[0], index + '.jpg')
    elif image_set == 'testing':
        image_path = os.path.join('JPEGImages',
                image_set, index + '.jpg')
    return image_path

def annotation_path_from_index(image_set, index):
    """
    Construct an annotation path from the image's "index" identifier.
    """
    anno_path =os.path.join('Annotations', image_set, index + '.xml')
    return anno_path

def load_image_set_index(data_dir, image_set):
    """
    Load the indexes listed in this dataset's image set file.
    """
    # Example path to image set file:
    image_index = [fn.split('.')[0] for fn in os.listdir(os.path.join(
            data_dir, 'Annotations', image_set))]
    return image_index

def gen_list(data_dir, redo=False):
    output_fns = ['training.txt', 'testing.txt', 'testing_name_size.txt']
    all_exist = True
    for fn in output_fns:
        if not os.path.exists(fn):
            all_exist = False
            break
    if (not all_exist) or (all_exist and redo):
        for dataset in ['training', 'testing']:
            img_index = load_image_set_index(data_dir, dataset)
            with open('%s.txt' % dataset, 'w') as f:
                for index in img_index:
                    f.write('%s %s\n' % (image_path_from_index(dataset, index), 
                        annotation_path_from_index(dataset, index)))
        subprocess.call(['../../build/tools/get_image_size', data_dir, 'testing.txt', 'testing_name_size.txt'])

def gen_data(args):
    for dataset in ['training', 'testing']:
        subprocess.call(['python ../../scripts/create_annoset.py \
            --anno-type=%s --label-map-file=%s --min-dim=%d --max-dim=%d \
            --resize-width=%d --resize-height=%d --check-label %s \
            %s %s.txt \
            %s/%s/%s/%s__$db examples/$dataset_name' 
            % (args.anno_type, args.mapfile, args.min_dim, args.max_dim, 
                args.width, args.height, args.extra_cmd, args.dir, 
                dataset, args.dir, args.dataset_name, args.db, 
                args.dataset_name, dataset, args.db, args.dataset_name)], shell=True)

def main(args):
    gen_list(args.data_dir, args.redo_list)
    gen_data(args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare the bib data for ssd')
    parser.add_argument('--dir', dest='data_dir', 
            help='The path to the bib data',
            required=True, type=str)
    parser.add_argument('--redo_list', dest='redo_list', 
            help='True to regenerate the img/anno list no matter whether they already exist',
            required=False, type=bool)
    parser.add_argument('--redo_data', dest='redo_data',
            help='True to regenerate the data no matter whether they already exist',
            required=False, type=bool)
    parser.add_argument('--dataset_name', dest='dataset_name',
            help='',
            required=False, default='bib', type=str)
    parser.add_argument('--mapfile', dest='mapfile',
            help='',
            required=False, default='labelmap.prototxt', type=str)
    parser.add_argument('--anno_type', dest='anno_type',
            help='',
            required=False, default='detection', type=str)
    parser.add_argument('--db', dest='db',
            help='',
            required=False, default='lmdb', type=str)
    parser.add_argument('--min_dim', dest='min_dim',
            help='',
            required=False, default=0, type=int)
    parser.add_argument('--max_dim', dest='max_dim',
            help='',
            required=False, default=0, type=int)
    parser.add_argument('--width', dest='width',
            help='',
            required=False, default=0, type=int)
    parser.add_argument('--height', dest='height',
            help='',
            required=False, default=0, type=int)
    parser.add_argument('--extra_cmd', dest='extra_cmd',
            help='',
            required=False, default='--encode-type=jpg --encoded --redo', type=str)

    args = parser.parse_args()

    main(args)
