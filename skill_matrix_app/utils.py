from django.contrib.auth.tokens import PasswordResetTokenGenerator
import matplotlib.pyplot as plt
import base64
from io import BytesIO

class TokenGenerator(PasswordResetTokenGenerator):
    pass

generate_token=TokenGenerator()


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, y):
    plt.switch_backend('AGG')
    plt.figure(figsize=(9, 3))
    plt.title('')
    plt.plot(x, y, marker=".", color='#17a2b8')
    plt.xticks(rotation=45)
    # plt.xlabel('data')
    # plt.ylabel('poziom')
    # plt.box(False)
    ax = plt.gca()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.grid()
    plt.tight_layout()
    graph = get_graph()
    return graph