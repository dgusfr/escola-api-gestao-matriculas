from rest_framework import serializers

from escola.models import Curso, Estudante, Matricula
from escola.validators import celular_valido, cpf_valido, nome_valido


class EstudanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudante
        fields = ["id", "nome", "email", "cpf", "data_nascimento", "celular"]

    def validate(self, dados):
        if "cpf" in dados and not cpf_valido(dados["cpf"]):
            raise serializers.ValidationError({"cpf": "Número de CPF inválido."})
        if "nome" in dados and not nome_valido(dados["nome"]):
            raise serializers.ValidationError(
                {"nome": "O nome não deve conter dígitos numéricos ou caracteres especiais."}
            )
        if "celular" in dados and not celular_valido(dados["celular"]):
            raise serializers.ValidationError(
                {"celular": "O número de celular deve conter 11 dígitos com DDD (ex: 11988887777)."}
            )
        return dados


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = "__all__"


class MatriculaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matricula
        exclude = []


class ListaMatriculasEstudanteSerializer(serializers.ModelSerializer):
    curso = serializers.ReadOnlyField(source="curso.descricao")
    periodo = serializers.SerializerMethodField()

    class Meta:
        model = Matricula
        fields = ["curso", "periodo"]

    def get_periodo(self, obj):
        return obj.get_periodo_display()


class ListaMatriculasCursoSerializer(serializers.ModelSerializer):
    estudante_nome = serializers.ReadOnlyField(source="estudante.nome")

    class Meta:
        model = Matricula
        fields = ["estudante_nome"]
