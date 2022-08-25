import random


# [{'times':3,'number':[3,2],'result':'win'}]
last_result = []

def game_menu():
    print("Now you are in the game!")
    selected_number = ""
    selected_type = ""
    control_number = input("Please enter the game information and begin the game:\n1.Select the Number of Dice:\n2.Select the Type of Dice:\n3.Roll Dice:\n4.Check Win/Lose:\n5.Exit Game:\nCurrent number of dices:" + selected_number + "\nCurrent type of  dice:" + selected_type)
    while control_number in ['1', '2', '3', '4', '5']:
        one_game_dict = {}
        
        if selected_type != "" and control_number == '2':
            print("You only have one chance to select the type of the dice during once game")
            continue
        if control_number == '1':
            selected_number = select_the_number_of_dice()
        elif control_number == '2':
            selected_type = select_the_type_of_dice()

        #开始掷色子
        elif control_number == '3':
            if selected_number == '' or selected_type == '':
                print("select type and select number all need,please select")
                continue
            dice_resurt_list = []
            results_of_game = roll_dice(selected_number, selected_type)
            dice_resurt_list.append(results_of_game)
        elif control_number == '4':
            pass
        elif control_number == '5':

            exit_game()

        else:
            print("Please input the right number!")
            game_menu()



def select_the_number_of_dice():
    list1 = [2, 3, 4, 5, 6]
    number_of_dice = input(
        "Please select how many dices do you want to use?(you cna only select between 2 to 6) number of dice:")
    while int(number_of_dice) not in list1:
        number_of_dice = input("Please type the number between 2 to 6! type number of dice again:")
    return number_of_dice


def select_the_type_of_dice():
    list2 = [6, 8, 9]
    type_of_dice = input(
        "Please select which type dice do you want to use?(you cna only select below three type dices by input number 6,8 or 9):\n6. the dice will have values 1, 2, 3, 4, 5, or 6.\n8.the dice will have values 2, 2, 3, 3, 4, or 8.\n9.the dice will have values 1, 1, 1, 1, 5, 9.) \nPlease enter the tyoe of dice here:")
    while int(type_of_dice) not in list2:
        type_of_dice = input("Please type the number 6,8 or 9 only! enter the type of dice again:")
    return type_of_dice


def roll_dice(number_of_dice, type_of_dice):
    if number_of_dice not in [2, 3, 4, 5, 6] or type_of_dice not in [6, 8, 9]:
        print("Please select how many dices and which type dice do you want to use firstly")
        game_menu()
    else:
        roll_times = roll_times + 1
        results_list = []
        list_6 = [1, 2, 3, 4, 5, 6]
        list_8 = [2, 2, 3, 3, 4, 8]
        list_9 = [1, 1, 1, 1, 5, 9]
        for i in range(number_of_dice):
            if int(type_of_dice) == 6:
                num_items1 = len(list_6)
                random_index = random.randrange(num_items1)
                roll_results = list_6[random_index]
                results_list.append(roll_results)
            elif int(type_of_dice) == 8:
                num_items2 = len(list_8)
                random_index = random.randrange(num_items2)
                roll_results = list_8[random_index]
                results_list.append(roll_results)
            elif int(type_of_dice) == 9:
                num_items3 = len(list_9)
                random_index = random.randrange(num_items3)
                roll_results = list_9[random_index]
                results_list.append(roll_results)
            else:
                print("Please input the right number of type of dice!")
                game_menu()
            game_results = tuple(results_list)
            game_results2 = map(int, game_results)
            results_of_game = tuple(game_results2)

            return results_of_game


def check_results(dice_result_list):
    pass


def exit_game():
    print("You are exiting this game!")
    print("We will go to the initial menu!")
    main()


def game_history():
    # [{'times':3,'number':[3,2],'result':'win'}]
    game_result = sorted(last_result, key=lambda x:x['times'])
    for i in game_result:
        time = i['time']
        number = i['number']
        result = i['result']
        print(f"Dice rolling times: {time}, Number of dice: {number}, Result: {result}")


def main():
    #game_result_list = []
    select_number = '1'
    while True:
        print("Hello, welcome to the game!\n1.Start Game:\n2.Game History:\n3.Exit Program:")
        select_number = input("Please input the number to enter: ")
        if select_number == '1':
            game_menu()
        elif select_number == '2':
            game_history()
        elif select_number == '3':
            print("ByeBye!")
            break
        else:
            print("Please type the right number,you can only select'1,2 or 3'")
            continue


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
