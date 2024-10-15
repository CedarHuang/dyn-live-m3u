import quickjs

def check(dict, key, value):
    if key not in dict:
        dict[key] = value

def jsobject2json(str):
    stringify = quickjs.Function(
        "stringify",
        """
        function stringify() {{
            object = {str};
            return JSON.stringify(object);
        }}
        """.format(str = str))
    return stringify(str)
