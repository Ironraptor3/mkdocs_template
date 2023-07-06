# TODO Comments
# TODO Pylint
# TODO Pytest

import argparse
import os
import re

REF_REGEX = re.compile(r'- \[(.*?)\]\(<(.*?)\?n>\)\s*')
REF_GROUP = 2
NAME_REGEX = re.compile(r'(.*?) (.*?)\.md')
NAME_GROUP = 1
# --- TODO ---
IMG_REGEX = re.compile(r'')
IMG_GROUP = 1
# --- TODO ---

class NuclinoTree():

    def __init__(self, infile, outfile=None, startfile='index.md', is_root=True):
        self.file_dict = {}
        self.img_dict = {}
        self.issues = []

        self.infile = infile
        self.outfile = outfile

        self.is_root = is_root
        self.root = NuclinoTreeNode(self)

    def get_outpath(self, path):
        return os.path.join(outfile, path) if outfile is not None else path

    def parse(self):
        self.root.parse(is_root=self.is_root)

class NuclinoTreeNode():
    
    def __init__(self, tree, parent=None):
        self.tree = tree
        self.parent = parent
        self.children = None

    @staticmethod
    def get_img_refs(line):
        return [tup[IMG_GROUP] for tup in IMG_REGEX.findall(line)]

    @staticmethod
    def _update_path_dup(path_dup, name):
        if path_dup is None:
            return name
        ctr = path_dup.get(name, 0)
        if ctr:
            name = '%s_%d' % (name, ctr)
        path_dup[name] = ctr + 1
        return name

    def is_leaf(self):
        return not self.children

    def _parse_helper(self, path, file_refs):
        self.children = [NuclinoTreeNode(self.tree, parent=self) for _ in file_refs]
        path_dup = {}
        all_img_refs = set()
        for index, file_ref in file_refs:
            img_refs = self.children[index].parse(file_ref, path=path, path_dup=path_dup)
            for img_ref in img_refs:
                if img_ref in all_img_refs or img_ref not in self.tree.img_dict:
                    self.tree.img_dict[img_ref] = (path, self) # TODO fixup during processing
                all_img_refs.add(img_ref)
        return list(all_img_refs)
        
    def parse(self, nodefile, is_root=False, path=None, path_dup=None):
        file_refs = []
        img_refs = []
        path = os.path.join(path, nodefile) if path is not None else get_outpath(nodefile)

        with open(os.path.join(self.tree.infile, nodefile), 'r') as nodetxt:
            while line = nodetxt.readline():
                line = line.rstrip()
                if file_refs is not None:
                    ref_match = REF_REGEX.fullmatch(line)
                    if ref_match is None:
                        file_refs = None
                    else:
                        file_refs.append(ref_match.group(REF_GROUP))
                        continue
                img_refs.extend(self.get_img_refs(line))
        
        if is_root:
            assert file_refs
            if self.tree.outfile is not None:
                os.mkdirs(self.tree.outfile, exist_ok=True)
            return self._parse_helper(path, file_refs)
        
        name = nodefile
        name_match = NAME_REGEX.fullmatch(name)
        if name_match is not None:
            name = name_match.group(NAME_GROUP)
        name = self._update_path_dup(name, path_dup)
        self.file_dict[node] = (path, name, self)

        if file_refs:
            return self._parse_helper(path, file_refs)

        return img_refs

def main():
    parser.argparse.ArgumentParser()
    parser.add_argument('input', type=str,
                        help='Unzipped directory exported by Nuclino')
    parser.add_argument('-o', '--output', type=str, default='docs'
                        help='Where to build docs. Default = ./docs/')
    parser.add_argument('-i', '--issues', type=argparse.FileType('w'), default='-',
                        help='Where to print issues / reminders. Default = sys.stdout')
    args = parser.parse_args()

    tree = NuclinoTree(args.input, outfile=args.output)
    tree.parse()
    # TODO move and fixup all test - noting any issues
    if tree.issues:
        print('\n'.join(tree.issues), file=args.issues)
