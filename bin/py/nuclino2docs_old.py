'''
Inputs:
- input folder
- output folder

Process:
- Designate files as either pages or folders
- Replace images with appropriate HTML (centering, etc)
- Replace links:
  - Internal links with relative file links
  - Web links which refer to nuclino to relative file links (fixup)
'''

import argparse
import os
import re

def build_ref_regex():
    pattern = r'- \[(.*?)\]\(<(.*?)\?n>\)\s*'
    return re.compile(pattern)

def build_name_regex():
    pattern = r'(.*?) (.*?)\.md'
    return re.compile(pattern)

def parse_nuclino_tree(infile, outfile, file_dict, node, path=None, path_dup=None, re_ref=None, re_name=None):
    file_refs = []
    is_dir = True

    if re_ref is None:
        re_ref = build_ref_regex()

    if re_name is None:
        re_name = build_name_regex()

    with open(os.path.join(infile, node), 'r') as nodefile:
        while line = nodefile.readline():
            ref_match = re_ref.match(line)
            if ref_match is None:
                is_dir = False
                break
            file_refs.append(ref_match.group(2))

        if path is None:
            assert is_dir # Must be dir
            os.makedirs(outfile, exist_ok=True)
            path_dup_inner = {}
            for file_ref in file_refs:
                parse_nuclino_tree(infile,
                                   outfile,
                                   file_dict,
                                   file_ref,
                                   path=outfile,
                                   path_dup=path_dup_inner,
                                   re_ref=re_ref,
                                   re_name=re_name)
        else:
            name = node
            name_match = re_name.match(node)
            if name_match is not None:
                name = name_match.group(1)
            if path_dup is not None:
                ctr = path_dup.get(name, 0)
                if ctr > 0:
                    name = '%s_%d' % (name, ctr)
                path_dup[name] = ctr + 1
            file_dict[node]  = (os.join(path, name), name, is_dir)

            if is_dir:
                path_dup_inner = {} # Save next level down for the operation
                for file_ref in file_refs:
                    parse_nuclino_tree(infile,
                                       outfile,
                                       file_dict,
                                       file_ref,
                                       path=file_dict[node][0],
                                       path_dup=path_dup_inner,
                                       re_ref=re_ref,
                                       re_name=re_name)

# TODO images (Find highest common level - remap names - copy paste)
# TODO text (Fixup images, fixup app.nuclino.com and relative links - no relative support)
# TODO readme (If anything was found in need of fixing (linkwise) - index.md note)
# TODO pytest
# TODO linting



def main(infile, outfile):
    start = 'index.md' # Where to start
    file_dict = {} # Original Name: Path

    assert parse_nuclino_tree(infile, outfile, file_dict, start)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str,
                        help="Unzipped directory exported by Nuclino")
    parser.add_argument('-o', '--output', type=s0tr, default='docs',
                        help="Where to build docs. Default = ./docs/"
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args.input, args.output) 
