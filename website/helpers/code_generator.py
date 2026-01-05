import random, string, secrets

class CodeGenerator:

    @staticmethod
    def generator(
        length: int = 8
    ) -> str:
        # Alphabet
        alphabet = string.ascii_letters + string.digits

        # Secret Code
        return ''.join(secrets.choice(alphabet) for _ in range(self.length))