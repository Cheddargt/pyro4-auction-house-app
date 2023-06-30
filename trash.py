""" def login(name):
    global client_name
    client_name = name
    print("Digite sua senha:")
    password = input()
    res = auction_house.login(name, password)
    if res==200:
        print("Login successful!")
        print("-------------------------------------")
    elif res==500:
        print("Login failed. Client does not exist.")
        print("-------------------------------------")
        register(name)
    else:
        print("Login failed. Wrong password.")
        print("-------------------------------------")
        login(name) """
