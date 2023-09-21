import xlwt


def get_xls_recipes_file(recipes) -> xlwt.Workbook:
    """
    Возвращает xls workbook.

    Принимает queryset Recipe.
    """
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Recipes')

    row_num = 0
    columns = ['Название', 'Автор', 'Описание', 'Время приготовления']
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    for col_num, column_title in enumerate(columns):
        ws.write(row_num, col_num, column_title, font_style)

    font_style = xlwt.XFStyle()

    for recipe in recipes.all():
        row_num += 1
        row = [
            recipe.name,
            recipe.author.username,
            recipe.text,
            recipe.cooking_time
        ]
        for col_num, cell_value in enumerate(row):
            ws.write(row_num, col_num, cell_value, font_style)

    return wb
