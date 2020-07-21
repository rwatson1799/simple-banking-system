import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS card (
    id INTEGER,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
);
''')
conn.commit()


logged_in_account = None


def create_account():
    # create unique number
    acc_no = ''
    while len(acc_no) != 15:
        acc_no = '400000' + str(random.randint(000000000, 999999999))

    # calculate check sum
    checksum = [int(val) * 2 if (idx + 1) % 2 != 0 else int(val) for idx, val in enumerate(acc_no)]
    checksum = [val - 9 if val > 9 else val for val in checksum]
    checksum = sum(checksum)
    checksum = (checksum * 9) % 10

    # add checksum
    acc_no += str(checksum)

    # set pin number
    pin = 0
    while len(str(pin)) != 4:
        pin = random.randint(0000, 9999)
    pin = str(pin)

    return acc_no, pin


def pass_luhn_algorithm(card_num):
    nums = [int(val) * 2 if (idx + 1) % 2 != 0 else int(val) for idx, val in enumerate(card_num)]
    nums = [val - 9 if val > 9 else val for val in nums]
    return sum(nums) % 10 == 0


# interface
choice = -99
while choice != 0:
    # print prompt
    print("""1. Create an account
2. Log into account
0. Exit""")

    # get choice
    choice = int(input())
    print('\n')

    # create account
    if choice == 1:
        new_acc_no, new_pin = create_account()
        print('Your card has been created')
        print(f'Your card number:\n{new_acc_no}')
        print(f'Your card PIN:\n{new_pin}')
        print('\n')

        # insert into database
        cur.execute(f'INSERT INTO card (number, pin) VALUES ({new_acc_no}, {new_pin})')
        conn.commit()

    # log into account
    elif choice == 2:
        card_no = input('Enter your card number:\n')
        pin_no = int(input('Enter your PIN:\n'))
        print('\n')

        # try to log into account
        cur.execute(f'SELECT * FROM card WHERE number = {card_no} AND pin = {pin_no}')
        logged_in_account = cur.fetchone()

        if logged_in_account is not None:

            print('You have successfully logged in!')
            print('\n')

            option = -99
            while option != 0:
                logged_in_account = cur.execute(f'SELECT * FROM card WHERE number = {card_no} AND pin = {pin_no}').fetchone()
                logged_in_account = tuple(logged_in_account)

                # print prompt
                print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")

                # get choice
                option = int(input())
                print('\n')

                if option == 1:
                    print(f'Balance: {logged_in_account[3]}')
                    print('\n')
                elif option == 2:
                    print('Enter income:')
                    income = int(input())

                    # Add income to balance in database
                    cur.execute(f'UPDATE card SET balance = balance + {income} WHERE number = {logged_in_account[1]};')
                    conn.commit()

                    print('Income was added!')
                    print('\n')

                elif option == 3:
                    print('Enter card number:')
                    card_to_transfer_to = input()

                    # Check if valid card
                    if not pass_luhn_algorithm(card_to_transfer_to):
                        print('Probably you made mistake in the card number. Please try again!')
                        print('\n')
                        continue

                    # Check if same card
                    if card_to_transfer_to == logged_in_account[1]:
                        print("You can't transfer money to the same account!")
                        print('\n')
                        continue

                    # Check if card exists
                    cur.execute(f'SELECT * FROM card WHERE number = {card_to_transfer_to}')
                    card_to_transfer_to = cur.fetchone()
                    if card_to_transfer_to is not None:
                        card_to_transfer_to = tuple(card_to_transfer_to)
                        print('Enter how much money you want to transfer:')
                        transfer_amt = int(input())

                        # Check if user has enough money
                        if transfer_amt <= logged_in_account[3]:
                            # Transfer amount
                            cur.execute(f'UPDATE card SET balance = balance - {transfer_amt} WHERE number = {logged_in_account[1]};')
                            conn.commit()
                            cur.execute(f'UPDATE card SET balance = balance + {transfer_amt} WHERE number = {card_to_transfer_to[1]};')
                            conn.commit()
                            print('Success!')
                            print('\n')
                        else:
                            print('Not enough money!')
                            print('\n')
                    else:
                        print('Such a card does not exist.')
                        print('\n')

                elif option == 4:
                    cur.execute(f'DELETE FROM card WHERE number = {logged_in_account[1]};')
                    conn.commit()
                    print('The account has been closed!')
                    print('\n')
                    logged_in_account = None
                    break
                elif option == 5:
                    print('You have successfully logged out!')
                    print('\n')
                    logged_in_account = None
                    break
            else:
                print('Bye!')
                break
        else:
            print('Wrong card number or PIN!')
            print('\n')
else:
    print('Bye!')
    conn.close()
