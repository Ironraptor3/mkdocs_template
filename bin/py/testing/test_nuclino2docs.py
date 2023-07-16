'''Simple tests for Nuclino2Docs functionality.'''
import random
import string

from ..nuclino2docs import NuclinoTree, NuclinoTreeNode

def random_str(minlen=5, maxlen=20):
    '''
    Generates a random alphanumeric string at least size minlen and at most size maxlen
    '''
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits,
                   k=random.randrange(minlen, maxlen)))

def test_get_img_refs():
    '''Test NuclinoTreeNode get_img_refs (staticmethod)'''
    refs = {random_str() : bool(random.randrange(2))
            for _ in range(random.randrange(5, 20))}
    sample = ''.join([f'{random_str()}![{random_str()}]({("http://" if web else "") + ref})'
                      for ref, web in refs.items()])
    result = NuclinoTreeNode.get_img_refs(sample)

    assert sorted(result) == sorted([ref for ref, web in refs.items() if not web])

#pylint: disable=protected-access
def test_update_path_dup():
    '''Test NuclinoTreeNode _update_path_dup (staticmethod)'''
    sample = random_str()
    # If no dict passed in; return 2nd argument
    assert NuclinoTreeNode._update_path_dup(None, sample) == sample
    path_dup = {}
    # Assert name unchanged
    assert NuclinoTreeNode._update_path_dup(path_dup, sample) == sample
    # Assert path_dup modified after call
    assert sample in path_dup
    assert path_dup[sample] == 1
    # Try again, this time asserting sample has "_1" appended to the end
    assert NuclinoTreeNode._update_path_dup(path_dup, sample) == f'{sample}_1'
    assert sample in path_dup
    assert path_dup[sample] == 2
#pylint: enable=protected-access

def test_is_leaf():
    '''Test whether NuclinoTreeNode is a leaf'''
    tree = NuclinoTree(None) # No infile; dummy Tree
    node = NuclinoTreeNode(tree)
    # Not populated
    assert node.is_leaf()

    # Also with an empty list of children; still qualifies as leaf
    node.children = []
    assert node.is_leaf()

    # Append a child node
    node.children.append(NuclinoTreeNode(tree, parent=node))
    assert not node.is_leaf()
