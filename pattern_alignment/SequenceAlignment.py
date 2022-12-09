import numpy as np
import pandas as pd


class SequenceAlignment:

    def __init__(self, query_sequence: str, subject_sequence: str, comparator) -> None:
        self.QUERY = query_sequence
        self.SUBJECT = subject_sequence
        self.COMPARATOR = comparator

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


class NeedlemanWunsch:
    def __init__(self,
                 cost_equal: float = 2,
                 cost_unequal: float = 0,
                 cost_gap: float = -1
                 ) -> None:
        self.COST_EQUAL = cost_equal
        self.COST_UNEQUAL = cost_unequal
        self.COST_GAP = cost_gap

    def get_score(self, matrix, index_row, index_column, sequence_row, sequence_column) -> float:
        return max(
            # direct comparison
            matrix[index_row+1, index_column+1]
            + (self.COST_EQUAL if sequence_row[index_row] == sequence_column[index_column]
               else self.COST_UNEQUAL),
            # gap
            matrix[index_row+1, index_column] + self.COST_GAP,
            # gap
            matrix[index_row, index_column+1] + self.COST_GAP
        )
