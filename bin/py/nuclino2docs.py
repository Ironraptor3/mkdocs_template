'''
This file contains utilities for converting a Nuclino wiki export
to a format able to be used by the Python module mkdocs, which is able
to generate locally hosted Wiki websites in real time.

Mkdocs is much more flexible than Nuclino, and does not have hosting fees to work
alongside a team.
'''
# TODO Comments
# TODO Pytest - Test Brainstorming
# TODO Pytest - Test Implementation

import argparse
import os
import re
import shutil

REF_REGEX = re.compile(r'- \[(.*?)\]\(<(.*?)\?n>\)\s*') # Starting ref for trees
REF_GROUP = 2
NAME_REGEX = re.compile(r'(.*?) (.*?)\.md') # File Name
NAME_GROUP = 1
IMG_REGEX = re.compile(r'\!\[(.*?)\]\((.*?)\)') # Image ref
IMG_GROUP = 1
LINK_REGEX = re.compile(r'(\!?)\[(.*?)\]\((.*?)\)') # Any ref
# No LINK_GROUP

#pylint: disable=too-many-instance-attributes
class NuclinoTree():
    '''A file hierarchy built from a Nuclino export'''

    def __init__(self, infile, outfile=None, startfile='index.md', is_root=True):
        self.file_dict = {}
        self.img_dict = {}
        self.issues = []

        self.infile = infile
        self.outfile = outfile
        self.startfile = startfile

        self.is_root = is_root
        self.root = NuclinoTreeNode(self)

    def get_outpath(self, path):
        '''Shorthand for getting the output path given a relative path'''
        return os.path.join(self.outfile, path) if self.outfile is not None else path

    def parse(self):
        '''Parses the given Nuclino export; setting up directories if output is valid'''
        self.root.parse(self.startfile, is_root=self.is_root)

    def do_output_images(self):
        '''Moves image files to the appropriate location'''
        for img_src, img_data in self.img_dict.items():
            img_dst, _ = img_data
            img_src = os.path.join(self.outfile, img_src)
            shutil.copy2(img_src, img_dst)

    def pre_fixlines(self, srcfile, dstfile, file_data):
        '''Called before lines are edited, in case any headers are needed'''
        line = srcfile.readline()
        target_header = f'# {file_data[1]}\n' # Browsing Title
        if line != target_header:
            dstfile.write(target_header)
        srcfile.seek(0)

    def fixline(self, line, file_data):
        '''Updates a line of text with the correct reference / link fixes'''
        result = line
        offset = 0

        path = file_data[0]

        for link_match in LINK_REGEX.finditer(line):
            replace = None
            old_link = link_match.group(3)
            if link_match.group(1): # Image
                # New link
                replace = self.img_dict.get(old_link, None)
                if replace is None:
                    self.issues.append(f'Unknown image ({path}): {old_link}')
            # Nuclino link - BAD
            elif old_link.lstrip().startswith('https://app.nuclino.com/'):
                replace = 'TODO'
                self.issues.append(f'TODO fix Nuclino link ({path}): {old_link}')

            if replace is not None:
                repl_start = link_match.start(3) + offset
                repl_end = link_match.end(3) + offset

                result = ''.join([result[:repl_start],
                                  replace,
                                  result[repl_end:]])

                offset = len(replace) - len(old_link)
        return result

    def fixlines(self, srcfile, dstfile, file_data):
        '''Updates all lines of text with corrections when writing a file to a new location'''
        line = srcfile.readline()
        while line:
            line = self.fixline(line, file_data)
            dstfile.write(line)
            line = srcfile.readline()

    def do_output_files(self):
        '''Move and fix all text files based on previously parsed Nuclino parsing'''
        for file_src, file_data in self.file_dict.items():
            file_dst = file_data[0]
            file_src = os.path.join(self.infile, file_src)
            with open(file_src, 'r', encoding='UTF-8') as srcfile:
                with open(file_dst, 'w', encoding='UTF-8') as dstfile:
                    self.pre_fixlines(srcfile, dstfile, file_data)
                    self.fixlines(srcfile, dstfile, file_data)

    def check_issues(self):
        '''Raise general issues after parsing'''
        if self.outfile:
            out_len = len(self.outfile)
            has_home = False
            for _, file_data in self.file_dict.items():
                path, name, _ = file_data
                if len(path) >= out_len and path[out_len:] == name and name == 'index.md':
                    has_home = True
                    break
            if not has_home:
                self.issues.append('There is no index.md file in the root!')

    def do_output(self, regen_issues=False):
        '''Create mkdocs file structure after parsing the Nuclino export'''
        if not self.outfile:
            return False

        if regen_issues:
            self.issues = []

        self.do_output_images()
        self.do_output_files()
        self.check_issues()
        return True
