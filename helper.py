def chooise_integer_strict(include=[], question=""):
    chooise = input(question)
    if len(chooise) > 12:
        print("\n\tCannot insert value that exceeds the limit (on 100 billion), Please try again\n")
        return chooise_integer_strict(include=include, question=question)
    if chooise.isdigit() is False:
        print("\n\tOptions is not available, Try Again\n")
        return chooise_integer_strict(include=include, question=question)
    elif include != [] and int(chooise) not in include:
        print("\n\tOptions is not available, Try Again\n")
        return chooise_integer_strict(include=include, question=question)
    print("")
    return int(chooise)


def value_formatting(data:float=0.0) -> str:
    data = str(data) if type(data) == float else str(float(data))
    sep_data = data.split(".")
    digit, comma = sep_data[0], sep_data[1][:3]
    group = []
    while digit and digit[-1].isdigit():
        group.append(digit[-3:])
        digit = digit[:-3]
    return ",".join(reversed(group)) + "." + comma


def replacing(data="", rep=" ", be=""):
    data = data.replace(rep, "")
    return data
