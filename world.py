from task_progress import TaskProgress

class Island:
    """
    Representa cada ilha do jogo.
    """
    def __init__(self, id, name, color, minigame, password, todo):
        self.id = id                # ex: 1, 2, 3
        self.name = name            # ex: "Fish Island"
        self.color = color          # tupla RGB para o fundo do terminal
        self.minigame = minigame    # instância de Minigame
        self.password = password    # senha para a próxima ilha
        self.todo = todo            # lista de strings
        self.task_progress = TaskProgress(todo)
        
        # Associar este objeto ilha ao minigame
        self.minigame.island = self
        
    def unlock_next(self):
        """Verifica condição e retorna senha da próxima ilha."""
        # Verifica se todas as tarefas foram concluídas
        if self.task_progress.are_all_completed():
            return self.password
        return None
        
    def get_completion_status(self):
        """Retorna a porcentagem de conclusão da ilha"""
        return self.task_progress.get_completion_percentage()
    
    def complete_task(self, task_name):
        """Marca uma tarefa como concluída pelo nome"""
        return self.task_progress.complete_task_by_name(task_name)
    
    def get_formatted_tasks(self):
        """Retorna uma lista de tarefas formatada com status de conclusão"""
        return self.task_progress.get_formatted_tasks()