import csv
from ..models import Aluno, Turma

def import_alunos(filename):
    with open(filename, 'r', errors="ignore") as file:
        reader = csv.DictReader(file)
        for row in reader:

            aluno, created = Aluno.objects.update_or_create(
                matricula=row['matricula'],
                nome=row['nome_aluno'],
                curso=row['curso']
            )

            turma, created = Turma.objects.update_or_create(
                codigoDisciplina=row['cod_disciplina'],
                periodo=row['periodo'],
                nome = row['turma']
            )

            turma.alunos.add(aluno)