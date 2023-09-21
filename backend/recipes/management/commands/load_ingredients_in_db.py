import json
import os
import logging

from django.core.management import BaseCommand
from django.conf import settings
from typing import Dict, List

from recipes.models import Ingredient

logger = logging.getLogger(__name__)

INGREDIENTS_DIR = getattr(settings, 'INGREDIENTS_DIR', '')


def read_json_file(file_name: str) -> List[Dict]:
    file_path = os.path.join(INGREDIENTS_DIR, file_name)
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        logger.error(f"Can't read json file {file_path}.")

    return data


def load_ingredients(file_name: str) -> None:
    ingredients = read_json_file(file_name)
    for ingredient in ingredients:
        Ingredient.objects.create(
            name=ingredient.get("name"),
            measurement_unit=ingredient.get("measurement_unit")
        )
    logger.info("Ingredients loaded into database.")


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Загружаем json файл c ингредиентами')
        load_ingredients("ingredients.json")
