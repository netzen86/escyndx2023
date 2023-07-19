def parse_log(filename):
    '''parse log'''
    dict_unic = {"user": "", "ip": "", "dom": ""}
    user_dict = {}
    with open(filename, "r", encoding="utf-8") as logfile:
        for row in logfile:
            if "User" in row:
                dict_unic["user"] = row.split(":")[1].strip()
            if "IP" in row:
                dict_unic["ip"] = row.split(":")[1].strip()
            if "In domain" in row:
                dict_unic["dom"] = row.split(":")[1].strip()
            if '---"' in row:
                if (
                    (dict_unic["dom"] == "False")
                    and (dict_unic["ip"][0:10] == "67.45.123.")
                    and (int(dict_unic["ip"][10:]) in range(126))
                ):
                    user_dict[dict_unic["user"]] = ""
                    dict_unic.clear()
        print(len(user_dict))


if __name__ == "__main__":
    parse_log("log.txt")
