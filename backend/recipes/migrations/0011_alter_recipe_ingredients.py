# Generated by Django 3.2.3 on 2023-09-12 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_alter_recipeingredient_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipeIngredient', to='recipes.Ingredient', verbose_name='Список ингредиентов'),
        ),
    ]
