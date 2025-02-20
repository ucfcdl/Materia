from abc import ABC, abstractmethod
from core.models import LogPlay, WidgetInstance
from utils.Semester import Semester
from util.logging.session_play import SessionPlay
from util.logging.session_logger import SessionLogger
from django.utils.timezone import now

class ScoreModule(ABC):

    def __init__(self, play_id: str, instance: WidgetInstance, play=None):
        self.logs = []
        self.play_id = play_id
        self.instance = instance
        self.play = play
        self.verified_score = 0
        self.calculated_percent = 0  # Full precision percent!! Not Rounded!
        self.total_questions = 0
        self.finished = False
        self.log_problems = False
        self.global_modifiers = []
        self.custom_methods = None
        self.questions = []
        self.score_display = []
        self._ss_table_title = "Responses:"
        self._ss_table_headers = ["Question Score", "The Question", "Your Response", "Correct Answer"]


    def validate(self) -> bool:
        """Perform all validation"""
        return self.validate_times() and self.validate_scores()


    def validate_times(self) -> bool:
        """Validate that the logs we received make sense in time,
        both in our server time and in the player time.
        Adds a validation fail log for every log that is found to be out of order (time-wise).
        """
        session = SessionPlay.get_or_none(str(self.play_id))
        if not session:
            return False
        logs = session.get_logs()
        last_time = 0
        for log in logs:
            #if we are in preview, use dict, in play use model
            game_time = log.game_time if hasattr(log, "game_time") else log["game_time"]
            if game_time < last_time and game_time != -1:
                if self.log_problems:
                    # Record a time validation failure log
                    SessionLogger.add_log(
                        log_type=1509,  # ERROR_TIME_VALIDATION
                        item_id=log.item_id if hasattr(log, "item_id") else log["item_id"],
                        text=str(log.id) if hasattr(log, "id") else "preview_log",
                        value=str(last_time),
                        game_time=game_time,
                        created_at=timezone.now(),
                        play_id=session,
                    )
            last_time = game_time

        return True



    def validate_scores(self, timestamp=False) -> bool:
        """Calculates score for this session. Updates `verified_score` and
        `calculated_percent`, which are eventually written to the database
        by the API. Validates the individual question scores are valid.
        """
        session = SessionPlay.get_or_none(str(self.play_id))
        if not session:
            return False

        if not timestamp:
            if not self.play:
                self.play = LogPlay.objects.get(id=self.play_id)

            # except for previews, check that attempts are not exceeded.
            if self.play_id != -1:
                semester = Semester.get_current_semester()
                attempts_used = LogPlay.objects.filter(
                    instance=self.instance, context_id=self.play.context_id, semester=semester
                ).count()

                if self.instance.attempts != -1 and attempts_used >= self.instance.attempts:
                    raise Exception("Attempt Limit Met: You have already met the attempt limit for this widget.")

        self.load_questions(timestamp)

        if not self.logs:
            self.logs = session.get_logs()

        self.process_score_logs()
        self.calculate_score()

        return True


    def process_score_logs(self)->None:
        """Processes logs to determine score"""
        for log in self.logs:
            log_type = log.log_type if hasattr(log, "log_type") else log["type"]
            if log_type == "WIDGET_END":
                self.finished = True
            elif log_type == "FINAL_SCORE_FROM_CLIENT":
                self.handle_log_client_final_score(log)
            elif log_type == "QUESTION_ANSWERED":
                self.handle_log_question_answered(log)
            elif log_type == "WIDGET_INTERACTION":
                self.handle_log_widget_interaction(log)
            elif log.type == "SCORE_PARTICIPATION":
                self.verified_score = log.value if hasattr(log, "value") else log["value"]


    def handle_log_client_final_score(self, log)->None:
        """Handles the log when a final score is received from the client"""
        self.verified_score = 0
        self.total_questions = 0
        val = log.value if hasattr(log, "value") else log["value"]
        self.global_modifiers.append(int(val) - 100)


    def handle_log_question_answered(self, log)->None:
        """Handles scoring when a question is answered"""
        self.total_questions += 1
        self.verified_score += self.check_answer(log)


    @abstractmethod
    def check_answer(self, log):
        """Abstract method to check answers. Implement this in child classes."""
        pass


    def calculate_score(self):
        """Calculate final score percentage"""
        global_mod = sum(self.global_modifiers)
        if self.total_questions > 0:
            points = self.verified_score + global_mod * self.total_questions
            self.calculated_percent = points / self.total_questions
        else:
            points = self.verified_score + global_mod
            self.calculated_percent = points

        # make sure score is between 0 and 100
        self.calculated_percent = max(0, min(self.calculated_percent, 100))


    def get_score_report(self)-> object:
        """Returns a report of the calculated score"""
        self.score_display["overview"] = self.get_score_overview()
        self.score_display["details"] = self.get_score_details()
        return self.score_display


    def get_score_overview():
        complete = False
        if self.play_id == "-1":
            complete = True
        else:
            complete = bool(self.play.is_complete) if self.play else False

        return {
            "complete": complete,
            "score": self.calculated_percent,
            "table": self.get_overview_items(),
            "referrer_url": self.play.referrer_url if self.play and self.play.referrer_url else "",
            "created_at": self.play.created_at if self.play and self.play.created_at else "",
            "auth": self.play.auth if self.play and self.play.auth else "",
        }


    def get_overview_items():
        overview_items = []
        overview_items.append({"message": "Points Lost", "value": self.calculated_percent-100})
        overview_items.append({"message": "Final Score", "value": self.calculated_percent})
        return overview_items


    def load_questions(self, timestamp=False)->None:
        """Loads questions associated with the widget instance"""
        if not self.instance.qset.data:
            self.instance.get_qset(self.instance.id, timestamp)

        if self.instance.qset.data:
            self.questions = self.instance.qset.find_questions(self.instance.qset.data)


    def get_score_details():
        details = []
        for logs in self.logs:
            log_type = log.log_type if hasattr(log, "log_type") else log["type"]
            if log_type == "QUESTION_ANSWERED":
                item_id = log.item_id if hasattr(log, "item_id") else log["item_id"]
                if item_id in self.questions:
                    #self.details_for_question_answered(log)?
                    details.append(self.details_for_question_answered(log))
        return [{
            "title": self._ss_table_title,
            "headers": self._ss_table_headers,
            "table": details
        }]


    def details_for_question_answered(self, log)-> dict:
        """BUilds an item in the table array like in php"""
        item_id = log.item_id if hasattr(log, "item_id") else log["item_id"]
        question = self.questions[item_id]
        score = self.check_answer(log)

        return {
            "data": [
                self.get_ss_question(log,question),
                self.get_ss_answer(log,question),
                self.get_ss_expected_answers(log,question)
            ],
            "data_style": ["question", "response", "answer"],
            "score": score,
            "feedback": self.get_feedback(log, question["answers"]),  # or question.answers if object
            "type": log.log_type if hasattr(log, "log_type") else log["type"],
            "style": self.get_detail_style(score),
            "tag": "div",
            "symbol": "%",
            "graphic": "score",
            "display_score": True
        }


    def get_feedback(self, log, answers:list)-> str | None:
        """"If log text matches an answer return it"""
        text = log.text if hasattr(log, "text") else log["text"]
        for answer in answers:
            if text == answer["text"]:
                feedback = answer["options"].get("feedback", "")
                if feedback:
                    return feedback
        return None


    def get_detail_style(self, score)-> str:
        """determines how to style row based on score"""
        if score in (-1, "-1"):
            return "ignored-value"
        if score in (100, "100"):
            return "full-value"
        if score in (0, "0"):
            return "no-value"
        return "partial-value"


    def get_ss_answer(self, log, question) -> str:
        return log.text if hasattr(log, "text") else log["text"]


    def get_ss_expected_answers(self, log, question) -> str:
        if question["type"] == "MC":
            max_value = 0
            max_answers = []
            for ans in question["answers"]:
                val = int(ans["value"])
                if val > max_value:
                    max_value = val
                    max_answers = [ans["text"]]
                elif val == max_value:
                    max_answers.append(ans["text"])
            return " or ".join(max_answers)
        else:
            return question["answers"][0]["text"]


    def log_problem(self, item_id: str, value: str, error_code: int, description: str) -> None:
        if self.log_problems:
            from util.logging.session_logger import SessionLogger
            SessionLogger.add_log(
                log_type=error_code,
                item_id=item_id,
                text=description,
                value=value,
                game_time=-1,
                created_at=now(),
                play_id=self.play_id
            )

