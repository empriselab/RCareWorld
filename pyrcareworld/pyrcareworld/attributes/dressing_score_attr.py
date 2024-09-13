import os
import json
import pyrcareworld.attributes as attr

class DressingScoreAttr(attr.BaseAttr):
    """
    DressingScoreAttr class to interact with the DressingScoreAttr in Unity.
    """
    
    def get_scores(self):
        """
        Get the current scores from Unity.

        :return: Dictionary containing the scores.
        """
        self._send_data("GetScores")
        self.env._step()
        return self.data.get("scores", {})

    def get_score_for_task(self, task_name):
        """
        Get the score for a specific task.

        :param task_name: Name of the task.
        :return: Score for the task.
        """
        scores = self.get_scores()
        return scores.get(task_name, 0)

    def save_scores_to_file(self, file_path):
        """
        Save the current scores to a JSON file.

        :param file_path: Path to the JSON file.
        """
        scores = self.get_scores()
        with open(file_path, 'w') as file:
            json.dump(scores, file, indent=4)

    def load_scores_from_file(self, file_path):
        """
        Load scores from a JSON file and update the Unity scores.

        :param file_path: Path to the JSON file.
        """
        with open(file_path, 'r') as file:
            scores = json.load(file)
        
        self._send_data("LoadScores", scores)
        self.env._step()
