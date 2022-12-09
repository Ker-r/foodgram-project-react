from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


@staticmethod
def download_file(dictionary):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; \
    filename="ShopList.pdf"'
    begin_position_x, begin_position_y = 40, 50
    leaf = canvas.Canvas(response, pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', 'data/FreeSas.ttf'))
    leaf.setFont('FreeSans', 50)
    leaf.setTitle('Список покупок')
    leaf.drawString(
        begin_position_x, begin_position_y + 40,
        'Список покупок: '
    )
    leaf.setFont('FreeSans', 24)
    for num, item in enumerate(dictionary, start=1):
        if begin_position_y < 100:
            begin_position_y = 700
            leaf.showPage()
            leaf.setFont('FreeSans', 24)
        leaf.drawString(
            begin_position_x, begin_position_y,
            f'{num}. {item["ingredient__name"]} - '
            f'{item["ingredient_total"]}'
            f'{item["ingredient__measurement_unit"]}'
        )
        begin_position_y -= 30
        leaf.save()
        return response
