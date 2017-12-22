import os
from tools.image2webp import *

print('Convert all png/jpg size under 1000\n\n')

ls = findFilesRecursively('assets/img', lambda x: x.lower().endswith('.png') or x.lower().endswith('jpg') or x.lower().endswith('jpeg'))
for f in ls:
    os.system('convert {0} -resize "1000>" {0}'.format(f))

print('Convert png/jpg to webp\n\n')

processImagesInDirRecursively('assets/img')

print('\n\ndone!')