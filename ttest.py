# Ein einzelnes Wort farbig machen (z. B. "rot")
text = f"Hallo, dieser Text ist ganz normal und das Wort \033[31mrot\033[0m wird farbig angezeigt."
print(text)
text = f"Hallo, dieser Text ist ganz normal und das Wort \033[0;34mblau\033[0m wird farbig angezeigt."
print(text)
