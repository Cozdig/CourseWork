from src.reports import spending_by_category
from src.services import re_sort
from src.utils import read_xlsx
from src.views import main_views


def main():
    """Главная функция. Запускает все остальные функции и выдает результат в json файлах."""
    date_string = "11.07.2020 23:11:24"
    main_views(date_string)
    df = read_xlsx(input_file="../data/operations.xlsx")
    re_sort(df, "Колхоз")
    spending_by_category(df, "Супермаркеты", "30.07.2021")


main()