#pylint: enable=too-many-instance-attributes

class NuclinoTreeNode():
    '''Helper class: Represents a node in the file tree while parsing Nuclino export'''
    def __init__(self, tree, parent=None):
        self.tree = tree
        self.parent = parent
        self.children = None

    @staticmethod
    def get_img_refs(line):
        '''Gets all image references in a markdown-based line of text'''
        return [tup[IMG_GROUP + 1] for tup in IMG_REGEX.findall(line)]

    @staticmethod
    def _update_path_dup(path_dup, name):
        '''
        Helper method:
        Returns a new name given a dictionary which has previously encountered names.
        E.g. _update_path_dup({'abc' : 2}, 'abc') => 'abc_2'
            Also modifies the dictionary => {'abc' : 3}
        '''
        if path_dup is None:
            return name
        ctr = path_dup.get(name, 0)
        if ctr:
            name = f'{name}_{ctr}'
        path_dup[name] = ctr + 1
        return name

    def is_leaf(self):
        '''Was this node a leaf node?'''
        return not self.children

    def _parse_helper(self, path, file_refs):
        '''Recursion helper; Also handles images. Return list of images encountered.'''
        self.children = [NuclinoTreeNode(self.tree, parent=self) for _ in file_refs]
        path_dup = {}
        all_img_refs = set()
        for index, file_ref in file_refs:
            img_refs = self.children[index].parse(file_ref, path=path, path_dup=path_dup)
            for img_ref in img_refs:
                if img_ref in all_img_refs or img_ref not in self.tree.img_dict:
                    self.tree.img_dict[img_ref] = (path, self)
                all_img_refs.add(img_ref)
        return list(all_img_refs)

    def parse(self, nodefile, is_root=False, path=None, path_dup=None):
        '''Parses the nodefile:
        @param is_root: Whether this is the true top of a tree
        @param path: Current path in parsing
        @param path_dup: Dictionary of parent node containing duplicate names
        @return A list of image references encountered (to bubble back up the tree)
        '''
        file_refs = []
        img_refs = []

        with open(os.path.join(self.tree.infile, nodefile), 'r', encoding='UTF-8') as nodetxt:
            line = nodetxt.readline()
            while line:
                line = line.rstrip()
                if file_refs is not None:
                    ref_match = REF_REGEX.fullmatch(line)
                    if ref_match is None:
                        file_refs = None
                    else:
                        file_refs.append(ref_match.group(REF_GROUP))
                        continue
                img_refs.extend(self.get_img_refs(line))

                line = nodetxt.readline()

        if is_root:
            assert file_refs
            if self.tree.outfile is not None:
                os.makedirs(self.tree.outfile, exist_ok=True)
            return self._parse_helper(path, file_refs)

        name = nodefile
        name_match = NAME_REGEX.fullmatch(name)
        if name_match is not None:
            name = name_match.group(NAME_GROUP)
        name = self._update_path_dup(path_dup, name)

        path = os.path.join(path, name) if path is not None else self.tree.get_outpath(name)

        self.tree.file_dict[nodefile] = (path, name, self)

        if file_refs:
            return self._parse_helper(path, file_refs)

        return img_refs

def main():
    '''Perform functionality from the command line'''
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str,
                        help='Unzipped directory exported by Nuclino')
    parser.add_argument('-o', '--output', type=str, default='docs',
                        help='Base of output directory. Default = ./docs')
    parser.add_argument('-i', '--issues', type=argparse.FileType('w'), default='-',
                        help='Where to print issues / reminders. Default = sys.stdout')
    args = parser.parse_args()

    tree = NuclinoTree(args.input, outfile=args.output)
    tree.parse()
    tree.do_output()

    if tree.issues:
        print('\n'.join(tree.issues), file=args.issues)

if __name__ == '__main__':
    main()
