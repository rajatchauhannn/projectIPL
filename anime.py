import json

while True:
    question=input("Enter question : ")
    options=input("Enter options divded by (,) : ")
    correct_answer=input("Enter correct answer : ")

    print("\n")

    options = list(options.split(','))
    
    entry={'question': question, 'options': options, 'correct_answer': correct_answer}

    with open('anime.json', "r") as file:
        data = json.load(file)

    data.append(entry)

    with open('anime.json', "w") as file:
        json.dump(data, file)


