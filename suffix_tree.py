from json import dumps as json_dumps
from collections import OrderedDict

class SuffixTree:
    # ~ I'm a cheap ol' compact Suffix Tree with way too high memory usage ~
    def __init__(self, text: str) -> None:
        self.tree = self.__build_tree__(text)
        self.suffix_array = None

    def __str__(self) -> str:
        return json_dumps(self.tree, indent=4, sort_keys=True)

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
            insertion = f"{text[i:]}$"
            print(f"Inserting suffix {insertion}")

            node, insertion = cls.__insertion_search__(tree, insertion)
            node[f"{insertion}"] = i+1
            print(f"Inserted edge {insertion} with end node [{i+1}]")
            print()

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

        # no edge with prefix
        if prefix == None:
            print("Returning node for insertion." if edge == None
                  else "End node found.")
            return node, text

        # prefix matches edge
        if edge == text[:prefix]:
            # follow edge, cut off prefix and repeat
            print(f"Digging deeper on {edge = }...")
            return cls.__insertion_search__(node[edge], text[prefix:])

        # prefix matches edge partially: split edge and create new node
        prefix_edge, suffix_edge = edge[:prefix], edge[prefix:]
        print(f"Splitting {edge = } into '{prefix_edge}' / '{suffix_edge}'")
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
        # check for leaf/end node
        if type(node) == int:
            return (node, None)

        for edge in node.keys():
            if not edge.startswith(pattern[:1]):
                # print(f"Does not match: {edge = }, {pattern[:1]}")
                continue

            if edge == pattern:
                print(f"Found edge with equal pattern: {edge = }, {pattern}")
                return (edge, len(pattern))

            # find biggest common prefix
            size_prefix = 1
            while True:
                if not edge.startswith(pattern[:size_prefix+1]):
                    print(f"Found prefix of size {size_prefix}: "
                          f"{edge = }, {pattern[:size_prefix]}")
                    return (edge, size_prefix)
                size_prefix += 1

        print("No matching edge found.")
        return (None, None)

    # ======== AUFGABE 7a / Pattern Search ========

    def find_pattern(self, pattern: str) -> list:
        return self.__pattern_search__(pattern, self.tree, indeces=[])

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
        # Check for leaf/exit node
        # --> finished path & look for pattern
        if type(node) == int:
            if text.startswith(pattern):
                indeces.append(node)
                print(
                    f"'{pattern}' found in suffix '{text}' with index {node}.")
            return indeces

        # Go down every subtree
        for edge in node.keys():
            cls.__pattern_search__(
                pattern, node[edge], (text + edge), indeces)

        return indeces

    # ======== AUFGABE 7b / Longest Repeated Substring ========

    # TODO

    # ======== Aufgabe 8 / Memory Size ========

    def get_size(self) -> int:
        """Calculate the tree's total memory size.

        Returns:
            int: Size in bytes
        """
        return SuffixTree.__get_size__(self.tree)

    @classmethod
    def __get_size__(cls, node: dict, size: int = 0) -> int:
        """Get the memory size of a (Sub)Tree.

        Args:
            node (dict): (Sub)Tree to calculate size of.
            size (int, optional): Size buffer. Defaults to 0.

        Returns:
            int: Size in bytes
        """
        size += node.__sizeof__()   # size of node's dict or leaf's integer

        if type(node) == int:
            return size

        for edge in node.keys():
            size += edge.__sizeof__()   # size of edge label (string)
            cls.__get_size__(node[edge], size)

        return size

    # ======== Suffix Array ========

    def get_array(self) -> OrderedDict:
        if self.suffix_array is None:
            self.suffix_array = OrderedDict()
            self.__create_suffix_array__(self.tree)
        return self.suffix_array

    def __create_suffix_array__(self, tree: dict, s: str = '') -> None:
        for branch in sorted(tree.keys()):
            node = tree[branch]
            s_tmp = s + branch
            if isinstance(node, int):
                self.suffix_array[node] = s_tmp
            elif isinstance(node, dict):
                self.__create_suffix_array__(node, s_tmp)
