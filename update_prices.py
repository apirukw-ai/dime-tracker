for fund in funds:

    code = fund["code"]

    quote = Finnhub(code)

    fund["currentNav"] = quote["c"]

save firebase
