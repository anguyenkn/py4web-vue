PRODUCT_LIST = [
    dict(id=1, name="Teddy Bear", file="teddy_bear.jpg"),
    dict(id=2, name="Colander", file="colander.jpg"),
    dict(id=3, name="Rabbit", file="rabbit.jpg"),
    dict(id=4, name="Cowboy Hat", file="cowboy_hat.jpg"),
    dict(id=5, name="Rubber Duck", file="rubber-duck.jpg"),
    dict(id=6, name="Espresso Cup", file="coffeecup.jpg"),
]

product_dict = {prod['id']: prod for prod in PRODUCT_LIST}

def split_list(l, n):
    """Splits a list l into lists of length n max, and returns the
    list of lists."""
    return [l[k * n : (k + 1) * n]
            for k in range(1 + (len(l) - 1) // n)]
            