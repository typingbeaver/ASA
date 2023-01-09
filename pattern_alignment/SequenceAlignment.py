import numpy as np
import pandas as pd


class SequenceAlignment:

    def __init__(self, query_sequence: str, subject_sequence: str, comparator) -> None:
        self.QUERY = query_sequence
        self.SUBJECT = subject_sequence
        self.COMPARATOR = comparator

        self.LEN_QUERY = len(self.QUERY)
        self.LEN_SUBJECT = len(self.SUBJECT)

        self.score_matrix = self.__create_score_matrix__(
            self.QUERY, self.SUBJECT, self.COMPARATOR)

    def __str__(self) -> str:
        pass

    def __create_score_matrix__(self, query: str, subject: str, comparator) -> np.ndarray:
        LEN_QUERY = len(query)
        LEN_SUBJECT = len(subject)

        # initialize matrix
        score_matrix = np.empty((LEN_SUBJECT+1, LEN_QUERY+1), order='C')
        # columns -> last row
        score_matrix[-1, :] = np.arange(-LEN_QUERY, 1)
        # rows -> last column
        score_matrix[:, -1] = np.arange(-LEN_SUBJECT, 1)

        # calculate alignment factors
        for row in reversed(range(LEN_SUBJECT)):
            for column in reversed(range(LEN_QUERY)):

                score_matrix[row, column] = comparator.get_score(
                    score_matrix, row, column, subject, query)

        return score_matrix

    def get_score_matrix_as_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.score_matrix[:-1, :-1],
                            index=[*self.SUBJECT],
                            columns=[*self.QUERY],
                            )

    def get_alignment_value(self) -> float:
        return self.score_matrix[0, 0]

    def find_optimal_alignments(self, max: int = -1) -> list:
        return self.__find_optimal_alignments__(path=list(), alignments=list(), max=max)

    def __find_optimal_alignments__(self, index_subject: int = 0, index_query: int = 0, path: list = None, alignments: list = None, max: int = -1) -> list:
        if (max >= 0) and (len(alignments) >= max):
            return

        if index_subject == self.LEN_SUBJECT or index_query == self.LEN_QUERY:
            alignments.append(path)
            return

        path.append((index_subject, index_query))
        diagonal, down, right = self.COMPARATOR.check_score(
            self, index_subject, index_query)

        if diagonal:
            self.__find_optimal_alignments__(
                index_subject+1, index_query+1, path.copy(), alignments, max)

        if down:
            self.__find_optimal_alignments__(
                index_subject+1, index_query, path.copy(), alignments, max)

        if right:
            self.__find_optimal_alignments__(
                index_subject, index_query+1, path.copy(), alignments, max)

        return alignments

    def read_alignment(self, alignment: list = None):
        str_query = ""
        str_subject = ""
        old_index_query = -1
        old_index_subject = -1

        for index_subject, index_query in alignment:
            str_query += self.QUERY[index_query] if index_query > old_index_query else "-"
            str_subject += self.SUBJECT[index_subject] if index_subject > old_index_subject else "-"
            old_index_query = index_query
            old_index_subject = index_subject

        return str_query, str_subject


class NeedlemanWunschSimple:
    def __init__(self,
                 cost_match: float = 2,
                 cost_mismatch: float = 0,
                 cost_gap: float = -1
                 ) -> None:
        self.COST_MATCH = cost_match
        self.COST_MISMATCH = cost_mismatch
        self.COST_GAP = cost_gap

    def get_score(self, matrix: list, index_subject: int, index_query: int, sequence_subject: str, sequence_query: str) -> float:
        return max(
            self.__get_score_diagonal__(
                matrix, index_subject, index_query, sequence_subject, sequence_query),
            self.__get_score_down__(
                matrix, index_subject, index_query),
            self.__get_score_right__(
                matrix, index_subject, index_query),
        )

    def check_score(self, alignment: SequenceAlignment, index_subject: int, index_query: int) -> set:
        SCORE = alignment.score_matrix[index_subject, index_query]
        return \
            SCORE == self.__get_score_diagonal__(alignment.score_matrix, index_subject, index_query, alignment.SUBJECT, alignment.QUERY), \
            SCORE == self.__get_score_down__(alignment.score_matrix, index_subject, index_query), \
            SCORE == self.__get_score_right__(
                alignment.score_matrix, index_subject, index_query)

    def __get_score_diagonal__(self, matrix: list, index_subject: int, index_query: int, sequence_row: str, sequence_column: str) -> float:
        return matrix[index_subject+1, index_query+1] \
            + (self.COST_MATCH if sequence_row[index_subject] == sequence_column[index_query]
               else self.COST_MISMATCH)

    def __get_score_down__(self, matrix: list, index_subject: int, index_query: int) -> float:
        return matrix[index_subject+1, index_query] + self.COST_GAP

    def __get_score_right__(self, matrix: list, index_subject: int, index_query: int) -> float:
        return matrix[index_subject, index_query+1] + self.COST_GAP