from bisect import bisect
from datasize import DataSize
from json import dumps as json_dumps

# //////////////// SUFFIX TREE ////////////////
class SuffixTree:
    # ~ I'm a cheap ol' compact Suffix Tree with way too high memory usage ~
    def __init__(self, text: str) -> None:
        self.text_len = len(text)
        self.tree = self.__build_tree__(text)
        self.suffix_array = None

    def __str__(self) -> str:
        return json_dumps(self.tree, indent=4)

    @staticmethod
    def is_leaf(node: dict) -> bool:
        return type(node) is int

    # ======== Aufgabe 7 / Suffix Tree Construction ========
    @classmethod
    def __build_tree__(cls, text: str) -> dict:
        """Builds a Suffix Tree from given text

        Args:
            text (str): Text to insert

        Returns:
            dict: Suffix Tree
        """
        tree = dict()

        for i in range(len(text)):
            suffix = f"{text[i:]}$"
            node, insertion = cls.__insertion_search__(tree, suffix)
            node[f"{insertion}"] = i+1

        return tree

    @classmethod
    def __insertion_search__(cls, node: dict, text: str) -> tuple:
        """Finds last failing node

        Args:
            node (dict): (Sub)Tree to search in
            text (str): Text to search for

        Returns:
            tuple: (node, remaining text to insert)
        """
        edge, prefix = cls.__find_max_prefix__(node, text)

        if prefix is None:
            return node, text

        # Exact match: Follow edge, cut off prefix and repeat
        if edge == text[:prefix]:
            return cls.__insertion_search__(node[edge], text[prefix:])

        # Partial match: Split edge and create new node
        prefix_edge, suffix_edge = edge[:prefix], edge[prefix:]
        node[prefix_edge] = {suffix_edge: node.pop(edge)}
        return node[prefix_edge], text[prefix:]

    @staticmethod
    def __find_max_prefix__(node: dict, pattern: str) -> tuple:
        """Find a matching edge with biggest common prefix.

        Args:
            node (dict): (Sub)Tree to search in
            pattern (str): Pattern to find prefix of

        Returns:
            tuple: (edge label, size of prefix)
        """
        if SuffixTree.is_leaf(node):
            return (node, None)

        for edge in node.keys():
            if not edge.startswith(pattern[:1]):
                continue

            if edge == pattern:
                return (edge, len(pattern))

            # Find biggest common prefix
            size_prefix = 1
            while True:
                if not edge.startswith(pattern[:size_prefix+1]):
                    return (edge, size_prefix)
                size_prefix += 1

        # No matching edge found
        return (None, None)

    # ======== AUFGABE 7a / Pattern Search ========

    # Awfully lazy implementation <( ~.~ )>
    def find_pattern(self, pattern: str) -> list:
        return SuffixTree.__pattern_search__(pattern, self.tree, indeces=[])

    @classmethod
    def __pattern_search__(cls, pattern: str, node: dict, text: str = "", indeces: list = None) -> list:
        """Checks if a pattern is present in the Suffix Tree.

        Args:
            pattern (str): Pattern to search for
            node (dict): (Sub)Tree to search in
            text (str, optional): Text of already passed edges. Defaults to "".
            indeces (list, optional): List of indices. Defaults to None.

        Returns:
            list: Indeces of substrings with presence of pattern
        """
        if cls.is_leaf(node):
            if text.startswith(pattern):
                indeces.append(node)
                print(
                    f"'{pattern}' found at index {node}: '{text}'")
            return indeces

        # Go down every subtree
        for edge in node.keys():
            cls.__pattern_search__(
                pattern, node[edge], (text + edge), indeces)

        return indeces

    # ======== AUFGABE 7b / Longest Repeated Substring ========

    def get_longest_repetition(self) -> str:
        """Finds the longest repeated substring in the tree.

        Returns:
            str: Longest repeated substring
        """
        return SuffixTree.__get_longest_substring__(self.tree)

    @classmethod
    def __get_longest_substring__(cls, node: dict, parent_path: str = "", longest: str = "") -> str:
        """Finds longest repeated substring in a suffix tree.

        Args:
            node (dict): (Sub-)Tree to search in
            parent_path (str, optional): Already passed path. Defaults to "".
            longest (str, optional): Longest known repetition. Defaults to "".

        Returns:
            str: Longest repeated substring
        """
        for edge in node.keys():
            # Check for splitting node
            if cls.is_leaf(node[edge]):
                continue

            path = parent_path + edge
            if len(path) > len(longest):
                longest = path
            longest = cls.__get_longest_substring__(node[edge], path, longest)

        return longest

    # ======== Aufgabe 8 / Memory Size ========

    def get_tree_size(self) -> tuple:
        """Calculate the tree's total memory size & size per character.

        Returns:
            tuple: (Total size in bytes, Size per character in bytes)
        """
        size = SuffixTree.__get_tree_size__(self.tree)
        return size, size/self.text_len

    @classmethod
    def __get_tree_size__(cls, node: dict, size: int = 0) -> int:
        """Get the memory size of a (Sub)Tree.

        Args:
            node (dict): (Sub)Tree to calculate size of.
            size (int, optional): Size buffer. Defaults to 0.

        Returns:
            int: Size in bytes
        """
        size += node.__sizeof__()   # size of node

        if cls.is_leaf(node):
            return size

        for edge in node.keys():
            size += edge.__sizeof__()   # size of edge label (string)
            size = cls.__get_tree_size__(node[edge], size)

        return size

    def print_tree_size(self) -> None:
        total_size, char_size = self.get_tree_size()
        print(f"Total size: {DataSize(total_size):.2a}")
        print(f"==> {DataSize(char_size):.2a} per character")


# //////////////// SUFFIX ARRAY ////////////////
class SuffixArray:

    def __init__(self, suffix_tree: SuffixTree) -> None:
        self.text_len = suffix_tree.text_len
        self.array = self.__create_array__(suffix_tree.tree, array=list())

    # ======== Construction ========
    @classmethod
    def __create_array__(cls, node: dict, path: str = '', array: list = None) -> list:
        """Creates a Suffix Array out of a Suffix Tree.

        Args:
            node (dict): (Sub)Tree to conquer
            path (str, optional): Text of already passed edges. Defaults to "".
            array (list): Suffix Array

        Returns:
            list: Suffix Array
        """
        if SuffixTree.is_leaf(node):
            array.append((node, path))
            return array

        # Follow edges in alphabetical order
        for edge in sorted(node.keys()):
            cls.__create_array__(node[edge], (path + edge), array)

        return array

    # ======== Pattern Search ========

    def find_pattern(self, pattern: str) -> list:
        indices = []

        index = bisect(self.array, pattern, key=lambda set: set[1])
        while (set := self.array[index])[1].startswith(pattern):
            print(f"'{pattern}' found at index {set[0]}: '{set[1]}'")
            indices.append(set[0])
            index += 1

        return indices

    # ======== Memory Size ========

    def get_size(self) -> int:
        size = self.array.__sizeof__()
        for item in self.array:
            size += item.__sizeof__()
            size += item[0].__sizeof__()
            size += item[1].__sizeof__()

        return size, size/self.text_len

    def print_size(self) -> None:
        total_size, char_size = self.get_size()
        print(f"Total size: {DataSize(total_size):.2a}")
        print(f"==> {DataSize(char_size):.2a} per character")
