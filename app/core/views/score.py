# Not sure this belongs in views, but it's a start
from abc import ABC, abstractmethod


"""
Example usage in score_module.py (in a widget's _score-modules directory):

from core.views.score import ScoreModule


class ScoreModuleCrossword(ScoreModule):
    def test_function():
        return "it worked!"

"""


class ScoreModule(ABC):
    # # vars
    # logs
    # inst
    # play_id
    # play
    # verified_score
    # calculated_score
    # total_questions
    # finished
    # log_problems
    # global_modifiers
    # # following are "protected" in PHP, consider _ prefix or name-mangling
    # custom_methods
    # questions
    # score_display
    # _ss_table_title
    # _ss_table_headers

    def __init__(self, play_id, inst, play=None):
        """
        :param play_id: The play ID of the game being scored
        :type play_id: int
        :param inst: Scoring type for the game to score
        :type inst: int
        :param play: TODO
        :type play: TODO
        """
        self.play_id = play_id
        self.inst = inst
        self.play = play

    def validate(self):
        """
        Perform all validation

        :rtype: bool
        :return: True if validation passes, False otherwise
        """
        return self.validate_times() and self.validate_scores()

    def validate_times(self):
        """
        Validate that the logs we recieved make sense in time,
        both in our server time and in the player time.
        Adds a validation fail log for every log that is found to be
        out of order (time-wise)

        :rtype: bool
        :returns: whether or not any logs were founds
        """
        # TODO
        pass

    def validate_scores(self):
        """
        Calculates score for this session. Updates "verified_score" and
        "calculated_percent" which are eventualy written to the database
        by the API.

        Validates that the individual question scores are valid.

        :rtype: bool
        """
        # TODO
        pass

    # was protected final in PHP
    def process_score_logs(self):
        """
        TODO: docstring
        """
        # TODO
        pass

    # was protected in PHP
    def handle_log_client_final_score(self, log):
        """
        TODO: docstring
        """
        # TODO
        pass

    # was protected in PHP
    def handle_log_question_answered(self, log):
        """
        TODO: docstring
        """
        # TODO
        pass

    # was protected in PHP
    def handle_log_widget_interaction(self, log):
        """
        TODO: docstring
        """
        # was empty in PHP
        pass

    # was protected in PHP
    def calculate_score(self):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_score_report(self):
        """
        TODO: docstring
        """
        # TODO
        pass

    def load_questions(self, timestamp=False):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_score_overview(self):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_overview_items(self):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_score_details(self):
        """
        TODO: docstring
        """
        # TODO
        pass

    def details_for_question_answered(self, log):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_feedback(self, log, answers):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_detail_style(self, score):
        """
        TODO: docstring
        """
        # TODO
        pass

    # was protected in PHP
    def log_problem(self, id, value, error_code, description):
        """
        TODO: docstring
        """
        # TODO
        pass

    # was abstract public in PHP
    def check_answer(self, log):
        """
        Check the answer of a given question (meant to be extended)

        :param log: Contains information about this play session

        :rtype: TODO (unsure if int, float, etc. was Number in PHP)
        :returns: the score received for this question (range: [0-100])
        """
        # TODO
        pass

    # was protected in PHP
    def get_ss_expected_answers(self, log, question):
        """
        TODO: docstring
        """
        # TODO
        pass

    def get_ss_answer(self, log, question):
        """
        Determine what the score page should display for the user's answer
        :param log: Contains information about this play session
        :type log: TODO
        :param question: TODO
        :type question: TODO
        """
        # TODO
        pass

    def get_ss_question(self, log, question):
        """
        TODO: docstring
        """
        # TODO
        pass

    # was protected final in PHP
    def query_logs(
        self, where_conditions, order_conditions=None, group_conditions=None
    ):
        """
        Proxy function to query session logs based on some parameters given by a widget score module

        TODO: args
        """
        # TODO
        pass

    # was protected final in PHP
    def hide_correct(self):
        """
        TODO: docstring
        """
        # TODO
        pass
