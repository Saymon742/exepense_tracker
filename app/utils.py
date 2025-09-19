import base64
from typing import List
from datetime import datetime
import csv
from io import StringIO

def generate_expense_chart(expenses_data: List):
    """Генерация простого текстового отчета вместо графика"""
    if not expenses_data:
        return "Нет данных для отображения"
    
    report = "Отчет по расходам:\n"
    report += "=" * 30 + "\n"
    
    for item in expenses_data:
        category = item[0].value if hasattr(item[0], 'value') else str(item[0])
        report += f"{category}: {item[1]:.2f} руб. ({item[2]} записей)\n"
    
    return report

def generate_csv_report(expenses_data: List):
    """Генерация CSV отчета без pandas"""
    output = StringIO()
    writer = csv.writer(output)
    
    # Заголовки
    writer.writerow(['Категория', 'Сумма', 'Количество'])
    
    # Данные
    for item in expenses_data:
        category = item[0].value if hasattr(item[0], 'value') else str(item[0])
        writer.writerow([category, item[1], item[2]])
    
    return output.getvalue()