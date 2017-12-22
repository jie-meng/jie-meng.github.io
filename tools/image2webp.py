import os

def findFilesRecursively(path, pred = None, ls = None):
    if ls == None:
        ls = []
        
    for p in os.listdir(path):
        p = os.path.join(path, p)
        if os.path.isdir(p):
            findFilesRecursively(p, pred, ls)
        elif os.path.isfile(p):
            if not pred or pred(p):
                ls.append(p)
    
    return ls

def processImagesInDirRecursively(dir):
    ls = findFilesRecursively(dir, lambda x: x.lower().endswith('.png') or x.lower().endswith('jpg') or x.lower().endswith('jpeg'))
    for f in ls:
        print('\n\n>>> Process {} ... '.format(f))
        os.system('cwebp -m 6 -pass 10 -mt -lossless -v {0} -o {1}.webp'.format(f, os.path.splitext(f)[0]))
