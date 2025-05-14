class TaskProgress:
    """
    Gerencia o progresso das tarefas de uma ilha.
    """
    def __init__(self, tasks):
        self.tasks = tasks
        self.completed = [False] * len(tasks)
    
    def complete_task(self, index):
        """Marca uma tarefa como concluída pelo índice"""
        if 0 <= index < len(self.completed):
            self.completed[index] = True
            return True
        return False
    
    def complete_task_by_name(self, task_name):
        """Marca uma tarefa como concluída pelo nome"""
        for i, task in enumerate(self.tasks):
            if task.lower() == task_name.lower():
                self.completed[i] = True
                return True
        return False
    
    def is_completed(self, index):
        """Verifica se uma tarefa está concluída"""
        if 0 <= index < len(self.completed):
            return self.completed[index]
        return False
    
    def get_completion_percentage(self):
        """Retorna a porcentagem de conclusão das tarefas"""
        if not self.completed:
            return 0
        return sum(self.completed) / len(self.completed) * 100
    
    def get_completed_tasks(self):
        """Retorna uma lista com todas as tarefas concluídas"""
        return [task for i, task in enumerate(self.tasks) if self.completed[i]]
    
    def get_pending_tasks(self):
        """Retorna uma lista com todas as tarefas pendentes"""
        return [task for i, task in enumerate(self.tasks) if not self.completed[i]]
    
    def get_formatted_tasks(self):
        """Retorna uma lista formatada com indicadores de conclusão"""
        return [f"[{'X' if self.completed[i] else ' '}] {task}" for i, task in enumerate(self.tasks)]
    
    def are_all_completed(self):
        """Verifica se todas as tarefas foram concluídas"""
        return all(self.completed)