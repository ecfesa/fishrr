from game import Game

def setup_game():
    """
    Função auxiliar para configurar e iniciar o jogo.
    Utilizada para facilitar testes e execução.
    """
    game = Game()
    return game

if __name__ == "__main__":
    game = setup_game()
    game.run()