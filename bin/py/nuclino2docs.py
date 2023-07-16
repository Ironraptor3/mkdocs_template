'''
This file contains utilities for converting a Nuclino wiki export
to a format able to be used by the Python module mkdocs, which is able
to generate locally hosted Wiki websites in real time.

Mkdocs is much more flexible than Nuclino, and does not have hosting fees to work
alongside a team.

LIMITATION: This will not pull / download https images into the markdown.
This may make it harder for some offline exports to view certain images.
'''
import argparse
import logging
import os
import re
import shutil

REF_REGEX = re.compile(r'- \[(.*?)\]\(<(.*?)\?n>\)\s*') # Starting ref for trees
REF_GROUP = 2
NAME_REGEX = re.compile(r'(.*) (.*?)\.md') # File Name
NAME_GROUP = 1
IMG_REGEX = re.compile(r'\!\[(.*?)\]\((.*?)\)') # Image ref
IMG_GROUP = 2
LINK_REGEX = re.compile(r'(\!?)\[(.*?)\]\((.*?)\)') # Any ref
# No LINK_GROUP
BADIMG_REGEX = re.compile(r'h *ttps://lh\d+\.googleusercontent.com/')
# No BADIMG_GROUP

#pylint: disable=too-many-instance-attributes
class NuclinoTree():
    '''A file hierarchy built from a Nuclino export'''

    #pylint: disable=too-many-arguments
    def __init__(self, infile, outfile=None, startfile='index.md', is_root=True, logfile=None):
        self.file_dict = {}
        self.img_dict = {}
        self.issues = []
        self.log = self._setup_log(logfile)

        self.infile = infile
        self.outfile = outfile
        self.startfile = startfile

        self.is_root = is_root
        self.root = NuclinoTreeNode(self)

        self._parsed = False
    #pylint: enable=too-many-arguments

    @staticmethod
    def _setup_log(logfile):
        '''Setup Python logging, especially useful for debugging complex state'''
        log = logging.getLogger('NuclinoTree')
        log.setLevel(logging.INFO)
        handler = None
        if logfile is None:
            # Log to NullHandler; dropping output without warning
            handler = logging.NullHandler()
        else:
            handler = logging.FileHandler(logfile, mode='w', encoding='UTF-16')
        formatter = logging.Formatter(fmt='%(asctime)s %(name)-10s %(levelname)-8s: %(message)s',
                                      datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        return log

    def get_outpath(self, path):
        '''
        Shorthand for getting the output path given a relative path
        @param path: Path relative to self.outfile
        @return outpath (if it exists) joined with path
        '''
        return os.path.join(self.outfile, path) if self.outfile is not None else path

    def parse(self):
        '''
        Parses the given Nuclino export; setting up directories if output is valid
        Do nothing if already parsed
        '''
        if not self._parsed:
            self.root.parse(self.startfile, is_root=self.is_root)
            self._parsed = True

    def _do_output_images(self):
        '''Moves image data to appropriate places'''
        self.log.info('Outputting images')
        for img_src, img_data in self.img_dict.items():
            img_dst, _ = img_data
            # Need to append infile here
            img_src = os.path.join(self.infile, img_src)

            # Ensure the proper directory exists
            dst_path = os.path.dirname(img_dst)
            os.makedirs(dst_path, exist_ok=True)

            self.log.info('Copying %s to %s', img_src, img_dst)
            # Care for fragility: Markdown uses linux extensions always
            # (may get linux paths in parsing; os and shutil should handle this)
            shutil.copy2(img_src, img_dst)
        self.log.info('Finished outputting images')

    def pre_fixlines(self, srcfile, dstfile, file_data):
        '''
        Called before lines are edited, in case any headers are needed
        @param srcfile: Open handle of source file (read)
        @param dstfile: Open handle of destination file (write)
        @param file_data: (Path, Associated NuclinoTreeNode) of srcfile
        '''
        self.log.info('Doing pre_fixlines')
        line = srcfile.readline()
        target_header = f'# {file_data[1].name.lstrip()[:-len(".md")]}\n\n' # Browsing Title
        if line != target_header:
            dstfile.write(target_header)
        srcfile.seek(0)

    def fixline(self, line, file_data):
        '''
        Updates a line of text with the correct reference / link fixes
        @param line original line of text
        @param file_data (Path, Associated NuclinoTreeNode) of file line is from
        @return edited line of text
        '''
        result = line
        offset = 0

        path = file_data[0]

        for link_match in LINK_REGEX.finditer(line):
            replace = None
            old_link = link_match.group(3)
            if link_match.group(1): # Image
                # New link
                img_val = self.img_dict.get(old_link, None)
                replace_link = old_link
                if img_val is None:
                    if BADIMG_REGEX.match(old_link):
                        self.issues.append(f'Potentially bad Nuclino image ({path}): {old_link}')
                    elif not (old_link.startswith('https://') or old_link.startswith('http://')):
                        self.issues.append(f'Unknown image (no weblink): ({path}): {old_link}')
                        replace_link = 'TODO'
                else:
                    sep = '/' # Markdown uses Linux path separators always
                    relative_path = img_val[1].get_relative_path(file_data[1],
                                                                 start='..',
                                                                 sep=sep,
                                                                 rev=True)
                    if not relative_path:
                        self.issues.append(f'Issue getting the relative path for {img_val[0]}')
                        replace_link = 'TODO'
                    else:
                        replace_link = sep.join([relative_path, os.path.basename(old_link)])
                    #pylint:disable = line-too-long
                    # Replace with a centered image
                    replace = f'''\n<div style="text-align:center"><img alt="{link_match.group(2)}" src="{replace_link}"/></div>\n'''
                    #pylint:enable = line-too-long
            # Nuclino link - BAD
            elif old_link.lstrip().startswith('https://app.nuclino.com/'):
                replace = f'[{link_match.group(2)}](TODO)'
                self.issues.append(f'TODO fix Nuclino link ({path}): {old_link}')

            if replace is not None:
                self.log.info('Replacing %s with %s', old_link, replace)
                repl_start = link_match.start(0) + offset
                repl_end = link_match.end(0) + offset
                result = ''.join([result[:repl_start],
                                  replace,
                                  result[repl_end:]])
                # Update offset
                offset = len(replace) - len(old_link)
        return result

    def fixlines(self, srcfile, dstfile, file_data):
        '''
        Updates all lines of text with corrections when writing a file to a new location
        @param srcfile: Open handle of source file (read)
        @param dstfile: Open handle of destination file (write)
        @param file_data: (Path, Associated NuclinoTreeNode) of srcfile
        '''
        self.log.info('Fixing lines of %s -> %s', srcfile, dstfile)
        line = srcfile.readline()
        while line:
            # Call fixline on each line, then write it and get the next line
            line = self.fixline(line, file_data)
            dstfile.write(line)
            line = srcfile.readline()
        self.log.info('Finished fixing lines of %s', srcfile)

    def _do_output_files(self):
        '''Moves all files and fixes up their text in the process'''
        self.log.info('Outputting all parsed files')
        for file_src, file_data in self.file_dict.items():
            file_dst, dst_node = file_data

            if not dst_node.is_leaf():
                continue # Skip non-leaves

            file_src = os.path.join(self.infile, file_src) # Append infile to path

            with open(file_src, 'r', encoding='UTF-8') as srcfile:
                with open(file_dst, 'w', encoding='UTF-8') as dstfile:
                    # pre_fixlines, then fixlines. post_fixlines here too if it wasn't a no op
                    self.pre_fixlines(srcfile, dstfile, file_data)
                    self.fixlines(srcfile, dstfile, file_data)
        self.log.info('Finished outputting all parsed files')

    def check_issues(self):
        '''Raise general issues after parsing (append to self.issues)'''
        if self.outfile:
            out_len = len(self.outfile)
            has_home = False
            for _, file_data in self.file_dict.items():
                path, node = file_data
                # index.md file located at the root of the outfile
                # Account for sep
                if len(path) > out_len and path[out_len+1:] == node.name and node.name == 'index.md':
                    has_home = True
                    break
            if not has_home:
                self.issues.append('There is no index.md file in the root!')

    def do_output(self, regen_issues=False):
        '''
        Create mkdocs file structure after parsing the Nuclino export
        @param regen_issues Whether to reset self.issues before appending new issues
        @return True if successful; False if in a bad state (not parsed / no outfile)
        '''
        if not (self._parsed and self.outfile):
            return False

        if regen_issues:
            self.issues = []

        self._do_output_images()
        self._do_output_files()
        self.check_issues()
        return True
#pylint: enable=too-many-instance-attributes

class NuclinoTreeNode():
    '''Helper class: Represents a node in the file tree while parsing Nuclino export'''
    def __init__(self, tree, parent=None):
        self.tree = tree
        self.parent = parent
        self.name = None
        self.children = None

    @staticmethod
    def get_img_refs(line):
        '''
        Gets all image references in a markdown-based line of text
        @param line line of text to scan
        @return a list of image links from markdown format
        '''
        img_refs = [tup[IMG_GROUP - 1] for tup in IMG_REGEX.findall(line)]
        def is_weblink(ref):
            ref = ref.lstrip()
            return ref.startswith('https://') or ref.startswith('http://')
        # Filter out web links - Do nothing with them (aside from mentioning the issue later)
        return [ref for ref in img_refs if not is_weblink(ref)]

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
        path_dup[name] = ctr + 1
        if ctr:
            name = f'{name}_{ctr}'
            # Degenerate case
            while name in path_dup: # Unsure of correct behavior here
                name = f'{name}_overlap_correction'
        return name

    def is_leaf(self):
        '''
        Was this node a leaf node?
        @return True if self.children is None or empty; False otherwise
        '''
        return not self.children

    #pylint: disable=too-many-arguments
    def get_relative_path(self, other_node, start='.', next_start='', sep='/', rev=False):
        '''
        Gets the relative filesystem path between self and the other node.
        Assumes the other_node is below self in the file tree.
        Start defaults to '.' and is used for the recursive call
        Specify rev to reference something further up the tree from the lower node.

        @param other_node Other node to get the path to
        @param start Starting path, defaults to '.'
        @param next_start Path to append on the next evaluation step of the recursion. Default ''
        @param sep Separator to use in the returned path
        @param rev Towards the root of the tree? Default = False
        @return straight path to other node or None if no such path exists
        '''
        if self == other_node:
            return start

        if self.is_leaf():
            # Not found
            return None

        for child_node in self.children:
            # Iterate through children
            next_path = sep.join([start, next_start]) if next_start else start
            result = child_node.get_relative_path(other_node,
                                                  start=next_path,
                                                  next_start = '..' if rev else self.name,
                                                  sep=sep,
                                                  rev=rev)
            if result:
                return result
        # Not found
        return None
    #pylint: disable=too-many-arguments

    def _parse_helper(self, path, file_refs):
        '''Recursion helper; Also handles images. Return list of images encountered.'''
        self.children = [NuclinoTreeNode(self.tree, parent=self) for _ in file_refs]
        path_dup = {}
        all_img_refs = set()
        for index, file_ref in enumerate(file_refs):
            img_refs = self.children[index].parse(file_ref, path=path, path_dup=path_dup)
            for img_ref in img_refs:
                if img_ref in all_img_refs or img_ref not in self.tree.img_dict:
                    self.tree.img_dict[img_ref] = (path, self)
                all_img_refs.add(img_ref)
        return list(all_img_refs)

    def parse(self, nodefile, is_root=False, path=None, path_dup=None):
        '''
        Parses the nodefile:
        @param is_root: Whether this is the true top of a tree
        @param path: Current path in parsing
        @param path_dup: Dictionary of parent node containing duplicate names
        @return A list of image references encountered (to bubble back up the tree)
        '''
        self.tree.log.info('Parsing %s', nodefile)
        file_refs = []
        img_refs = []

        try:
            with open(os.path.join(self.tree.infile, nodefile), 'r', encoding='UTF-8') as nodetxt:
                line = nodetxt.readline()
                while line:
                    line = line.rstrip()
                    if file_refs is not None: # Still looking to see whether this is a parent
                        ref_match = REF_REGEX.fullmatch(line)
                        if ref_match is None: # Disqualify
                            file_refs = None
                        else:
                            file_refs.append(ref_match.group(REF_GROUP))
                            line = nodetxt.readline()
                            continue
                    img_refs.extend(self.get_img_refs(line))
                    line = nodetxt.readline()
        except (OSError, IOError):
            self.tree.log(f'An issue occured parsing {nodefile}')
            return []

        if is_root:
            assert file_refs # Has to be parent here
            if self.tree.outfile is not None: # Init outfile here
                os.makedirs(self.tree.outfile, exist_ok=True)
            self.tree.log.info('Finished parsing root file (path=%s)', path)
            return self._parse_helper(path, file_refs)

        name = nodefile
        name_match = NAME_REGEX.fullmatch(name)
        if name_match is not None: # Get rid of junk
            name = name_match.group(NAME_GROUP)
        name = self._update_path_dup(path_dup, name) # Handle duplicates in new layout
        if not file_refs:
            name = f'{name}.md' # Append .md to end of filename if leaf
        path = os.path.join(path, name) if path is not None else self.tree.get_outpath(name)
        self.name = name # Update name field
        self.tree.file_dict[nodefile] = (path, self) # Save path alongside this object
        self.tree.log.info('Finished parsing %s -> %s', nodefile, path)
        if file_refs:
            if self.tree.outfile is not None:
                os.makedirs(path, exist_ok=True)
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
    parser.add_argument('-l', '--logfile', default=None,
                        help='Where to print logging data? Default = None')
    args = parser.parse_args()

    tree = NuclinoTree(args.input, outfile=args.output, logfile=args.logfile)
    tree.parse()
    tree.do_output()

    if tree.issues:
        issues = '\n\t'.join(tree.issues)
        print(f'Issues:\n{issues}', file=args.issues)

if __name__ == '__main__':
    main()
