import xlwt

from recipes.models import Recipe


def get_xls_recipes_file(recipes: list[Recipe]) -> xlwt.Workbook:
    """
    Возвращает xls workbook.

    Принимает queryset Recipe.
    """
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet("Recipes")

    row_num = 0
    columns = [
        "Номер", "Ингредиент", "Мера измерение", "Количество ингредиента",
        "Название рецепта", "Автор", "Описание", "Время приготовления"
    ]
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    for recipe in recipes:
        number_ingredient = 0

        for recipe_ingredient in recipe.recipes_ingredients.all():
            row_num += 1
            row = [
                str(number_ingredient),
                recipe_ingredient.indredient.name,
                recipe_ingredient.indredient.measurement_unit,
                recipe_ingredient.amount,
                recipe.name,
                recipe.author.username,
                recipe.text,
                recipe.cooking_time
            ]
            number_ingredient += 1

            for col_num, cell_value in enumerate(row):
                ws.write(row_num, col_num, cell_value, font_style)

    return wb
