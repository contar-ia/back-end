from abc import ABC, abstractmethod

class ContAI_UserAPI(ABC):

    @abstractmethod
    def register_user(self, email, username, password):
        pass

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def create_story(self, story_prompt, grade, purpose):
        pass

    @abstractmethod
    def view_story(self, story_id):
        pass

    @abstractmethod
    def approve_story(self, approval):
        pass

    @abstractmethod
    def manual_edit(self, story_id, new_content):
        pass

    @abstractmethod
    def prompt_edit(self, story_id, prompt):
        pass

    @abstractmethod
    def user_history(self):
        pass

    @abstractmethod
    def recover_story(self, story_id):
        pass

    @abstractmethod
    def export_story(self, story_id, format):
        pass

    @abstractmethod
    def illustrate_story(self, story_id):
        pass

    @abstractmethod
    def edit_image(self, story_id, prompt):
        pass