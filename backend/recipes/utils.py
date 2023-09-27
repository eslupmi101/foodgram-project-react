import xlwt

from recipes.models import Recipe


def add_recipe_row(ws, row_num, recipe):
    row = [
        recipe.name,
        recipe.author.username,
        recipe.text,
        recipe.cooking_time
    ]

    font_style = xlwt.XFStyle()

    for col_num, cell_value in enumerate(row):
        ws.write(row_num, col_num, cell_value, font_style)


def add_ingredient_row(ws, row_num, recipe_ingredient, number_ingredient):
    row = [
        str(number_ingredient),
        recipe_ingredient.indredient.name,
        recipe_ingredient.indredient.measurement_unit,
        str(recipe_ingredient.amount),
    ]

    font_style = xlwt.XFStyle()

    for col_num, cell_value in enumerate(row):
        ws.write(row_num, col_num, cell_value, font_style)


def add_ingredients_titles(ws, row_num):
    columns = [
        "Номер ингредиента", "Название",
        "Мера измерения", "Количество ингредиента"
    ]
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)


def add_recipe_titles(ws, row_num):
    columns = [
        "Название рецепта", "Автор",
        "Описание", "Время приготовления"
    ]
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)


def get_xls_recipes_file(recipes: list[Recipe]) -> xlwt.Workbook:
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Recipes")

    row_num = 0

    for recipe in recipes:
        add_recipe_titles(ws, row_num)
        row_num += 1

        add_recipe_row(ws, row_num, recipe)
        row_num += 1

        add_ingredients_titles(ws, row_num, recipe)
        row_num += 1

        number_ingredient = 0
        for recipe_ingredient in recipe.recipes_ingredients.all():
            add_ingredient_row(
                ws,
                row_num,
                recipe_ingredient,
                number_ingredient
            )
            row_num += 1
            number_ingredient += 1

    return wb
