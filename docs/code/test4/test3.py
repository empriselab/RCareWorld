class Human:
    """Foo class"""

    def __init__(self, gender, name):
        """Make a virtual human.

        :param sex: gender of human.
        :param name: name of human.
        """
        self.gender = gender
        self.name = name

    def speak(self, words):
        """speak some words.

        :param words: words to speak.
        :return: None
        """
        print(words)

    def get_intro(self):
        """get man's introduction.

        :return: self introduction string.
        """
        return f'Name: {self.name};Gender: {self.gender}'