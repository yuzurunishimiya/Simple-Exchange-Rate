
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from helper import (
    chooise_integer_strict,
    value_formatting,
    replacing
)

import json
import pprint
import requests


def soup_parsing(content):
    collection_data = []
    soup = BeautifulSoup(content, "html.parser")
    date = soup.find(id="ctl00_PlaceHolderMain_biWebKursTransaksiBI_lblUpdate").text if soup.find(id="ctl00_PlaceHolderMain_biWebKursTransaksiBI_lblUpdate") else ""
    table = soup.find(id="ctl00_PlaceHolderMain_biWebKursTransaksiBI_GridView1")
    tdata = table.find_all("tr")
    for d in tdata:
        try:
            data = {}
            table_data = d.find_all("td")
            if len(table_data) >= 4:
                data["currency"] = replacing(data=table_data[0].text, rep=" ")
                data["value"] = float(replacing(data=table_data[1].text, rep=","))
                data["selling_rate"] = float(replacing(data=table_data[2].text, rep=","))
                data["buying_rate"] = float(replacing(data=table_data[3].text, rep=","))
                collection_data.append(data)
        except:
            continue
    return collection_data, date


def open_file(name=""):
    data = {}
    try:
        with open(name, "rb") as fp:
            data = json.load(fp)
            fp.close()
    except:
        pass
    return data


def printing_data(data=[], dict_name={}):
    x = PrettyTable()
    x.field_names = ["Code", "Currency", "Value", "Selling Rate", "Buying Rate"]
    for coll in data:
        x.add_row([coll["currency"], dict_name.get(coll["currency"], "-"), value_formatting(coll["value"]), value_formatting(coll["selling_rate"]), value_formatting(coll["buying_rate"])])
    print(x)


def convert_value(data=[], convert_val=1, chooise=0, rate_type=1):
    new_data = list()
    if chooise == 1:
        for coll in data:
            new_coll = coll.copy()
            new_coll["selling_rate"] = coll["selling_rate"] * convert_val
            new_coll["buying_rate"] = coll["buying_rate"] * convert_val
            new_coll["value"] = coll["value"] * convert_val
            new_data.append(new_coll)
        return new_data
    elif chooise == 2:
        if rate_type == 1:
            for coll in data:
                new_coll = coll.copy()
                new_coll["value"] = (convert_val*new_coll["value"]) / new_coll["selling_rate"]
                new_coll["selling_rate"] = float(convert_val)
                new_coll["buying_rate"] = 0
                new_data.append(new_coll)
        elif rate_type == 2:
            for coll in data:
                new_coll = coll.copy()
                new_coll["value"] = (convert_val*new_coll["value"]) / new_coll["buying_rate"]
                new_coll["selling_rate"] = 0
                new_coll["buying_rate"] = float(convert_val)
                new_data.append(new_coll)
    return new_data


def set_menu() -> int:
    question = "Menu: \n1. MULTIPLE OF VALUE FOR EACH CURRENCY\n2. CONVERSIONS FOR EACH CURRENCY FROM INDONESIAN RUPIAH\n3. CONVERSION OF ONE FOREIGN CURRENCRY TO RUPIAH, VICE VERSA\n\
    Your Chooise: "
    chooise = chooise_integer_strict(include=[1,2,3], question=question)
    return chooise


def process_menu(chooise, data=[], dict_name=[]):
    if chooise == 1:
        multiple = chooise_integer_strict(question="Multiple Value (on digits): ")
        new_data = convert_value(data=data, convert_val=multiple, chooise=1)
        return new_data
    elif chooise == 2:
        question = "Rate Options\n\
        1. Selling Rate\n\
        2. Buying Rate\n\
            Your Chooise: "
        type_rate = chooise_integer_strict(include=[1,2], question=question)
        idr_val = chooise_integer_strict(question="Insert value in IDR (without any comma or dot): ")
        if type_rate == 1:
            new_data = convert_value(data=data, convert_val=idr_val, chooise=2, rate_type=1)
        elif type_rate == 2:
            new_data = convert_value(data=data, convert_val=idr_val, chooise=2, rate_type=2)
        return new_data
    elif chooise == 3:
        code = input("insert Code (example JPY or jpy): ").upper()
        if code in dict_name:
            question = "Conversion Type\n\
            1. IDR to {0}\n\
            2. {0} to IDR\n\
            Your Chooise: ".format(code)
            new_coll = {}
            for coll in data:
                if coll["currency"] == code:
                    new_coll = coll.copy()
                    break
            which_conversion = chooise_integer_strict(include=[1,2], question=question)

            if which_conversion == 1:
                question = "Rate Options\n\
            1. Selling Rate\n\
            2. Buying Rate\n\
                Your Chooise: "
                type_rate = chooise_integer_strict(include=[1,2], question=question)
                idr_val = chooise_integer_strict(question="insert value in IDR: ")

                if type_rate == 1:
                    new_coll["value"] = idr_val*new_coll["value"] / new_coll["selling_rate"]
                    new_coll["buying_rate"] = 0
                    new_coll["selling_rate"] = idr_val
                elif type_rate == 2:
                    new_coll["value"] = idr_val*new_coll["value"] / new_coll["buying_rate"]
                    new_coll["buying_rate"] = idr_val
                    new_coll["selling_rate"] = 0

            elif which_conversion == 2:
                code_val = chooise_integer_strict(question="Insert Value in {}: ".format(new_coll["currency"]))
                new_coll["value"] = code_val
                new_coll["buying_rate"] *= code_val
                new_coll["selling_rate"] *= code_val

            return [new_coll]
        else:
            print("Currency code not found, Try Again")
            return process_menu(chooise, data=data, dict_name=dict_name)

def main(json_data, collection_data):
    print("=====>     RATE RUPIAH TO OTHERS CURRENCIES, UPDATED AT: {}     <=====".format(date))
    printing_data(data=collection_data, dict_name=json_data)
    print("\n"*2)
    chooise = set_menu()
    new_data = process_menu(chooise, data=collection_data, dict_name=json_data)
    printing_data(data=new_data, dict_name=json_data)
    print("\n"*2)
    question = "Options:\n\
    1. Repeat\n\
    Press any to exit\n\
    Your Chooise: "
    chooise = input(question)
    if chooise == "1":
        main(json_data=json_data, collection_data=collection_data)
    exit()


if __name__ == "__main__":
    json_data = open_file(name="currencies.json")
    site = "https://www.bi.go.id/id/moneter/informasi-kurs/transaksi-bi/Default.aspx"
    r = requests.get(site)
    collection_data, date = soup_parsing(r.content)
    status = True
    main(json_data, collection_data)
